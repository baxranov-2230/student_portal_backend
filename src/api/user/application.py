from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.application import Application
from src.models.user import User
from src.models.user_gpa import UserGpa
from src.utils.auth import RoleChecker
from src.core.base import get_db
from typing import List
from docx import Document
from src.schemas.application import ApplicationCreateResponse , ApplicationDeleteResponse
import os
from src.utils.pdf_generator import generate_grant_pdf , generate_rejection_pdf

application_router = APIRouter(prefix="/application")

@application_router.post("/create", response_model=ApplicationCreateResponse)
async def create_application(
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(UserGpa).where(
        UserGpa.user_id == current_user.id,
        UserGpa.level == "1-kurs"
    )
    result = await db.execute(stmt)
    user_gpa = result.scalars().first()

    if not user_gpa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi uchun GPA ma'lumotlari topilmadi"
        )


    
    stmt_app = select(Application).where(Application.user_id == current_user.id)
    result_app = await db.execute(stmt_app)
    existing_application = result_app.scalars().first()

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Siz allaqachon ariza topshirgansiz"
        )
    
    try:
        start_year = int(user_gpa.educationYear.split("-")[0])
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ta'lim yili formati noto'g'ri"
        )

    if start_year < 2024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arizalar faqat 2024 yoki undan keyingi ta'lim yillari uchun qabul qilinadi"
        )
    
    
    upload_dir = "uploads/"
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"user_{current_user.full_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(upload_dir, filename)


    if user_gpa.gpa < 3.5:
        generate_rejection_pdf(filepath=filename , user=current_user , gpa=user_gpa.gpa)
    else: 
        generate_grant_pdf(filepath=filepath , user=current_user , gpa=user_gpa.gpa)


    # Create Application entry in DB
    new_application = Application(
        user_id=current_user.id,
        full_name=current_user.full_name,
        student_id_number=current_user.student_id_number,
        image_path=current_user.image_path,
        group=current_user.group,
        faculty=current_user.faculty,
        gpa=user_gpa.gpa,
        filepath=filepath,
        create_date=datetime.now().replace(microsecond=0)
    )

    try:
        db.add(new_application)
        await db.commit()
        await db.refresh(new_application)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ariza yaratishda xatolik yuz berdi: {e}"
        )

    return new_application

@application_router.get("/get_by_id/{application_id}", response_model=ApplicationCreateResponse)
async def get_application_by_id(
    application_id: int,
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):

    if application_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ariza ID musbat butun son bo'lishi kerak"
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
            detail="Ariza topilmadi"
        )

    return application

@application_router.get("/download/{application_id}")
async def download_application_pdf(
    application_id: int,
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    if application_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ariza ID musbat butun son bo'lishi kerak"
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

@application_router.get("/get_all", response_model=List[ApplicationCreateResponse])
async def get_all_applications(
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    """Autentifikatsiya qilingan talaba uchun barcha arizalarni olish."""
    stmt = select(Application).where(Application.user_id == current_user.id)
    result = await db.execute(stmt)
    applications = result.scalars().all()

    if not applications:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi uchun hech qanday ariza topilmadi"
        )

    return applications



@application_router.delete("/{application_id}", response_model=ApplicationDeleteResponse)
async def delete_application(
    application_id: int,
    current_user: User = Depends(RoleChecker("student")),
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
        Application.user_id == current_user.id
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