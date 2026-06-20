from fastapi.testclient import TestClient


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_login_me_and_password_hash_is_never_returned(
    client: TestClient, seeded_users, login
) -> None:
    tokens = login("admin@example.com", "Admin#123")

    assert tokens["token_type"] == "bearer"
    assert tokens["expires_in"] == 900
    response = client.get("/api/v1/auth/me", headers=bearer(tokens["access_token"]))

    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"
    assert "senha_hash" not in response.text


def test_login_rejects_invalid_credentials(client: TestClient, seeded_users) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "senha": "errada"},
    )

    assert response.status_code == 401
    assert "senha_hash" not in response.text


def test_refresh_token_is_rotated_and_old_token_is_rejected(
    client: TestClient, seeded_users, login
) -> None:
    tokens = login("admin@example.com", "Admin#123")
    rotated = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert rotated.status_code == 200
    assert rotated.json()["refresh_token"] != tokens["refresh_token"]
    reuse = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert reuse.status_code == 401


def test_logout_revokes_refresh_token(client: TestClient, seeded_users, login) -> None:
    tokens = login("admin@example.com", "Admin#123")

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
    )
    refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert logout.status_code == 204
    assert refresh.status_code == 401


def test_forced_user_can_only_change_password_then_access_api(
    client: TestClient, seeded_users, login
) -> None:
    tokens = login("forced@example.com", "Temporaria#123")
    headers = bearer(tokens["access_token"])

    blocked = client.get("/api/v1/users", headers=headers)
    changed = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={
            "senha_atual": "Temporaria#123",
            "nova_senha": "NovaSenha#456",
        },
    )
    me = client.get("/api/v1/auth/me", headers=headers)

    assert blocked.status_code == 403
    assert changed.status_code == 204
    assert me.status_code == 200
    assert me.json()["force_password_change"] is False


def test_login_rate_limit_blocks_sixth_attempt(
    client: TestClient, seeded_users
) -> None:
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "senha": "errada"},
        )
        assert response.status_code == 401

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "senha": "errada"},
    )
    assert response.status_code == 429
