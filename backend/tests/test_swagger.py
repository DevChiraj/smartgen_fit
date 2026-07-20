import re

IGNORED_ENDPOINT_PREFIXES = ("flasgger", "static")
IGNORED_METHODS = {"HEAD", "OPTIONS"}


def _to_swagger_path(flask_rule: str) -> str:
    """Converts Flask's <int:id>/<path:filename> style to Swagger's {id}/{filename}."""
    return re.sub(r"<(?:[a-zA-Z_]+:)?([a-zA-Z_]+)>", r"{\1}", flask_rule)


def test_docs_ui_is_served(client):
    response = client.get("/api/docs/")
    assert response.status_code == 200


def test_apispec_json_is_valid(client):
    response = client.get("/api/docs/apispec.json")
    assert response.status_code == 200
    spec = response.get_json()
    assert spec["info"]["title"] == "SmartGen Fit API"
    assert len(spec["paths"]) > 0


def test_every_registered_route_is_documented(app, client):
    spec = client.get("/api/docs/apispec.json").get_json()
    documented = {
        (path, method.upper()) for path, methods in spec["paths"].items() for method in methods
    }

    undocumented = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint.startswith(IGNORED_ENDPOINT_PREFIXES):
            continue
        swagger_path = _to_swagger_path(rule.rule)
        for method in rule.methods - IGNORED_METHODS:
            if (swagger_path, method) not in documented:
                undocumented.append(f"{method} {swagger_path} ({rule.endpoint})")

    assert not undocumented, f"Routes missing Swagger docs: {undocumented}"
