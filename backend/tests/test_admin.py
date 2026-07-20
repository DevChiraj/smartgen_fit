from app.extensions import db
from app.models import BMICategory, BodyTypeCategory, Exercise, SriLankanFood, User


def register(client, username, role="user"):
    payload = {
        "full_name": "Admin Test User",
        "date_of_birth": "1995-06-15",
        "gender": "male",
        "email": f"{username}@example.com",
        "username": username,
        "password": "supersecret",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    body = response.get_json()
    user_id = body["user"]["user_id"] if "user" in body else None

    if role != "user":
        user = User.query.filter_by(username=username).first()
        user.role = role
        db.session.commit()
        login_response = client.post(
            "/api/v1/auth/login", json={"identifier": username, "password": "supersecret"}
        )
        return login_response.get_json()["access_token"], user.user_id

    if user_id is None:
        user_id = User.query.filter_by(username=username).first().user_id
    return body["access_token"], user_id


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# --- Access control ---


def test_admin_routes_require_auth(client, db):
    assert client.get("/api/v1/admin/users").status_code == 401
    assert client.get("/api/v1/admin/body-types").status_code == 401


def test_admin_routes_reject_regular_users(client, db):
    token, _ = register(client, "regular", role="user")
    response = client.get("/api/v1/admin/users", headers=auth_headers(token))
    assert response.status_code == 403
    assert response.get_json()["error"] == "ForbiddenError"


# --- Users ---


def test_admin_can_list_and_get_users(client, db):
    admin_token, _ = register(client, "admin1", role="admin")
    register(client, "plainuser")

    response = client.get("/api/v1/admin/users", headers=auth_headers(admin_token))
    assert response.status_code == 200
    usernames = [u["username"] for u in response.get_json()["users"]]
    assert "admin1" in usernames and "plainuser" in usernames


def test_admin_get_user_404_for_missing_id(client, db):
    admin_token, _ = register(client, "admin1", role="admin")
    response = client.get("/api/v1/admin/users/999999", headers=auth_headers(admin_token))
    assert response.status_code == 404


def test_admin_can_promote_a_user_to_admin(client, db):
    admin_token, _ = register(client, "admin1", role="admin")
    _, other_id = register(client, "plainuser")

    response = client.put(
        f"/api/v1/admin/users/{other_id}",
        json={"role": "admin"},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "admin"


def test_admin_cannot_demote_the_last_admin(client, db):
    admin_token, admin_id = register(client, "admin1", role="admin")

    response = client.put(
        f"/api/v1/admin/users/{admin_id}",
        json={"role": "user"},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 409


def test_admin_can_demote_an_admin_when_another_admin_remains(client, db):
    admin_token, _ = register(client, "admin1", role="admin")
    _, admin2_id = register(client, "admin2", role="admin")

    response = client.put(
        f"/api/v1/admin/users/{admin2_id}",
        json={"role": "user"},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "user"


def test_admin_cannot_delete_own_account(client, db):
    admin_token, admin_id = register(client, "admin1", role="admin")
    response = client.delete(f"/api/v1/admin/users/{admin_id}", headers=auth_headers(admin_token))
    assert response.status_code == 409


def test_admin_cannot_delete_the_last_admin(client, db):
    """Deleting the sole remaining admin is blocked independently of the
    self-delete guard - checked via the service directly with a
    requesting_admin_id that isn't the target, so only the last-admin
    guard (not the self-delete one) is under test."""
    from app.services import admin_user_service
    from app.utils.exceptions import AppError

    _, admin_id = register(client, "onlyadmin", role="admin")
    _, other_admin_id = register(client, "secondadmin", role="admin")

    admin_user_service.delete_user(other_admin_id, requesting_admin_id=admin_id)

    try:
        admin_user_service.delete_user(admin_id, requesting_admin_id=999999)
        assert False, "expected LastAdminError"
    except AppError as exc:
        assert exc.status_code == 409


def test_admin_can_delete_a_regular_user(client, db):
    admin_token, _ = register(client, "admin1", role="admin")
    _, plain_id = register(client, "plainuser")

    response = client.delete(f"/api/v1/admin/users/{plain_id}", headers=auth_headers(admin_token))
    assert response.status_code == 204
    assert User.query.filter_by(user_id=plain_id).first() is None


# --- Foods ---


def _food_payload(**overrides):
    payload = dict(
        food_name="Test Food",
        category="Grain",
        serving_size="100g",
        calories=200,
        protein_g=5,
        carbs_g=30,
        fat_g=2,
    )
    payload.update(overrides)
    return payload


def test_admin_can_create_update_delete_food(client, db):
    admin_token, _ = register(client, "admin1", role="admin")

    create_response = client.post(
        "/api/v1/admin/foods", json=_food_payload(), headers=auth_headers(admin_token)
    )
    assert create_response.status_code == 201
    food_id = create_response.get_json()["food"]["food_id"]

    update_response = client.put(
        f"/api/v1/admin/foods/{food_id}",
        json={"calories": 250},
        headers=auth_headers(admin_token),
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["food"]["calories"] == 250

    delete_response = client.delete(
        f"/api/v1/admin/foods/{food_id}", headers=auth_headers(admin_token)
    )
    assert delete_response.status_code == 204
    assert SriLankanFood.query.filter_by(food_id=food_id).first() is None


def test_admin_create_food_rejects_missing_required_field(client, db):
    admin_token, _ = register(client, "admin1", role="admin")
    payload = _food_payload()
    del payload["calories"]

    response = client.post("/api/v1/admin/foods", json=payload, headers=auth_headers(admin_token))
    assert response.status_code == 400


# --- Exercises ---


def _exercise_payload(**overrides):
    payload = dict(
        exercise_name="Test Exercise",
        target_muscle="Core",
        difficulty="Beginner",
        sets=3,
        reps=10,
        calories_per_30min=150,
        benefit="Improves core strength",
    )
    payload.update(overrides)
    return payload


def test_admin_can_create_update_delete_exercise(client, db):
    admin_token, _ = register(client, "admin1", role="admin")

    create_response = client.post(
        "/api/v1/admin/exercises", json=_exercise_payload(), headers=auth_headers(admin_token)
    )
    assert create_response.status_code == 201
    exercise_id = create_response.get_json()["exercise"]["exercise_id"]

    update_response = client.put(
        f"/api/v1/admin/exercises/{exercise_id}",
        json={"difficulty": "Advanced"},
        headers=auth_headers(admin_token),
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["exercise"]["difficulty"] == "Advanced"

    delete_response = client.delete(
        f"/api/v1/admin/exercises/{exercise_id}", headers=auth_headers(admin_token)
    )
    assert delete_response.status_code == 204
    assert Exercise.query.filter_by(exercise_id=exercise_id).first() is None


# --- Body types ---


def test_admin_can_list_and_update_body_type_description(client, db):
    admin_token, _ = register(client, "admin1", role="admin")
    body_type = BodyTypeCategory(name="Normal", description="original")
    db.session.add(body_type)
    db.session.commit()

    list_response = client.get("/api/v1/admin/body-types", headers=auth_headers(admin_token))
    assert list_response.status_code == 200
    assert len(list_response.get_json()["body_types"]) == 1

    update_response = client.put(
        f"/api/v1/admin/body-types/{body_type.body_type_id}",
        json={"description": "updated description"},
        headers=auth_headers(admin_token),
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["body_type"]["description"] == "updated description"
    assert update_response.get_json()["body_type"]["name"] == "Normal"


def test_admin_update_body_type_does_not_accept_name_change(client, db):
    admin_token, _ = register(client, "admin1", role="admin")
    body_type = BodyTypeCategory(name="Normal", description="original")
    db.session.add(body_type)
    db.session.commit()

    response = client.put(
        f"/api/v1/admin/body-types/{body_type.body_type_id}",
        json={"description": "updated", "name": "Renamed"},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    assert response.get_json()["body_type"]["name"] == "Normal"


# --- BMI categories ---


def test_admin_can_crud_bmi_categories(client, db):
    admin_token, _ = register(client, "admin1", role="admin")
    # a second category must already exist, or deleting the one created
    # below would hit the "can't delete the last category" guard
    db.session.add(BMICategory(category_name="Existing", min_bmi=18.5, max_bmi=100))
    db.session.commit()

    create_response = client.post(
        "/api/v1/admin/bmi-categories",
        json={"category_name": "Test Range", "min_bmi": 0, "max_bmi": 18.5},
        headers=auth_headers(admin_token),
    )
    assert create_response.status_code == 201
    category_id = create_response.get_json()["bmi_category"]["bmi_category_id"]

    update_response = client.put(
        f"/api/v1/admin/bmi-categories/{category_id}",
        json={"max_bmi": 19.0},
        headers=auth_headers(admin_token),
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["bmi_category"]["max_bmi"] == "19.0"

    delete_response = client.delete(
        f"/api/v1/admin/bmi-categories/{category_id}", headers=auth_headers(admin_token)
    )
    assert delete_response.status_code == 204
    assert BMICategory.query.filter_by(bmi_category_id=category_id).first() is None


def test_admin_cannot_delete_the_last_bmi_category(client, db):
    admin_token, _ = register(client, "admin1", role="admin")
    category = BMICategory(category_name="Only One", min_bmi=0, max_bmi=100)
    db.session.add(category)
    db.session.commit()

    response = client.delete(
        f"/api/v1/admin/bmi-categories/{category.bmi_category_id}",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 409
