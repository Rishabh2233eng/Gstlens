from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.deps import get_current_user
from app.extraction_schema import ExtractedInvoice
from app.extractor import ExtractionError, extract_invoice
from app.file_utils import detect_file_type
from app.models import Invoice, User

router = APIRouter(prefix="/invoices", tags=["extraction"])


@router.post("/{invoice_id}/extract", response_model=ExtractedInvoice)
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
        raise HTTPException(status_code=404, detail="The file is missing on the server")

    data = path.read_bytes()
    kind = detect_file_type(data)
    try:
        return extract_invoice(data, kind)
    except ExtractionError as e:
        raise HTTPException(status_code=502, detail=str(e))