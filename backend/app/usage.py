from datetime import date

from sqlalchemy.orm import Session

from app.models import Usage, User


def current_month_key(today: date | None = None) -> str:
    d = today or date.today()
    return f"{d.year:04d}-{d.month:02d}"


def get_or_create_usage(db: Session, user_id: int) -> Usage:
    month = current_month_key()
    usage = (
        db.query(Usage)
        .filter(Usage.user_id == user_id, Usage.month == month)
        .first()
    )
    if usage is None:
        usage = Usage(user_id=user_id, month=month, pages_used=0)
        db.add(usage)
        db.flush()
    return usage


def pages_remaining(db: Session, user: User) -> int:
    if user.plan is None:
        return 0
    usage = get_or_create_usage(db, user.id)
    return max(user.plan.monthly_page_limit - usage.pages_used, 0)


def record_usage(db: Session, user_id: int, pages: int) -> None:
    usage = get_or_create_usage(db, user_id)
    usage.pages_used += pages