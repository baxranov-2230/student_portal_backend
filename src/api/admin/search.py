from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import Optional
from src.models.user import User
from src.schemas.search import SearchBase
from src.core.base import get_db
from src.utils.auth import RoleChecker

search_router = APIRouter()

@search_router.get("/search", response_model=list[SearchBase])
async def generic_search(
    last_name: Optional[str] = Query(None, description="Last name to search"),
    first_name: Optional[str] = Query(None, description="First name to search"),
    student_id_number: Optional[str] = Query(None, description="Student ID number"),
    faculty: Optional[str] = Query(None, description="Faculty"),
    limit: int = Query(10, ge=1, le=100, description="Max number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker("admin")),
):
    query_params = {
        "last_name": last_name,
        "first_name": first_name,
        "student_id_number": student_id_number,
        "faculty": faculty,
    }

    filters = []
    for key, value in query_params.items():
        if value is None:
            continue
        if hasattr(User, key):
            column_attr = getattr(User, key)
            filters.append(column_attr.ilike(f"%{value}%"))
        else:
            raise HTTPException(status_code=400, detail=f"Invalid filter field: {key}")

    if not filters:
        raise HTTPException(status_code=400, detail="At least one search parameter is required")

    stmt = select(User).where(and_(*filters)).offset(offset).limit(limit)

    result = await db.execute(stmt)
    users = result.scalars().all()

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    return users
