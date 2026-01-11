from dataclasses import dataclass
from typing import Optional

@dataclass
class ProdutoInfo:
    """Informações do produto no catálogo (em memória)"""
    nome: str
    categoria: str
    calorias: Optional[float] = None
    proteina_g: Optional[float] = None
    carboidratos_g: Optional[float] = None
    gordura_g: Optional[float] = None


# Catálogo centralizado de produtos
CATALOGO_PRODUTOS = {
    # Frutas
    "Maçã": ProdutoInfo(nome="Maçã", categoria="fruta", calorias=52, proteina_g=0.3),
    "Pera": ProdutoInfo(nome="Pera", categoria="fruta", calorias=57, proteina_g=0.4),
    "Laranja": ProdutoInfo(nome="Laranja", categoria="fruta", calorias=47, proteina_g=0.9),
    "Banana": ProdutoInfo(nome="Banana", categoria="fruta", calorias=89, proteina_g=1.1),
    "Morango": ProdutoInfo(nome="Morango", categoria="fruta", calorias=32, proteina_g=0.6),
    "Mirtilo": ProdutoInfo(nome="Mirtilo", categoria="fruta", calorias=57, proteina_g=0.7),
    "Framboesa": ProdutoInfo(nome="Framboesa", categoria="fruta", calorias=52, proteina_g=1.2),
    "Cereja": ProdutoInfo(nome="Cereja", categoria="fruta", calorias=63, proteina_g=1.1),
    "Uva": ProdutoInfo(nome="Uva", categoria="fruta", calorias=67, proteina_g=0.6),
    "Melancia": ProdutoInfo(nome="Melancia", categoria="fruta", calorias=30, proteina_g=0.6),
    "Melão": ProdutoInfo(nome="Melão", categoria="fruta", calorias=34, proteina_g=0.8),
    "Pêssego": ProdutoInfo(nome="Pêssego", categoria="fruta", calorias=39, proteina_g=0.9),
    "Ameixa": ProdutoInfo(nome="Ameixa", categoria="fruta", calorias=46, proteina_g=0.7),
    "Kiwi": ProdutoInfo(nome="Kiwi", categoria="fruta", calorias=61, proteina_g=1.1),
    
    # Hortícolas - Folha
    "Alface": ProdutoInfo(nome="Alface", categoria="hortícola-folha", calorias=15, proteina_g=1.2),
    "Rúcula": ProdutoInfo(nome="Rúcula", categoria="hortícola-folha", calorias=25, proteina_g=2.6),
    "Espinafre": ProdutoInfo(nome="Espinafre", categoria="hortícola-folha", calorias=23, proteina_g=2.7),
    "Couve": ProdutoInfo(nome="Couve", categoria="hortícola-folha", calorias=49, proteina_g=4.3),
    "Acelga": ProdutoInfo(nome="Acelga", categoria="hortícola-folha", calorias=19, proteina_g=1.8),
    "Nabiça": ProdutoInfo(nome="Nabiça", categoria="hortícola-folha", calorias=23, proteina_g=2.2),
    
    # Hortícolas - Fruto
    "Tomate": ProdutoInfo(nome="Tomate", categoria="hortícola-fruto", calorias=18, proteina_g=0.9),
    "Pimento": ProdutoInfo(nome="Pimento", categoria="hortícola-fruto", calorias=31, proteina_g=1.0),
    "Beringela": ProdutoInfo(nome="Beringela", categoria="hortícola-fruto", calorias=25, proteina_g=0.98),
    "Tomate Cereja": ProdutoInfo(nome="Tomate Cereja", categoria="hortícola-fruto", calorias=27, proteina_g=1.2),
    "Tomate Coração de Boi": ProdutoInfo(nome="Tomate Coração de Boi", categoria="hortícola-fruto", calorias=19, proteina_g=0.95),
    
    # Hortícolas - Tubérculo
    "Cenoura": ProdutoInfo(nome="Cenoura", categoria="tubérculo", calorias=41, proteina_g=0.9),
    "Beterraba": ProdutoInfo(nome="Beterraba", categoria="tubérculo", calorias=43, proteina_g=1.6),
    "Nabo": ProdutoInfo(nome="Nabo", categoria="tubérculo", calorias=36, proteina_g=1.2),
    "Batata": ProdutoInfo(nome="Batata", categoria="tubérculo", calorias=77, proteina_g=2.0),
    "Batata Doce": ProdutoInfo(nome="Batata Doce", categoria="tubérculo", calorias=86, proteina_g=1.6),
    "Abóbora": ProdutoInfo(nome="Abóbora", categoria="tubérculo", calorias=26, proteina_g=1.0),
    "Curgete": ProdutoInfo(nome="Curgete", categoria="tubérculo", calorias=21, proteina_g=1.5),
    
    # Proteínas - Carne
    "Frango": ProdutoInfo(nome="Frango", categoria="proteína", calorias=165, proteina_g=31),
    "Carne de Vaca": ProdutoInfo(nome="Carne de Vaca", categoria="proteína", calorias=250, proteina_g=26),
    "Carne de Porco": ProdutoInfo(nome="Carne de Porco", categoria="proteína", calorias=242, proteina_g=27),
    "Peru": ProdutoInfo(nome="Peru", categoria="proteína", calorias=189, proteina_g=29),
    
    # Proteínas - Peixe
    "Peixe": ProdutoInfo(nome="Peixe", categoria="proteína", calorias=82, proteina_g=17.4),
    "Salmão": ProdutoInfo(nome="Salmão", categoria="proteína", calorias=208, proteina_g=25),
    "Pescada": ProdutoInfo(nome="Pescada", categoria="proteína", calorias=82, proteina_g=17),
    "Bacalhau": ProdutoInfo(nome="Bacalhau", categoria="proteína", calorias=82, proteina_g=17.7),
    
    # Proteínas - Ovos e Leguminosas
    "Ovos": ProdutoInfo(nome="Ovos", categoria="proteína", calorias=155, proteina_g=13),
    "Tofu": ProdutoInfo(nome="Tofu", categoria="proteína", calorias=76, proteina_g=8),
    "Grão-de-Bico": ProdutoInfo(nome="Grão-de-Bico", categoria="proteína", calorias=364, proteina_g=19),
    "Lentilhas": ProdutoInfo(nome="Lentilhas", categoria="proteína", calorias=116, proteina_g=9),
    
    # Cereais
    "Arroz": ProdutoInfo(nome="Arroz", categoria="cereais", calorias=130, proteina_g=2.7),
    "Massa": ProdutoInfo(nome="Massa", categoria="cereais", calorias=131, proteina_g=5.0),
    "Pão": ProdutoInfo(nome="Pão", categoria="cereais", calorias=265, proteina_g=9),
    "Aveia": ProdutoInfo(nome="Aveia", categoria="cereais", calorias=389, proteina_g=17),
    "Quinoa": ProdutoInfo(nome="Quinoa", categoria="cereais", calorias=368, proteina_g=14),
    "Milho": ProdutoInfo(nome="Milho", categoria="cereais", calorias=86, proteina_g=3.3),
    
    # Laticínios
    "Leite": ProdutoInfo(nome="Leite", categoria="laticínios", calorias=61, proteina_g=3.2),
    "Queijo": ProdutoInfo(nome="Queijo", categoria="laticínios", calorias=402, proteina_g=25),
    "Iogurte": ProdutoInfo(nome="Iogurte", categoria="laticínios", calorias=59, proteina_g=3.5),
    "Manteiga": ProdutoInfo(nome="Manteiga", categoria="laticínios", calorias=717, proteina_g=0.9),
    "Nata": ProdutoInfo(nome="Nata", categoria="laticínios", calorias=340, proteina_g=2.2),
    
    # Outros
    "Azeite": ProdutoInfo(nome="Azeite", categoria="outro", calorias=884, proteina_g=0),
    "Mel": ProdutoInfo(nome="Mel", categoria="outro", calorias=304, proteina_g=0.3),
    "Ervas Aromáticas": ProdutoInfo(nome="Ervas Aromáticas", categoria="outro", calorias=261, proteina_g=12.6),
    "Especiarias": ProdutoInfo(nome="Especiarias", categoria="outro", calorias=251, proteina_g=9.0),
}


def produto_existe(nome: str) -> bool:
    """Valida se produto está no catálogo"""
    return nome in CATALOGO_PRODUTOS


def obter_info_produto(nome: str) -> Optional[ProdutoInfo]:
    """Retorna informações do produto do catálogo"""
    return CATALOGO_PRODUTOS.get(nome)


def listar_produtos() -> list[ProdutoInfo]:
    """Lista todos os produtos do catálogo"""
    return list(CATALOGO_PRODUTOS.values())


def listar_categorias() -> set[str]:
    """Lista todas as categorias de produtos"""
    return {prod.categoria for prod in CATALOGO_PRODUTOS.values()}


def produtos_por_categoria(categoria: str) -> list[ProdutoInfo]:
    """Retorna produtos de uma categoria específica"""
    return [prod for prod in CATALOGO_PRODUTOS.values() if prod.categoria == categoria]
