"""
Service para Receitas
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from ..repositories.receitaRepo import ReceitaRepository
from ..repositories.fornecedorRepo import FornecedorRepo
from ..dtos.receitaDTO import ReceitaDTO, ReceitaCreateDTO, ReceitaUpdateDTO, ItemReceitaDTO
from ..models.receita import ReceitaModel, ItemReceitaModel
from ..mappings.mappers import ReceitaMapper


class ReceitaService:
    """Service para lógica de negócio de receitas"""
    
    def __init__(self, session: Session):
        self.repository = ReceitaRepository(session)
        self.session = session
    
    def criar_receita(self, dto: ReceitaCreateDTO) -> ReceitaDTO:
        """Cria uma nova receita"""
        # Validar que os produtos existem
        self._validar_produtos(dto.ingredientes)
        
        # Converter DTO para Model
        model = ReceitaMapper.dto_create_to_model(dto)
        
        # Criar no repositório
        receita_criada = self.repository.criar_receita(model)
        
        # Converter para DTO de resposta
        return ReceitaMapper.model_to_dto(receita_criada)
    
    def listar_receitas(self, apenas_ativas: bool = True) -> List[ReceitaDTO]:
        """Lista todas as receitas"""
        receitas = self.repository.listar_receitas(apenas_ativas)
        return [ReceitaMapper.model_to_dto(r) for r in receitas]

    def listar_receitas_disponiveis_semana(self, semana: int, tipo: str | None = None, data: 'date | None' = None) -> List[ReceitaDTO]:
        """Lista receitas cujos ingredientes estão disponíveis na semana indicada.
        
        Args:
            semana: número da semana ISO (1-52)
            tipo: opcional para filtrar por tipo de refeição
            data: data opcional para validar o ano (evita receitas em anos sem produtos)
        """
        produtos_disponiveis = self._produtos_disponiveis_semana(semana, data)
        receitas = self.repository.listar_receitas(apenas_ativas=True)
        if tipo:
            receitas = [r for r in receitas if r.tipo_refeicao in [tipo, "ambos"]]
        disponiveis = [r for r in receitas if r.verifica_disponibilidade(produtos_disponiveis)]
        return [ReceitaMapper.model_to_dto(r) for r in disponiveis]
    
    def obter_receita(self, receita_id: int) -> Optional[ReceitaDTO]:
        """Obtém uma receita por ID"""
        receita = self.repository.obter_receita(receita_id)
        return ReceitaMapper.model_to_dto(receita) if receita else None
    
    def atualizar_receita(self, receita_id: int, dto: ReceitaUpdateDTO) -> Optional[ReceitaDTO]:
        """Atualiza uma receita existente"""
        # Validar produtos se ingredientes foram fornecidos
        if dto.ingredientes:
            self._validar_produtos(dto.ingredientes)
        
        # Converter para Model
        model = ReceitaMapper.dto_update_to_model(dto)
        
        # Atualizar
        receita_atualizada = self.repository.atualizar_receita(receita_id, model)
        
        return ReceitaMapper.model_to_dto(receita_atualizada) if receita_atualizada else None
    
    def deletar_receita(self, receita_id: int) -> bool:
        """Deleta (desativa) uma receita"""
        return self.repository.deletar_receita(receita_id)
    
    def listar_receitas_por_categoria(self, categoria: str) -> List[ReceitaDTO]:
        """Lista receitas de uma categoria"""
        receitas = self.repository.listar_receitas_por_categoria(categoria)
        return [ReceitaMapper.model_to_dto(r) for r in receitas]
    
    def listar_receitas_por_tipo(self, tipo_refeicao: str) -> List[ReceitaDTO]:
        """Lista receitas por tipo (almoço/jantar)"""
        receitas = self.repository.listar_receitas_por_tipo(tipo_refeicao)
        return [ReceitaMapper.model_to_dto(r) for r in receitas]
    
    def listar_receitas_disponiveis(self, produtos_disponiveis: dict) -> List[ReceitaDTO]:
        """
        Lista receitas que podem ser feitas com os produtos disponíveis
        produtos_disponiveis: dict {nome_produto: quantidade_disponivel}
        """
        todas_receitas = self.repository.listar_receitas(apenas_ativas=True)
        
        receitas_disponiveis = []
        for receita in todas_receitas:
            if receita.verifica_disponibilidade(produtos_disponiveis):
                receitas_disponiveis.append(ReceitaMapper.model_to_dto(receita))
        
        return receitas_disponiveis
    
    def calcular_necessidades_para_porcoes(self, receita_id: int, num_porcoes: int) -> dict:
        """Calcula as quantidades necessárias de cada ingrediente para N porções"""
        receita = self.repository.obter_receita(receita_id)
        
        if not receita:
            return None
        
        return {
            "receita_nome": receita.nome,
            "porcoes_solicitadas": num_porcoes,
            "ingredientes": receita.calcular_ingredientes_para_porcoes(num_porcoes)
        }
    
    def _validar_produtos(self, ingredientes: List[ItemReceitaDTO]):
        """Valida que todos os produtos existem no catálogo"""
        from ..db.models import ProdutoORM
        
        for ing in ingredientes:
            produto = self.session.query(ProdutoORM).filter(
                ProdutoORM.id == ing.produto_catalogo_id
            ).first()
            
            if not produto:
                raise ValueError(f"Produto com ID {ing.produto_catalogo_id} não encontrado")
            
            if not produto.ativo:
                raise ValueError(f"Produto '{produto.nome}' está inativo")

    def _produtos_disponiveis_semana(self, semana: int, data: 'date | None' = None) -> dict:
        """Obtém produtos aprovados disponíveis na semana (considera intervalos circulares e ano).
        
        IMPORTANTE: Se data for fornecida, valida que o ano está dentro do intervalo permitido.
        Sem dados para anos muito distantes no futuro, retorna dict vazio.
        
        Args:
            semana: número da semana ISO (1-52)
            data: data opcional para validar o ano (evita produtos de anos sem dados)
        """
        from datetime import date as date_class
        
        # Validação de ano se data foi fornecida
        if data:
            ano_solicitado = data.year
            ano_atual = date_class.today().year
            if ano_solicitado > ano_atual + 1:
                return {}  # Sem produtos para anos muito distantes
        
        repo = FornecedorRepo(self.session)
        fornecedores = repo.listar_fornecedores()
        aprovados = [f for f in fornecedores if f.aprovado and not f.em_quarentena]

        produtos_disponiveis = {}

        def _disponivel(semana_num: int, inicio: int, fim: int) -> bool:
            if inicio <= fim:
                return inicio <= semana_num <= fim
            return semana_num >= inicio or semana_num <= fim

        for f in aprovados:
            for p in f.produtos:
                if _disponivel(semana, p.semana_producao_inicio, p.semana_producao_fim):
                    produtos_disponiveis[p.nome.lower()] = True

        return produtos_disponiveis
