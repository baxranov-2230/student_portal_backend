from fastapi import APIRouter , Depends , HTTPException , status , Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db
from sqlalchemy.future import select
from src.models.user import User
from src.models.user_gpa import UserGpa
from src.models.user_subject import UserSubject
from sqlalchemy import select



get_router = APIRouter()


@get_router.get("/get-by-id/{user_id}")
async def get_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"


        )
    
    stmt = select(UserSubject).where(UserSubject.user_id == user.id)
    result = await db.execute(stmt)
    user_subjects = result.scalars().all()

    return {
            "id": user.id,
            "studentStatus": user.studentStatus,
            "semester": user.semester,
            "educationForm": user.educationForm,
            "address": user.address,
            "educationType": user.educationType ,
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
            "subjects": [{
                "subject":  user_subject.subject_name,
                "gade": user_subject.grade,
                "subjec_code": user_subject.semester_code
            } for user_subject in user_subjects]
            }


@get_router.get("/get-all")
async def get_all(
    min_gpa: float = Query(None),
    limit: int = Query(25, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
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
