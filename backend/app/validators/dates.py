from datetime import date, timedelta

MAX_PAST_YEARS = 6  # GST records are generally kept for this long


def check_invoice_date(invoice_date: date | None, today: date | None = None) -> list[str]:
    if invoice_date is None:
        return ["missing_date"]

    today = today or date.today()
    problems = []

    if invoice_date > today + timedelta(days=1):
        # allow 1 day of slack for time zone differences
        problems.append("future_date")

    earliest_allowed = date(today.year - MAX_PAST_YEARS, today.month, today.day)
    if invoice_date < earliest_allowed:
        problems.append("date_too_old")

    return problems