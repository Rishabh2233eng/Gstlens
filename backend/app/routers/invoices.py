import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.deps import get_current_user
from app.file_utils import count_pdf_pages, detect_file_type
from app.models import Invoice, User
from app.schemas import InvoiceOut

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/upload", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # read at most limit + 1 bytes, so we can tell if the file is too big
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

    # save under a random name; keep the original name only in the database
    stored_name = f"{current_user.id}/{uuid.uuid4().hex}.{kind}"
    path = config.UPLOAD_DIR / stored_name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

    original_name = (file.filename or "invoice").replace("\\", "/").split("/")[-1][:255]
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
        path.unlink(missing_ok=True)  # do not leave an orphan file behind
        raise
    return invoice