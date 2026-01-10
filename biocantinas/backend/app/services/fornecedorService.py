from typing import List, Dict, Protocol
from ..dtos.fornecedorDTO import Fornecedor as FornecedorDTO, OrdemFornecedor, FornecedorCreate as FornecedorCreateDTO, ProdutoFornecedorAdd
from ..models.fornecedor import FornecedorModel
from ..models.produto import ProdutoFornecedorModel
from ..mappings.mappers import dto_to_model_create, model_to_dto
from ..db.session import SessionLocal, init_db
from ..repositories.fornecedorRepo import FornecedorRepo
from ..models.catalogo_produtos import obter_info_produto

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
        # ID é atribuído pelo autoincrement da BD
        model = dto_to_model_create(data, new_id=0)
        model.usuario_id = usuario_id  # Vincular ao usuário
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
    
    def adicionar_produto_fornecedor(self, usuario_id: int, produto_data: ProdutoFornecedorAdd) -> FornecedorDTO:
        """Adiciona um novo produto a um fornecedor existente"""
        fornecedor = None
        for f in self.repo.listar_fornecedores():
            if f.usuario_id == usuario_id:
                fornecedor = f
                break
        
        if not fornecedor:
            raise ValueError("Fornecedor não encontrado")
        
        # Obter o tipo do produto do catálogo
        produto_info = obter_info_produto(produto_data.nome)
        tipo_produto = produto_info.categoria if produto_info else "Outro"
        
        # Criar novo produto
        novo_produto = ProdutoFornecedorModel(
            nome=produto_data.nome,
            tipo=tipo_produto,
            biologico=produto_data.biologico,
            semana_producao_inicio=produto_data.semana_producao_inicio,
            semana_producao_fim=produto_data.semana_producao_fim,
            capacidade=produto_data.capacidade,
            unidade=produto_data.unidade,
            certificado=produto_data.certificado,
        )
        
        # Adicionar ao fornecedor
        fornecedor.produtos.append(novo_produto)
        
        # Atualizar no banco de dados
        self.repo.atualizar_fornecedor(fornecedor)
        
        return model_to_dto(fornecedor)

    def aprovar_fornecedor(self, fid: int, aprovado: bool) -> FornecedorDTO:
        fornecedor = self.repo.obter_fornecedor(fid)
        if not fornecedor:
            raise ValueError("Fornecedor não encontrado")
        fornecedor.aprovado = aprovado
        self.repo.atualizar_fornecedor(fornecedor)
        return model_to_dto(fornecedor)

    def calcular_ordem_por_produto(self, semana: int, fator_correcao: float = 1.0) -> List[OrdemFornecedor]:
        """Calcula ordem de prioridade dos fornecedores por produto.
        
        Filtra apenas fornecedores com produtos disponíveis na semana especificada.
        
        Critérios de ordenação:
        1. Apenas fornecedores com produto disponível naquela semana
        2. Ordenação por data de inscrição (mais antigo = maior prioridade)
        
        Args:
            semana: número da semana do ano (1-52). Obrigatório e deve estar entre 1 e 52.
            fator_correcao: multiplicador para ajustar as necessidades (padrão 1.0).
            
        Raises:
            ValueError: Se semana não está entre 1 e 52.
        """
        if not (1 <= semana <= 52):
            raise ValueError(f"Semana deve estar entre 1 e 52, recebido: {semana}")
        
        fornecedores = [f for f in self.repo.listar_fornecedores() if f.aprovado]
        mapa: Dict[str, List[FornecedorModel]] = {}

        for f in fornecedores:
            for p in f.produtos:
                # Verificar se o produto está disponível nesta semana
                if not (p.semana_producao_inicio <= semana <= p.semana_producao_fim):
                    # Produto não está disponível nesta semana
                    continue
                
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
