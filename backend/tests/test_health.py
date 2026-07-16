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
