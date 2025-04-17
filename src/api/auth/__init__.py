from .login import login_router
from .logout import logout_router
from .refresh import refresh_router
from fastapi import APIRouter


auth_router = APIRouter(
    tags=["Auth"],
    prefix="/auth"
)


auth_router.include_router(login_router)
auth_router.include_router(logout_router)
auth_router.include_router(refresh_router)
