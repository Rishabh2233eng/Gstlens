import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.deps import get_current_user
from app.file_utils import count_pdf_pages, detect_file_type
from app.models import Invoice, InvoiceItem, User, ValidationIssue
from app.schemas import (
    InvoiceDetailOut,
    InvoiceListOut,
    InvoiceOut,
    InvoiceUpdate,
    ValidationIssueOut,
)
from app.validation_pipeline import run_validation

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/upload", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = file.file.read(config.MAX_UPLOAD_BYTES + 1)
    if len(data) > config.MAX_UPLOAD_BYTES:
        max_mb = config.MAX_UPLOAD_BYTES / 1024 / 1024
        raise HTTPException(status_code=413, detail=f"File too large. Maximum is {max_mb:g} MB")
    if not data:
        raise HTTPException(status_code=400, detail="The file is empty")

    kind = detect_file_type(data)
    if kind is None:
        raise HTTPException(status_code=400, detail="Only PDF, JPG and PNG files are allowed")

    if kind == "pdf":
        try:
            pages = count_pdf_pages(data)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception:
            raise HTTPException(
                status_code=400, detail="Could not read this PDF. It may be corrupted"
            )
        if pages < 1:
            raise HTTPException(status_code=400, detail="This PDF has no pages")
        if pages > config.MAX_PDF_PAGES:
            raise HTTPException(
                status_code=400,
                detail=f"PDF has {pages} pages. Maximum is {config.MAX_PDF_PAGES}",
            )
    else:
        pages = 1

    stored_name = f"{current_user.id}/{uuid.uuid4().hex}.{kind}"
    path = config.UPLOAD_DIR / stored_name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

    original_name = (file.filename or "invoice").replace("\\", "/").split("/")[-1][:255] or "invoice"
    invoice = Invoice(
        user_id=current_user.id,
        filename=original_name,
        file_path=stored_name,
        page_count=pages,
        status="uploaded",
    )
    try:
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
    except Exception:
        db.rollback()
        path.unlink(missing_ok=True)
        raise
    return invoice


@router.get("", response_model=list[InvoiceListOut])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Invoice, func.count(ValidationIssue.id).label("issue_count"))
        .outerjoin(ValidationIssue, ValidationIssue.invoice_id == Invoice.id)
        .filter(Invoice.user_id == current_user.id)
        .group_by(Invoice.id)
        .order_by(Invoice.created_at.desc())
        .all()
    )
    results = []
    for invoice, issue_count in rows:
        item = InvoiceListOut.model_validate(invoice)
        item.issue_count = issue_count
        results.append(item)
    return results


@router.get("/{invoice_id}", response_model=InvoiceDetailOut)
def get_invoice(
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
    return invoice


@router.get("/{invoice_id}/issues", response_model=list[ValidationIssueOut])
def get_invoice_issues(
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
    return invoice.issues


@router.patch("/{invoice_id}", response_model=InvoiceDetailOut)
def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
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

    data = payload.model_dump(exclude_unset=True, exclude={"items"})
    for field, value in data.items():
        setattr(invoice, field, value)

    if payload.items is not None:
        existing_by_id = {item.id: item for item in invoice.items}
        keep_ids = set()

        for item_in in payload.items:
            if item_in.id is not None and item_in.id in existing_by_id:
                item = existing_by_id[item_in.id]
                for field, value in item_in.model_dump(exclude_unset=True, exclude={"id"}).items():
                    setattr(item, field, value)
                keep_ids.add(item.id)
            else:
                new_item = InvoiceItem(
                    invoice_id=invoice.id,
                    **item_in.model_dump(exclude_unset=True, exclude={"id"}),
                )
                db.add(new_item)

        for item in list(invoice.items):
            if item.id is not None and item.id not in keep_ids and item.id in existing_by_id:
                if not any(i.id == item.id for i in payload.items):
                    db.delete(item)

    db.flush()
    run_validation(db, invoice)
    db.commit()
    db.refresh(invoice)
    return invoice