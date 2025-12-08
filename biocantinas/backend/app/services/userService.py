from typing import Optional, List
from passlib.context import CryptContext
from ..db.session import SessionLocal, init_db
from ..repositories.userRepo import UserRepo
from ..db.models import UserORM


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self):
        init_db()
        self.session = SessionLocal()
        self.repo = UserRepo(self.session)

    def create_user(self, username: str, password: str, role: str) -> UserORM:
        # bcrypt has a 72-byte limit; truncate password to 72 bytes (not characters)
        password_bytes = password.encode('utf-8')[:72]
        password_hash = pwd_context.hash(password_bytes.decode('utf-8', errors='ignore'))
        return self.repo.create(username=username, password_hash=password_hash, role=role)

    def verify_user(self, username: str, password: str) -> Optional[UserORM]:
        user = self.repo.get_by_username(username)
        if not user:
            return None
        # bcrypt has a 72-byte limit; truncate password to 72 bytes
        password_bytes = password.encode('utf-8')[:72]
        safe_password = password_bytes.decode('utf-8', errors='ignore')
        if not pwd_context.verify(safe_password, user.hashed_password):
            return None
        return user

    def get_user(self, user_id: int) -> Optional[UserORM]:
        return self.repo.get(user_id)

    def list_users(self) -> List[UserORM]:
        return self.repo.list()

_users = UserService()

def get_user_service() -> UserService:
    return _users
