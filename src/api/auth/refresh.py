from fastapi import APIRouter , Request , Response , Depends , HTTPException , status
from fastapi.responses import JSONResponse
from src.core.base import get_db
from src.utils.jwt_utils import decode_token
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.jwt_utils import access_token_create , create_refresh_token
from datetime import timedelta
from src.core.config import settings


refresh_router = APIRouter()


@refresh_router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    try:
        
        token_data = await decode_token(db, refresh_token)
        user = token_data["user"]

        
        access_token = await access_token_create(
            data={"sub": user.student_id_number},
            expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        
        new_refresh_token = await create_refresh_token(
            data={"sub": user.student_id_number},
            expire_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        return JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer"
            },
            status_code=status.HTTP_200_OK
        )

    except HTTPException:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        raise
    except Exception as e:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )