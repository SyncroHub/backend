import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.config import Settings
from app.models import User


def hash_password(password: str, rounds: int) -> str:
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


def validate_password_policy(password: str) -> list[str]:
    errors: list[str] = []
    if len(password) < 8:
        errors.append("ter pelo menos 8 caracteres")
    if not any(character.isupper() for character in password):
        errors.append("conter uma letra maiúscula")
    if not any(character.isdigit() for character in password):
        errors.append("conter um número")
    if not any(not character.isalnum() for character in password):
        errors.append("conter um símbolo")
    return errors


def permission_codes(user: User) -> list[str]:
    if user.tipo.value == "super_admin":
        return ["*"]
    return sorted(
        {
            permission.codigo
            for access_type in user.tipos_acesso
            if access_type.ativo
            for permission in access_type.permissions
        }
    )


def create_access_token(user: User, config: Settings) -> tuple[str, int]:
    expires_in = config.access_token_minutes * 60
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.id,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "func_ids": permission_codes(user),
        "force_password_change": user.force_password_change,
    }
    token = jwt.encode(payload, config.jwt_secret, algorithm=config.jwt_algorithm)
    return token, expires_in


def decode_access_token(token: str, config: Settings) -> dict[str, Any]:
    payload = jwt.decode(token, config.jwt_secret, algorithms=[config.jwt_algorithm])
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Tipo de token inválido")
    return payload


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_temporary_password(length: int = 16) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%&*+-_"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if not validate_password_policy(password):
            return password
