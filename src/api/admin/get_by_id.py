from fastapi import APIRouter , Depends , HTTPException , status , Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db
from sqlalchemy.future import select
from src.models.user import User
from src.models.user_gpa import UserGpa



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
    min_gpa: float = Query(None),
    limit: int = Query(25 , ge=1),
    offset: int = Query(0 , ge=0),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).join(UserGpa , User.id == UserGpa.user_id)

    if min_gpa is not None:
        stmt = stmt.where(UserGpa.gpa >= min_gpa)

    stmt = stmt.order_by(UserGpa.gpa.desc())

    stmt = stmt.offset(offset).limit(limit=limit)

    result = await db.execute(stmt)
    user = result.scalars().all()

    return user


