from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from .address import Address

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True
    role: str = "customer"

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
    role: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    addresses: Optional[List[Address]] = []

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    class Config:
        from_attributes = True 