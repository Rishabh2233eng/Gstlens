from datetime import datetime

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