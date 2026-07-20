from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.auth.enums import Role


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: Role
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    user: AuthUser


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser


class CurrentUserResponse(BaseModel):
    user: AuthUser