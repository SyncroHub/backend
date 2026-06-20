import argparse
import json
import os
from pathlib import Path
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import (
    AccessType,
    FunctionCatalog,
    ModuleCatalog,
    Permission,
    ReportCatalog,
    Store,
    User,
    UserType,
)
from app.routers.access_types import normalize_name
from app.security import generate_temporary_password, hash_password
from app.seed_data import (
    ACCESS_TYPES,
    FUNCTIONS,
    MODULES,
    PDV_USERS,
    REPORTS,
    STORES,
    SUPER_ADMINS,
)


def _existing_by_legacy(db: Session, model: type[Any], legacy_id: int) -> Any | None:
    return db.scalar(select(model).where(model.legacy_id == legacy_id))


def seed_catalogs(db: Session) -> dict[str, dict[int, Any]]:
    modules: dict[int, ModuleCatalog] = {}
    for legacy_id, code, name, category in MODULES:
        item = _existing_by_legacy(db, ModuleCatalog, legacy_id)
        if item is None:
            item = ModuleCatalog(
                legacy_id=legacy_id,
                codigo=code,
                nome=name,
                categoria=category,
            )
            db.add(item)
        modules[legacy_id] = item
    db.flush()

    permissions: dict[int, Permission] = {}
    for legacy_id, module_legacy_id, code, name in FUNCTIONS:
        function = _existing_by_legacy(db, FunctionCatalog, legacy_id)
        if function is None:
            function = FunctionCatalog(
                legacy_id=legacy_id,
                modulo_id=modules[module_legacy_id].id,
                codigo=code,
                nome=name,
            )
            db.add(function)
        permission = db.scalar(select(Permission).where(Permission.codigo == code))
        if permission is None:
            permission = Permission(codigo=code, nome=name)
            db.add(permission)
        permissions[legacy_id] = permission
    db.flush()

    reports: dict[int, ReportCatalog] = {}
    for legacy_id, module_legacy_id, code, name in REPORTS:
        report = _existing_by_legacy(db, ReportCatalog, legacy_id)
        if report is None:
            report = ReportCatalog(
                legacy_id=legacy_id,
                modulo_id=modules[module_legacy_id].id,
                codigo=code,
                nome=name,
            )
            db.add(report)
        reports[legacy_id] = report
    db.flush()
    return {
        "modules": modules,
        "permissions": permissions,
        "reports": reports,
    }


def seed_stores(db: Session) -> dict[int, Store]:
    stores: dict[int, Store] = {}
    for legacy_id, name, city, state, active in STORES:
        store = _existing_by_legacy(db, Store, legacy_id)
        if store is None:
            store = Store(
                legacy_id=legacy_id,
                nome=name,
                cidade=city,
                uf=state,
                ativo=active,
            )
            db.add(store)
        stores[legacy_id] = store
    db.flush()
    return stores


def _select_ids(items: dict[int, Any], selected: object) -> list[Any]:
    if selected == "all":
        return list(items.values())
    selected_ids = cast(list[int], selected)
    return [items[item_id] for item_id in selected_ids]


def seed_access_types(
    db: Session, catalogs: dict[str, dict[int, Any]]
) -> dict[int, AccessType]:
    access_types: dict[int, AccessType] = {}
    for (
        legacy_id,
        name,
        description,
        color,
        module_ids,
        permission_ids,
        report_ids,
    ) in ACCESS_TYPES:
        access_type = _existing_by_legacy(db, AccessType, legacy_id)
        if access_type is None:
            access_type = AccessType(
                legacy_id=legacy_id,
                nome=name,
                nome_normalizado=normalize_name(name),
                descricao=description,
                cor=color,
                ativo=True,
                sistema=True,
            )
            db.add(access_type)
        access_type.modules = _select_ids(catalogs["modules"], module_ids)
        access_type.permissions = _select_ids(catalogs["permissions"], permission_ids)
        access_type.reports = _select_ids(catalogs["reports"], report_ids)
        access_types[legacy_id] = access_type
    db.flush()
    return access_types


def seed_users(
    db: Session,
    stores: dict[int, Store],
    access_types: dict[int, AccessType],
) -> list[dict[str, str]]:
    credentials: list[dict[str, str]] = []
    for name, email in SUPER_ADMINS:
        if db.scalar(select(User).where(User.email == email)):
            continue
        password = generate_temporary_password()
        db.add(
            User(
                nome=name,
                email=email,
                senha_hash=hash_password(password, settings.bcrypt_rounds),
                tipo=UserType.SUPER_ADMIN,
                cargo="Super Admin",
                nivel=5,
                ativo=True,
                force_password_change=True,
                tipos_acesso=[access_types[1]],
            )
        )
        credentials.append({"email": email, "senha_temporaria": password})

    store_legacy_ids = [store[0] for store in STORES]
    for index, (user_id, email) in enumerate(PDV_USERS):
        if db.scalar(select(User).where(User.email == email)):
            continue
        store = stores[store_legacy_ids[index]]
        password = generate_temporary_password()
        db.add(
            User(
                nome=store.nome,
                email=email,
                senha_hash=hash_password(password, settings.bcrypt_rounds),
                tipo=UserType.PDV,
                cargo="PDV",
                nivel=1,
                ativo=store.ativo,
                force_password_change=True,
                loja=store,
                tipos_acesso=[access_types[8]],
            )
        )
        credentials.append(
            {
                "usuario_legado_id": str(user_id),
                "email": email,
                "senha_temporaria": password,
            }
        )
    db.flush()
    return credentials


def write_credentials(path: Path, credentials: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        json.dump(credentials, output, ensure_ascii=False, indent=2)
        output.write("\n")


def run_seed(credentials_output: Path | None, catalogs_only: bool) -> None:
    if not catalogs_only and credentials_output is None:
        raise SystemExit("--credentials-output é obrigatório para o seed de usuários")
    with SessionLocal() as db:
        catalogs = seed_catalogs(db)
        stores = seed_stores(db)
        access_types = seed_access_types(db, catalogs)
        credentials = [] if catalogs_only else seed_users(db, stores, access_types)
        if credentials and credentials_output:
            write_credentials(credentials_output, credentials)
        db.commit()
    print(f"Seed concluído; {len(credentials)} credenciais temporárias criadas.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed inicial do SyncroHUB")
    parser.add_argument("--credentials-output", type=Path)
    parser.add_argument("--catalogs-only", action="store_true")
    arguments = parser.parse_args()
    run_seed(arguments.credentials_output, arguments.catalogs_only)


if __name__ == "__main__":
    main()
