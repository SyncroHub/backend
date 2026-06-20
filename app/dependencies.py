from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.database import get_db
from app.models import AccessType, User
from app.security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)
DatabaseSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DatabaseSession,
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de acesso inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = decode_access_token(credentials.credentials, settings)
    except jwt.PyJWTError as error:
        raise unauthorized from error

    user = db.scalar(
        select(User)
        .where(User.id == payload.get("sub"), User.deleted_at.is_(None))
        .options(
            selectinload(User.loja),
            selectinload(User.tipos_acesso).selectinload(AccessType.permissions),
        )
    )
    if user is None or not user.ativo:
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_password_changed(user: CurrentUser) -> User:
    if user.force_password_change:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Troca de senha obrigatória antes de acessar este recurso",
        )
    return user


def check_permission(permission_code: str) -> Callable[..., User]:
    def dependency(user: CurrentUser) -> User:
        if user.force_password_change:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Troca de senha obrigatória antes de acessar este recurso",
            )
        if user.tipo.value == "super_admin":
            return user
        permissions = {
            permission.codigo
            for access_type in user.tipos_acesso
            if access_type.ativo
            for permission in access_type.permissions
        }
        if permission_code not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão necessária: {permission_code}",
            )
        return user

    return dependency


def enforce_hierarchy(actor: User, target_level: int) -> None:
    if actor.tipo.value == "super_admin":
        return
    if target_level >= actor.nivel:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é permitido gerenciar usuário de nível igual ou superior",
        )
