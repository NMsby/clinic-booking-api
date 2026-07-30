from pydantic import BaseModel, EmailStr, Field


class PatientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(max_length=255)
    phone: str = Field(min_length=1, max_length=50)
