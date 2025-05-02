from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

# Đường dẫn đến file .env ở thư mục gốc
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(dotenv_path=dotenv_path)

# Hàm để chuyển đổi chuỗi CORS origins thành list
def get_cors_origins():
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:5175")
    return [origin.strip() for origin in cors_origins.split(",")]

# Các biến bắt buộc phải có trong .env
required_env_vars = [
    "POSTGRES_SERVER",
    "POSTGRES_PORT",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "SECRET_KEY"
]

# Kiểm tra các biến môi trường bắt buộc
missing_vars = [var for var in required_env_vars if os.getenv(var) is None]
if missing_vars:
    raise ValueError(f"Thiếu các biến môi trường bắt buộc: {', '.join(missing_vars)}")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Spotifood API"
    API_V1_STR: str = "/api"
    
    # Thông tin kết nối PostgreSQL từ biến môi trường
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    
    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # CORS settings - đọc từ biến môi trường
    BACKEND_CORS_ORIGINS: List[str] = get_cors_origins()
    
    # Xây dựng chuỗi kết nối database
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 phút

    class Config:
        case_sensitive = True
        env_file = dotenv_path

settings = Settings() 