from typing import List
from ..dtos.fornecedorDTO import Fornecedor as FornecedorDTO, FornecedorCreate as FornecedorCreateDTO
from ..dtos.userDTO import User as UserDTO, UserCreate as UserCreateDTO
from ..dtos.produtoDTO import ProdutoCatalogoDTO, ProdutoCatalogoCreateDTO, ProdutoDTO, ProdutoFornecedorDTO
from ..models.fornecedor import FornecedorModel
from ..models.produto import ProdutoFornecedorModel, ProdutoModel
from ..models.user import UserModel
from ..db.models import UserORM, ProdutoORM, ProdutoFornecedorORM


def dto_to_model_create(dto: FornecedorCreateDTO, new_id: int) -> FornecedorModel:
    produtos: List[ProdutoFornecedorModel] = [
        ProdutoFornecedorModel(
            id=0,
            fornecedor_id=new_id,
            produto_id=p.produto_id,
            produto_nome="",
            produto_tipo=None,
            preco_unitario=p.preco_unitario,
            capacidade=p.capacidade,
            unidade_medida=p.unidade_medida,
            intervalo_producao_inicio=p.intervalo_producao_inicio,
            intervalo_producao_fim=p.intervalo_producao_fim,
            prioridade=p.prioridade,
            biologico=p.biologico,
            disponivel=p.disponivel,
        )
        for p in dto.produtos
    ]
    return FornecedorModel(
        id=new_id,
        nome=dto.nome,
        data_inscricao=dto.data_inscricao,
        produtos=produtos,
        aprovado=False,
		local=dto.local,
		certificado=dto.certificado,
        usuario_id=None,  # Será definido no serviço
    )


def model_to_dto(model: FornecedorModel) -> FornecedorDTO:
    produtos: List[ProdutoFornecedorDTO] = [
        ProdutoFornecedorDTO(
            produto_id=p.produto_id,
            preco_unitario=p.preco_unitario,
            capacidade=p.capacidade,
            unidade_medida=p.unidade_medida,
            intervalo_producao_inicio=p.intervalo_producao_inicio,
            intervalo_producao_fim=p.intervalo_producao_fim,
            prioridade=p.prioridade,
            biologico=p.biologico,
            disponivel=p.disponivel,
        )
        for p in model.produtos
    ]
    return FornecedorDTO(
        id=model.id,
        nome=model.nome,
        data_inscricao=model.data_inscricao,
        produtos=produtos,
        aprovado=model.aprovado,
		local=model.local,
		certificado=model.certificado,
    )


# User mappers
def user_orm_to_model(orm: UserORM) -> UserModel:
    return UserModel(id=orm.id, username=orm.username, password_hash=orm.password_hash, role=orm.role)

def user_model_to_dto(model: UserModel) -> UserDTO:
    return UserDTO(id=model.id, username=model.username, role=model.role)

def user_create_dto_to_model(dto: UserCreateDTO, hashed_password: str, new_id: int = 0) -> UserModel:
    return UserModel(id=new_id, username=dto.username, password_hash=hashed_password, role=dto.role)


# ============ Produto Catalogo Mappers ============

def produto_orm_to_model(orm: ProdutoORM) -> ProdutoModel:
    """Converte ProdutoORM para ProdutoModel"""
    return ProdutoModel(
        id=orm.id,
        nome=orm.nome,
        tipo=orm.tipo,
        descricao=orm.descricao,
        unidade_medida=orm.unidade_medida,
        epoca_tipica=orm.epoca_tipica,
        ativo=orm.ativo
    )

def produto_model_to_dto(model: ProdutoModel) -> ProdutoCatalogoDTO:
    """Converte ProdutoModel para ProdutoCatalogoDTO"""
    return ProdutoCatalogoDTO(
        id=model.id,
        nome=model.nome,
        tipo=model.tipo,
        descricao=model.descricao,
        unidade_medida=model.unidade_medida,
        epoca_tipica=model.epoca_tipica,
        ativo=model.ativo
    )

def produto_create_dto_to_model(dto: ProdutoCatalogoCreateDTO, new_id: int) -> ProdutoModel:
    """Converte ProdutoCatalogoCreateDTO para ProdutoModel"""
    return ProdutoModel(
        id=new_id,
        nome=dto.nome,
        tipo=dto.tipo,
        descricao=dto.descricao,
        unidade_medida=dto.unidade_medida,
        epoca_tipica=dto.epoca_tipica,
        ativo=dto.ativo
    )


# ============ ProdutoFornecedor Mappers ============

def produto_fornecedor_orm_to_model(orm: ProdutoFornecedorORM) -> ProdutoFornecedorModel:
    """Converte ProdutoFornecedorORM para ProdutoFornecedorModel"""
    return ProdutoFornecedorModel(
        id=orm.id,
        fornecedor_id=orm.fornecedor_id,
        produto_id=orm.produto_id,
        produto_nome=orm.produto.nome if orm.produto else "",
        produto_tipo=orm.produto.tipo if orm.produto else None,
        preco_unitario=orm.preco_unitario,
        capacidade=orm.capacidade,
        unidade_medida=orm.unidade_medida,
        intervalo_producao_inicio=orm.intervalo_producao_inicio,
        intervalo_producao_fim=orm.intervalo_producao_fim,
        prioridade=orm.prioridade,
        biologico=orm.biologico,
        local=orm.local,
        disponivel=orm.disponivel
    )

def produto_fornecedor_model_to_dto(model: ProdutoFornecedorModel) -> ProdutoDTO:
    """Converte ProdutoFornecedorModel para ProdutoDTO"""
    return ProdutoDTO(
        id=model.id,
        fornecedor_id=model.fornecedor_id,
        produto_id=model.produto_id,
        produto_nome=model.produto_nome,
        produto_tipo=model.produto_tipo,
        preco_unitario=model.preco_unitario,
        capacidade=model.capacidade,
        unidade_medida=model.unidade_medida,
        intervalo_producao_inicio=model.intervalo_producao_inicio,
        intervalo_producao_fim=model.intervalo_producao_fim,
        prioridade=model.prioridade,
        biologico=model.biologico,
        local=model.local,
        disponivel=model.disponivel
    )

