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





async def access_token_create(data: dict, expire_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = await asyncio.to_thread(
        jwt.encode,
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt

async def create_refresh_token(data: dict, expire_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return await asyncio.to_thread(
        jwt.encode,
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

async def decode_token(db: AsyncSession, token: str):
    try:
        payload = await asyncio.to_thread(
            jwt.decode,
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )
        
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: username not found"
            )

        user = await get_user(db=db, username=username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return {
            "user": user,
            "expiration_time": datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        }
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

async def get_current_user_from_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    jwt_token = request.cookies.get("access_token")
    if not jwt_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing"
        )
    
    token_data = await decode_token(db, jwt_token)
    return token_data["user"]


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
