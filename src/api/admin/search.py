from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from src.models.user import User  
from src.core.base import get_db  

search_router = APIRouter()

@search_router.get("/search")
async def search(
    first_name: str | None = None,
    last_name: str | None = None,
    student_id : str | None = None,
    db: AsyncSession = Depends(get_db)
):
    filters = []
    if first_name:
        filters.append(User.first_name == first_name)
    if last_name:
        filters.append(User.last_name == last_name)
    if student_id:
        filters.append(User.student_id_number == student_id)
    
    
    stmt = select(User)
    if filters:
        stmt = stmt.where(and_(*filters))
    
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users
    