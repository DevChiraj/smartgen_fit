"""CLI command: promotes an already-registered user to admin.

    flask promote-admin someone@example.com

Deliberately not an HTTP endpoint - promoting the very first admin (and
any admin added outside the panel) requires direct server/DB access,
not a self-service API a regular user could ever reach. Once at least
one admin exists, further promotions can happen through the admin
panel's user management page (Module 14) instead.
"""

import click

from app.repositories import user_repository
from app.utils.exceptions import AppError


class UserNotFoundError(AppError):
    status_code = 404


def promote_to_admin(email: str):
    user = user_repository.get_by_email(email)
    if user is None:
        raise UserNotFoundError(
            f"No registered user with email {email!r}. They must register an account first."
        )
    user.role = "admin"
    return user_repository.save(user)


def register_promote_admin_command(app):
    @app.cli.command("promote-admin")
    @click.argument("email")
    def promote_admin_cli(email):
        user = promote_to_admin(email)
        click.echo(f"{user.username} ({user.email}) is now an admin.")
