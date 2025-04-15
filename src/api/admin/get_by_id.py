from fastapi import APIRouter , Depends , HTTPException , status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db
from sqlalchemy.future import select
from src.models.user import User


get_router = APIRouter()


@get_router.get("/get-by-id")
async def get_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@get_router.get("/get-all")
async def get_all(
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).limit(25)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return users


