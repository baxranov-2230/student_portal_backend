from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.application import Application
from src.utils.auth import RoleChecker
from src.core.base import get_db
from pydantic import BaseModel
from typing import List

# Pydantic model for response
class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    last_name: str
    first_name: str
    third_name: str | None
    student_id_number: str
    image_path: str | None
    group: str
    faculty: str
    gpa: float

 

# Router setup
get_router = APIRouter(prefix="/applications", tags=["Admin Applications"])

@get_router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application_by_id(
    application_id: int,
    current_user: dict = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve an application by its ID for admin users."""
    if application_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application ID must be a positive integer"
        )

    stmt = select(Application).where(Application.id == application_id)
    result = await db.execute(stmt)
    application = result.scalars().first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    return application

@get_router.get("/", response_model=List[ApplicationResponse])
async def get_all_applications(
    min_gpa: float = Query(None, ge=0.0, le=5.0),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all applications with optional GPA filtering and pagination for admin users."""
    stmt = select(Application)

    # Apply GPA filter if provided
    if min_gpa is not None:
        stmt = stmt.where(Application.gpa >= min_gpa)

    # Apply pagination
    stmt = stmt.offset(offset).limit(limit)

    try:
        result = await db.execute(stmt)
        applications = result.scalars().all()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve applications"
        )

    if not applications:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No applications found"
        )

    return applications