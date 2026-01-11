from typing import List
from datetime import date, timedelta
from random import choice, sample
from ..dtos.ementaDTO import Ementa as EmentaDTO, EmentaCreate as EmentaCreateDTO, Refeicao as RefeicaoDTO, ItemRefeicao as ItemRefeicaoDTO
from ..models.ementa import EmentaModel, RefeicaoModel, ItemRefeicaoModel
from ..db.session import SessionLocal, init_db
from ..repositories.ementaRepo import EmentaRepo
from ..repositories.fornecedorRepo import FornecedorRepo
from ..repositories.receitaRepo import ReceitaRepository


class EmentaService:
    def __init__(self):
        init_db()
        self.session = SessionLocal()
        self.repo = EmentaRepo(self.session)
        self.fornecedor_repo = FornecedorRepo(self.session)
        self.receita_repo = ReceitaRepository(self.session)

    def criar_ementa(self, data: EmentaCreateDTO) -> EmentaDTO:
        model = self._dto_to_model_create(data, new_id=0)
        stored = self.repo.criar_ementa(model)
        return self._model_to_dto(stored)

    def listar_ementas(self) -> List[EmentaDTO]:
        return [self._model_to_dto(m) for m in self.repo.listar_ementas()]

    def obter_ementa(self, ementa_id: int) -> EmentaDTO | None:
        m = self.repo.obter_ementa(ementa_id)
        return self._model_to_dto(m) if m else None

    def atualizar_ementa(self, ementa_id: int, data: EmentaCreateDTO) -> EmentaDTO | None:
        model = self._dto_to_model_create(data, new_id=ementa_id)
        atualizado = self.repo.atualizar_ementa(model)
        return self._model_to_dto(atualizado) if atualizado else None

    def deletar_ementa(self, ementa_id: int) -> bool:
        return self.repo.deletar_ementa(ementa_id)

    def gerar_ementa_automatica(self, data_inicio: date, nome: str | None = None) -> EmentaDTO:
        """
        Gera uma ementa semanal automática (5 dias úteis, 2 refeições/dia)
        baseada nas RECEITAS do catálogo que podem ser feitas com produtos disponíveis.
        
        Restrições:
        - A ementa deve começar numa segunda-feira
        - Deve ser criada com pelo menos 7 dias de antecedência
        - Usa receitas do catálogo que têm ingredientes disponíveis
        - Considera a sazonalidade dos produtos (semana_producao_inicio/fim)
        """
        from datetime import datetime
        
        # Validar que é uma segunda-feira (weekday() == 0)
        if data_inicio.weekday() != 0:
            raise ValueError("A ementa deve começar numa segunda-feira")
        
        # Validar antecedência mínima de 7 dias
        hoje = date.today()
        dias_antecedencia = (data_inicio - hoje).days
        if dias_antecedencia < 7:
            raise ValueError(f"A ementa deve ser criada com pelo menos 7 dias de antecedência (faltam {7 - dias_antecedencia} dias)")
        
        # Calcular datas da semana (segunda a sexta)
        data_fim = data_inicio + timedelta(days=4)
        
        if not nome:
            nome = f"Ementa {data_inicio.strftime('%d/%m/%Y')} - {data_fim.strftime('%d/%m/%Y')}"
        
        # Calcular semana do ano para verificar produtos sazonais
        semana_ementa = data_inicio.isocalendar()[1]
        
        # Obter produtos disponíveis PARA ESSA SEMANA específica
        produtos_disponiveis = self._obter_produtos_disponiveis_dict(semana_ementa)
        
        # Obter receitas disponíveis (que podem ser feitas com os produtos)
        receitas_almoco = self.receita_repo.listar_receitas_por_tipo("almoço")
        receitas_jantar = self.receita_repo.listar_receitas_por_tipo("jantar")
        
        # Filtrar receitas que têm todos os ingredientes disponíveis
        receitas_almoco_viaveis = [r for r in receitas_almoco if r.verifica_disponibilidade(produtos_disponiveis)]
        receitas_jantar_viaveis = [r for r in receitas_jantar if r.verifica_disponibilidade(produtos_disponiveis)]
        
        if not receitas_almoco_viaveis or not receitas_jantar_viaveis:
            raise ValueError("Não há receitas suficientes com os produtos disponíveis para gerar a ementa")
        
        # Gerar refeições
        refeicoes = []
        receitas_usadas_almoco = set()
        receitas_usadas_jantar = set()
        
        for dia in range(1, 6):  # Segunda a Sexta
            # Almoço - escolher receita diferente a cada dia
            receita_almoco = self._escolher_receita_unica(
                receitas_almoco_viaveis, 
                receitas_usadas_almoco
            )
            if receita_almoco:
                receitas_usadas_almoco.add(receita_almoco.id)
                refeicoes.append(self._criar_refeicao_de_receita(dia, "almoço", receita_almoco))
            
            # Jantar - escolher receita diferente a cada dia
            receita_jantar = self._escolher_receita_unica(
                receitas_jantar_viaveis,
                receitas_usadas_jantar
            )
            if receita_jantar:
                receitas_usadas_jantar.add(receita_jantar.id)
                refeicoes.append(self._criar_refeicao_de_receita(dia, "jantar", receita_jantar))
        
        # Criar modelo
        model = EmentaModel(
            id=0,
            nome=nome,
            data_inicio=data_inicio,
            data_fim=data_fim,
            refeicoes=refeicoes
        )
        
        stored = self.repo.criar_ementa(model)
        return self._model_to_dto(stored)

    def _obter_produtos_disponiveis_dict(self, semana_ano: int) -> dict:
        """
        Retorna dicionário com produtos disponíveis {nome: True}
        Considera apenas produtos sazonais disponíveis na semana especificada
        
        Args:
            semana_ano: Semana do ano (1-52) para verificar disponibilidade
        """
        fornecedores = self.fornecedor_repo.listar_fornecedores()
        aprovados = [f for f in fornecedores if f.aprovado]
        
        produtos_disponiveis = {}
        for f in aprovados:
            for p in f.produtos:
                # Verificar se o produto está em temporada nesta semana
                inicio = p.semana_producao_inicio
                fim = p.semana_producao_fim
                
                # Lidar com sazonalidade que atravessa o ano novo (ex: semana 50 a semana 10)
                if inicio <= fim:
                    # Período contínuo dentro do mesmo ano
                    produto_disponivel = inicio <= semana_ano <= fim
                else:
                    # Período que atravessa o ano novo (ex: 48-52 e 1-10)
                    produto_disponivel = semana_ano >= inicio or semana_ano <= fim
                
                if produto_disponivel:
                    produtos_disponiveis[p.nome.lower()] = True
        
        return produtos_disponiveis
    
    def _escolher_receita_unica(self, receitas_disponiveis, receitas_usadas):
        """Escolhe uma receita que ainda não foi usada"""
        receitas_nao_usadas = [r for r in receitas_disponiveis if r.id not in receitas_usadas]
        
        # Se todas foram usadas, permitir reutilização
        if not receitas_nao_usadas:
            receitas_nao_usadas = receitas_disponiveis
        
        return choice(receitas_nao_usadas) if receitas_nao_usadas else None
    
    def _criar_refeicao_de_receita(self, dia_semana: int, tipo: str, receita) -> RefeicaoModel:
        """Cria uma RefeicaoModel a partir de uma receita do catálogo.
        
        As quantidades vêm da receita tal qual — sem multiplicação.
        A receita do catálogo já define as quantidades finais para aquela refeição.
        """
        # Usar ingredientes da receita diretamente (sem factor de porções)
        itens = [
            ItemRefeicaoModel(
                ingrediente=ing.produto_nome,
                produto_id=None,
                quantidade_estimada=ing.quantidade_por_porcao,
                unidade_medida=ing.unidade_medida
            )
            for ing in receita.ingredientes
        ]
        
        return RefeicaoModel(
            dia_semana=dia_semana,
            tipo=tipo,
            descricao=receita.nome,
            itens=itens,
            receita_id=receita.id,
            numero_porcoes=None
        )

    def _obter_produtos_stock(self) -> dict:
        """Organiza produtos aprovados por tipo"""
        fornecedores = self.fornecedor_repo.listar_fornecedores()
        aprovados = [f for f in fornecedores if f.aprovado]
        
        produtos_por_tipo = {}
        for f in aprovados:
            for p in f.produtos:
                # Normalizar tipo para lowercase
                tipo = (p.tipo or "Sem categoria").lower()
                if tipo not in produtos_por_tipo:
                    produtos_por_tipo[tipo] = []
                produtos_por_tipo[tipo].append({
                    "nome": p.nome,
                    "tipo": tipo,
                    "capacidade": p.capacidade,
                    "fornecedor": f.nome
                })
        
        return produtos_por_tipo

    def _gerar_refeicao(self, dia_semana: int, tipo: str, produtos_por_tipo: dict) -> RefeicaoModel:
        """Gera uma refeição balanceada com base no stock"""
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        dia_nome = dias[dia_semana - 1]
        
        itens = []
        descricao_partes = []
        
        # Proteína (obrigatória)
        proteinas = produtos_por_tipo.get("proteína", [])
        if proteinas:
            proteina = choice(proteinas)
            itens.append(ItemRefeicaoModel(
                ingrediente=proteina["nome"],
                produto_id=None,
                quantidade_estimada=5
            ))
            descricao_partes.append(proteina["nome"])
        
        # Hortícola (obrigatória)
        horticolas = produtos_por_tipo.get("hortícola", [])
        if horticolas:
            # Escolher 1-2 hortícolas
            num_horticolas = min(2, len(horticolas))
            selecionados = sample(horticolas, num_horticolas)
            for h in selecionados:
                itens.append(ItemRefeicaoModel(
                    ingrediente=h["nome"],
                    produto_id=None,
                    quantidade_estimada=3
                ))
                descricao_partes.append(h["nome"])
        
        # Cereais (acompanhamento)
        cereais = produtos_por_tipo.get("cereais", [])
        if cereais:
            cereal = choice(cereais)
            itens.append(ItemRefeicaoModel(
                ingrediente=cereal["nome"],
                produto_id=None,
                quantidade_estimada=4
            ))
            descricao_partes.append(cereal["nome"])
        
        # Fruta (sobremesa, mais comum no almoço)
        if tipo == "almoço":
            frutas = produtos_por_tipo.get("fruta", [])
            if frutas:
                fruta = choice(frutas)
                itens.append(ItemRefeicaoModel(
                    ingrediente=fruta["nome"],
                    produto_id=None,
                    quantidade_estimada=2
                ))
                descricao_partes.append(fruta["nome"])
        
        # Laticínios (opcional, mais comum no jantar)
        if tipo == "jantar":
            laticinios = produtos_por_tipo.get("laticínios", [])
            if laticinios:
                laticinio = choice(laticinios)
                itens.append(ItemRefeicaoModel(
                    ingrediente=laticinio["nome"],
                    produto_id=None,
                    quantidade_estimada=2
                ))
                descricao_partes.append(laticinio["nome"])
        
        # Gerar descrição
        descricao = f"{dia_nome} - {tipo.capitalize()}: " + " com ".join(descricao_partes) if descricao_partes else f"{dia_nome} - {tipo.capitalize()}"
        
        return RefeicaoModel(
            dia_semana=dia_semana,
            tipo=tipo,
            descricao=descricao,
            itens=itens
        )

    def _dto_to_model_create(self, dto: EmentaCreateDTO, new_id: int) -> EmentaModel:
        refeicoes = [
            RefeicaoModel(
                dia_semana=r.dia_semana,
                tipo=r.tipo,
                descricao=r.descricao,
                receita_id=r.receita_id,
                numero_porcoes=r.numero_porcoes,
                itens=[
                    ItemRefeicaoModel(
                        produto_id=i.produto_id,
                        ingrediente=i.ingrediente,
                        quantidade_estimada=i.quantidade_estimada,
                        unidade_medida=i.unidade_medida
                    )
                    for i in r.itens
                ]
            )
            for r in dto.refeicoes
        ]
        
        return EmentaModel(
            id=new_id,
            nome=dto.nome,
            data_inicio=dto.data_inicio,
            data_fim=dto.data_fim,
            refeicoes=refeicoes
        )

    def _model_to_dto(self, model: EmentaModel) -> EmentaDTO:
        refeicoes = [
            RefeicaoDTO(
                dia_semana=r.dia_semana,
                tipo=r.tipo,
                descricao=r.descricao,
                receita_id=r.receita_id,
                numero_porcoes=r.numero_porcoes,
                itens=[
                    ItemRefeicaoDTO(
                        produto_id=i.produto_id,
                        ingrediente=i.ingrediente,
                        quantidade_estimada=float(i.quantidade_estimada) if i.quantidade_estimada is not None else None,
                        unidade_medida=i.unidade_medida
                    )
                    for i in r.itens
                ]
            )
            for r in model.refeicoes
        ]
        
        return EmentaDTO(
            id=model.id,
            nome=model.nome,
            data_inicio=model.data_inicio,
            data_fim=model.data_fim,
            refeicoes=refeicoes
        )


_service = EmentaService()

def get_ementa_service() -> EmentaService:
    return _service
