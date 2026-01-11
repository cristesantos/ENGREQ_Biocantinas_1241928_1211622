from typing import List, Optional
from sqlalchemy.orm import Session
from ..db.models import FornecedorORM, ProdutoFornecedorORM, FornecedorEstadoORM, FreguesiaFechoORM, ProdutoORM
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
			local=model.local,
			certificado=model.certificado,
			usuario_id=model.usuario_id,
		)
		orm.produtos = []
		for p in model.produtos:
			# Buscar ou criar produto no catálogo
			produto_catalogo = self.session.query(ProdutoORM).filter_by(nome=p.nome).first()
			if not produto_catalogo:
				produto_catalogo = ProdutoORM(
					nome=p.nome,
					tipo=p.tipo,
					unidade_medida=p.unidade_medida,
					ativo=True
				)
				self.session.add(produto_catalogo)
				self.session.flush()
			
			produto_fornecedor = ProdutoFornecedorORM(
				produto_id=produto_catalogo.id,
				biologico=p.biologico,
				semana_producao_inicio=p.semana_producao_inicio,
				semana_producao_fim=p.semana_producao_fim,
				capacidade=p.capacidade,
				unidade_medida=p.unidade_medida,
				certificado=p.certificado,
			)
			orm.produtos.append(produto_fornecedor)
		self.session.add(orm)
		self.session.commit()
		self.session.refresh(orm)
		# Criar estado sanitário associado
		estado = FornecedorEstadoORM(
			fornecedor_id=orm.id,
			em_quarentena=model.em_quarentena,
			freguesia=model.freguesia,
		)
		self.session.add(estado)
		self.session.commit()
		model.id = orm.id
		return model

	def listar_fornecedores(self) -> List[FornecedorModel]:
		results = self.session.query(FornecedorORM).all()
		estados = {
			e.fornecedor_id: e
			for e in self.session.query(FornecedorEstadoORM).all()
		}
		return [self._to_model(orm, estados.get(orm.id)) for orm in results]

	def obter_fornecedor(self, fid: int) -> Optional[FornecedorModel]:
		orm = self.session.get(FornecedorORM, fid)
		estado = None
		if orm:
			estado = self.session.query(FornecedorEstadoORM).filter_by(fornecedor_id=orm.id).first()
		return self._to_model(orm, estado) if orm else None

	def atualizar_fornecedor(self, f: FornecedorModel) -> None:
		orm = self.session.get(FornecedorORM, f.id)
		if not orm:
			return
		orm.nome = f.nome
		orm.data_inscricao = f.data_inscricao
		orm.aprovado = f.aprovado
		orm.local = f.local
		orm.certificado = f.certificado
		orm.usuario_id = f.usuario_id
		
		# Atualizar produtos: remover antigos e adicionar novos
		orm.produtos.clear()
		for p in f.produtos:
			# Buscar ou criar produto no catálogo
			produto_catalogo = self.session.query(ProdutoORM).filter_by(nome=p.nome).first()
			if not produto_catalogo:
				produto_catalogo = ProdutoORM(
					nome=p.nome,
					tipo=p.tipo,
					unidade_medida=p.unidade_medida,
					ativo=True
				)
				self.session.add(produto_catalogo)
				self.session.flush()
			
			produto_fornecedor = ProdutoFornecedorORM(
				produto_id=produto_catalogo.id,
				biologico=p.biologico,
				semana_producao_inicio=p.semana_producao_inicio,
				semana_producao_fim=p.semana_producao_fim,
				capacidade=p.capacidade,
				unidade_medida=p.unidade_medida,
				certificado=p.certificado,
			)
			orm.produtos.append(produto_fornecedor)
		# Atualizar estado sanitário
		estado = self.session.query(FornecedorEstadoORM).filter_by(fornecedor_id=f.id).first()
		if not estado:
			estado = FornecedorEstadoORM(fornecedor_id=f.id)
			self.session.add(estado)
		if f.em_quarentena is not None:
			estado.em_quarentena = f.em_quarentena
		if f.freguesia is not None:
			estado.freguesia = f.freguesia
		self.session.commit()

	def atualizar_estado(self, fornecedor_id: int, em_quarentena: bool | None, freguesia: str | None) -> None:
		estado = self.session.query(FornecedorEstadoORM).filter_by(fornecedor_id=fornecedor_id).first()
		if not estado:
			estado = FornecedorEstadoORM(fornecedor_id=fornecedor_id)
			self.session.add(estado)
		if em_quarentena is not None:
			estado.em_quarentena = em_quarentena
			# Quarentena implica reprovação imediata
			fornecedor = self.session.get(FornecedorORM, fornecedor_id)
			if fornecedor and em_quarentena:
				fornecedor.aprovado = False
		if freguesia is not None:
			estado.freguesia = freguesia
		self.session.commit()

	def adicionar_produto(self, fornecedor_id: int, produto: ProdutoFornecedorModel) -> None:
		"""Adiciona um novo produto ao fornecedor sem afetar os existentes"""
		# Buscar ou criar produto no catálogo
		produto_catalogo = self.session.query(ProdutoORM).filter_by(nome=produto.nome).first()
		if not produto_catalogo:
			produto_catalogo = ProdutoORM(
				nome=produto.nome,
				tipo=produto.tipo,
				unidade_medida=produto.unidade_medida,
				ativo=True
			)
			self.session.add(produto_catalogo)
			self.session.flush()
		
		# Criar produto_fornecedor
		produto_fornecedor = ProdutoFornecedorORM(
			fornecedor_id=fornecedor_id,
			produto_id=produto_catalogo.id,
			biologico=produto.biologico,
			semana_producao_inicio=produto.semana_producao_inicio,
			semana_producao_fim=produto.semana_producao_fim,
			capacidade=produto.capacidade,
			unidade_medida=produto.unidade_medida,
			certificado=produto.certificado,
		)
		self.session.add(produto_fornecedor)
		self.session.commit()

	def listar_fechos_freguesia(self, apenas_ativos: bool = False) -> List[FreguesiaFechoORM]:
		q = self.session.query(FreguesiaFechoORM)
		if apenas_ativos:
			q = q.filter_by(ativo=True)
		return q.all()

	def definir_fecho_freguesia(self, nome: str, ativo: bool) -> FreguesiaFechoORM:
		registro = self.session.query(FreguesiaFechoORM).filter_by(nome=nome).first()
		if not registro:
			registro = FreguesiaFechoORM(nome=nome, ativo=ativo)
			self.session.add(registro)
		else:
			registro.ativo = ativo
		self.session.commit()
		return registro

	def _to_model(self, orm: FornecedorORM, estado: FornecedorEstadoORM | None = None) -> FornecedorModel:
		produtos = [
			ProdutoFornecedorModel(
				fornecedor_id=orm.id,
				produto_id=p.produto_id,
				nome=p.produto.nome if p.produto else None,
				tipo=p.produto.tipo if p.produto else None,
				biologico=p.biologico,
				semana_producao_inicio=p.semana_producao_inicio,
				semana_producao_fim=p.semana_producao_fim,
				capacidade=p.capacidade,
				unidade_medida=p.unidade_medida,
				certificado=p.certificado,
				data_inscricao=p.data_inscricao,
			)
			for p in orm.produtos
		]
		return FornecedorModel(
			id=orm.id,
			nome=orm.nome,
			data_inscricao=orm.data_inscricao,
			produtos=produtos,
			aprovado=orm.aprovado,
			local=orm.local,
			certificado=orm.certificado,
			usuario_id=orm.usuario_id,
			em_quarentena=estado.em_quarentena if estado else False,
			freguesia=estado.freguesia if estado else None,
		)
