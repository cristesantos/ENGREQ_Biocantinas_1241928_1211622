from typing import List, Dict
from .schemas import Fornecedor, OrdemFornecedor
from .storage import listar_fornecedores, obter_fornecedor, atualizar_fornecedor
from datetime import date

def aprovar_fornecedor(fid: int, aprovado: bool) -> Fornecedor:
    fornecedor = obter_fornecedor(fid)
    if not fornecedor:
        raise ValueError("Fornecedor não encontrado")
    fornecedor.aprovado = aprovado
    atualizar_fornecedor(fornecedor)
    return fornecedor

def calcular_ordem_por_produto() -> List[OrdemFornecedor]:
    fornecedores = [f for f in listar_fornecedores() if f.aprovado]

    mapa: Dict[str, List[Fornecedor]] = {}

    for f in fornecedores:
        # garantir que a data esteja no formato date
        if isinstance(f.data_inscricao, str):
            f.data_inscricao = date.fromisoformat(f.data_inscricao)

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