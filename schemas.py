from datetime import date

from pydantic import BaseModel, EmailStr, Field


class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    date_of_birth: date
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    course: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=255)
    enrollment_date: date | None = None


class StudentUpdate(BaseModel):
    """All fields optional: PATCH changes only what is sent."""
    name: str | None = Field(default=None, min_length=2, max_length=100)
    date_of_birth: date | None = None
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    course: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=255)
    enrollment_date: date | None = None


class StudentResponse(BaseModel):
    id: int
    name: str
    date_of_birth: date
    email: EmailStr
    phone: str | None = None
    course: str | None = None
    address: str | None = None
    enrollment_date: date | None = None
