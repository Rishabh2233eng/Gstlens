from pydantic import BaseModel, Field


class ExtractedItem(BaseModel):
    description: str | None = None
    hsn_code: str | None = Field(default=None, description="HSN or SAC code exactly as printed")
    quantity: float | None = None
    unit_price: float | None = None
    taxable_value: float | None = Field(default=None, description="Taxable amount of this line before tax")
    tax_rate: float | None = Field(default=None, description="Total GST rate in percent, for example 18")
    tax_amount: float | None = Field(default=None, description="Total GST amount of this line")
    line_total: float | None = Field(default=None, description="Line amount including tax")


class ExtractedInvoice(BaseModel):
    supplier_name: str | None = Field(default=None, description="Seller who issued the invoice")
    supplier_gstin: str | None = Field(default=None, description="Seller GSTIN exactly as printed")
    buyer_name: str | None = Field(default=None, description="Customer the invoice is billed to")
    buyer_gstin: str | None = Field(default=None, description="Buyer GSTIN exactly as printed")
    invoice_number: str | None = None
    invoice_date: str | None = Field(default=None, description="Date in YYYY-MM-DD format")
    taxable_value: float | None = Field(default=None, description="Total taxable value of the invoice")
    cgst: float | None = Field(default=None, description="Total CGST amount")
    sgst: float | None = Field(default=None, description="Total SGST or UTGST amount")
    igst: float | None = Field(default=None, description="Total IGST amount")
    total_amount: float | None = Field(default=None, description="Final invoice total including tax")
    items: list[ExtractedItem] = Field(default_factory=list)