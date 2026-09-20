from pydantic import BaseModel, Field


class ExtractedItem(BaseModel):
    description: str | None = Field(description="Item or service description")
    hsn_code: str | None = Field(description="HSN or SAC code exactly as printed")
    quantity: float | None
    unit_price: float | None
    taxable_value: float | None = Field(description="Taxable amount of this line before tax")
    tax_rate: float | None = Field(description="Total GST rate in percent, for example 18")
    tax_amount: float | None = Field(description="Total GST amount of this line")
    line_total: float | None = Field(description="Line amount including tax")


class ExtractedInvoice(BaseModel):
    supplier_name: str | None = Field(description="Seller who issued the invoice")
    supplier_gstin: str | None = Field(description="Seller GSTIN exactly as printed")
    buyer_name: str | None = Field(description="Customer the invoice is billed to")
    buyer_gstin: str | None = Field(description="Buyer GSTIN exactly as printed")
    invoice_number: str | None
    invoice_date: str | None = Field(description="Date in YYYY-MM-DD format")
    taxable_value: float | None = Field(description="Total taxable value of the invoice")
    cgst: float | None = Field(description="Total CGST amount")
    sgst: float | None = Field(description="Total SGST or UTGST amount")
    igst: float | None = Field(description="Total IGST amount")
    total_amount: float | None = Field(description="Final invoice total including tax")
    items: list[ExtractedItem]