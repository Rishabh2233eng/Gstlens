import csv
import io

from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy.orm import Session

from app.models import Invoice

HEADERS = [
    "Invoice No", "Invoice Date", "Supplier Name", "Supplier GSTIN",
    "Buyer Name", "Buyer GSTIN", "Taxable Value", "CGST", "SGST", "IGST",
    "Total Amount", "Status", "Issue Count",
]


def _row(inv: Invoice) -> list:
    return [
        inv.invoice_number or "",
        inv.invoice_date.isoformat() if inv.invoice_date else "",
        inv.supplier_name or "",
        inv.supplier_gstin or "",
        inv.buyer_name or "",
        inv.buyer_gstin or "",
        float(inv.taxable_value) if inv.taxable_value is not None else "",
        float(inv.cgst) if inv.cgst is not None else "",
        float(inv.sgst) if inv.sgst is not None else "",
        float(inv.igst) if inv.igst is not None else "",
        float(inv.total_amount) if inv.total_amount is not None else "",
        inv.status,
        len(inv.issues),
    ]


def invoices_to_excel_bytes(invoices: list[Invoice]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Invoices"
    ws.append(HEADERS)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for inv in invoices:
        ws.append(_row(inv))
    for col in ws.columns:
        width = max(len(str(c.value)) if c.value is not None else 0 for c in col) + 2
        ws.column_dimensions[col[0].column_letter].width = min(width, 40)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def invoices_to_tally_csv_bytes(invoices: list[Invoice]) -> bytes:
    """A simple Tally-style purchase voucher CSV: one row per line item,
    with GST split into CGST/SGST or IGST ledger columns."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "Voucher Date", "Voucher No", "Party Name", "Party GSTIN",
        "Item Name", "HSN/SAC", "Quantity", "Rate", "Taxable Amount",
        "CGST Amount", "SGST Amount", "IGST Amount", "Total Amount",
    ])
    for inv in invoices:
        date_str = inv.invoice_date.isoformat() if inv.invoice_date else ""
        if inv.items:
            for item in inv.items:
                writer.writerow([
                    date_str,
                    inv.invoice_number or "",
                    inv.supplier_name or "",
                    inv.supplier_gstin or "",
                    item.description or "",
                    item.hsn_code or "",
                    float(item.quantity) if item.quantity is not None else "",
                    float(item.unit_price) if item.unit_price is not None else "",
                    float(item.taxable_value) if item.taxable_value is not None else "",
                    "", "", "",
                    float(item.line_total) if item.line_total is not None else "",
                ])
        else:
            writer.writerow([
                date_str, inv.invoice_number or "", inv.supplier_name or "",
                inv.supplier_gstin or "", "", "", "", "",
                float(inv.taxable_value) if inv.taxable_value is not None else "",
                float(inv.cgst) if inv.cgst is not None else "",
                float(inv.sgst) if inv.sgst is not None else "",
                float(inv.igst) if inv.igst is not None else "",
                float(inv.total_amount) if inv.total_amount is not None else "",
            ])
    return buf.getvalue().encode("utf-8-sig")  # BOM so Excel/Tally read it correctly