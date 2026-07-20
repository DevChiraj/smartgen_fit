import pytest

from app.models import User
from app.promote_admin import UserNotFoundError, promote_to_admin


def register(client, username="bootstrapuser"):
    payload = {
        "full_name": "Bootstrap User",
        "date_of_birth": "1995-06-15",
        "gender": "female",
        "email": f"{username}@example.com",
        "username": username,
        "password": "supersecret",
    }
    client.post("/api/v1/auth/register", json=payload)


def test_promote_to_admin_promotes_existing_user(app, db, client):
    register(client)
    user = promote_to_admin("bootstrapuser@example.com")
    assert user.role == "admin"
    assert User.query.filter_by(username="bootstrapuser").first().role == "admin"


def test_promote_to_admin_raises_for_unknown_email(app, db, client):
    with pytest.raises(UserNotFoundError):
        promote_to_admin("nobody@example.com")
