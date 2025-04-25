from fastapi import APIRouter , Depends , Request , HTTPException , status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import settings
from src.core.base import get_db
from src.utils.main_crud import get_user
from src.utils.auth import oauth2_scheme
import jwt

me_router = APIRouter()

@me_router.get("/me")
async def get_info(
    token : str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            settings.ACCESS_SECRET_KEY,
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



    