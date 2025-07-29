from fastapi import  HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user_gpa import UserGpa
from src.utils.auth import fetch_user_data

async def user_gpa_update(token: str, user_id: int , db:AsyncSession):

    user_response = await fetch_user_data(token=token)

    # If fetch_user_data returns the full response, extract "data"

    avg_gpa = user_response.get("avg_gpa")

    if avg_gpa is None:
        raise HTTPException(status_code=400, detail="GPA not found in response")

    # Step 3: Fetch existing GPA record
    stmt = select(UserGpa).where(
        UserGpa.user_id == user_id,
        UserGpa.level == "1-kurs"  # fallback to "1-kurs"
    )

    result = await db.execute(stmt)
    user_gpa = result.scalars().first()

    if not user_gpa:
        raise HTTPException(status_code=404, detail="User GPA record not found")

    # Step 4: Update and commit GPA
    user_gpa.gpa = float(avg_gpa)
    await db.commit()
    await db.refresh(user_gpa)
    
 
