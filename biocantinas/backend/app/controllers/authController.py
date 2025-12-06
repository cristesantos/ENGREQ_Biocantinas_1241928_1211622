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


class Credentials(BaseModel):
    username: str
    password: str


@router.post("/signup", response_model=User)
def signup(payload: Credentials):
	# Force role to PRODUTOR for signup, ignore provided role
	svc = get_user_service()
	try:
		user = svc.create_user(username=payload.username, password=payload.password, role="PRODUTOR")
		return user
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(payload: Credentials):
	svc = get_user_service()
	user = svc.verify_user(username=payload.username, password=payload.password)
	if not user:
		raise HTTPException(status_code=401, detail="Credenciais inválidas")
	token = create_access_token(user)
	return TokenResponse(access_token=token, role=user.role, username=user.username)

