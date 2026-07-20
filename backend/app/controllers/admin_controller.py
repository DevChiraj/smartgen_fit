"""Request/response orchestration for every admin-only endpoint. Kept in
one file (rather than scattered across the public foods/exercises
controllers) so the whole admin-write surface is auditable in one place.
"""

from app.schemas.admin_schema import (
    AdminUserSchema,
    AdminUserUpdateSchema,
    BodyTypeCategorySchema,
    BodyTypeUpdateSchema,
    BMICategoryWriteSchema,
    ExerciseWriteSchema,
    SriLankanFoodWriteSchema,
)
from app.schemas.bmi_schema import BMICategorySchema
from app.schemas.exercise_schema import ExerciseSchema
from app.schemas.food_schema import SriLankanFoodSchema
from app.services import (
    admin_user_service,
    bmi_category_service,
    body_type_service,
    exercise_service,
    food_service,
)

admin_user_schema = AdminUserSchema()
admin_users_schema = AdminUserSchema(many=True)
admin_user_update_schema = AdminUserUpdateSchema()

food_schema = SriLankanFoodSchema()
food_write_schema = SriLankanFoodWriteSchema()

exercise_schema = ExerciseSchema()
exercise_write_schema = ExerciseWriteSchema()

body_type_schema = BodyTypeCategorySchema()
body_types_schema = BodyTypeCategorySchema(many=True)
body_type_update_schema = BodyTypeUpdateSchema()

bmi_category_schema = BMICategorySchema()
bmi_categories_schema = BMICategorySchema(many=True)
bmi_category_write_schema = BMICategoryWriteSchema()


# --- Users ---


def handle_list_users():
    users = admin_user_service.list_users()
    return {"users": admin_users_schema.dump(users)}, 200


def handle_get_user(user_id: int):
    user = admin_user_service.get_user(user_id)
    return {"user": admin_user_schema.dump(user)}, 200


def handle_update_user(user_id: int, json_body):
    data = admin_user_update_schema.load(json_body or {}, partial=True)
    user = admin_user_service.update_user(user_id, data)
    return {"user": admin_user_schema.dump(user)}, 200


def handle_delete_user(user_id: int, requesting_admin_id: int):
    admin_user_service.delete_user(user_id, requesting_admin_id)
    return {}, 204


# --- Foods ---


def handle_create_food(json_body):
    data = food_write_schema.load(json_body or {})
    food = food_service.create_food(data)
    return {"food": food_schema.dump(food)}, 201


def handle_update_food(food_id: int, json_body):
    data = food_write_schema.load(json_body or {}, partial=True)
    food = food_service.update_food(food_id, data)
    return {"food": food_schema.dump(food)}, 200


def handle_delete_food(food_id: int):
    food_service.delete_food(food_id)
    return {}, 204


# --- Exercises ---


def handle_create_exercise(json_body):
    data = exercise_write_schema.load(json_body or {})
    exercise = exercise_service.create_exercise(data)
    return {"exercise": exercise_schema.dump(exercise)}, 201


def handle_update_exercise(exercise_id: int, json_body):
    data = exercise_write_schema.load(json_body or {}, partial=True)
    exercise = exercise_service.update_exercise(exercise_id, data)
    return {"exercise": exercise_schema.dump(exercise)}, 200


def handle_delete_exercise(exercise_id: int):
    exercise_service.delete_exercise(exercise_id)
    return {}, 204


# --- Body types ---


def handle_list_body_types():
    body_types = body_type_service.list_body_types()
    return {"body_types": body_types_schema.dump(body_types)}, 200


def handle_update_body_type(body_type_id: int, json_body):
    data = body_type_update_schema.load(json_body or {}, partial=True)
    body_type = body_type_service.update_body_type(body_type_id, data)
    return {"body_type": body_type_schema.dump(body_type)}, 200


# --- BMI categories ---


def handle_list_bmi_categories():
    categories = bmi_category_service.list_categories()
    return {"bmi_categories": bmi_categories_schema.dump(categories)}, 200


def handle_create_bmi_category(json_body):
    data = bmi_category_write_schema.load(json_body or {})
    category = bmi_category_service.create_category(data)
    return {"bmi_category": bmi_category_schema.dump(category)}, 201


def handle_update_bmi_category(bmi_category_id: int, json_body):
    data = bmi_category_write_schema.load(json_body or {}, partial=True)
    category = bmi_category_service.update_category(bmi_category_id, data)
    return {"bmi_category": bmi_category_schema.dump(category)}, 200


def handle_delete_bmi_category(bmi_category_id: int):
    bmi_category_service.delete_category(bmi_category_id)
    return {}, 204
