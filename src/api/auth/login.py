from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends 
from fastapi.security import OAuth2PasswordRequestForm
from src.utils.auth import ( 
    authenticate_admin, 
    authenticate_user, 
    fetch_user_data, 
    map_user_data, 
    save_user_data_to_db,
    check_semester,
    fetch_user_gpa,
    map_user_gpa,
    fetch_subject,
    save_user_subject_to_db,
    save_user_gpa_to_db,
    map_subject_grades,
    # fetch_attendance,
    # map_attendance_records,
    # save_attendance_to_db,
)
from src.utils.update_user_gpa import user_gpa_update
from src.core.config import settings
from src.models.user import User
from datetime import timedelta
from src.utils.jwt_utils import create_access_token, create_refresh_token
from src.core.base import get_db

login_router = APIRouter()

@login_router.post("/login")
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    admin_data: User = await authenticate_admin(credentials=credentials, db=db)
    if admin_data:
        access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(
            {"sub": admin_data.full_name, "role": "admin"}, access_token_expire
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
    
    token = await authenticate_user(credentials=credentials)

    if token:

        user_data = await fetch_user_data(token=token)
        user_data = map_user_data(user_data)
        user_data = await save_user_data_to_db(db=db, user_data=user_data)
   

        user_id = user_data.id
        if user_id is None:
            raise ValueError("Foydalanuvchi ID si mavjud emas")


        if user_data.semester is None:
            raise ValueError("Semestr qiymati mavjud emas")
        
        semester_number = check_semester(semestr=user_data.semester)


        access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(
            {"sub": user_data.student_id_number, "role": "student"}, access_token_expire
        )
        refresh_token_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = await create_refresh_token(
            {"sub": user_data.student_id_number}, refresh_token_expire
        )

        user_gpa = await fetch_user_gpa(token=token)

        user_gpa_list = map_user_gpa(user_gpa)  # returns list of dicts
        await save_user_gpa_to_db(db=db, user_id=user_id, user_gpa_list=user_gpa_list)
        
        await user_gpa_update(db=db, user_id=user_id , token=token)
        print("User GPA updated successfully")
        
        
        


        subject_data = []
        # attendance_data = []
        for i in range(11, semester_number + 1):
            user_subjects = await fetch_subject(token=token, semester=i)
            user_subjects = map_subject_grades(api_data=user_subjects)
            subject_data.extend(user_subjects)

            # user_attendance = await fetch_attendance(token=token , semester_code=i)
            # user_attendance = map_attendance_records(api_data=user_attendance)
            # attendance_data.extend(user_attendance)


        
        await save_user_subject_to_db(
            db=db, user_id=user_id, user_subjects=subject_data
        )

        # await save_attendance_to_db(
        #     db=db , user_id=user_id , user_attendance=attendance_data
        # )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
