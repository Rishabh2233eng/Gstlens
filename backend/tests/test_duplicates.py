from datetime import date
from decimal import Decimal

from app.validators.duplicates import find_duplicate_invoices
from app.database import Base
from app.models import Invoice, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
Session = sessionmaker(bind=engine)


def make_db():
    Base.metadata.create_all(engine)
    db = Session()
    user = User(email="d@example.com", hashed_password="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    return db, user.id


def teardown_function(_):
    Base.metadata.drop_all(engine)


def add_invoice(db, user_id, **kw):
    inv = Invoice(
        user_id=user_id,
        filename="a.pdf",
        file_path="a/a.pdf",
        page_count=1,
        status="done",
        **kw,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def test_no_duplicates_when_no_other_invoices():
    db, uid = make_db()
    problems = find_duplicate_invoices(
        db, uid, current_invoice_id=999, supplier_gstin="27ABCDE1234F1Z5",
        invoice_number="INV-1", invoice_date=date(2026, 9, 1), total_amount=1000,
    )
    assert problems == []


def test_same_gstin_and_invoice_number_is_duplicate():
    db, uid = make_db()
    existing = add_invoice(
        db, uid, supplier_gstin="27ABCDE1234F1Z5", invoice_number="INV-1",
        invoice_date=date(2026, 9, 1), total_amount=Decimal("1000.00"),
    )
    problems = find_duplicate_invoices(
        db, uid, current_invoice_id=existing.id + 1, supplier_gstin="27ABCDE1234F1Z5",
        invoice_number="INV-1", invoice_date=date(2026, 9, 5), total_amount=2000,
    )
    assert "duplicate_invoice_number" in problems


def test_different_invoice_number_is_not_duplicate():
    db, uid = make_db()
    add_invoice(
        db, uid, supplier_gstin="27ABCDE1234F1Z5", invoice_number="INV-1",
        invoice_date=date(2026, 9, 1), total_amount=Decimal("1000.00"),
    )
    problems = find_duplicate_invoices(
        db, uid, current_invoice_id=999, supplier_gstin="27ABCDE1234F1Z5",
        invoice_number="INV-2", invoice_date=date(2026, 9, 1), total_amount=1000,
    )
    assert "duplicate_invoice_number" not in problems


def test_same_date_and_amount_flags_possible_duplicate():
    db, uid = make_db()
    add_invoice(
        db, uid, supplier_gstin="27ABCDE1234F1Z5", invoice_number="INV-1",
        invoice_date=date(2026, 9, 1), total_amount=Decimal("1000.00"),
    )
    problems = find_duplicate_invoices(
        db, uid, current_invoice_id=999, supplier_gstin="27ABCDE1234F1Z5",
        invoice_number="INV-99", invoice_date=date(2026, 9, 1), total_amount=1000,
    )
    assert "possible_duplicate_same_date_and_amount" in problems


def test_does_not_flag_across_different_users():
    db, uid = make_db()
    other = User(email="other3@example.com", hashed_password="x")
    db.add(other)
    db.commit()
    db.refresh(other)
    add_invoice(
        db, other.id, supplier_gstin="27ABCDE1234F1Z5", invoice_number="INV-1",
        invoice_date=date(2026, 9, 1), total_amount=Decimal("1000.00"),
    )
    problems = find_duplicate_invoices(
        db, uid, current_invoice_id=999, supplier_gstin="27ABCDE1234F1Z5",
        invoice_number="INV-1", invoice_date=date(2026, 9, 1), total_amount=1000,
    )
    assert problems == []


def test_ignores_self_when_re_extracting():
    db, uid = make_db()
    existing = add_invoice(
        db, uid, supplier_gstin="27ABCDE1234F1Z5", invoice_number="INV-1",
        invoice_date=date(2026, 9, 1), total_amount=Decimal("1000.00"),
    )
    problems = find_duplicate_invoices(
        db, uid, current_invoice_id=existing.id, supplier_gstin="27ABCDE1234F1Z5",
        invoice_number="INV-1", invoice_date=date(2026, 9, 1), total_amount=1000,
    )
    assert problems == []


def test_missing_gstin_skips_check():
    db, uid = make_db()
    add_invoice(
        db, uid, supplier_gstin=None, invoice_number="INV-1",
        invoice_date=date(2026, 9, 1), total_amount=Decimal("1000.00"),
    )
    problems = find_duplicate_invoices(
        db, uid, current_invoice_id=999, supplier_gstin=None,
        invoice_number="INV-1", invoice_date=date(2026, 9, 1), total_amount=1000,
    )
    assert problems == []