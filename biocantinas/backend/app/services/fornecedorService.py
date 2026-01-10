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
    def criar_fornecedor(self, data: FornecedorCreateDTO, usuario_id: int) -> FornecedorDTO:
        # Verificar se o usuário já tem um fornecedor registado
        fornecedores_existentes = self.repo.listar_fornecedores()
        fornecedor_existente = None
        for f in fornecedores_existentes:
            if f.usuario_id == usuario_id:
                fornecedor_existente = f
                break
        
        # Se já existe fornecedor para este usuário, verificar produtos duplicados
        if fornecedor_existente:
            produtos_existentes_ids = {p.produto_id for p in fornecedor_existente.produtos}
            produtos_novos_ids = {p.produto_id for p in data.produtos}
            
            # Verificar se há duplicados
            duplicados = produtos_existentes_ids & produtos_novos_ids
            if duplicados:
                raise ValueError(f"Produto(s) já registado(s) por este fornecedor: {duplicados}")
        
        # ID é atribuído pelo autoincrement da BD
        model = dto_to_model_create(data, new_id=0)
        model.usuario_id = usuario_id  # Vincular ao usuário
        
        # Reprovar automaticamente se não for produtor local
        if not model.local:
            model.aprovado = False
        
        stored = self.repo.criar_fornecedor(model)
        return model_to_dto(stored)

    def listar_fornecedores(self) -> List[FornecedorDTO]:
        return [model_to_dto(m) for m in self.repo.listar_fornecedores()]

    def obter_fornecedor(self, fid: int) -> FornecedorDTO | None:
        m = self.repo.obter_fornecedor(fid)
        return model_to_dto(m) if m else None

    def obter_fornecedor_por_nome(self, nome: str) -> FornecedorDTO | None:
        """Obtém fornecedor pelo nome (usado para matching com username)"""
        fornecedores = self.repo.listar_fornecedores()
        for f in fornecedores:
            if f.nome.lower() == nome.lower():
                return model_to_dto(f)
        return None
    
    def obter_fornecedor_por_usuario_id(self, usuario_id: int) -> FornecedorDTO | None:
        """Obtém fornecedor pelo ID do usuário"""
        fornecedores = self.repo.listar_fornecedores()
        for f in fornecedores:
            if f.usuario_id == usuario_id:
                return model_to_dto(f)
        return None

    def aprovar_fornecedor(self, fid: int, aprovado: bool) -> FornecedorDTO:
        fornecedor = self.repo.obter_fornecedor(fid)
        if not fornecedor:
            raise ValueError("Fornecedor não encontrado")
        
        # Regra: Apenas produtores locais podem ser aprovados
        if aprovado and not fornecedor.local:
            raise ValueError("Apenas produtores locais podem ser aprovados")
        
        fornecedor.aprovado = aprovado
        self.repo.atualizar_fornecedor(fornecedor)
        return model_to_dto(fornecedor)

    def calcular_ordem_por_produto(self) -> List[OrdemFornecedor]:
        # Apenas produtores aprovados E locais
        fornecedores = [f for f in self.repo.listar_fornecedores() if f.aprovado and f.local]
        
        # Mapa: nome_produto -> lista de tuplas (fornecedor, produto)
        mapa: Dict[str, List[tuple]] = {}

        for f in fornecedores:
            for p in f.produtos:
                mapa.setdefault(p.produto_nome, []).append((f, p))

        ordens: List[OrdemFornecedor] = []
        for nome_produto, lista_tuplas in mapa.items():
            # Ordenar por:
            # 1. Local (sempre True aqui, já filtrado)
            # 2. Certificado (True primeiro)
            # 3. Biológico com prioridade especial:
            #    - Certificado + Biológico = 0 (mais alta)
            #    - Certificado + Não Biológico = 1
            #    - Não Certificado + Não Biológico = 2
            #    - Não Certificado + Biológico = 3 (mais baixa)
            # 4. Data de inscrição (mais antigo primeiro)
            lista_ordenada = sorted(
                lista_tuplas,
                key=lambda item: (
                    0 if item[0].certificado else 1,  # certificados primeiro
                    self._calcular_prioridade_biologico(item[0].certificado, item[1].biologico),
                    item[0].data_inscricao
                )
            )
            ordens.append(
                OrdemFornecedor(
                    produto=nome_produto,
                    fornecedores_ids=[f.id for f, p in lista_ordenada]
                )
            )
        return ordens
    
    def _calcular_prioridade_biologico(self, certificado: bool, biologico: bool) -> int:
        """Calcula prioridade baseada em certificação e se produto é biológico.
        
        Prioridade (menor = melhor):
        0: Certificado + Biológico
        1: Certificado + Não Biológico  
        2: Não Certificado + Não Biológico
        3: Não Certificado + Biológico
        """
        if certificado and biologico:
            return 0
        elif certificado and not biologico:
            return 1
        elif not certificado and not biologico:
            return 2
        else:  # not certificado and biologico
            return 3

_services = Services()

def get_services() -> Services:
    return _services
