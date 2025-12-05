from typing import List
from ..dtos.fornecedorDTO import Fornecedor as FornecedorDTO, FornecedorCreate as FornecedorCreateDTO, ProdutoFornecedor as ProdutoFornecedorDTO
from ..models.fornecedor import FornecedorModel
from ..models.produto import ProdutoFornecedorModel


def dto_to_model_create(dto: FornecedorCreateDTO, new_id: int) -> FornecedorModel:
    produtos: List[ProdutoFornecedorModel] = [
        ProdutoFornecedorModel(
            nome=p.nome,
            intervalo_producao_inicio=p.intervalo_producao_inicio,
            intervalo_producao_fim=p.intervalo_producao_fim,
            capacidade=p.capacidade,
        )
        for p in dto.produtos
    ]
    return FornecedorModel(
        id=new_id,
        nome=dto.nome,
        data_inscricao=dto.data_inscricao,
        produtos=produtos,
        aprovado=False,
    )


def model_to_dto(model: FornecedorModel) -> FornecedorDTO:
    produtos: List[ProdutoFornecedorDTO] = [
        ProdutoFornecedorDTO(
            nome=p.nome,
            intervalo_producao_inicio=p.intervalo_producao_inicio,
            intervalo_producao_fim=p.intervalo_producao_fim,
            capacidade=p.capacidade,
        )
        for p in model.produtos
    ]
    return FornecedorDTO(
        id=model.id,
        nome=model.nome,
        data_inscricao=model.data_inscricao,
        produtos=produtos,
        aprovado=model.aprovado,
    )
