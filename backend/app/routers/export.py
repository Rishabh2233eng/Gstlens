from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user
from app.export import invoices_to_excel_bytes, invoices_to_tally_csv_bytes
from app.models import Invoice, User
from app.schemas import ExportRequest

router = APIRouter(prefix="/invoices", tags=["export"])

EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _get_owned_invoices(db: Session, user_id: int, ids: list[int]) -> list[Invoice]:
    invoices = (
        db.query(Invoice)
        .options(joinedload(Invoice.items))
        .filter(Invoice.user_id == user_id, Invoice.id.in_(ids))
        .all()
    )
    if not invoices:
        raise HTTPException(status_code=404, detail="No matching invoices found")
    return invoices


def _filename(prefix: str, ext: str, count: int) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{count}invoices_{stamp}.{ext}"


@router.get("/{invoice_id}/export/excel")
def export_one_excel(
    invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    invoices = _get_owned_invoices(db, current_user.id, [invoice_id])
    data = invoices_to_excel_bytes(invoices)
    name = _filename("gstlens", "xlsx", len(invoices))
    return Response(
        content=data, media_type=EXCEL_MIME,
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@router.get("/{invoice_id}/export/csv")
def export_one_csv(
    invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    invoices = _get_owned_invoices(db, current_user.id, [invoice_id])
    data = invoices_to_tally_csv_bytes(invoices)
    name = _filename("gstlens_tally", "csv", len(invoices))
    return Response(
        content=data, media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@router.post("/export/excel")
def export_batch_excel(
    payload: ExportRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    invoices = _get_owned_invoices(db, current_user.id, payload.invoice_ids)
    data = invoices_to_excel_bytes(invoices)
    name = _filename("gstlens", "xlsx", len(invoices))
    return Response(
        content=data, media_type=EXCEL_MIME,
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@router.post("/export/csv")
def export_batch_csv(
    payload: ExportRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    invoices = _get_owned_invoices(db, current_user.id, payload.invoice_ids)
    data = invoices_to_tally_csv_bytes(invoices)
    name = _filename("gstlens_tally", "csv", len(invoices))
    return Response(
        content=data, media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )