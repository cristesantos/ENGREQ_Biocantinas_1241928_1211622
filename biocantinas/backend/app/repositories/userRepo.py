from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..db.models import UserORM


class UserRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, username: str, password_hash: str, role: str) -> UserORM:
        try:
            user = UserORM(username=username, hashed_password=password_hash, role=role)
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except IntegrityError:
            self.session.rollback()
            raise ValueError(f"Username '{username}' já existe")

    def get_by_username(self, username: str) -> Optional[UserORM]:
        return self.session.query(UserORM).filter(UserORM.username == username).first()

    def get(self, user_id: int) -> Optional[UserORM]:
        return self.session.get(UserORM, user_id)

    def list(self) -> List[UserORM]:
        return self.session.query(UserORM).all()

    def delete(self, user_id: int) -> None:
        try:
            user = self.session.get(UserORM, user_id)
            if user:
                self.session.delete(user)
                self.session.commit()
        except Exception:
            self.session.rollback()
            raise
