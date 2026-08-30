from datetime import date

from app.utils.validators import calculate_age


def test_calculate_age_after_birthday_this_year():
    # Born 2000-01-01, "today" is 2020-06-15 -> birthday already passed this year
    assert calculate_age(date(2000, 1, 1), today=date(2020, 6, 15)) == 20


def test_calculate_age_before_birthday_this_year():
    # Born 2000-12-25, "today" is 2020-06-15 -> birthday hasn't happened yet this year
    assert calculate_age(date(2000, 12, 25), today=date(2020, 6, 15)) == 19


def test_calculate_age_on_exact_birthday():
    assert calculate_age(date(2000, 6, 15), today=date(2020, 6, 15)) == 20


def test_calculate_age_defaults_to_today_when_not_given():
    born_15_years_ago = date(date.today().year - 15, date.today().month, date.today().day)
    assert calculate_age(born_15_years_ago) == 15
