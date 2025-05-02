from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database.database import get_db
from ...models.user import User
from ...schemas.user import User as UserSchema
from ..deps import get_current_active_user, get_current_admin_user

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Chỉ admin mới được xem danh sách
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Lấy thông tin user hiện tại
    """
    return current_user

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Chỉ cho phép user xem thông tin của chính mình hoặc admin xem thông tin của bất kỳ ai
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Không có quyền truy cập thông tin của người dùng khác"
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user 