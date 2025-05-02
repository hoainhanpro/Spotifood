from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """
    Schema cho JWT token
    """
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Schema cho JWT payload
    """
    sub: Optional[str] = None
    exp: Optional[int] = None 