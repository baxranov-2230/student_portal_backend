from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.core.base import get_db
from src.models import User  ,  Application
from src.utils.auth import RoleChecker

count_router = APIRouter(
    prefix="/count",
)


@count_router.get("/count_by_specialty")
async def count_get(
    specialty_name: str | None = Query(None, description="Optional faculty name to count users from"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker("admin"))
):
    filters = []
    if specialty_name:
        filters.append(User.specialty.ilike(f"%{specialty_name}%"))

    # Talabalar soni GPA < 3.5
    stmt_low = (
        select(func.count())
        .select_from(Application)
        .join(User, User.id == Application.user_id)
        .where(*filters, Application.gpa < 3.5)
    )
    low_result = await db.execute(stmt_low)
    low_count = low_result.scalar()

    # Talabalar soni GPA >= 3.5
    stmt_high = (
        select(func.count())
        .select_from(Application)
        .join(User, User.id == Application.user_id)
        .where(*filters, Application.gpa >= 3.5)
    )
    high_result = await db.execute(stmt_high)
    high_count = high_result.scalar()

    # Umumiy Application soni
    stmt_all = (
        select(func.count())
        .select_from(Application)
        .join(User, User.id == Application.user_id)
        .where(*filters)
    )
    all_result = await db.execute(stmt_all)
    all_count = all_result.scalar()

    return {
        "specialty": specialty_name or "All specialties",
        "total_applications": all_count,
        "gpa_fit_applications": high_count,
        "gpa_not_fit_applications": low_count
    }

    

