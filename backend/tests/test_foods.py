from app.extensions import db
from app.models import SriLankanFood


def seed_foods():
    foods = [
        dict(
            food_name="White Rice",
            category="Grain",
            serving_size="80g",
            calories=110,
            protein_g=2,
            carbs_g=24,
            fat_g=0,
        ),
        dict(
            food_name="Chicken Curry",
            category="Protein",
            serving_size="100g",
            calories=190,
            protein_g=24,
            carbs_g=4,
            fat_g=9,
        ),
        dict(
            food_name="Banana",
            category="Fruit",
            serving_size="100g",
            calories=95,
            protein_g=1,
            carbs_g=27,
            fat_g=0.3,
        ),
    ]
    for food in foods:
        db.session.add(SriLankanFood(**food))
    db.session.commit()


def test_list_foods_does_not_require_auth(client, db):
    seed_foods()
    response = client.get("/api/v1/foods")
    assert response.status_code == 200
    assert len(response.get_json()["foods"]) == 3


def test_list_foods_filters_by_category(client, db):
    seed_foods()
    response = client.get("/api/v1/foods?category=Fruit")
    assert response.status_code == 200
    foods = response.get_json()["foods"]
    assert len(foods) == 1
    assert foods[0]["food_name"] == "Banana"


def test_list_foods_category_filter_is_case_insensitive(client, db):
    seed_foods()
    response = client.get("/api/v1/foods?category=fruit")
    assert len(response.get_json()["foods"]) == 1


def test_list_foods_search_matches_partial_name(client, db):
    seed_foods()
    response = client.get("/api/v1/foods?q=chick")
    foods = response.get_json()["foods"]
    assert len(foods) == 1
    assert foods[0]["food_name"] == "Chicken Curry"


def test_list_categories_returns_distinct_sorted_categories(client, db):
    seed_foods()
    response = client.get("/api/v1/foods/categories")
    assert response.status_code == 200
    assert response.get_json()["categories"] == ["Fruit", "Grain", "Protein"]


def test_get_food_returns_full_detail(client, db):
    seed_foods()
    food = SriLankanFood.query.filter_by(food_name="Banana").first()
    response = client.get(f"/api/v1/foods/{food.food_id}")
    assert response.status_code == 200
    body = response.get_json()["food"]
    assert body["food_name"] == "Banana"
    assert body["calories"] == 95
    assert body["serving_size"] == "100g"


def test_get_food_returns_404_for_missing_id(client, db):
    response = client.get("/api/v1/foods/999999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "NotFoundError"


def test_get_food_returns_404_for_non_numeric_id(client, db):
    response = client.get("/api/v1/foods/not-a-number")
    assert response.status_code == 404
