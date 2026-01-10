from typing import List, Optional
from ..repositories.produtoFornecedorRepo import ProdutoFornecedorRepo
from ..models.produto import ProdutoFornecedorModel
from ..dtos.produtoDTO import ProdutoFornecedorDTO, ProdutoFornecedorCreateDTO, ProdutoFornecedorUpdateDTO
from ..db.session import SessionLocal, init_db
from ..mappings.mappers import produto_fornecedor_model_to_dto


class ProdutoFornecedorService:
    def __init__(self):
        init_db()
        self.session = SessionLocal()
        self.repo = ProdutoFornecedorRepo(self.session)

    def criar_produto(self, fornecedor_id: int, data: ProdutoFornecedorCreateDTO) -> ProdutoFornecedorDTO:
        """Cria um produto para um fornecedor"""
        criado = self.repo.criar_produto(
            fornecedor_id=fornecedor_id,
            produto_id=data.produto_id,
            capacidade=data.capacidade,
            preco_unitario=data.preco_unitario,
            unidade_medida=data.unidade_medida,
            intervalo_producao_inicio=data.intervalo_producao_inicio,
            intervalo_producao_fim=data.intervalo_producao_fim,
            prioridade=data.prioridade,
            biologico=data.biologico,
            local=data.local,
            disponivel=data.disponivel
        )
        return produto_fornecedor_model_to_dto(criado)

    def obter_produto(self, produto_fornecedor_id: int) -> Optional[ProdutoFornecedorDTO]:
        """Obtém um produto de fornecedor por ID"""
        model = self.repo.obter_produto(produto_fornecedor_id)
        if not model:
            return None
        return produto_fornecedor_model_to_dto(model)

    def listar_todos(self) -> List[ProdutoFornecedorDTO]:
        """Lista todos os produtos de fornecedores"""
        models = self.repo.listar_todos()
        return [produto_fornecedor_model_to_dto(m) for m in models]

    def listar_por_fornecedor(self, fornecedor_id: int) -> List[ProdutoFornecedorDTO]:
        """Lista produtos de um fornecedor"""
        models = self.repo.listar_por_fornecedor(fornecedor_id)
        return [produto_fornecedor_model_to_dto(m) for m in models]

    def listar_por_tipo(self, tipo: str) -> List[ProdutoFornecedorDTO]:
        """Lista produtos por tipo (do catálogo)"""
        models = self.repo.listar_por_tipo(tipo)
        return [produto_fornecedor_model_to_dto(m) for m in models]

    def listar_biologicos(self) -> List[ProdutoFornecedorDTO]:
        """Lista apenas produtos biológicos"""
        models = self.repo.listar_biologicos()
        return [produto_fornecedor_model_to_dto(m) for m in models]
    
    def listar_disponiveis(self, fornecedor_id: Optional[int] = None) -> List[ProdutoFornecedorDTO]:
        """Lista produtos disponíveis"""
        models = self.repo.listar_disponiveis(fornecedor_id)
        return [produto_fornecedor_model_to_dto(m) for m in models]

    def atualizar_produto(self, produto_fornecedor_id: int, data: ProdutoFornecedorUpdateDTO) -> Optional[ProdutoFornecedorDTO]:
        """Atualiza um produto de fornecedor"""
        updates = {}
        if data.produto_id is not None:
            updates['produto_id'] = data.produto_id
        if data.preco_unitario is not None:
            updates['preco_unitario'] = data.preco_unitario
        if data.capacidade is not None:
            updates['capacidade'] = data.capacidade
        if data.unidade_medida is not None:
            updates['unidade_medida'] = data.unidade_medida
        if data.intervalo_producao_inicio is not None:
            updates['intervalo_producao_inicio'] = data.intervalo_producao_inicio
        if data.intervalo_producao_fim is not None:
            updates['intervalo_producao_fim'] = data.intervalo_producao_fim
        if data.prioridade is not None:
            updates['prioridade'] = data.prioridade
        if data.biologico is not None:
            updates['biologico'] = data.biologico
        if data.local is not None:
            updates['local'] = data.local
        if data.disponivel is not None:
            updates['disponivel'] = data.disponivel
        
        atualizado = self.repo.atualizar_produto(produto_fornecedor_id, **updates)
        if not atualizado:
            return None
        return produto_fornecedor_model_to_dto(atualizado)

    def deletar_produto(self, produto_fornecedor_id: int) -> bool:
        """Remove um produto de fornecedor"""
        return self.repo.deletar_produto(produto_fornecedor_id)


_service = ProdutoFornecedorService()

def get_produto_service() -> ProdutoFornecedorService:
    return _service

