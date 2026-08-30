"""Domain-level exceptions, mapped to consistent JSON errors by utils/errors.py."""


class AppError(Exception):
    status_code = 400

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class ValidationFailedError(AppError):
    status_code = 400


class DuplicateResourceError(AppError):
    status_code = 409


class InvalidCredentialsError(AppError):
    status_code = 401


class UnderMinimumAgeError(AppError):
    status_code = 400


class ForbiddenError(AppError):
    status_code = 403


class NotFoundError(AppError):
    status_code = 404
