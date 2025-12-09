from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..dtos.userDTO import User
from ..services.userService import get_user_service
from ..auth.jwt import create_access_token

router = APIRouter(tags=["auth"], prefix="/auth")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class SignupCredentials(BaseModel):
    username: str
    password: str
    role: str


class LoginCredentials(BaseModel):
    username: str
    password: str


@router.post("/signup", response_model=User)
def signup(payload: SignupCredentials):
    svc = get_user_service()
    try:
        # Do not force a default role; require provided role
        if payload.role is None or not isinstance(payload.role, str) or payload.role.strip() == "":
            raise ValueError("Role é obrigatório no registo")
        user = svc.create_user(username=payload.username, password=payload.password, role=payload.role)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginCredentials):
	svc = get_user_service()
	user = svc.verify_user(username=payload.username, password=payload.password)
	if not user:
		raise HTTPException(status_code=401, detail="Credenciais inválidas")
	token = create_access_token(user)
	return TokenResponse(access_token=token, role=user.role, username=user.username)

