"""DB access for the User model."""

from app.extensions import db
from app.models import User


def get_by_id(user_id: int) -> User | None:
    return db.session.get(User, user_id)


def get_by_email(email: str) -> User | None:
    return User.query.filter_by(email=email).first()


def get_by_username(username: str) -> User | None:
    return User.query.filter_by(username=username).first()


def create(user: User) -> User:
    db.session.add(user)
    db.session.commit()
    return user


def save(user: User) -> User:
    db.session.commit()
    return user
