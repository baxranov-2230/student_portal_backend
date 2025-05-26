from pydantic import BaseModel
from src.models.user import UserRole


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class RegisterUser(BaseModel):
    full_name: str
    password: str


class AdminCreate(RegisterUser):
    role: UserRole
