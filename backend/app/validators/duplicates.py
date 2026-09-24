from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import Invoice


def find_duplicate_invoices(
    db: Session,
    user_id: int,
    current_invoice_id: int,
    supplier_gstin: str | None,
    invoice_number: str | None,
    invoice_date,
    total_amount,
) -> list[str]:
    """Looks for other invoices belonging to the same user that look like the same
    real-world invoice. Returns a list of problem codes."""
    problems = []

    if supplier_gstin and invoice_number:
        exact = (
            db.query(Invoice.id)
            .filter(
                Invoice.user_id == user_id,
                Invoice.id != current_invoice_id,
                Invoice.supplier_gstin == supplier_gstin,
                Invoice.invoice_number == invoice_number,
            )
            .first()
        )
        if exact:
            problems.append("duplicate_invoice_number")

    if supplier_gstin and invoice_date is not None and total_amount is not None:
        total = Decimal(str(total_amount))
        near_match = (
            db.query(Invoice.id)
            .filter(
                Invoice.user_id == user_id,
                Invoice.id != current_invoice_id,
                Invoice.supplier_gstin == supplier_gstin,
                Invoice.invoice_date == invoice_date,
                Invoice.total_amount == total,
            )
            .first()
        )
        if near_match and "duplicate_invoice_number" not in problems:
            problems.append("possible_duplicate_same_date_and_amount")

    return problems