from typing import List, Dict, Protocol
from datetime import date
from ..dtos.fornecedorDTO import (
    Fornecedor as FornecedorDTO,
    OrdemFornecedor,
    FornecedorCreate as FornecedorCreateDTO,
    ProdutoFornecedorAdd,
    FornecedorEstadoUpdate,
    FreguesiaFecho,
)
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
    def atualizar_estado(self, fornecedor_id: int, em_quarentena: bool | None, freguesia: str | None) -> None: ...
    def adicionar_produto(self, fornecedor_id: int, produto: ProdutoFornecedorModel) -> None: ...
    def definir_fecho_freguesia(self, nome: str, ativo: bool): ...
    def listar_fechos_freguesia(self, apenas_ativos: bool = False): ...

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

    def atualizar_estado(self, fornecedor_id: int, em_quarentena: bool | None, freguesia: str | None) -> None:
        self.repo.atualizar_estado(fornecedor_id, em_quarentena, freguesia)

    def adicionar_produto(self, fornecedor_id: int, produto: ProdutoFornecedorModel) -> None:
        self.repo.adicionar_produto(fornecedor_id, produto)

    def definir_fecho_freguesia(self, nome: str, ativo: bool):
        return self.repo.definir_fecho_freguesia(nome, ativo)

    def listar_fechos_freguesia(self, apenas_ativos: bool = False):
        return self.repo.listar_fechos_freguesia(apenas_ativos)

class Services:
    def __init__(self, repo: Repository | None = None):
        self.repo: Repository = repo or SqlRepository()

    # CRUD + business
    def criar_fornecedor(self, data: FornecedorCreateDTO, usuario_id: int) -> FornecedorDTO:
        # ID é atribuído pelo autoincrement da BD
        # Garantir que não há produtos duplicados no payload
        nomes = [p.nome.strip().lower() for p in data.produtos]
        if len(nomes) != len(set(nomes)):
            raise ValueError("O mesmo produto não pode ser registrado duas vezes para o fornecedor.")

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

    def atualizar_estado_fornecedor(self, fid: int, estado: FornecedorEstadoUpdate) -> FornecedorDTO:
        fornecedor = self.repo.obter_fornecedor(fid)
        if not fornecedor:
            raise ValueError("Fornecedor não encontrado")
        self.repo.atualizar_estado(fid, estado.em_quarentena, estado.freguesia)
        atualizado = self.repo.obter_fornecedor(fid)
        return model_to_dto(atualizado)
    
    def adicionar_produto_fornecedor(self, usuario_id: int, produto_data: ProdutoFornecedorAdd) -> FornecedorDTO:
        """Adiciona um novo produto a um fornecedor existente"""
        fornecedor = None
        for f in self.repo.listar_fornecedores():
            if f.usuario_id == usuario_id:
                fornecedor = f
                break
        
        if not fornecedor:
            raise ValueError("Fornecedor não encontrado")

        # Impedir duplicação de produto para o mesmo fornecedor
        produto_nome = produto_data.nome.strip().lower()
        if any((p.nome or "").strip().lower() == produto_nome for p in fornecedor.produtos):
            raise ValueError("Este produto já está cadastrado para o fornecedor.")
        
        # Obter o tipo do produto do catálogo
        produto_info = obter_info_produto(produto_data.nome)
        tipo_produto = produto_info.categoria if produto_info else "Outro"
        
        # Criar novo produto
        novo_produto = ProdutoFornecedorModel(
            fornecedor_id=fornecedor.id,
            produto_id=0,  # Será preenchido pelo repo
            nome=produto_data.nome,
            tipo=tipo_produto,
            biologico=produto_data.biologico,
            semana_producao_inicio=produto_data.semana_producao_inicio,
            semana_producao_fim=produto_data.semana_producao_fim,
            capacidade=produto_data.capacidade,
            unidade_medida=produto_data.unidade,
            certificado=produto_data.certificado,
            data_inscricao=produto_data.data_inscricao or date.today(),
        )
        
        # Adicionar produto diretamente sem afetar os existentes
        self.repo.adicionar_produto(fornecedor.id, novo_produto)
        
        # Recarregar fornecedor atualizado
        fornecedor_atualizado = self.repo.obter_fornecedor(fornecedor.id)
        return model_to_dto(fornecedor_atualizado)

    def aprovar_fornecedor(self, fid: int, aprovado: bool) -> FornecedorDTO:
        fornecedor = self.repo.obter_fornecedor(fid)
        if not fornecedor:
            raise ValueError("Fornecedor não encontrado")

        # Não permitir aprovação se estiver em quarentena
        if aprovado and fornecedor.em_quarentena:
            raise ValueError("Fornecedor em quarentena não pode ser aprovado")

        # Não permitir aprovação se a freguesia estiver em fecho sanitário
        if aprovado and fornecedor.freguesia:
            fechadas = {f.nome.lower() for f in self.repo.listar_fechos_freguesia(apenas_ativos=True)}
            if fornecedor.freguesia.lower() in fechadas:
                raise ValueError("Freguesia em fecho sanitário não pode ser aprovada")

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
        
        fornecedores = [f for f in self.repo.listar_fornecedores() if f.aprovado and not f.em_quarentena]
        freguesias_bloqueadas = {f.nome.lower() for f in self.repo.listar_fechos_freguesia(apenas_ativos=True)}
        mapa: Dict[str, List[tuple]] = {}

        def _disponivel(semana_num: int, inicio: int, fim: int) -> bool:
            """Suporta intervalos lineares (inicio<=fim) e circulares (inicio>fim) cruzando fim de ano."""
            if inicio <= fim:
                return inicio <= semana_num <= fim
            return semana_num >= inicio or semana_num <= fim

        for f in fornecedores:
            for p in f.produtos:
                if not _disponivel(semana, p.semana_producao_inicio, p.semana_producao_fim):
                    continue

                # Bloquear fornecedores em fecho sanitário por freguesia
                if f.freguesia and f.freguesia.lower() in freguesias_bloqueadas:
                    continue
                
                mapa.setdefault(p.nome, []).append((f, p))

        ordens: List[OrdemFornecedor] = []
        for nome_produto, lista in mapa.items():
            # Ordenar por múltiplos critérios de prioridade
            lista_ordenada = sorted(
                lista,
                key=lambda x: (
                    # Prioridade 1: Data de inscrição (mais antigo = maior prioridade)
                    x[1].data_inscricao if x[1].data_inscricao else float('inf'),
                    # Prioridade 2: Produtor LOCAL
                    not (x[0].local or False),
                    # Prioridade 3: Certificação agrícola
                    not (x[0].certificado or False),
                    # Prioridade 4: Produto biológico
                    not (x[1].biologico or False),
                )
            )
            ordens.append(
                OrdemFornecedor(
                    produto=nome_produto,
                    fornecedores_ids=[f.id for f, p in lista_ordenada]
                )
            )
        return ordens

    def definir_fecho_freguesia(self, nome: str, ativo: bool) -> FreguesiaFecho:
        registro = self.repo.definir_fecho_freguesia(nome, ativo)

        # Se fechar uma freguesia, reprovar todos os fornecedores nela
        if ativo:
            nome_normalizado = (nome or "").strip().lower()
            if nome_normalizado:
                for f in self.repo.listar_fornecedores():
                    if (f.freguesia or "").strip().lower() == nome_normalizado:
                        f.aprovado = False
                        self.repo.atualizar_fornecedor(f)

        return FreguesiaFecho(nome=registro.nome, ativo=registro.ativo)

    def listar_fechos_freguesia(self, apenas_ativos: bool = False) -> List[FreguesiaFecho]:
        return [FreguesiaFecho(nome=r.nome, ativo=r.ativo) for r in self.repo.listar_fechos_freguesia(apenas_ativos)]

_services = Services()

def get_services() -> Services:
    return _services
