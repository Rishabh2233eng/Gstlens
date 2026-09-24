from sqlalchemy.orm import Session

from app.models import Invoice, ValidationIssue
from app.validators.dates import check_invoice_date
from app.validators.duplicates import find_duplicate_invoices
from app.validators.gstin import validate_gstin
from app.validators.messages import message_for, severity_for
from app.validators.place_of_supply import check_place_of_supply
from app.validators.tax import (
    check_invoice_totals,
    check_line_item_tax,
    check_line_items_sum_to_invoice,
    check_tax_split,
)


def _add(problems: dict, code: str, field: str | None):
    problems.setdefault(code, field)


def run_validation(db: Session, invoice: Invoice) -> None:
    """Runs every validator on the given invoice and (re)writes its ValidationIssue rows."""
    found: dict[str, str | None] = {}

    for code in validate_gstin(invoice.supplier_gstin):
        _add(found, f"supplier_gstin_{code}", "supplier_gstin")
    for code in validate_gstin(invoice.buyer_gstin):
        _add(found, f"buyer_gstin_{code}", "buyer_gstin")

    for item in invoice.items:
        for code in check_line_item_tax(item.taxable_value, item.tax_rate, item.tax_amount):
            _add(found, code, "items")

    for code in check_tax_split(invoice.cgst, invoice.sgst, invoice.igst):
        _add(found, code, "tax")

    for code in check_invoice_totals(
        invoice.taxable_value, invoice.cgst, invoice.sgst, invoice.igst, invoice.total_amount
    ):
        _add(found, code, "total_amount")

    for code in check_line_items_sum_to_invoice(
        [i.taxable_value for i in invoice.items], invoice.taxable_value
    ):
        _add(found, code, "items")

    for code in check_place_of_supply(
        invoice.supplier_gstin, invoice.buyer_gstin, invoice.cgst, invoice.sgst, invoice.igst
    ):
        _add(found, code, "tax")

    for code in check_invoice_date(invoice.invoice_date):
        _add(found, code, "invoice_date")

    for code in find_duplicate_invoices(
        db, invoice.user_id, invoice.id, invoice.supplier_gstin,
        invoice.invoice_number, invoice.invoice_date, invoice.total_amount,
    ):
        _add(found, code, "invoice_number")

    # replace old issues, in case this invoice is re-extracted
    for old in list(invoice.issues):
        db.delete(old)

    for code, field in found.items():
        clean_code = code.split("supplier_gstin_")[-1].split("buyer_gstin_")[-1]
        db.add(
            ValidationIssue(
                invoice_id=invoice.id,
                code=code,
                severity=severity_for(clean_code),
                field=field,
                message=message_for(clean_code),
            )
        )