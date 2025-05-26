from fastapi import APIRouter, Depends
from src.utils.auth import *
from datetime import *
from fastapi.security import OAuth2PasswordRequestForm
from src.utils.jwt_utils import create_access_token, create_refresh_token
from src.core.base import get_db


login_router = APIRouter()


@login_router.post("/login")
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    admin_data: User = await authenticate_admin(credentials=credentials, db=db)
    token = await authenticate_user(credentials=credentials)

    if admin_data:
        access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = await create_access_token(
            {"sub": admin_data.full_name}, access_token_expire
        )

        refresh_token_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token = await create_refresh_token(
            {"sub": admin_data.full_name}, refresh_token_expire
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }


    if token:
        user_data = await fetch_user_data(token=token)
        user_data = map_user_data(user_data)
        user_data = await save_user_data_to_db(db=db, user_data=user_data)
        access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = await create_access_token(
            {"sub": user_data.student_id_number}, access_token_expire
        )

        refresh_token_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token = await create_refresh_token(
            {"sub": user_data.student_id_number}, refresh_token_expire
        )

        user_gpa = await fetch_user_gpa(token=token)
        user_gpa = map_user_gpa(user_gpa)
        await save_user_gpa_to_db(db=db, user_id=user_data.id, user_gpa=user_gpa)

        semester_number = check_semester(semestr=user_data.semester)

        subject_data = []

        for i in range(11, semester_number + 1):
            user_subjects = await fetch_subject(token=token, semester=i)
            user_subjects = map_subject_grades(api_data=user_subjects)
            subject_data.extend(user_subjects)

        await save_user_subject_to_db(
            db=db, user_id=user_data.id, user_subjects=subject_data
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
