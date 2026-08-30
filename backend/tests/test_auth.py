from app.utils.validators import calculate_age


def valid_payload(**overrides):
    payload = {
        "full_name": "Test User",
        "date_of_birth": "2000-01-01",
        "gender": "female",
        "email": "test.user@example.com",
        "username": "test_user",
        "password": "supersecret",
    }
    payload.update(overrides)
    return payload


def register(client, **overrides):
    return client.post("/api/v1/auth/register", json=valid_payload(**overrides))


def test_register_success(client):
    from datetime import date

    response = register(client)
    assert response.status_code == 201
    body = response.get_json()
    assert body["user"]["username"] == "test_user"
    assert body["user"]["age"] == calculate_age(date(2000, 1, 1))
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]
    assert body["access_token"]
    assert body["refresh_token"]


def test_register_under_minimum_age(client):
    from datetime import date

    too_young_dob = date.today().replace(year=date.today().year - 10).isoformat()
    response = register(
        client, date_of_birth=too_young_dob, email="young@example.com", username="young_user"
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "UnderMinimumAgeError"


def test_register_duplicate_email(client):
    register(client)
    response = register(client, username="different_username")
    assert response.status_code == 409
    assert "Email" in response.get_json()["message"]


def test_register_duplicate_username(client):
    register(client)
    response = register(client, email="different@example.com")
    assert response.status_code == 409
    assert "Username" in response.get_json()["message"]


def test_register_missing_required_field(client):
    payload = valid_payload()
    del payload["email"]
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "email" in response.get_json()["message"]


def test_register_password_too_short(client):
    response = register(client, password="short")
    assert response.status_code == 400


def test_login_with_username(client):
    register(client)
    response = client.post(
        "/api/v1/auth/login", json={"identifier": "test_user", "password": "supersecret"}
    )
    assert response.status_code == 200
    assert response.get_json()["access_token"]


def test_login_with_email(client):
    register(client)
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "test.user@example.com", "password": "supersecret"},
    )
    assert response.status_code == 200


def test_login_invalid_credentials(client):
    register(client)
    response = client.post(
        "/api/v1/auth/login", json={"identifier": "test_user", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "InvalidCredentialsError"


def test_me_requires_auth(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.get_json()["status"] == 401


def test_me_returns_user_without_password(client):
    register_response = register(client)
    token = register_response.get_json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.get_json()["user"]
    assert body["username"] == "test_user"
    assert "password_hash" not in body


def test_refresh_issues_new_access_token(client):
    register_response = register(client)
    refresh_token = register_response.get_json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == 200
    assert response.get_json()["access_token"]


def test_refresh_rejects_access_token(client):
    register_response = register(client)
    access_token = register_response.get_json()["access_token"]

    response = client.post(
        "/api/v1/auth/refresh", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code != 200
