from typing import List, Dict, Protocol
from ..dtos.fornecedorDTO import Fornecedor as FornecedorDTO, OrdemFornecedor, FornecedorCreate as FornecedorCreateDTO
from ..models.fornecedor import FornecedorModel
from ..mappings.mappers import dto_to_model_create, model_to_dto
from ..db.session import SessionLocal, init_db
from ..repositories.fornecedorRepo import FornecedorRepo

class Repository(Protocol):
    def criar_fornecedor(self, model: FornecedorModel) -> FornecedorModel: ...
    def listar_fornecedores(self) -> List[FornecedorModel]: ...
    def obter_fornecedor(self, fid: int) -> FornecedorModel | None: ...
    def atualizar_fornecedor(self, f: FornecedorModel) -> None: ...

class SqlRepository:
    def __init__(self):
        init_db()
        self.session = SessionLocal()
        self.repo = FornecedorRepo(self.session)

    def criar_fornecedor(self, model: FornecedorModel) -> FornecedorModel:
        return self.repo.criar_fornecedor(model)

    def listar_fornecedores(self) -> List[FornecedorModel]:
        return self.repo.listar_fornecedores()

    def obter_fornecedor(self, fid: int) -> FornecedorModel | None:
        return self.repo.obter_fornecedor(fid)

    def atualizar_fornecedor(self, f: FornecedorModel) -> None:
        self.repo.atualizar_fornecedor(f)

class Services:
    def __init__(self, repo: Repository | None = None):
        self.repo: Repository = repo or SqlRepository()

    # CRUD + business
    def criar_fornecedor(self, data: FornecedorCreateDTO) -> FornecedorDTO:
        # ID é atribuído pelo autoincrement da BD
        model = dto_to_model_create(data, new_id=0)
        stored = self.repo.criar_fornecedor(model)
        return model_to_dto(stored)

    def listar_fornecedores(self) -> List[FornecedorDTO]:
        return [model_to_dto(m) for m in self.repo.listar_fornecedores()]

    def obter_fornecedor(self, fid: int) -> FornecedorDTO | None:
        m = self.repo.obter_fornecedor(fid)
        return model_to_dto(m) if m else None

    def aprovar_fornecedor(self, fid: int, aprovado: bool) -> FornecedorDTO:
        fornecedor = self.repo.obter_fornecedor(fid)
        if not fornecedor:
            raise ValueError("Fornecedor não encontrado")
        fornecedor.aprovado = aprovado
        self.repo.atualizar_fornecedor(fornecedor)
        return model_to_dto(fornecedor)

    def calcular_ordem_por_produto(self) -> List[OrdemFornecedor]:
        fornecedores = [f for f in self.repo.listar_fornecedores() if f.aprovado]
        mapa: Dict[str, List[FornecedorModel]] = {}

        for f in fornecedores:
            for p in f.produtos:
                mapa.setdefault(p.nome, []).append(f)

        ordens: List[OrdemFornecedor] = []
        for nome_produto, lista in mapa.items():
            lista_ordenada = sorted(lista, key=lambda f: f.data_inscricao)
            ordens.append(
                OrdemFornecedor(
                    produto=nome_produto,
                    fornecedores_ids=[f.id for f in lista_ordenada]
                )
            )
        return ordens

_services = Services()

def get_services() -> Services:
    return _services
