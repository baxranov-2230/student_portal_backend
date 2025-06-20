from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.application import Application
from src.models.user import User
from src.models.user_gpa import UserGpa
from src.utils.auth import RoleChecker
from src.core.base import get_db
from typing import List
from src.schemas.application import ApplicationCreateResponse , ApplicationDeleteResponse





application_router = APIRouter(prefix="/application")

@application_router.post("/create", response_model=ApplicationCreateResponse)
async def create_application(
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new application for the authenticated student."""
    # Fetch user's GPA for level "1-kurs"
    stmt = select(UserGpa).where(
        UserGpa.user_id == current_user.id,
        UserGpa.level == "1-kurs"
    )
    result = await db.execute(stmt)
    user_gpa = result.scalars().first()

    if not user_gpa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GPA record not found for the user"
        )

    # Check GPA eligibility
    if user_gpa.gpa < 3.5:  # Changed to < for clarity (adjust as needed)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="GPA must be at least 3.5 to apply"
        )

    # Validate education year format and check start year
    try:
        start_year = int(user_gpa.educationYear.split("-")[0])
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid education year format"
        )

    if start_year < 2024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Applications are only allowed for education years starting 2024 or later"
        )

    # Create new application
    new_application = Application(
        user_id=current_user.id,
        full_name = current_user.full_name,
        student_id_number=current_user.student_id_number,
        image_path=current_user.image_path,
        group=current_user.group,
        faculty=current_user.faculty,
        gpa=user_gpa.gpa
    )

    try:
        db.add(new_application)
        await db.commit()
        await db.refresh(new_application)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application"
        )

    return new_application

@application_router.get("/get_by_id/{application_id}", response_model=ApplicationCreateResponse)
async def get_application_by_id(
    application_id: int,
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve an application by its ID for the authenticated student."""
    if application_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application ID must be a positive integer"
        )

    stmt = select(Application).where(
        Application.user_id == current_user.id,
        Application.id == application_id
    )
    result = await db.execute(stmt)
    application = result.scalars().first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    return application

@application_router.get("/get_all", response_model=List[ApplicationCreateResponse])
async def get_all_applications(
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all applications for the authenticated student."""
    stmt = select(Application).where(Application.user_id == current_user.id)
    result = await db.execute(stmt)
    applications = result.scalars().all()

    if not applications:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No applications found for the user"
        )

    return applications

@application_router.delete("/{application_id}", response_model=ApplicationDeleteResponse)
async def delete_application(
    application_id: int,
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    """Delete an application by its ID for the authenticated student."""
    if application_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application ID must be a positive integer"
        )

    stmt = select(Application).where(
        Application.id == application_id,
        Application.user_id == current_user.id
    )
    result = await db.execute(stmt)
    application = result.scalars().first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    try:
        await db.delete(application)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete application"
        )

    return {"message": "Application deleted successfully"}