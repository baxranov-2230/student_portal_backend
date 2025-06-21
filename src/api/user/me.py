from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.base import settings
from src.core.base import get_db
from src.utils.main_crud import get_user
from src.utils.auth import oauth2_scheme
from src.models.user_subject import UserSubject
from src.models.user_gpa import UserGpa
import jwt


me_router = APIRouter()


@me_router.get("/me")
async def get_info(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            settings.ACCESS_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True},
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: username not found",
            )

        user = await get_user(db=db, username=username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        stmt = select(UserSubject).where(UserSubject.user_id == user.id)
        result = await db.execute(stmt)
        user_subjects = result.scalars().all()

        stmt_gpa = select(UserGpa).where(UserGpa.user_id == user.id)
        result_gpa = await db.execute(stmt_gpa)
        user_gpa = result_gpa.scalars().first()


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
            "passport_pin": user.passport_pin,
            "passport_number": user.passport_number,
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
            "gpa" : user_gpa.gpa,
            "subjects": [
                {
                    "subject": user_subject.subject_name,
                    "gade": user_subject.grade,
                    "subjec_code": user_subject.semester_code,
                }
                for user_subject in user_subjects
            ],
        }

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}"
        )
