from fastapi import APIRouter
from .get_by_id import get_router
from .search import search_router



admin_router = APIRouter()


admin_router.include_router(get_router)
admin_router.include_router(search_router)

