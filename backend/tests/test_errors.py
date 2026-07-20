from datetime import timedelta

from flask_jwt_extended import create_access_token


def test_expired_token_returns_401_with_clear_message(app, db, client):
    with app.app_context():
        expired_token = create_access_token(identity="1", expires_delta=timedelta(seconds=-1))

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"
    assert "expired" in response.get_json()["message"].lower()


def test_unexpected_exception_returns_generic_500_without_leaking_details(app, db):
    @app.route("/api/v1/_test/boom")
    def boom():
        raise RuntimeError("some internal detail that should not reach the client")

    with app.test_client() as client:
        response = client.get("/api/v1/_test/boom")

    assert response.status_code == 500
    body = response.get_json()
    assert body["error"] == "Internal Server Error"
    assert "some internal detail" not in body["message"]
