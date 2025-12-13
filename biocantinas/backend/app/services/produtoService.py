from typing import List
from ..repositories.produtoRepo import ProdutoRepo
from ..models.produto import ProdutoFornecedorModel
from ..dtos.produtoDTO import ProdutoDTO, ProdutoCreateDTO, ProdutoUpdateDTO
from ..db.session import SessionLocal, init_db


class ProdutoService:
    def __init__(self):
        init_db()
        self.session = SessionLocal()
        self.repo = ProdutoRepo(self.session)

    def criar_produto(self, fornecedor_id: int, data: ProdutoCreateDTO) -> ProdutoDTO:
        """Cria um produto para um fornecedor"""
        model = ProdutoFornecedorModel(
            nome=data.nome,
            tipo=data.tipo,
            biologico=data.biologico,
            intervalo_producao_inicio=data.intervalo_producao_inicio,
            intervalo_producao_fim=data.intervalo_producao_fim,
            capacidade=data.capacidade,
        )
        produto_id, forn_id, criado = self.repo.criar_produto(fornecedor_id, model)
        return self._model_to_dto(criado, produto_id, forn_id)

    def obter_produto(self, produto_id: int) -> ProdutoDTO | None:
        """Obtém um produto por ID"""
        resultado = self.repo.obter_produto(produto_id)
        if not resultado:
            return None
        pid, forn_id, model = resultado
        return self._model_to_dto(model, pid, forn_id)

    def listar_todos(self) -> List[ProdutoDTO]:
        """Lista todos os produtos (simplificado - sem ID no retorno de lista)"""
        # Para KPIs, não precisamos de DTOs completos, apenas Models
        return []  # Implementar se necessário

    def listar_por_fornecedor(self, fornecedor_id: int) -> List[ProdutoDTO]:
        """Lista produtos de um fornecedor (simplificado)"""
        return []  # Implementar se necessário

    def listar_por_tipo(self, tipo: str) -> List[ProdutoDTO]:
        """Lista produtos por tipo (simplificado)"""
        return []  # Implementar se necessário

    def listar_biologicos(self) -> List[ProdutoDTO]:
        """Lista apenas produtos biológicos (simplificado)"""
        return []  # Implementar se necessário

    def atualizar_produto(self, produto_id: int, data: ProdutoUpdateDTO) -> ProdutoDTO | None:
        """Atualiza um produto"""
        # Buscar produto atual para obter fornecedor_id
        resultado = self.repo.obter_produto(produto_id)
        if not resultado:
            return None
        
        _, forn_id, _ = resultado
        
        model = ProdutoFornecedorModel(
            nome=data.nome,
            tipo=data.tipo,
            biologico=data.biologico,
            intervalo_producao_inicio=data.intervalo_producao_inicio,
            intervalo_producao_fim=data.intervalo_producao_fim,
            capacidade=data.capacidade,
        )
        atualizado = self.repo.atualizar_produto(produto_id, model)
        if not atualizado:
            return None
        return self._model_to_dto(atualizado, produto_id, forn_id)

    def deletar_produto(self, produto_id: int) -> bool:
        """Remove um produto"""
        return self.repo.deletar_produto(produto_id)

    def _model_to_dto(self, model: ProdutoFornecedorModel, produto_id: int, fornecedor_id: int) -> ProdutoDTO:
        return ProdutoDTO(
            id=produto_id,
            fornecedor_id=fornecedor_id,
            nome=model.nome,
            tipo=model.tipo,
            biologico=model.biologico,
            intervalo_producao_inicio=model.intervalo_producao_inicio,
            intervalo_producao_fim=model.intervalo_producao_fim,
            capacidade=model.capacidade,
        )


_service = ProdutoService()

def get_produto_service() -> ProdutoService:
    return _service
