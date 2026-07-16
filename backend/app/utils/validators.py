"""Server-side validation helpers that don't belong in a schema."""

from datetime import date


def calculate_age(date_of_birth: date, today: date | None = None) -> int:
    today = today or date.today()
    age = today.year - date_of_birth.year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age
