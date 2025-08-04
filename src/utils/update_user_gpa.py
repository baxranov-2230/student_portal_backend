from fastapi import  HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from src.models.user import User
from src.models.application import Application
from src.utils.auth import fetch_user_data

async def user_gpa_update(token: str, user_id: int, db: AsyncSession):
    user_response = await fetch_user_data(token=token)

    avg_gpa = user_response.get("avg_gpa")

    if avg_gpa is None:
        raise HTTPException(status_code=400, detail="GPA not found in response")

    
    stmt_user = (
        update(User)
        .where(
            User.id == user_id,
            User.level == "1-kurs"
        )
        .values(gpa=str(avg_gpa))
    )
    await db.execute(stmt_user)

    # Then update Application table
    stmt_app = (
        update(Application)
        .where(Application.user_id == user_id)
        .values(gpa=avg_gpa)
    )
    await db.execute(stmt_app)

    await db.commit()
