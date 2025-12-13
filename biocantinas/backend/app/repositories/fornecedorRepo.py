from typing import List, Optional
from sqlalchemy.orm import Session
from ..db.models import FornecedorORM, ProdutoFornecedorORM
from ..models.fornecedor import FornecedorModel
from ..models.produto import ProdutoFornecedorModel

class FornecedorRepo:
	def __init__(self, session: Session):
		self.session = session

	def criar_fornecedor(self, model: FornecedorModel) -> FornecedorModel:
		orm = FornecedorORM(
			nome=model.nome,
			data_inscricao=model.data_inscricao,
			aprovado=model.aprovado,
		)
		orm.produtos = [
			ProdutoFornecedorORM(
				nome=p.nome,
				tipo=p.tipo,
				biologico=p.biologico,
				intervalo_producao_inicio=p.intervalo_producao_inicio,
				intervalo_producao_fim=p.intervalo_producao_fim,
				capacidade=p.capacidade,
			)
			for p in model.produtos
		]
		self.session.add(orm)
		self.session.commit()
		self.session.refresh(orm)
		model.id = orm.id
		return model

	def listar_fornecedores(self) -> List[FornecedorModel]:
		results = self.session.query(FornecedorORM).all()
		return [self._to_model(orm) for orm in results]

	def obter_fornecedor(self, fid: int) -> Optional[FornecedorModel]:
		orm = self.session.get(FornecedorORM, fid)
		return self._to_model(orm) if orm else None

	def atualizar_fornecedor(self, f: FornecedorModel) -> None:
		orm = self.session.get(FornecedorORM, f.id)
		if not orm:
			return
		orm.nome = f.nome
		orm.data_inscricao = f.data_inscricao
		orm.aprovado = f.aprovado
		self.session.commit()

	def _to_model(self, orm: FornecedorORM) -> FornecedorModel:
		produtos = [
			ProdutoFornecedorModel(
				nome=p.nome,
				tipo=p.tipo,
				biologico=p.biologico,
				intervalo_producao_inicio=p.intervalo_producao_inicio,
				intervalo_producao_fim=p.intervalo_producao_fim,
				capacidade=p.capacidade,
			)
			for p in orm.produtos
		]
		return FornecedorModel(
			id=orm.id,
			nome=orm.nome,
			data_inscricao=orm.data_inscricao,
			produtos=produtos,
			aprovado=orm.aprovado,
		)
