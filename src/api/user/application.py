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

from src.schemas.application import ApplicationCreateResponse 
import os
from src.utils.pdf_generator import generate_acceptance_pdf , generate_rejection_pdf ,  generate_application_pdf , generate_filename

application_router = APIRouter(prefix="/application")

@application_router.post("/create", response_model=ApplicationCreateResponse)
async def create_application(
    special_field: bool | None = False,
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    stmt_app = select(Application).where(Application.user_id == current_user.id)
    result_app = await db.execute(stmt_app)
    existing_application = result_app.scalars().first()

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Siz allaqachon ariza topshirgansiz"
        )
    # Check for GPA data
    stmt = select(UserGpa).where(
        UserGpa.user_id == current_user.id,
        # UserGpa.level == "1-kurs"
    )
    result = await db.execute(stmt)
    user_gpa = result.scalars().first()

    if not user_gpa or user_gpa.gpa is None:
        raise HTTPException(
            status_code=404,
            detail="Foydalanuvchi uchun GPA ma'lumotlari topilmadi"
        )

    # Validate education year
    try:
        start_year = int(user_gpa.educationYear.split("-")[0])
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail="Ta'lim yili formati noto'g'ri"
        )

    if start_year < 2024:
        raise HTTPException(
            status_code=400,
            detail="Arizalar faqat 2024 yoki undan keyingi ta'lim yillari uchun qabul qilinadi"
        )

    # Prepare file paths
    upload_dir = "uploads/"
    os.makedirs(upload_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # 202506231904
    filename = f"user_{current_user.full_name.replace(' ', '_')}_{timestamp}.pdf"
    filepath = os.path.join(upload_dir, filename)

    # Generate initial application PDF
    generate_application_pdf(filepath=filepath, user=current_user, gpa=user_gpa.gpa)

    # Determine response type and generate appropriate PDF
    if user_gpa.gpa < 3.5:
        generated_filename = generate_filename(prefix="rejection", extension="pdf")
        rejection_filepath = os.path.join(upload_dir, generated_filename)
        generate_rejection_pdf(filepath=rejection_filepath, user=current_user, gpa=user_gpa.gpa)
        response_file_path = rejection_filepath
    else:
        generated_filename = generate_filename(prefix="acceptance", extension="pdf")
        acceptance_filepath = os.path.join(upload_dir, generated_filename)
        generate_acceptance_pdf(filepath=acceptance_filepath, user=current_user, gpa=user_gpa.gpa)
        response_file_path = acceptance_filepath

    # Create Application entry
    new_application = Application(
        user_id=current_user.id,
        full_name=current_user.full_name,
        student_id_number=current_user.student_id_number,
        image_path=current_user.image_path,
        group=current_user.group,
        faculty=current_user.faculty,
        gpa=user_gpa.gpa,
        filepath=filepath,
        special_field = special_field,
        reponse_file=response_file_path,
        create_date=datetime.now().replace(microsecond=0)
    )

    # Save to database
    try:
        db.add(new_application)
        await db.commit()
        await db.refresh(new_application)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ariza yaratishda xatolik yuz berdi: {str(e)}"
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



@application_router.get("/get_all", response_model=list[ApplicationCreateResponse])
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




@application_router.put("/update_pdf")
async def update_pdf(
    special_field: bool | None = False,
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    
    stmt_app = select(Application).where(Application.user_id == current_user.id)
    result_app = await db.execute(stmt_app)
    existing_application = result_app.scalars().first()

    if not existing_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avval ariza yaratilmadi"
        )

    # Fetch GPA data
    stmt = select(UserGpa).where(UserGpa.user_id == current_user.id)
    result = await db.execute(stmt)
    user_gpa = result.scalars().first()

    if not user_gpa or user_gpa.gpa is None:
        raise HTTPException(
            status_code=404,
            detail="Foydalanuvchi uchun GPA ma'lumotlari topilmadi"
        )
        
    try:
        start_year = int(user_gpa.educationYear.split("-")[0])
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail="Ta'lim yili formati noto'g'ri"
        )

    if start_year < 2024:
        raise HTTPException(
            status_code=400,
            detail="Arizalar faqat 2024 yoki undan keyingi ta'lim yillari uchun qabul qilinadi"
        )

    # Remove old file if it exists
    old_path = existing_application.reponse_file
    if not old_path:
        raise HTTPException(
            status_code=404,
            detail="Old file path not found"
        )
    if os.path.exists(old_path):
        os.remove(old_path)

    # Prepare upload directory and filenames
    upload_dir = "uploads/"
    os.makedirs(upload_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    base_filename = f"user_{current_user.full_name.replace(' ', '_')}_{timestamp}.pdf"
    base_filepath = os.path.join(upload_dir, base_filename)

    # Generate base application PDF
    generate_application_pdf(filepath=base_filepath, user=current_user, gpa=user_gpa.gpa)

    # Decide acceptance/rejection
    is_rejected = user_gpa.gpa < 3.5
    pdf_prefix = "rejection" if is_rejected else "acceptance"
    response_filename = generate_filename(prefix=pdf_prefix, extension="pdf")
    response_filepath = os.path.join(upload_dir, response_filename)

    # Generate response-specific PDF
    generator = generate_rejection_pdf if is_rejected else generate_acceptance_pdf
    generator(filepath=response_filepath, user=current_user, gpa=user_gpa.gpa)

    # Update and persist
    existing_application.filepath = response_filepath
    existing_application.special_field = special_field
    
    await db.commit()
    await db.refresh(existing_application)
    return {"message": "Regenerate succefully"}
