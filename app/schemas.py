from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import UserType


class ErrorResponse(BaseModel):
    detail: str


class AccessTypeBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    cor: str | None


class StoreBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    cidade: str
    uf: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    email: EmailStr
    tipo: UserType
    cargo: str | None
    nivel: int
    ativo: bool
    force_password_change: bool
    loja: StoreBrief | None
    tipos_acesso: list[AccessTypeBrief]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class UserCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=255)
    email: EmailStr
    senha: str
    tipo: UserType
    cargo: str | None = Field(default=None, max_length=100)
    nivel: int = Field(ge=1, le=5)
    ativo: bool = True
    force_password_change: bool = False
    loja_id: str | None = None
    tipos_acesso_ids: list[str] = Field(default_factory=list)


class UserUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    senha: str | None = None
    tipo: UserType | None = None
    cargo: str | None = Field(default=None, max_length=100)
    nivel: int | None = Field(default=None, ge=1, le=5)
    force_password_change: bool | None = None
    loja_id: str | None = None
    tipos_acesso_ids: list[str] | None = None


class UserStatusUpdate(BaseModel):
    ativo: bool


class PaginatedUsers(BaseModel):
    items: list[UserResponse]
    page: int
    limit: int
    total: int
    pages: int


class UserSummary(BaseModel):
    total: int
    admins: int
    supervisoes: int
    lojas: int
    inativos: int


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20)


class LogoutRequest(RefreshRequest):
    pass


class ChangePasswordRequest(BaseModel):
    senha_atual: str
    nova_senha: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    force_password_change: bool


class AccessTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    descricao: str | None
    cor: str | None
    ativo: bool
    sistema: bool
    modulo_ids: list[str]
    permission_ids: list[str]
    relatorio_ids: list[str]
    usuarios_vinculados: int


class AccessTypeWrite(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    descricao: str | None = Field(default=None, max_length=500)
    cor: str | None = Field(default=None, max_length=20)
    ativo: bool = True
    modulo_ids: list[str] = Field(default_factory=list)
    permission_ids: list[str] = Field(default_factory=list)
    relatorio_ids: list[str] = Field(default_factory=list)

    @field_validator("nome")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()


class AccessTypeStatusUpdate(BaseModel):
    ativo: bool
