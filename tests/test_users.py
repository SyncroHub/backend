from fastapi.testclient import TestClient


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def user_payload(email: str = "novo@example.com", nivel: int = 1) -> dict:
    return {
        "nome": "Novo Usuário",
        "email": email,
        "senha": "Segura#123",
        "tipo": "loja",
        "cargo": "Loja",
        "nivel": nivel,
        "ativo": True,
        "force_password_change": False,
        "tipos_acesso_ids": [],
    }


def test_user_crud_summary_pagination_and_soft_delete(
    client: TestClient, seeded_users, login
) -> None:
    token = login("admin@example.com", "Admin#123")["access_token"]
    auth = headers(token)

    created = client.post("/api/v1/users", headers=auth, json=user_payload())
    assert created.status_code == 201, created.text
    assert "senha_hash" not in created.text
    user_id = created.json()["id"]

    duplicate = client.post("/api/v1/users", headers=auth, json=user_payload())
    assert duplicate.status_code == 409

    updated = client.put(
        f"/api/v1/users/{user_id}",
        headers=auth,
        json={"nome": "Usuário Editado"},
    )
    status_response = client.patch(
        f"/api/v1/users/{user_id}/status",
        headers=auth,
        json={"ativo": False},
    )
    listing = client.get(
        "/api/v1/users?page=1&limit=2&status=inativo&q=Editado",
        headers=auth,
    )
    summary = client.get("/api/v1/users/summary", headers=auth)
    deleted = client.delete(f"/api/v1/users/{user_id}", headers=auth)
    missing = client.get(f"/api/v1/users/{user_id}", headers=auth)

    assert updated.json()["nome"] == "Usuário Editado"
    assert status_response.json()["ativo"] is False
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["limit"] == 2
    assert summary.status_code == 200
    assert summary.json()["total"] == 5
    assert deleted.status_code == 204
    assert missing.status_code == 404


def test_user_without_permission_receives_403(
    client: TestClient, seeded_users, login
) -> None:
    token = login("regular@example.com", "Regular#123")["access_token"]

    response = client.post(
        "/api/v1/users",
        headers=headers(token),
        json=user_payload(),
    )

    assert response.status_code == 403


def test_manager_cannot_manage_equal_or_higher_level(
    client: TestClient, seeded_users, login
) -> None:
    token = login("gestor@example.com", "Gestor#123")["access_token"]

    create_equal = client.post(
        "/api/v1/users",
        headers=headers(token),
        json=user_payload("igual@example.com", nivel=4),
    )
    edit_super_admin = client.put(
        f"/api/v1/users/{seeded_users['super_admin'].id}",
        headers=headers(token),
        json={"nome": "Tentativa"},
    )

    assert create_equal.status_code == 403
    assert edit_super_admin.status_code == 403


def test_password_policy_is_enforced(client: TestClient, seeded_users, login) -> None:
    token = login("admin@example.com", "Admin#123")["access_token"]
    payload = user_payload()
    payload["senha"] = "fraca"

    response = client.post("/api/v1/users", headers=headers(token), json=payload)

    assert response.status_code == 422
