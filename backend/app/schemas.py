from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str | None = None


class PlanOut(BaseModel):
    name: str
    price_inr: int
    monthly_page_limit: int
    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    plan: PlanOut | None = None
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class InvoiceOut(BaseModel):
    id: int
    filename: str
    page_count: int
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InvoiceItemOut(BaseModel):
    id: int
    description: str | None
    hsn_code: str | None
    quantity: Decimal | None
    unit_price: Decimal | None
    taxable_value: Decimal | None
    tax_rate: Decimal | None
    tax_amount: Decimal | None
    line_total: Decimal | None
    model_config = ConfigDict(from_attributes=True)


class InvoiceListOut(BaseModel):
    id: int
    filename: str
    page_count: int
    status: str
    supplier_name: str | None
    invoice_number: str | None
    invoice_date: date | None
    total_amount: Decimal | None
    issue_count: int = 0
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InvoiceDetailOut(BaseModel):
    id: int
    filename: str
    page_count: int
    status: str
    error_message: str | None
    supplier_name: str | None
    supplier_gstin: str | None
    buyer_name: str | None
    buyer_gstin: str | None
    invoice_number: str | None
    invoice_date: date | None
    taxable_value: Decimal | None
    cgst: Decimal | None
    sgst: Decimal | None
    igst: Decimal | None
    total_amount: Decimal | None
    created_at: datetime
    items: list[InvoiceItemOut]
    model_config = ConfigDict(from_attributes=True)


class ValidationIssueOut(BaseModel):
    id: int
    code: str
    severity: str
    field: str | None
    message: str
    model_config = ConfigDict(from_attributes=True)

class InvoiceItemUpdate(BaseModel):
    id: int | None = None  # omit for a new item, include to update an existing one
    description: str | None = None
    hsn_code: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    taxable_value: Decimal | None = None
    tax_rate: Decimal | None = None
    tax_amount: Decimal | None = None
    line_total: Decimal | None = None


class InvoiceUpdate(BaseModel):
    supplier_name: str | None = None
    supplier_gstin: str | None = None
    buyer_name: str | None = None
    buyer_gstin: str | None = None
    invoice_number: str | None = None
    invoice_date: date | None = None
    taxable_value: Decimal | None = None
    cgst: Decimal | None = None
    sgst: Decimal | None = None
    igst: Decimal | None = None
    total_amount: Decimal | None = None
    items: list[InvoiceItemUpdate] | None = None  # omit to leave items unchanged