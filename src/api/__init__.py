from fastapi import APIRouter
from .auth import auth_router
from .user import user_router
from .admin import admin_router

api_router = APIRouter()


api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(admin_router)
