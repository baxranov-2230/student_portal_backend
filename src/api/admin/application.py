from fastapi import APIRouter, Depends, HTTPException, status, Query 
from fastapi.responses import StreamingResponse
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.application import Application
from src.utils.auth import RoleChecker
from src.core.base import get_db
from src.schemas.application import ApplicationResponse
from typing import List
from src.models import User
from sqlalchemy.orm import joinedload
from sqlalchemy import and_ , desc 
from sqlalchemy.orm import selectinload
from fastapi.responses import FileResponse
import os
from io import BytesIO
from openpyxl import Workbook




# Router setup
application_router = APIRouter(
    prefix="/applications"
    )

@application_router.get("/get_by_id/{application_id}", response_model=ApplicationResponse)
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



@application_router.get("/get_all", response_model=List[ApplicationResponse])
async def get_all_applications(
    min_gpa: float = Query(None, ge=0.0, le=5.0),
    max_gpa: float = Query(None, ge=0.0, le=5.0),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all applications with optional GPA filtering, ordered by GPA descending, and pagination."""
    stmt = select(Application)

    # Apply GPA filter if provided
    if min_gpa is not None:
        stmt = stmt.where(Application.gpa >= min_gpa)

    if max_gpa is not None:
        stmt = stmt.filter(Application.gpa < max_gpa)

    # Order by GPA descending (high to low)
    stmt = stmt.order_by(desc(Application.gpa))

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



@application_router.get("/download/{application_id}")
async def download_application_pdf(
    application_id: int,
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db)
):
    if application_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ariza ID musbat butun son bo'lishi kerak"
        )

    stmt = select(Application).where(
        Application.id == application_id
    )
    result = await db.execute(stmt)
    application = result.scalars().first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ariza topilmadi"
        )

    if not os.path.exists(application.filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fayl tizimida ariza topilmadi"
        )

    return FileResponse(
        path=application.filepath,
        media_type="application/pdf",
        filename=os.path.basename(application.filepath)
    )


@application_router.get("/search")
async def generic_search(
    full_name: Optional[str] = None,
    student_id_number: Optional[str] = Query(None, description="Student ID number"),
    faculty: Optional[str] = Query(None, description="Faculty name"),
    group: Optional[str] = Query(None, description="Student group"),
    specialty: Optional[str] = Query(None, description="Specialty from user model"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker("admin")),
):
    filters = []

    # Filter Application fields
    if full_name:
        filters.append(Application.full_name.ilike(f"%{full_name}%"))
    if student_id_number:
        filters.append(Application.student_id_number.ilike(f"%{student_id_number}%"))
    if faculty:
        filters.append(Application.faculty.ilike(f"%{faculty}%"))
    if group:
        filters.append(Application.group.ilike(f"%{group}%"))

    # Filter by User.specialty
    if specialty:
        filters.append(User.specialty.ilike(f"%{specialty}%"))

    if not filters:
        raise HTTPException(status_code=400, detail="At least one search parameter is required")

    stmt = (
        select(Application)
        .join(User, Application.user_id == User.id)
        .options(joinedload(Application.user))  # optional: eager load user if needed
        .where(and_(*filters))
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    applications = result.scalars().all()

    if not applications:
        raise HTTPException(status_code=404, detail="No applications found")

    return applications



@application_router.delete("/{application_id}")
async def delete_application(
    application_id: int,
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Autentifikatsiya qilingan talaba uchun ariza ID bo'yicha o'chirish."""
    if application_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ariza ID musbat butun son bo'lishi kerak"
        )

    stmt = select(Application).where(
        Application.id == application_id,
    )
    result = await db.execute(stmt)
    application = result.scalars().first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ariza topilmadi"
        )

    try:
        await db.delete(application)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ariza o'chirishda xatolik yuz berdi"
        )

    return {"message": "Ariza muvaffaqiyatli o'chirildi"}


@application_router.post('/download')
async def download_user_info(
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Application)
        .options(selectinload(Application.user))  # Ensure Application has a `user` relationship
    )
    result = await db.execute(stmt)
    applications = result.scalars().all()

    # Create Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Applications"

    # Write header row
    ws.append([
        "Application ID",
        "Full Name",
        "Group",
        "Specialty",
        "GPA",
        "Student ID Number",
        "Education Type",
        "Date"
    ])

    # Write data rows
    for app in applications:
        user = app.user
        if user:
            ws.append([
                app.id,
                user.full_name,
                user.group,
                user.specialty,
                app.gpa,
                user.student_id_number,
                user.education_type,
                app.create_date  
            ])

    # Save to memory
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    # Return Excel file
    return StreamingResponse(
        file_stream,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": "attachment; filename=all_applications.xlsx"}
    )



@application_router.post("/grade/{user_id}")
async def user_grade(
    user_id: int,
    grade: int,
    _ : User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Application).where(Application.user_id == user_id)
    result = await db.execute(stmt)
    application_data = result.scalars().first()

    if not application_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    application_data.grade = grade

    await db.commit()  
    await db.refresh(application_data)

    return application_data
