from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from src.core.config import settings
from src.utils.main_crud import get_user
import jwt
import asyncio


async def create_access_token(data: dict, expire_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode.update({"exp": expire})
    return await asyncio.to_thread(
        jwt.encode,
        to_encode,
        settings.ACCESS_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

async def create_refresh_token(data: dict , expire_delta: timedelta)-> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode.update({"exp": expire})
    return await asyncio.to_thread(
        jwt.encode,
        to_encode,
        settings.REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

async def refresh_access_token(refresh_token: str):
    payload = jwt.decode(
        refresh_token,
        settings.REFRESH_SECRET_KEY,
        algorithms= settings.ALGORITHM
    )

    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    new_access_token = await create_access_token(
        data={
            "sub": payload.get("sub")
        },
        expire_delta=access_token_expire
    )

    return {
            "access_token": new_access_token,
            "refresh_token": refresh_token
    }


async def get_user_from_token(db: AsyncSession , token: str):
    payload = jwt.decode(token , settings.ACCESS_SECRET_KEY , algorithms=[settings.ALGORITHM])
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username not found"
        )
    user = await get_user(db=db , username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user
