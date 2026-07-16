"""Protected-route decorator: requires a valid JWT and an allowed role."""

from functools import wraps

from flask_jwt_extended import get_jwt, jwt_required

from app.utils.exceptions import ForbiddenError


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if get_jwt().get("role") not in roles:
                raise ForbiddenError("You do not have permission to access this resource.")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
