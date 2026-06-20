from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import AccessType, Permission, User, UserType
from app.routers.auth import rate_limiter
from app.security import hash_password


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    with testing_session() as session:
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    rate_limiter._redis = None
    rate_limiter._attempts.clear()
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()


@pytest.fixture()
def seeded_users(db_session: Session) -> dict[str, User | AccessType]:
    permissions = [
        Permission(codigo=code, nome=code)
        for code in (
            "usuarios_criar",
            "usuarios_editar",
            "usuarios_desativar",
            "tipos_acesso_gerenciar",
        )
    ]
    admin_access = AccessType(
        nome="Administrativo",
        nome_normalizado="administrativo",
        sistema=True,
        ativo=True,
        permissions=permissions,
    )
    empty_access = AccessType(
        nome="Sem permissões",
        nome_normalizado="sem permissoes",
        sistema=False,
        ativo=True,
    )
    super_admin = User(
        nome="Super Admin",
        email="admin@example.com",
        senha_hash=hash_password("Admin#123", 4),
        tipo=UserType.SUPER_ADMIN,
        cargo="Super Admin",
        nivel=5,
        ativo=True,
        force_password_change=False,
        tipos_acesso=[admin_access],
    )
    manager = User(
        nome="Gestor",
        email="gestor@example.com",
        senha_hash=hash_password("Gestor#123", 4),
        tipo=UserType.ADMINISTRATIVO,
        cargo="Gestor",
        nivel=4,
        ativo=True,
        force_password_change=False,
        tipos_acesso=[admin_access],
    )
    regular = User(
        nome="Regular",
        email="regular@example.com",
        senha_hash=hash_password("Regular#123", 4),
        tipo=UserType.LOJA,
        cargo="Loja",
        nivel=1,
        ativo=True,
        force_password_change=False,
        tipos_acesso=[empty_access],
    )
    forced = User(
        nome="Troca Obrigatória",
        email="forced@example.com",
        senha_hash=hash_password("Temporaria#123", 4),
        tipo=UserType.PDV,
        cargo="PDV",
        nivel=1,
        ativo=True,
        force_password_change=True,
        tipos_acesso=[empty_access],
    )
    db_session.add_all([super_admin, manager, regular, forced])
    db_session.commit()
    return {
        "super_admin": super_admin,
        "manager": manager,
        "regular": regular,
        "forced": forced,
        "admin_access": admin_access,
        "empty_access": empty_access,
    }


@pytest.fixture()
def login(client: TestClient):
    def perform(email: str, password: str) -> dict[str, str | int | bool]:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "senha": password},
        )
        assert response.status_code == 200, response.text
        return response.json()

    return perform
