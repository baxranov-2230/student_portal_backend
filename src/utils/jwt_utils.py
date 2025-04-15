import jwt 
from datetime import *
from src.core.config import settings
from fastapi import Request
from fastapi import HTTPException , status , Depends
from src.core.base import get_db
from src.utils.main_crud import *
import asyncio

async def access_token_create(data:dict, expire_delta:timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode.update({"exp": expire})
    encoded_jwt = await asyncio.to_thread(
        jwt.encode,
        to_encode,
        settings.SECRET_KEY,
        algorithm = settings.ALGORITHM
    )
    return encoded_jwt



async def get_current_user_from_token(
    request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        jwt_token = request.cookies.get("jwt_token")
        if not jwt_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token missing"
            )
        
        # Decode JWT with explicit verification
        payload = jwt.decode(
            jwt_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: username not found"
            )

        user = await get_user(db=db, username=username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )





async def decode_token(db: AsyncSession, token: str):
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    try:
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: username not found"
            )

        user = await get_user(db=db, username=username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

