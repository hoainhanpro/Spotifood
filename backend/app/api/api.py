from fastapi import APIRouter
from .endpoints import auth, users, addresses

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["addresses"]) 