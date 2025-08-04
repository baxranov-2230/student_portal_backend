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




        response_data = {
            "id": user.id,
            "student_status": user.student_status,
            "semester": user.semester,
            "education_form": user.education_form,
            "address": user.address,
            "education_type": user.education_type,
            "last_name": user.last_name,
            "phone": user.phone,
            "payment_form": user.payment_form,
            "first_name": user.first_name,
            "group": user.group,
            "third_name": user.third_name,
            "student_id_number": user.student_id_number,
            "gender": user.gender,
            "education_lang": user.education_lang,
            "full_name": user.full_name,
            "image_path": user.image_path,
            "university": user.university,
            "faculty": user.faculty,
            "birth_date": user.birth_date,
            "specialty": user.specialty,
            "level": user.level,
            "gpa": user.gpa,
            "subjects": [
                {
                    "subject": user_subject.subject_name,
                    "grade": user_subject.grade,
                    "subjec_code": user_subject.semester_code,
                }
                for user_subject in user_subjects
            ],
        }

        if user.passport_pin:
            response_data["passport_pin"] = user.passport_pin

        if user.passport_number:
            response_data["passport_number"] = user.passport_number

        return response_data

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}"
        )
