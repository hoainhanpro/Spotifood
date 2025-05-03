from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Lấy user theo email
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Lấy user theo ID
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_create: UserCreate) -> User:
    """
    Tạo người dùng mới
    
    Args:
        db: Database session
        user_create: Thông tin người dùng cần tạo
        
    Returns:
        User đã được tạo
    """
    # Tạo hash password từ password thô
    hashed_password = get_password_hash(user_create.password)
    
    # Tạo đối tượng User từ schema UserCreate
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        phone_number=user_create.phone_number,
        hashed_password=hashed_password,
        is_active=user_create.is_active,
        role=user_create.role
    )
    
    # Thêm vào database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Xác thực user
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def change_user_password(db: Session, user: User, new_password: str) -> User:
    """
    Đổi mật khẩu cho user
    """
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """
    Cập nhật thông tin người dùng dựa trên UserUpdate schema
    
    Args:
        db: Database session
        user_id: ID của người dùng cần cập nhật
        user_update: Thông tin cần cập nhật
        
    Returns:
        User đã được cập nhật hoặc None nếu không tìm thấy
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    # Chuyển đổi từ UserUpdate thành dữ liệu cập nhật
    update_data = user_update.dict(exclude_unset=True)
    
    # Cập nhật các trường thông tin
    for key, value in update_data.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    
    # Cập nhật thời gian sửa đổi
    user.updated_at = datetime.utcnow()
    
    # Lưu vào database
    db.commit()
    db.refresh(user)
    
    return user 