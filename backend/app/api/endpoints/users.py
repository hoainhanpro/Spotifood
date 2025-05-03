from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from ...database.database import get_db
from ...models.user import User
from ...models.address import Address
from ...schemas.user import User as UserSchema, UserUpdate
from ...services.user_service import update_user
from ..deps import get_current_active_user, get_current_admin_user

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Chỉ admin mới được xem danh sách
):
    # Truy vấn users với eager loading addresses
    users = db.query(User).options(
        # Load mối quan hệ addresses để tránh N+1 query
        joinedload(User.addresses)
    ).offset(skip).limit(limit).all()
    
    return users

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lấy thông tin user hiện tại kèm địa chỉ
    """
    # Load lại user từ database để đảm bảo có thông tin địa chỉ
    user = db.query(User).options(
        joinedload(User.addresses)
    ).filter(User.id == current_user.id).first()
    
    return user

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
        
    user = db.query(User).options(
        joinedload(User.addresses)
    ).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user_info(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Chỉ admin mới có quyền cập nhật
):
    """
    Cập nhật thông tin người dùng (chỉ admin mới có quyền)
    """
    # Kiểm tra xem người dùng cần cập nhật có tồn tại không
    updated_user = update_user(db, user_id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người dùng để cập nhật"
        )
    
    # Load lại user để lấy thông tin địa chỉ
    user = db.query(User).options(
        joinedload(User.addresses)
    ).filter(User.id == user_id).first()
    
    return user 