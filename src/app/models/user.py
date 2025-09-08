from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from .base import BaseModel as BaseModelWithId


class User(BaseModelWithId):
    """User model for database operations."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    hashed_password: Optional[str] = Field(None, description="Hashed password")


class UserCreate(BaseModel):
    """User creation model."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update model."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserInDB(User):
    """User model with hashed password for database storage."""

    hashed_password: str
