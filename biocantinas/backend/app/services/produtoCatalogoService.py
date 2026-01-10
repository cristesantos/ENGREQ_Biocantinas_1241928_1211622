from typing import List, Optional
from sqlalchemy.orm import Session
from ..repositories.produtoCatalogoRepo import ProdutoCatalogoRepository
from ..models.produto import ProdutoModel
from ..dtos.produtoDTO import ProdutoCatalogoDTO, ProdutoCatalogoCreateDTO, ProdutoCatalogoUpdateDTO
from ..mappings.mappers import produto_create_dto_to_model, produto_model_to_dto


class ProdutoCatalogoService:
    """Serviço para gerenciar o catálogo global de produtos"""

    @staticmethod
    def listar_produtos(session: Session, apenas_ativos: bool = True) -> List[ProdutoCatalogoDTO]:
        """Lista todos os produtos do catálogo"""
        produtos = ProdutoCatalogoRepository.get_all(session, apenas_ativos)
        return [produto_model_to_dto(p) for p in produtos]

    @staticmethod
    def buscar_produto(session: Session, produto_id: int) -> Optional[ProdutoCatalogoDTO]:
        """Busca um produto por ID"""
        produto = ProdutoCatalogoRepository.get_by_id(session, produto_id)
        return produto_model_to_dto(produto) if produto else None

    @staticmethod
    def buscar_por_nome(session: Session, nome: str) -> Optional[ProdutoCatalogoDTO]:
        """Busca um produto por nome exato"""
        produto = ProdutoCatalogoRepository.get_by_nome(session, nome)
        return produto_model_to_dto(produto) if produto else None

    @staticmethod
    def pesquisar_produtos(session: Session, nome: str) -> List[ProdutoCatalogoDTO]:
        """Pesquisa produtos por nome parcial"""
        produtos = ProdutoCatalogoRepository.search_by_nome(session, nome)
        return [produto_model_to_dto(p) for p in produtos]

    @staticmethod
    def listar_por_tipo(session: Session, tipo: str) -> List[ProdutoCatalogoDTO]:
        """Lista produtos de um tipo específico"""
        produtos = ProdutoCatalogoRepository.get_by_tipo(session, tipo)
        return [produto_model_to_dto(p) for p in produtos]

    @staticmethod
    def listar_por_epoca(session: Session, epoca: str) -> List[ProdutoCatalogoDTO]:
        """Lista produtos de uma época específica"""
        produtos = ProdutoCatalogoRepository.get_by_epoca(session, epoca)
        return [produto_model_to_dto(p) for p in produtos]

    @staticmethod
    def criar_produto(session: Session, produto_dto: ProdutoCatalogoCreateDTO) -> ProdutoCatalogoDTO:
        """Cria um novo produto no catálogo"""
        # Verifica se já existe produto com o mesmo nome
        existe = ProdutoCatalogoRepository.get_by_nome(session, produto_dto.nome)
        if existe:
            raise ValueError(f"Já existe um produto com o nome '{produto_dto.nome}'")

        produto_model = produto_create_dto_to_model(produto_dto, new_id=0)
        produto_criado = ProdutoCatalogoRepository.create(session, produto_model)
        session.commit()
        return produto_model_to_dto(produto_criado)

    @staticmethod
    def atualizar_produto(session: Session, produto_id: int, produto_dto: ProdutoCatalogoUpdateDTO) -> Optional[ProdutoCatalogoDTO]:
        """Atualiza um produto existente"""
        produto_existente = ProdutoCatalogoRepository.get_by_id(session, produto_id)
        if not produto_existente:
            return None

        # Verifica se o novo nome já existe em outro produto
        if produto_dto.nome and produto_dto.nome != produto_existente.nome:
            existe = ProdutoCatalogoRepository.get_by_nome(session, produto_dto.nome)
            if existe:
                raise ValueError(f"Já existe outro produto com o nome '{produto_dto.nome}'")

        # Cria modelo com os dados atualizados
        produto_atualizado = ProdutoModel(
            id=produto_id,
            nome=produto_dto.nome if produto_dto.nome else produto_existente.nome,
            tipo=produto_dto.tipo if produto_dto.tipo is not None else produto_existente.tipo,
            descricao=produto_dto.descricao if produto_dto.descricao is not None else produto_existente.descricao,
            unidade_medida=produto_dto.unidade_medida if produto_dto.unidade_medida is not None else produto_existente.unidade_medida,
            epoca_tipica=produto_dto.epoca_tipica if produto_dto.epoca_tipica is not None else produto_existente.epoca_tipica,
            ativo=produto_dto.ativo if produto_dto.ativo is not None else produto_existente.ativo
        )

        produto_atualizado = ProdutoCatalogoRepository.update(session, produto_id, produto_atualizado)
        session.commit()
        return produto_model_to_dto(produto_atualizado) if produto_atualizado else None

    @staticmethod
    def desativar_produto(session: Session, produto_id: int) -> bool:
        """Desativa um produto (soft delete)"""
        sucesso = ProdutoCatalogoRepository.delete(session, produto_id)
        if sucesso:
            session.commit()
        return sucesso

    @staticmethod
    def remover_produto(session: Session, produto_id: int) -> bool:
        """Remove permanentemente um produto (apenas se não houver fornecedores associados)"""
        try:
            sucesso = ProdutoCatalogoRepository.hard_delete(session, produto_id)
            if sucesso:
                session.commit()
            return sucesso
        except Exception as e:
            session.rollback()
            raise ValueError(f"Não é possível remover o produto. Pode estar associado a fornecedores: {str(e)}")
