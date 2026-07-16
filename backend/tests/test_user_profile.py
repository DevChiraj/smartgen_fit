from io import BytesIO

from PIL import Image


def make_test_image_bytes(fmt="PNG", size=(10, 10)):
    buffer = BytesIO()
    Image.new("RGB", size, color="red").save(buffer, format=fmt)
    buffer.seek(0)
    return buffer


def register_and_get_token(client, username="profile_user"):
    payload = {
        "full_name": "Profile User",
        "date_of_birth": "1995-06-15",
        "gender": "female",
        "email": f"{username}@example.com",
        "username": username,
        "password": "supersecret",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    return response.get_json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_get_me_requires_auth(client, db):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_get_me_returns_profile(client, db):
    token = register_and_get_token(client)
    response = client.get("/api/v1/users/me", headers=auth_headers(token))
    assert response.status_code == 200
    body = response.get_json()["user"]
    assert body["username"] == "profile_user"
    assert body["profile_picture_url"] is None


def test_update_me_success(client, db):
    token = register_and_get_token(client)
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"full_name": "Updated Name", "phone_number": "0771234567", "height_cm": "165.50"},
    )
    assert response.status_code == 200
    body = response.get_json()["user"]
    assert body["full_name"] == "Updated Name"
    assert body["phone_number"] == "0771234567"
    assert body["height_cm"] == "165.50"


def test_update_me_ignores_unknown_fields(client, db):
    token = register_and_get_token(client)
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers(token),
        json={"full_name": "Still Valid", "role": "admin"},
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "user"


def test_upload_profile_picture_success(client, db):
    token = register_and_get_token(client)
    image = make_test_image_bytes()

    response = client.post(
        "/api/v1/users/me/profile-picture",
        headers=auth_headers(token),
        data={"profile_picture": (image, "avatar.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    url = response.get_json()["user"]["profile_picture_url"]
    assert url.startswith("/api/v1/users/uploads/profile-pictures/")

    served = client.get(url)
    assert served.status_code == 200
    assert served.content_type == "image/png"


def test_upload_profile_picture_rejects_non_image(client, db):
    token = register_and_get_token(client)
    fake_file = BytesIO(b"this is not an image")

    response = client.post(
        "/api/v1/users/me/profile-picture",
        headers=auth_headers(token),
        data={"profile_picture": (fake_file, "fake.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "ValidationFailedError"


def test_upload_profile_picture_rejects_disallowed_extension(client, db):
    token = register_and_get_token(client)
    image = make_test_image_bytes()

    response = client.post(
        "/api/v1/users/me/profile-picture",
        headers=auth_headers(token),
        data={"profile_picture": (image, "avatar.gif")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_upload_profile_picture_rejects_oversized_file(client, db):
    token = register_and_get_token(client)
    oversized = BytesIO(b"0" * (2 * 1024 * 1024 + 1))

    response = client.post(
        "/api/v1/users/me/profile-picture",
        headers=auth_headers(token),
        data={"profile_picture": (oversized, "big.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "too large" in response.get_json()["message"].lower()


def test_upload_profile_picture_replaces_old_file(client, db, app):
    token = register_and_get_token(client)

    first = client.post(
        "/api/v1/users/me/profile-picture",
        headers=auth_headers(token),
        data={"profile_picture": (make_test_image_bytes(), "first.png")},
        content_type="multipart/form-data",
    )
    first_url = first.get_json()["user"]["profile_picture_url"]

    second = client.post(
        "/api/v1/users/me/profile-picture",
        headers=auth_headers(token),
        data={"profile_picture": (make_test_image_bytes(), "second.png")},
        content_type="multipart/form-data",
    )
    second_url = second.get_json()["user"]["profile_picture_url"]

    assert first_url != second_url
    assert client.get(first_url).status_code == 404
    assert client.get(second_url).status_code == 200

    import os

    files_on_disk = os.listdir(app.config["UPLOAD_FOLDER"])
    assert len(files_on_disk) == 1
