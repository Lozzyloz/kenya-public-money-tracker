from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal[
    "administrator",
    "auditor_reviewer",
    "citizen",
    "journalist_researcher",
    "government_officer",
]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)
    full_name: str = Field(min_length=1, max_length=200)
    role: Role


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
