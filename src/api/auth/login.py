from fastapi import APIRouter, Depends, Response
from src.utils.auth import *
from datetime import *
from src.utils.jwt_utils import access_token_create
from src.schemas.user import LoginRequest
from src.core.base import get_db

login_router = APIRouter()


@login_router.post("/login")
async def login(
        credentials: LoginRequest,
        response: Response,
        db: AsyncSession = Depends(get_db)
):
    token = await authenticate_user(credentials=credentials)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        max_age=86400,
    )

    user_data = await fetch_user_data(token=token)
    user_data = map_user_data(user_data)
    user_data = await save_user_data_to_db(db=db, user_data=user_data)
    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    jwt_token = await access_token_create(
        {
            "sub": user_data.student_id_number
        },
        access_token_expire
    )

    response.set_cookie(
        key="jwt_token",
        value=jwt_token,
        httponly=False,
        max_age=int(access_token_expire.total_seconds())
    )

    user_gpa = await fetch_user_gpa(token=token)
    user_gpa = map_user_gpa(user_gpa)
    await save_user_gpa_to_db(db=db, user_id=user_data.id, user_gpa=user_gpa)

    return {
        "user_id": user_data.id,
            "message": "Loggened succesfuly"}
