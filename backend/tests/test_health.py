from app import create_app


def make_client():
    app = create_app("testing")
    return app.test_client()


def test_api_health_returns_ok():
    client = make_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "service": "smartgen-fit-api"}


def test_db_health_reports_status():
    client = make_client()
    response = client.get("/api/health/db")
    assert response.status_code in (200, 503)
    assert "database" in response.get_json()


def test_db_health_returns_503_when_database_is_unreachable(monkeypatch):
    app = create_app("testing")

    def raise_operational_error(*args, **kwargs):
        raise Exception("simulated connection failure")

    with app.app_context():
        from app.extensions import db

        monkeypatch.setattr(db.session, "execute", raise_operational_error)

        with app.test_client() as client:
            response = client.get("/api/health/db")

    assert response.status_code == 503
    body = response.get_json()
    assert body["status"] == "error"
    assert body["database"] == "unreachable"
    assert "simulated connection failure" in body["detail"]
