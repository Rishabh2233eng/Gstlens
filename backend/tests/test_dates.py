from datetime import date

from app.validators.dates import check_invoice_date

TODAY = date(2026, 9, 25)


def test_normal_recent_date_is_fine():
    assert check_invoice_date(date(2026, 9, 15), today=TODAY) == []


def test_missing_date():
    assert check_invoice_date(None, today=TODAY) == ["missing_date"]


def test_future_date_is_flagged():
    problems = check_invoice_date(date(2026, 10, 5), today=TODAY)
    assert "future_date" in problems


def test_one_day_ahead_is_tolerated():
    # allows small timezone slack
    assert check_invoice_date(date(2026, 9, 26), today=TODAY) == []


def test_very_old_date_is_flagged():
    problems = check_invoice_date(date(2015, 1, 1), today=TODAY)
    assert "date_too_old" in problems


def test_date_within_allowed_years_is_fine():
    assert check_invoice_date(date(2021, 9, 25), today=TODAY) == []


def test_today_is_fine():
    assert check_invoice_date(TODAY, today=TODAY) == []