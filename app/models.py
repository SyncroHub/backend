from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid.uuid4())


class UserType(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    SUPERVISAO_GERAL = "supervisao_geral"
    SUPERVISAO_REGIONAL = "supervisao_regional"
    LOJA = "loja"
    PDV = "pdv"
    FINANCEIRO = "financeiro"
    COMPRAS = "compras"
    RH_PESSOAL = "rh_pessoal"
    ADMINISTRATIVO = "administrativo"
    GERADOR_COTAS = "gerador_cotas"
    PREV_RECEBER = "prev_receber"
    GERADOR_COMPRAS = "gerador_compras"


user_access_types = Table(
    "users_tipos_acesso",
    Base.metadata,
    Column(
        "user_id",
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tipo_acesso_id",
        String(36),
        ForeignKey("tipos_acesso.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

access_type_modules = Table(
    "tipos_acesso_modulos",
    Base.metadata,
    Column(
        "tipo_acesso_id",
        String(36),
        ForeignKey("tipos_acesso.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "modulo_id",
        String(36),
        ForeignKey("modulos_catalogo.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

access_type_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "tipo_acesso_id",
        String(36),
        ForeignKey("tipos_acesso.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        String(36),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

access_type_reports = Table(
    "tipos_acesso_relatorios",
    Base.metadata,
    Column(
        "tipo_acesso_id",
        String(36),
        ForeignKey("tipos_acesso.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "relatorio_id",
        String(36),
        ForeignKey("rels_catalogo.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class Store(TimestampMixin, Base):
    __tablename__ = "lojas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    legacy_id: Mapped[int | None] = mapped_column(Integer, unique=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    users: Mapped[list[User]] = relationship(back_populates="loja")


class ModuleCatalog(Base):
    __tablename__ = "modulos_catalogo"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    legacy_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    codigo: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    categoria: Mapped[str] = mapped_column(String(80), nullable=False)


class FunctionCatalog(Base):
    __tablename__ = "funcs_catalogo"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    legacy_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    modulo_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("modulos_catalogo.id"), nullable=False
    )
    codigo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    codigo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)

    access_types: Mapped[list[AccessType]] = relationship(
        secondary=access_type_permissions, back_populates="permissions"
    )


class ReportCatalog(Base):
    __tablename__ = "rels_catalogo"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    legacy_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    modulo_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("modulos_catalogo.id"), nullable=False
    )
    codigo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)


class AccessType(TimestampMixin, Base):
    __tablename__ = "tipos_acesso"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    legacy_id: Mapped[int | None] = mapped_column(Integer, unique=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    nome_normalizado: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False
    )
    descricao: Mapped[str | None] = mapped_column(String(500))
    cor: Mapped[str | None] = mapped_column(String(20))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sistema: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    users: Mapped[list[User]] = relationship(
        secondary=user_access_types, back_populates="tipos_acesso"
    )
    modules: Mapped[list[ModuleCatalog]] = relationship(secondary=access_type_modules)
    permissions: Mapped[list[Permission]] = relationship(
        secondary=access_type_permissions, back_populates="access_types"
    )
    reports: Mapped[list[ReportCatalog]] = relationship(secondary=access_type_reports)


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_tipo_ativo", "tipo", "ativo"),
        Index("ix_users_nome", "nome"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[UserType] = mapped_column(
        Enum(
            UserType,
            name="tipo_usuario",
            native_enum=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        nullable=False,
    )
    cargo: Mapped[str | None] = mapped_column(String(100))
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    force_password_change: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    loja_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("lojas.id"), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    loja: Mapped[Store | None] = relationship(back_populates="users")
    tipos_acesso: Mapped[list[AccessType]] = relationship(
        secondary=user_access_types, back_populates="users"
    )
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
        Index("ix_refresh_tokens_user_active", "user_id", "revoked_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("refresh_tokens.id")
    )

    user: Mapped[User] = relationship(
        back_populates="refresh_tokens", foreign_keys=[user_id]
    )
