from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from sqlalchemy import select

async def save_password(db: AsyncSession , plain_password: str):
    password_save = User(
        password = plain_password
    )
    db.add(password_save)
    await db.commit()
    await db.refresh(password_save)


async def authenticate_user_from_db(db: AsyncSession , username: str , password: str):

    stmt = select(User).where(User.student_id_number == username , User.password == password)
    result = await db.execute(stmt)
    user_data = result.scalars().first()

    if not user_data:
        return None

    return  user_data