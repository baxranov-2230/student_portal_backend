from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from src.core.base import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
import asyncio
from src.core.config import settings
from src.utils.main_crud import get_user
from fastapi.responses import JSONResponse


async def create_token(data: dict, expire_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode.update({"exp": expire})
    return await asyncio.to_thread(
        jwt.encode,
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

async def refresh_access_token(refresh_token: str):
    payload = jwt.decode(
        refresh_token,
        settings.REFRESH_SECRET_KEY,
        algorithms= settings.ALGORITHM
    )

    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    new_access_token = await create_token(
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
    payload = jwt.decode(token , settings.SECRET_KEY , algorithms=[settings.ALGORITHM])
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
