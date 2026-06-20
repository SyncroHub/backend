from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.config import settings
from app.dependencies import CurrentUser, DatabaseSession
from app.models import AccessType, RefreshToken, User
from app.rate_limit import LoginRateLimiter
from app.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    validate_password_policy,
    verify_password,
)


router = APIRouter(prefix="/api/v1/auth", tags=["autenticação"])
rate_limiter = LoginRateLimiter(settings)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _is_expired(value: datetime) -> bool:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value <= _now()


def _issue_tokens(user: User, db: DatabaseSession) -> TokenResponse:
    access_token, expires_in = create_access_token(user, settings)
    refresh_token = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=_now() + timedelta(days=settings.refresh_token_days),
        )
    )
    db.flush()
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        force_password_change=user.force_password_change,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: DatabaseSession,
) -> TokenResponse:
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.check(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas de login. Tente novamente em um minuto",
        )

    user = db.scalar(
        select(User)
        .where(
            User.email == payload.email.lower(),
            User.deleted_at.is_(None),
        )
        .options(selectinload(User.tipos_acesso).selectinload(AccessType.permissions))
    )
    if (
        user is None
        or not user.ativo
        or not verify_password(payload.senha, user.senha_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
        )

    rate_limiter.reset(client_ip)
    response = _issue_tokens(user, db)
    db.commit()
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: DatabaseSession) -> None:
    token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(payload.refresh_token),
            RefreshToken.revoked_at.is_(None),
        )
    )
    if token is not None:
        token.revoked_at = _now()
        db.commit()


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: DatabaseSession) -> TokenResponse:
    current_token = db.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == hash_refresh_token(payload.refresh_token))
        .options(
            selectinload(RefreshToken.user)
            .selectinload(User.tipos_acesso)
            .selectinload(AccessType.permissions)
        )
    )
    if (
        current_token is None
        or current_token.revoked_at is not None
        or _is_expired(current_token.expires_at)
        or not current_token.user.ativo
        or current_token.user.deleted_at is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )

    current_token.revoked_at = _now()
    response = _issue_tokens(current_token.user, db)
    replacement = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(response.refresh_token)
        )
    )
    current_token.replaced_by_id = replacement.id if replacement else None
    db.commit()
    return response


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUser) -> User:
    return user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: ChangePasswordRequest,
    user: CurrentUser,
    db: DatabaseSession,
) -> None:
    if not verify_password(payload.senha_atual, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )
    policy_errors = validate_password_policy(payload.nova_senha)
    if policy_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="A nova senha deve " + ", ".join(policy_errors),
        )
    if verify_password(payload.nova_senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="A nova senha deve ser diferente da senha atual",
        )

    user.senha_hash = hash_password(payload.nova_senha, rounds=settings.bcrypt_rounds)
    user.force_password_change = False
    db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=_now())
    )
    db.commit()
