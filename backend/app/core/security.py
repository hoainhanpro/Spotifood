from datetime import datetime, timedelta
from typing import Any, Optional, Union
from jose import jwt
from passlib.context import CryptContext
import hashlib
from ..core.config import settings

# Sử dụng SHA-256 cho password hashing theo yêu cầu
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Xác thực mật khẩu
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash mật khẩu
    """
    return pwd_context.hash(password)

def hash_sha256(password: str) -> str:
    """
    Hash mật khẩu bằng SHA-256 (phương thức hỗ trợ thêm)
    """
    return hashlib.sha256(password.encode()).hexdigest() 