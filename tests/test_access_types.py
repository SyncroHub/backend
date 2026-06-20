from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def payload(name: str) -> dict:
    return {
        "nome": name,
        "descricao": "Perfil customizado",
        "cor": "#112233",
        "ativo": True,
        "modulo_ids": [],
        "permission_ids": [],
        "relatorio_ids": [],
    }


def test_access_type_crud_and_case_insensitive_uniqueness(
    client: TestClient, seeded_users, login
) -> None:
    auth = headers(login("admin@example.com", "Admin#123")["access_token"])

    created = client.post(
        "/api/v1/access-types", headers=auth, json=payload("Customizado")
    )
    duplicate = client.post(
        "/api/v1/access-types", headers=auth, json=payload("customizado")
    )
    access_type_id = created.json()["id"]
    updated_payload = payload("Customizado")
    updated_payload["descricao"] = "Atualizado"
    updated = client.put(
        f"/api/v1/access-types/{access_type_id}",
        headers=auth,
        json=updated_payload,
    )
    disabled = client.patch(
        f"/api/v1/access-types/{access_type_id}/status",
        headers=auth,
        json={"ativo": False},
    )
    deleted = client.delete(f"/api/v1/access-types/{access_type_id}", headers=auth)

    assert created.status_code == 201
    assert duplicate.status_code == 409
    assert updated.json()["descricao"] == "Atualizado"
    assert disabled.json()["ativo"] is False
    assert deleted.status_code == 204


def test_system_access_type_cannot_be_deleted(
    client: TestClient, seeded_users, login
) -> None:
    auth = headers(login("admin@example.com", "Admin#123")["access_token"])

    response = client.delete(
        f"/api/v1/access-types/{seeded_users['admin_access'].id}",
        headers=auth,
    )

    assert response.status_code == 409


def test_linked_custom_access_type_cannot_be_deleted(
    client: TestClient,
    db_session: Session,
    seeded_users,
    login,
) -> None:
    auth = headers(login("admin@example.com", "Admin#123")["access_token"])
    access_type = seeded_users["empty_access"]
    user = seeded_users["regular"]
    assert isinstance(user, User)

    response = client.delete(f"/api/v1/access-types/{access_type.id}", headers=auth)

    assert response.status_code == 409
    assert "2" in response.json()["detail"]
