from typing import List
from datetime import datetime
from ..dtos.fornecedorDTO import Fornecedor as FornecedorDTO, FornecedorCreate as FornecedorCreateDTO, ProdutoFornecedor as ProdutoFornecedorDTO
from ..dtos.userDTO import User as UserDTO, UserCreate as UserCreateDTO
from ..dtos.produtoDTO import ProdutoCatalogoDTO
from ..models.fornecedor import FornecedorModel
from ..models.produto import ProdutoFornecedorModel, ProdutoModel
from ..models.user import UserModel
from ..db.models import UserORM, ProdutoORM


def dto_to_model_create(dto: FornecedorCreateDTO, new_id: int) -> FornecedorModel:
    produtos: List[ProdutoFornecedorModel] = [
        ProdutoFornecedorModel(
            nome=p.nome,
            tipo=p.tipo,
            biologico=p.biologico,
            semana_producao_inicio=p.semana_producao_inicio,
            semana_producao_fim=p.semana_producao_fim,
            capacidade=p.capacidade,
            unidade=p.unidade,
            certificado=p.certificado,
            data_inscricao=p.data_inscricao,
        )
        for p in dto.produtos
    ]
    return FornecedorModel(
        id=new_id,
        nome=dto.nome,
        data_inscricao=dto.data_inscricao,
        produtos=produtos,
        aprovado=False,
		local=getattr(dto, 'local', False),
		certificado=getattr(dto, 'certificado', False),
        usuario_id=None,  # Será definido no serviço
        em_quarentena=dto.em_quarentena,
        freguesia=dto.freguesia,
    )


def model_to_dto(model: FornecedorModel) -> FornecedorDTO:
    produtos: List[ProdutoFornecedorDTO] = [
        ProdutoFornecedorDTO(
            nome=p.nome,
            tipo=p.tipo,
            biologico=p.biologico,
            semana_producao_inicio=p.semana_producao_inicio,
            semana_producao_fim=p.semana_producao_fim,
            capacidade=p.capacidade,
            unidade=p.unidade_medida,
            certificado=p.certificado,
            data_inscricao=p.data_inscricao.date() if isinstance(p.data_inscricao, datetime) else p.data_inscricao,
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
        em_quarentena=model.em_quarentena,
        freguesia=model.freguesia,
    )


# User mappers
def user_orm_to_model(orm: UserORM) -> UserModel:
    return UserModel(id=orm.id, username=orm.username, password_hash=orm.hashed_password, role=orm.role)

def user_model_to_dto(model: UserModel) -> UserDTO:
    return UserDTO(id=model.id, username=model.username, role=model.role)

def user_create_dto_to_model(dto: UserCreateDTO, hashed_password: str, new_id: int = 0) -> UserModel:
    return UserModel(id=new_id, username=dto.username, password_hash=hashed_password, role=dto.role)


# Produto mappers
def produto_orm_to_model(orm: ProdutoORM) -> ProdutoModel:
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
    return ProdutoCatalogoDTO(
        id=model.id,
        nome=model.nome,
        tipo=model.tipo,
        descricao=model.descricao,
        unidade_medida=model.unidade_medida,
        epoca_tipica=model.epoca_tipica,
        ativo=model.ativo
    )

def produto_create_dto_to_model(dto, new_id: int = 0) -> ProdutoModel:
    return ProdutoModel(
        id=new_id,
        nome=dto.nome,
        tipo=dto.tipo,
        descricao=dto.descricao if hasattr(dto, 'descricao') else None,
        unidade_medida=dto.unidade_medida if hasattr(dto, 'unidade_medida') else "kg",
        epoca_tipica=dto.epoca_tipica if hasattr(dto, 'epoca_tipica') else None,
        ativo=getattr(dto, 'ativo', True)
    )

def produto_fornecedor_model_to_dto(model: ProdutoFornecedorModel):
    from ..dtos.produtoDTO import ProdutoFornecedorDTO
    return ProdutoFornecedorDTO(
        id=getattr(model, 'id', 0),
        fornecedor_id=getattr(model, 'fornecedor_id', 0),
        produto_id=getattr(model, 'produto_id', 0),
        capacidade=model.capacidade,
        preco_unitario=getattr(model, 'preco_unitario', None),
        unidade_medida=model.unidade,
        intervalo_producao_inicio=model.semana_producao_inicio,
        intervalo_producao_fim=model.semana_producao_fim,
        prioridade=getattr(model, 'prioridade', None),
        biologico=model.biologico,
        local=getattr(model, 'local', False),
        disponivel=getattr(model, 'disponivel', True)
    )
