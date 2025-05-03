from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..models.user import User
from ..core.config import settings
from ..schemas.token import TokenPayload
from ..services.user_service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Xác thực và lấy user từ JWT token
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không thể xác thực thông tin",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Kiểm tra token hết hạn
    if token_data.exp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(db, int(token_data.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Kiểm tra user còn hoạt động hay không
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản người dùng không hoạt động",
        )
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Kiểm tra user có quyền admin hay không
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập",
        )
    return current_user

def get_current_restaurant_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Kiểm tra user có quyền nhà hàng hay không
    """
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ nhà hàng mới có quyền thực hiện thao tác này",
        )
    return current_user

def get_current_shipper_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Kiểm tra user có quyền shipper hay không
    """
    if current_user.role != "shipper":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ người giao hàng mới có quyền thực hiện thao tác này",
        )
    return current_user

def get_current_customer_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Kiểm tra user có quyền khách hàng hay không
    """
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ khách hàng mới có quyền thực hiện thao tác này",
        )
    return current_user 