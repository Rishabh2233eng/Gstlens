from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

Path("samples").mkdir(exist_ok=True)
c = canvas.Canvas("samples/invoice2.pdf", pagesize=A4)
w, h = A4
y = h - 50

def line(text, size=10, bold=False, gap=15):
    global y
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(50, y, text)
    y -= gap

line("TAX INVOICE", 18, True, 30)
line("Sharma Electronics & Co.", 13, True)
line("Shop No. 14, MG Road, Pune, Maharashtra - 411001")
line("GSTIN: 27AAPFU0939F1ZV   |   Phone: 9876543210", gap=25)
line(f"Invoice No: SE/2026/0187", bold=True)
line("Invoice Date: 20/09/2026", gap=25)
line("Bill To:", bold=True)
line("Rajesh Kumar Traders")
line("Shivaji Nagar, Pune, Maharashtra")
line("GSTIN: 27BBCDE5678G1Z3", gap=28)
line("Description            HSN      Qty   Rate      Taxable    GST%   Amount", bold=True, gap=18)
line("LED Monitor 24-inch    8528     3     7500.00   22500.00   18     4050.00")
line("USB Keyboard           8471     5     800.00    4000.00    18     720.00")
line("Wireless Mouse         8471     5     600.00    3000.00    18     540.00", gap=30)
line("Total Taxable Value: 29500.00", bold=True)
line("CGST (9%): 2655.00")
line("SGST (9%): 2655.00")
line("Grand Total: 34810.00", 13, True)
c.save()
print("Created samples/invoice2.pdf")