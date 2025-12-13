from typing import List
from ..dtos.fornecedorDTO import Fornecedor as FornecedorDTO, FornecedorCreate as FornecedorCreateDTO, ProdutoFornecedor as ProdutoFornecedorDTO
from ..dtos.userDTO import User as UserDTO, UserCreate as UserCreateDTO
from ..models.fornecedor import FornecedorModel
from ..models.produto import ProdutoFornecedorModel
from ..models.user import UserModel
from ..db.models import UserORM


def dto_to_model_create(dto: FornecedorCreateDTO, new_id: int) -> FornecedorModel:
    produtos: List[ProdutoFornecedorModel] = [
        ProdutoFornecedorModel(
            nome=p.nome,
            tipo=p.tipo,
            biologico=p.biologico,
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
            tipo=p.tipo,
            biologico=p.biologico,
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


# User mappers
def user_orm_to_model(orm: UserORM) -> UserModel:
    return UserModel(id=orm.id, username=orm.username, password_hash=orm.password_hash, role=orm.role)

def user_model_to_dto(model: UserModel) -> UserDTO:
    return UserDTO(id=model.id, username=model.username, role=model.role)

def user_create_dto_to_model(dto: UserCreateDTO, hashed_password: str, new_id: int = 0) -> UserModel:
    return UserModel(id=new_id, username=dto.username, password_hash=hashed_password, role=dto.role)
