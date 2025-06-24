from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.core.base import get_db
from src.models.user import User
from src.utils.auth import RoleChecker

count_router = APIRouter(
    prefix="/count",
    tags=["Count"]
)

@count_router.get("/count_by_faculty")
async def count_get(
    faculty_name: str = Query(..., description="Faculty name to count users from"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker("admin"))
):
    stmt = (
        select(func.count(), User.faculty)
        .where(User.faculty.ilike(f"%{faculty_name}%"))
        .group_by(User.faculty)
    )

    result = await db.execute(stmt)
    row = result.first()  # single row: (count, faculty)

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topilmadi"
        )

    count, faculty = row

    return {
        "faculty": faculty,  # real DB value
        "count": count
    }
