"""
Modelos de domínio para Receitas
"""
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ItemReceitaModel:
    """Ingrediente de uma receita com quantidade por porção"""
    produto_catalogo_id: int
    produto_nome: str
    quantidade_por_porcao: float  # quantidade na unidade do produto
    unidade_medida: str | None = None
    id: Optional[int] = None


@dataclass
class ReceitaModel:
    """Receita fixa do catálogo com ingredientes"""
    nome: str
    ingredientes: List[ItemReceitaModel]
    descricao: Optional[str] = None
    tipo_refeicao: Optional[str] = None  # "almoço", "jantar", "ambos"
    categoria: Optional[str] = None  # "carne", "peixe", "vegetariano", "vegano", etc.
    porcoes_base: int = 1
    tempo_preparo: Optional[int] = None  # minutos
    ativa: bool = True
    id: Optional[int] = None
    
    def calcular_ingredientes_para_porcoes(self, num_porcoes: int) -> List[dict]:
        """Calcula quantidades para o número de porções mantendo a unidade de cada produto"""
        fator = num_porcoes / self.porcoes_base
        return [
            {
                "produto_catalogo_id": ing.produto_catalogo_id,
                "produto_nome": ing.produto_nome,
                "quantidade_necessaria": ing.quantidade_por_porcao * fator,
                "unidade_medida": ing.unidade_medida,
            }
            for ing in self.ingredientes
        ]
    
    def verifica_disponibilidade(self, produtos_disponiveis: dict) -> bool:
        """
        Verifica se todos os ingredientes estão disponíveis
        produtos_disponiveis: dict com {nome_produto: quantidade_disponivel}
        """
        for ing in self.ingredientes:
            if ing.produto_nome.lower() not in [p.lower() for p in produtos_disponiveis.keys()]:
                return False
        return True
