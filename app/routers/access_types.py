import unicodedata
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.dependencies import DatabaseSession, check_permission
from app.models import (
    AccessType,
    ModuleCatalog,
    Permission,
    ReportCatalog,
    User,
)
from app.schemas import (
    AccessTypeResponse,
    AccessTypeStatusUpdate,
    AccessTypeWrite,
)


router = APIRouter(prefix="/api/v1/access-types", tags=["tipos de acesso"])
Manager = Annotated[User, Depends(check_permission("tipos_acesso_gerenciar"))]


def normalize_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name.strip())
    return "".join(
        character for character in normalized if not unicodedata.combining(character)
    ).casefold()


def _query():
    return select(AccessType).options(
        selectinload(AccessType.modules),
        selectinload(AccessType.permissions),
        selectinload(AccessType.reports),
        selectinload(AccessType.users),
    )


def _get_or_404(db: Session, access_type_id: str) -> AccessType:
    access_type = db.scalar(_query().where(AccessType.id == access_type_id))
    if access_type is None:
        raise HTTPException(status_code=404, detail="Tipo de acesso não encontrado")
    return access_type


def _response(access_type: AccessType) -> AccessTypeResponse:
    return AccessTypeResponse(
        id=access_type.id,
        nome=access_type.nome,
        descricao=access_type.descricao,
        cor=access_type.cor,
        ativo=access_type.ativo,
        sistema=access_type.sistema,
        modulo_ids=[module.id for module in access_type.modules],
        permission_ids=[permission.id for permission in access_type.permissions],
        relatorio_ids=[report.id for report in access_type.reports],
        usuarios_vinculados=len(access_type.users),
    )


def _relations(
    db: Session, payload: AccessTypeWrite
) -> tuple[list[ModuleCatalog], list[Permission], list[ReportCatalog]]:
    modules = list(
        db.scalars(
            select(ModuleCatalog).where(ModuleCatalog.id.in_(payload.modulo_ids))
        )
    )
    permissions = list(
        db.scalars(select(Permission).where(Permission.id.in_(payload.permission_ids)))
    )
    reports = list(
        db.scalars(
            select(ReportCatalog).where(ReportCatalog.id.in_(payload.relatorio_ids))
        )
    )
    if (
        len(modules) != len(set(payload.modulo_ids))
        or len(permissions) != len(set(payload.permission_ids))
        or len(reports) != len(set(payload.relatorio_ids))
    ):
        raise HTTPException(
            status_code=422,
            detail="Módulo, permissão ou relatório inválido",
        )
    return modules, permissions, reports


def _commit(db: Session, access_type: AccessType) -> AccessTypeResponse:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um tipo de acesso com este nome",
        ) from error
    return _response(_get_or_404(db, access_type.id))


@router.get("", response_model=list[AccessTypeResponse])
def list_access_types(db: DatabaseSession, _: Manager) -> list[AccessTypeResponse]:
    access_types = db.scalars(_query().order_by(AccessType.nome)).unique()
    return [_response(item) for item in access_types]


@router.post("", response_model=AccessTypeResponse, status_code=status.HTTP_201_CREATED)
def create_access_type(
    payload: AccessTypeWrite, db: DatabaseSession, _: Manager
) -> AccessTypeResponse:
    modules, permissions, reports = _relations(db, payload)
    access_type = AccessType(
        nome=payload.nome,
        nome_normalizado=normalize_name(payload.nome),
        descricao=payload.descricao,
        cor=payload.cor,
        ativo=payload.ativo,
        sistema=False,
        modules=modules,
        permissions=permissions,
        reports=reports,
    )
    db.add(access_type)
    return _commit(db, access_type)


@router.put("/{access_type_id}", response_model=AccessTypeResponse)
def update_access_type(
    access_type_id: str,
    payload: AccessTypeWrite,
    db: DatabaseSession,
    _: Manager,
) -> AccessTypeResponse:
    access_type = _get_or_404(db, access_type_id)
    modules, permissions, reports = _relations(db, payload)
    if (
        access_type.sistema
        and normalize_name(payload.nome) != access_type.nome_normalizado
    ):
        raise HTTPException(
            status_code=422,
            detail="O nome de um perfil de sistema não pode ser alterado",
        )
    access_type.nome = payload.nome
    access_type.nome_normalizado = normalize_name(payload.nome)
    access_type.descricao = payload.descricao
    access_type.cor = payload.cor
    access_type.ativo = payload.ativo
    access_type.modules = modules
    access_type.permissions = permissions
    access_type.reports = reports
    return _commit(db, access_type)


@router.patch("/{access_type_id}/status", response_model=AccessTypeResponse)
def update_access_type_status(
    access_type_id: str,
    payload: AccessTypeStatusUpdate,
    db: DatabaseSession,
    _: Manager,
) -> AccessTypeResponse:
    access_type = _get_or_404(db, access_type_id)
    access_type.ativo = payload.ativo
    return _commit(db, access_type)


@router.delete("/{access_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_access_type(access_type_id: str, db: DatabaseSession, _: Manager) -> None:
    access_type = _get_or_404(db, access_type_id)
    if access_type.sistema:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Perfis de sistema não podem ser removidos",
        )
    user_count = (
        db.scalar(
            select(func.count(User.id))
            .join(User.tipos_acesso)
            .where(AccessType.id == access_type.id)
        )
        or 0
    )
    if user_count:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(f"Tipo de acesso possui usuários vinculados: {user_count}"),
        )
    db.delete(access_type)
    db.commit()
