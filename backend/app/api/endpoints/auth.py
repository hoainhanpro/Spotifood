from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.security import create_access_token
from ...database.database import get_db
from ...schemas.token import Token
from ...schemas.user import UserCreate, UserLogin, UserChangePassword
from ...services.user_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    change_user_password
)
from ...models.user import User
from ..deps import get_current_active_user

router = APIRouter()


@router.post("/register", response_model=Token)
async def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Đăng ký tài khoản mới và trả về access token
    """
    # Kiểm tra email đã tồn tại chưa
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng",
        )
    
    # Tạo user mới
    user = create_user(db, user_in=user_in)
    
    # Tạo access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: Session = Depends(get_db)) -> Any:
    """
    Đăng nhập và lấy JWT access token
    """
    user = authenticate_user(db, email=user_in.email, password=user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kiểm tra user còn hoạt động không
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản không còn hoạt động",
        )
    
    # Tạo access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/oauth", response_model=Token)
async def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, để tương thích với OAuth2PasswordBearer
    """
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kiểm tra user còn hoạt động không
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản không còn hoạt động",
        )
    
    # Tạo access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/change-password")
async def change_password(
    password_in: UserChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Đổi mật khẩu cho tài khoản đã đăng nhập
    """
    # Xác thực mật khẩu hiện tại
    user = authenticate_user(db, email=current_user.email, password=password_in.current_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không chính xác",
        )
    
    # Đổi mật khẩu
    change_user_password(db, user=user, new_password=password_in.new_password)
    
    return {"message": "Đổi mật khẩu thành công"} 