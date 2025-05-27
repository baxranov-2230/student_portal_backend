from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db
from sqlalchemy.future import select
from src.models.user import User
from src.models.user_gpa import UserGpa
from src.models.user_subject import UserSubject
from sqlalchemy import select
from src.utils.auth import *


get_router = APIRouter()

@get_router.get("/get-by-id/{user_id}")
async def get_by_id(
    user_id: int,
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db),
):
    # Fetch the user by ID
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Fetch the user's subjects
    stmt = select(UserSubject).where(UserSubject.user_id == user.id)
    result = await db.execute(stmt)
    user_subjects = result.scalars().all()

    # Fetch the user's GPA (corrected to use user.id instead of current_user.id)
    query = select(UserGpa).where(UserGpa.user_id == user.id)
    result = await db.execute(query)
    user_gpa = result.scalars().first()

    # Handle case where GPA is not found
    gpa = user_gpa.gpa if user_gpa else None  # or use 0.0, or raise an exception

    return {
        "id": user.id,
        "studentStatus": user.studentStatus,
        "semester": user.semester,
        "educationForm": user.educationForm,
        "address": user.address,
        "educationType": user.educationType,
        "last_name": user.last_name,
        "phone": user.phone,
        "paymentForm": user.paymentForm,
        "first_name": user.first_name,
        "group": user.group,
        "third_name": user.third_name,
        "student_id_number": user.student_id_number,
        "gender": user.gender,
        "educationLang": user.educationLang,
        "full_name": user.full_name,
        "image_path": user.image_path,
        "university": user.university,
        "faculty": user.faculty,
        "birth_date": user.birth_date,
        "specialty": user.specialty,
        "level": user.level,
        "gpa": gpa,  # Use the safely handled GPA value
        "subjects": [
            {
                "subject": user_subject.subject_name,
                "gade": user_subject.grade,  # Note: Fix typo "gade" to "grade"
                "subject-code": user_subject.semester_code,  # Fix typo "subjec-code"
            }
            for user_subject in user_subjects
        ],
    }

@get_router.get("/get-all")
async def get_all(
    min_gpa: float = Query(None),
    limit: int = Query(25, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker("admin")),
):
    stmt = select(User, UserGpa.gpa).join(UserGpa, User.id == UserGpa.user_id)
    if min_gpa is not None:
        stmt = stmt.where(UserGpa.gpa >= min_gpa)
    stmt = stmt.order_by(UserGpa.gpa.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "group": user.group,
            "gpa": gpa,
        }
        for user, gpa in rows
    ]
