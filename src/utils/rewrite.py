from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, update
import httpx

from src.core.config import settings
from src.models.user import User
from src.core.base import get_db

API_URL = "https://student.ndki.uz/rest/v1/data/student-list"
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {settings.ADMIN_KEY}"
}

async def fetch_student_data(student_id: str) -> dict:
    params = {"search": student_id}
    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL, params=params, headers=HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch student data")

        items = response.json().get("data", {}).get("items", [])
        if not items:
            raise HTTPException(status_code=404, detail="Student not found")

        return items[0]

def map_student_data(student: dict) -> dict:
    return {
        "student_status": student.get("studentStatus", {}).get("name"),
        "education_form": student.get("educationForm", {}).get("name"),
        "education_type": student.get("educationType", {}).get("name"),
        "payment_form": student.get("paymentForm", {}).get("name"),
        "education_lang": student.get("group", {}).get("educationLang", {}).get("name"),
        "avg_gpa": student.get("avg_gpa")
    }

async def get_all_students(db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(
        or_(
            User.student_status == None,
            User.education_form == None,
            User.education_type == None,
            User.payment_form == None,
            User.education_lang == None,
            User.gpa == None,
        )
    )
    result = await db.execute(stmt)
    users = result.scalars().all()

    updated_count = 0

    for user in users:
        try:
            student_data = await fetch_student_data(user.student_id_number)
            mapped = map_student_data(student_data)

            stmt = (
                update(User)
                .where(User.id == user.id)
                .values(
                    student_status = mapped["student_status"],
                    education_form = mapped["education_form"],
                    education_type = mapped["education_type"],
                    payment_form = mapped["payment_form"],
                    education_lang = mapped["education_lang"],
                    gpa = str(mapped["avg_gpa"])
                )
            )
            await db.execute(stmt)
            updated_count += 1

        except HTTPException as e:
            print(f"Failed for {user.student_id_number}: {e.detail}")
            continue

    await db.commit()
    return {"updated_users": updated_count}


