import os
import time
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..dtos.userDTO import User
from ..services.userService import get_user_service
ALGORITHM = "HS256"
DEFAULT_EXP_SECONDS = 60 * 60 * 24  # 24h


def get_secret() -> str:
    secret = os.environ.get("BIOCANTINAS_JWT_SECRET")
    if not secret:
        # Dev fallback only
        secret = "dev-secret-change-me"
    return secret


def create_access_token(user: User, expires_in: int = DEFAULT_EXP_SECONDS) -> str:
    now = int(time.time())
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "iat": now,
        "exp": now + expires_in,
    }
    return jwt.encode(payload, get_secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, get_secret(), algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    data = decode_token(credentials.credentials)
    user_id = int(data.get("sub"))
    svc = get_user_service()
    user = svc.get_user(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Utilizador não existe")
    return user


def require_role(role: str):
    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role != role:
            raise HTTPException(status_code=403, detail="Sem permissão")
        return user
    return _dep
