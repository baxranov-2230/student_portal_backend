from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from src.core.base import get_db
from src.models import User

application_router = APIRouter()


@application_router.get('/user_detail/{user_id}')
async def application_detail(user_id: int,
                          db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(user_id == User.id))
    user = result.scalars().one_or_none()
    return user