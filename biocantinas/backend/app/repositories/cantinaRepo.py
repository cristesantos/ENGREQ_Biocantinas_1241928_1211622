from typing import List, Optional
from sqlalchemy.orm import Session
from ..db.models import CantinaORM


class CantinaRepo:
    def __init__(self, session: Session):
        self.session = session

    def criar(self, nome: str, localizacao: str | None, tipo: str, gestor_id: int | None) -> CantinaORM:
        cantina = CantinaORM(nome=nome, localizacao=localizacao, tipo=tipo, gestor_id=gestor_id)
        self.session.add(cantina)
        self.session.commit()
        self.session.refresh(cantina)
        return cantina

    def listar(self) -> List[CantinaORM]:
        return self.session.query(CantinaORM).all()

    def obter(self, cantina_id: int) -> Optional[CantinaORM]:
        return self.session.get(CantinaORM, cantina_id)

    def atualizar(self, cantina_id: int, **dados) -> Optional[CantinaORM]:
        cantina = self.session.get(CantinaORM, cantina_id)
        if not cantina:
            return None
        for k, v in dados.items():
            setattr(cantina, k, v)
        self.session.commit()
        self.session.refresh(cantina)
        return cantina

    def deletar(self, cantina_id: int) -> bool:
        cantina = self.session.get(CantinaORM, cantina_id)
        if not cantina:
            return False
        self.session.delete(cantina)
        self.session.commit()
        return True
