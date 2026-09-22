from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.deps import get_current_user
from app.extraction_schema import ExtractedInvoice
from app.extractor import ExtractionError, extract_invoice
from app.file_utils import detect_file_type
from app.models import Invoice, InvoiceItem, User
from app.schemas import InvoiceDetailOut

router = APIRouter(prefix="/invoices", tags=["extraction"])


def _parse_date(value: str | None) -> date_type | None:
    if not value:
        return None
    try:
        return date_type.fromisoformat(value)
    except ValueError:
        return None


def _apply_extraction(invoice: Invoice, result: ExtractedInvoice, db: Session) -> None:
    invoice.supplier_name = result.supplier_name
    invoice.supplier_gstin = result.supplier_gstin
    invoice.buyer_name = result.buyer_name
    invoice.buyer_gstin = result.buyer_gstin
    invoice.invoice_number = result.invoice_number
    invoice.invoice_date = _parse_date(result.invoice_date)
    invoice.taxable_value = result.taxable_value
    invoice.cgst = result.cgst
    invoice.sgst = result.sgst
    invoice.igst = result.igst
    invoice.total_amount = result.total_amount
    invoice.raw_json = result.model_dump()

    # replace old items, in case this invoice is re-extracted
    for old_item in list(invoice.items):
        db.delete(old_item)

    for item in result.items:
        db.add(
            InvoiceItem(
                invoice_id=invoice.id,
                description=item.description,
                hsn_code=item.hsn_code,
                quantity=item.quantity,
                unit_price=item.unit_price,
                taxable_value=item.taxable_value,
                tax_rate=item.tax_rate,
                tax_amount=item.tax_amount,
                line_total=item.line_total,
            )
        )


@router.post("/{invoice_id}/extract", response_model=InvoiceDetailOut)
def extract(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        .first()
    )
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    path = config.UPLOAD_DIR / invoice.file_path
    if not path.exists():
        invoice.status = "failed"
        invoice.error_message = "The file is missing on the server"
        db.commit()
        raise HTTPException(status_code=404, detail=invoice.error_message)

    invoice.status = "processing"
    db.commit()

    data = path.read_bytes()
    kind = detect_file_type(data)
    try:
        result = extract_invoice(data, kind)
    except ExtractionError as e:
        invoice.status = "failed"
        invoice.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=502, detail=str(e))

    _apply_extraction(invoice, result, db)
    invoice.status = "done"
    invoice.error_message = None
    db.commit()
    db.refresh(invoice)
    return invoice