from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

Path("samples").mkdir(exist_ok=True)
c = canvas.Canvas("samples/invoice1.pdf", pagesize=A4)
w, h = A4
y = h - 60

def line(text, size=10, bold=False, gap=16):
    global y
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(50, y, text)
    y -= gap

line("TAX INVOICE", 16, True, 26)
line("ABC Traders", 12, True)
line("GSTIN: 27ABCDE1234F1Z5")
line("Mumbai, Maharashtra", gap=24)
line("Invoice No: INV-2026-0042")
line("Date: 15/09/2026", gap=24)
line("Bill To: XYZ Enterprises", bold=True)
line("GSTIN: 27PQRSX5678L1Z2", gap=28)
line("Description       HSN     Qty    Rate      Taxable    GST%   Tax", bold=True)
line("Office Chair      9401    2      4000.00   8000.00    18     1440.00")
line("Desk Lamp         9405    5      600.00    3000.00    18     540.00", gap=28)
line("Taxable Value: 11000.00")
line("CGST (9%): 990.00")
line("SGST (9%): 990.00")
line("Total Amount: 12980.00", 12, True)
c.save()
print("Created samples/invoice1.pdf")