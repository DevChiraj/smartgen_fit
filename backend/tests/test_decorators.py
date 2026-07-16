from app.utils.decorators import role_required


def _register_and_login(client, username, role="user"):
    payload = {
        "full_name": "Role Test",
        "date_of_birth": "1995-06-15",
        "gender": "male",
        "email": f"{username}@example.com",
        "username": username,
        "password": "supersecret",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    body = response.get_json()

    if role != "user":
        from app.extensions import db
        from app.models import User

        user = User.query.filter_by(username=username).first()
        user.role = role
        db.session.commit()

        login_response = client.post(
            "/api/v1/auth/login", json={"identifier": username, "password": "supersecret"}
        )
        return login_response.get_json()["access_token"]

    return body["access_token"]


def test_role_required_blocks_disallowed_role(app, db, client):
    @app.route("/api/v1/_test/admin-only")
    @role_required("admin")
    def admin_only():
        return {"ok": True}

    token = _register_and_login(client, "regular_user", role="user")
    response = client.get("/api/v1/_test/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.get_json()["error"] == "ForbiddenError"


def test_role_required_allows_matching_role(app, db, client):
    @app.route("/api/v1/_test/admin-only-2")
    @role_required("admin")
    def admin_only_2():
        return {"ok": True}

    token = _register_and_login(client, "admin_user", role="admin")
    response = client.get(
        "/api/v1/_test/admin-only-2", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_role_required_requires_token(app, db, client):
    @app.route("/api/v1/_test/admin-only-3")
    @role_required("admin")
    def admin_only_3():
        return {"ok": True}

    response = client.get("/api/v1/_test/admin-only-3")
    assert response.status_code == 401
