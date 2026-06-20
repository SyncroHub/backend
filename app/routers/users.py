import math
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql.elements import ColumnElement

from app.config import settings
from app.dependencies import (
    DatabaseSession,
    check_permission,
    enforce_hierarchy,
    require_password_changed,
)
from app.models import AccessType, Store, User, UserType, user_access_types
from app.schemas import (
    PaginatedUsers,
    UserCreate,
    UserResponse,
    UserStatusUpdate,
    UserSummary,
    UserUpdate,
)
from app.security import hash_password, validate_password_policy


router = APIRouter(prefix="/api/v1/users", tags=["usuários"])
AuthenticatedUser = Annotated[User, Depends(require_password_changed)]


def _user_query():
    return select(User).options(
        selectinload(User.loja),
        selectinload(User.tipos_acesso),
    )


def _get_user_or_404(db: Session, user_id: str) -> User:
    user = db.scalar(_user_query().where(User.id == user_id, User.deleted_at.is_(None)))
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


def _validate_password(password: str) -> None:
    errors = validate_password_policy(password)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="A senha deve " + ", ".join(errors),
        )


def _load_relations(
    db: Session,
    loja_id: str | None,
    access_type_ids: list[str],
) -> tuple[Store | None, list[AccessType]]:
    store = None
    if loja_id:
        store = db.get(Store, loja_id)
        if store is None:
            raise HTTPException(status_code=422, detail="Loja inválida")
    access_types = list(
        db.scalars(select(AccessType).where(AccessType.id.in_(access_type_ids)))
    )
    if len(access_types) != len(set(access_type_ids)):
        raise HTTPException(
            status_code=422, detail="Um ou mais tipos de acesso são inválidos"
        )
    return store, access_types


def _commit_user(db: Session, user: User) -> User:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este email",
        ) from error
    return _get_user_or_404(db, user.id)


@router.get("", response_model=PaginatedUsers)
def list_users(
    db: DatabaseSession,
    _: AuthenticatedUser,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=15, ge=1, le=100),
    tipo: UserType | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    access_type_id: str | None = Query(default=None, alias="tiposAcesso"),
    q: str | None = Query(default=None, max_length=255),
) -> PaginatedUsers:
    conditions: list[ColumnElement[bool]] = [User.deleted_at.is_(None)]
    if tipo:
        conditions.append(User.tipo == tipo)
    if status_filter in {"ativo", "true", "1"}:
        conditions.append(User.ativo.is_(True))
    elif status_filter in {"inativo", "false", "0"}:
        conditions.append(User.ativo.is_(False))
    if q:
        search = f"%{q.strip()}%"
        conditions.append(or_(User.nome.ilike(search), User.email.ilike(search)))

    query = _user_query().where(*conditions)
    count_query = select(func.count(func.distinct(User.id))).where(*conditions)
    if access_type_id:
        query = query.join(user_access_types).where(
            user_access_types.c.tipo_acesso_id == access_type_id
        )
        count_query = count_query.join(user_access_types).where(
            user_access_types.c.tipo_acesso_id == access_type_id
        )

    total = db.scalar(count_query) or 0
    users = list(
        db.scalars(
            query.order_by(User.nome).offset((page - 1) * limit).limit(limit)
        ).unique()
    )
    return PaginatedUsers(
        items=users,
        page=page,
        limit=limit,
        total=total,
        pages=math.ceil(total / limit) if total else 0,
    )


@router.get("/summary", response_model=UserSummary)
def users_summary(db: DatabaseSession, _: AuthenticatedUser) -> UserSummary:
    users = list(db.scalars(select(User).where(User.deleted_at.is_(None))))
    return UserSummary(
        total=len(users),
        admins=sum(
            user.tipo in {UserType.SUPER_ADMIN, UserType.ADMINISTRATIVO}
            for user in users
        ),
        supervisoes=sum(
            user.tipo in {UserType.SUPERVISAO_GERAL, UserType.SUPERVISAO_REGIONAL}
            for user in users
        ),
        lojas=sum(user.tipo in {UserType.LOJA, UserType.PDV} for user in users),
        inativos=sum(not user.ativo for user in users),
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: DatabaseSession, _: AuthenticatedUser) -> User:
    return _get_user_or_404(db, user_id)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: DatabaseSession,
    actor: Annotated[User, Depends(check_permission("usuarios_criar"))],
) -> User:
    enforce_hierarchy(actor, payload.nivel)
    _validate_password(payload.senha)
    store, access_types = _load_relations(db, payload.loja_id, payload.tipos_acesso_ids)
    user = User(
        nome=payload.nome.strip(),
        email=payload.email.lower(),
        senha_hash=hash_password(payload.senha, settings.bcrypt_rounds),
        tipo=payload.tipo,
        cargo=payload.cargo,
        nivel=payload.nivel,
        ativo=payload.ativo,
        force_password_change=payload.force_password_change,
        loja=store,
        tipos_acesso=access_types,
    )
    db.add(user)
    return _commit_user(db, user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: DatabaseSession,
    actor: Annotated[User, Depends(check_permission("usuarios_editar"))],
) -> User:
    user = _get_user_or_404(db, user_id)
    enforce_hierarchy(actor, user.nivel)
    changes = payload.model_dump(exclude_unset=True)
    desired_level = changes.get("nivel", user.nivel)
    enforce_hierarchy(actor, desired_level)

    if "senha" in changes:
        _validate_password(changes["senha"])
        user.senha_hash = hash_password(changes.pop("senha"), settings.bcrypt_rounds)
    if "email" in changes:
        changes["email"] = str(changes["email"]).lower()
    if "loja_id" in changes or "tipos_acesso_ids" in changes:
        loja_id = changes.pop("loja_id", user.loja_id if user.loja_id else None)
        access_ids = changes.pop(
            "tipos_acesso_ids",
            [access_type.id for access_type in user.tipos_acesso],
        )
        store, access_types = _load_relations(db, loja_id, access_ids)
        user.loja = store
        user.tipos_acesso = access_types
    for field, value in changes.items():
        setattr(user, field, value)
    return _commit_user(db, user)


@router.patch("/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: str,
    payload: UserStatusUpdate,
    db: DatabaseSession,
    actor: Annotated[User, Depends(check_permission("usuarios_desativar"))],
) -> User:
    user = _get_user_or_404(db, user_id)
    if user.id == actor.id:
        raise HTTPException(
            status_code=422, detail="Não é possível alterar o próprio status"
        )
    enforce_hierarchy(actor, user.nivel)
    user.ativo = payload.ativo
    return _commit_user(db, user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: DatabaseSession,
    actor: Annotated[User, Depends(check_permission("usuarios_editar"))],
) -> None:
    user = _get_user_or_404(db, user_id)
    if user.id == actor.id:
        raise HTTPException(
            status_code=422, detail="Não é possível remover o próprio usuário"
        )
    enforce_hierarchy(actor, user.nivel)
    user.deleted_at = datetime.now(timezone.utc)
    user.ativo = False
    db.commit()
