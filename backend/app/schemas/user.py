from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    """
    Schema cho đăng nhập
    """
    email: EmailStr
    password: str

class UserChangePassword(BaseModel):
    """
    Schema cho đổi mật khẩu
    """
    current_password: str
    new_password: str

class UserUpdate(BaseModel):
    """
    Schema cho cập nhật thông tin người dùng (dành cho admin)
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 