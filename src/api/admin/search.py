from fastapi import APIRouter , Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db


search_router = APIRouter()


@search_router.get("/search")
async def search(
    
    group_name: str,
    db: AsyncSession = Depends(get_db)
):
    pass