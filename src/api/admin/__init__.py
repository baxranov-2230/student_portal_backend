from fastapi import APIRouter
from .get_by_id import get_router
from .search import search_router
from .count import count_router


admin_router = APIRouter(tags=["Admin"], prefix="/admin")


admin_router.include_router(get_router)
admin_router.include_router(search_router)
admin_router.include_router(count_router)