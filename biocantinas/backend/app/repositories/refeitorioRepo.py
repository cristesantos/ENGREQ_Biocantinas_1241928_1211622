from typing import List, Optional
from sqlalchemy.orm import Session
from ..db.models import RefeitorioORM


class RefeitorioRepo:
    def __init__(self, session: Session):
        self.session = session

    def criar(self, nome: str, localizacao: str | None, gestor_id: int | None, cantina_id: int | None) -> RefeitorioORM:
        refeitorio = RefeitorioORM(nome=nome, localizacao=localizacao, gestor_id=gestor_id, cantina_id=cantina_id)
        self.session.add(refeitorio)
        self.session.commit()
        self.session.refresh(refeitorio)
        return refeitorio

    def listar(self) -> List[RefeitorioORM]:
        return self.session.query(RefeitorioORM).all()

    def obter(self, refeitorio_id: int) -> Optional[RefeitorioORM]:
        return self.session.get(RefeitorioORM, refeitorio_id)

    def atualizar(self, refeitorio_id: int, **dados) -> Optional[RefeitorioORM]:
        ref = self.session.get(RefeitorioORM, refeitorio_id)
        if not ref:
            return None
        for k, v in dados.items():
            setattr(ref, k, v)
        self.session.commit()
        self.session.refresh(ref)
        return ref

    def deletar(self, refeitorio_id: int) -> bool:
        ref = self.session.get(RefeitorioORM, refeitorio_id)
        if not ref:
            return False
        self.session.delete(ref)
        self.session.commit()
        return True
