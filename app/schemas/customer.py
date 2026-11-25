from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
    company_name: str = Field(
        min_length=2,
        max_length=255,
    )

    contact_name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    phone: str | None = Field(
        default=None,
        max_length=30,
    )


class CustomerUpdate(BaseModel):
    company_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    contact_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    status: str | None = None


class CustomerResponse(BaseModel):
    id: int
    external_id: str | None
    company_name: str
    contact_name: str
    email: EmailStr
    phone: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
