from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from ..db.models import EmentaORM, RefeicaoORM, ItemRefeicaoORM
from ..models.ementa import EmentaModel, RefeicaoModel, ItemRefeicaoModel


class EmentaRepo:
    def __init__(self, session: Session):
        self.session = session

    def criar_ementa(self, model: EmentaModel) -> EmentaModel:
        orm = EmentaORM(
            nome=model.nome,
            data_inicio=model.data_inicio,
            data_fim=model.data_fim,
        )
        
        # Criar refeições
        orm.refeicoes = []
        for ref in model.refeicoes:
            refeicao_orm = RefeicaoORM(
                dia_semana=ref.dia_semana,
                tipo=ref.tipo,
                descricao=ref.descricao,
            )
            
            # Criar itens da refeição
            refeicao_orm.itens = [
                ItemRefeicaoORM(
                    produto_id=item.produto_id,
                    ingrediente=item.ingrediente,
                    quantidade_estimada=item.quantidade_estimada,
                )
                for item in ref.itens
            ]
            
            orm.refeicoes.append(refeicao_orm)
        
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        
        model.id = orm.id
        return model

    def listar_ementas(self) -> List[EmentaModel]:
        results = self.session.query(EmentaORM).all()
        return [self._to_model(orm) for orm in results]

    def obter_ementa(self, ementa_id: int) -> Optional[EmentaModel]:
        orm = self.session.get(EmentaORM, ementa_id)
        return self._to_model(orm) if orm else None

    def atualizar_ementa(self, model: EmentaModel) -> Optional[EmentaModel]:
        orm = self.session.get(EmentaORM, model.id)
        if not orm:
            return None
        
        orm.nome = model.nome
        orm.data_inicio = model.data_inicio
        orm.data_fim = model.data_fim
        
        # Remover refeições antigas e criar novas
        # (simplificado - em produção, considerar update inteligente)
        for ref in orm.refeicoes:
            self.session.delete(ref)
        
        orm.refeicoes = []
        for ref in model.refeicoes:
            refeicao_orm = RefeicaoORM(
                dia_semana=ref.dia_semana,
                tipo=ref.tipo,
                descricao=ref.descricao,
            )
            
            refeicao_orm.itens = [
                ItemRefeicaoORM(
                    produto_id=item.produto_id,
                    ingrediente=item.ingrediente,
                    quantidade_estimada=item.quantidade_estimada,
                )
                for item in ref.itens
            ]
            
            orm.refeicoes.append(refeicao_orm)
        
        self.session.commit()
        self.session.refresh(orm)
        return self._to_model(orm)

    def deletar_ementa(self, ementa_id: int) -> bool:
        orm = self.session.get(EmentaORM, ementa_id)
        if not orm:
            return False
        
        self.session.delete(orm)
        self.session.commit()
        return True

    def listar_por_periodo(self, data_inicio: date, data_fim: date) -> List[EmentaORM]:
        """
        Retorna todas as ementas que se sobrepõem ao período especificado.
        Uma ementa se sobrepõe se:
        - Começa antes do fim do período E
        - Termina depois do início do período
        """
        return self.session.query(EmentaORM).filter(
            EmentaORM.data_inicio <= data_fim,
            EmentaORM.data_fim >= data_inicio
        ).all()

    def _to_model(self, orm: EmentaORM) -> EmentaModel:
        refeicoes = []
        for ref_orm in orm.refeicoes:
            itens = [
                ItemRefeicaoModel(
                    produto_id=item.produto_id,
                    ingrediente=item.ingrediente,
                    quantidade_estimada=item.quantidade_estimada,
                )
                for item in ref_orm.itens
            ]
            
            refeicoes.append(RefeicaoModel(
                dia_semana=ref_orm.dia_semana,
                tipo=ref_orm.tipo,
                descricao=ref_orm.descricao,
                itens=itens,
            ))
        
        return EmentaModel(
            id=orm.id,
            nome=orm.nome,
            data_inicio=orm.data_inicio,
            data_fim=orm.data_fim,
            refeicoes=refeicoes,
        )
