"""Admin-only user management. Guards against an admin locking everyone
(including themselves) out of the panel: demoting or deleting the last
remaining admin, or an admin deleting their own account, are rejected
rather than silently allowed - recovering from either would need direct
DB access (the same bar as bootstrapping the first admin via
`flask promote-admin`).
"""

from app.models import User
from app.repositories import user_repository
from app.utils.exceptions import AppError, NotFoundError


class LastAdminError(AppError):
    status_code = 409


def list_users() -> list[User]:
    return user_repository.get_all()


def get_user(user_id: int) -> User:
    user = user_repository.get_by_id(user_id)
    if user is None:
        raise NotFoundError(f"No user found with id {user_id}.")
    return user


def _is_demoting_the_last_admin(user: User, data: dict) -> bool:
    return (
        user.role == "admin"
        and data.get("role") == "user"
        and user_repository.count_by_role("admin") <= 1
    )


def update_user(user_id: int, data: dict) -> User:
    user = get_user(user_id)
    if _is_demoting_the_last_admin(user, data):
        raise LastAdminError("Cannot demote the last remaining admin.")

    for field in ("full_name", "phone_number", "height_cm", "weight_kg", "role"):
        if field in data:
            setattr(user, field, data[field])
    return user_repository.save(user)


def delete_user(user_id: int, requesting_admin_id: int) -> None:
    user = get_user(user_id)
    if user.user_id == requesting_admin_id:
        raise AppError("You cannot delete your own account from the admin panel.", status_code=409)
    if user.role == "admin" and user_repository.count_by_role("admin") <= 1:
        raise LastAdminError("Cannot delete the last remaining admin.")
    user_repository.delete(user)
