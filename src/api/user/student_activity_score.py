from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File , Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.utils.auth import RoleChecker
from src.utils.file_work import save_uploaded_file
from src.models import User, StudentActivityScore
from src.core.base import get_db

student_activity_scores_router = APIRouter(prefix="/student_activity_scores")

# Helper function
async def get_path(file: UploadFile):
    return await save_uploaded_file(file) if file else None

# CREATE
@student_activity_scores_router.post("/create")
async def create_student_activity_scores(
    academic_performance: str = Form(...),
    reading_culture: UploadFile = File(None),
    five_initiatives: UploadFile = File(None),
    discipline_compliance: UploadFile = File(None),
    competition_achievements: UploadFile = File(None),
    attendance_punctuality: UploadFile = File(None),
    enlightenment_lessons: UploadFile = File(None),
    volunteering: UploadFile = File(None),
    cultural_visits: UploadFile = File(None),
    healthy_lifestyle: UploadFile = File(None),
    other_spiritual_activity: UploadFile = File(None),
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentActivityScore).where(StudentActivityScore.user_id == current_user.id)
    result = await db.execute(stmt)
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Siz allaqchon ariza yuborgansiz!! Boshqa ma'lumot qo'shish uchun o'zgartirish qilib qo'shing "
        )

    new_score = StudentActivityScore(
        user_id=current_user.id,
        academic_performance_path=academic_performance,
        reading_culture_path=await get_path(reading_culture),
        five_initiatives_path=await get_path(five_initiatives),
        discipline_compliance_path=await get_path(discipline_compliance),
        competition_achievements_path=await get_path(competition_achievements),
        attendance_punctuality_path=await get_path(attendance_punctuality),
        enlightenment_lessons_path=await get_path(enlightenment_lessons),
        volunteering_path=await get_path(volunteering),
        cultural_visits_path=await get_path(cultural_visits),
        healthy_lifestyle_path=await get_path(healthy_lifestyle),
        other_spiritual_activity_path=await get_path(other_spiritual_activity),
    )

    db.add(new_score)
    await db.commit()
    await db.refresh(new_score)

    return {"message": "Ma'lumotlar saqlandi", "data": new_score}


# GET BY ID
@student_activity_scores_router.get("/get_by_id/{student_activity_score_id}")
async def get_student_activity_score_by_id(
    student_activity_score_id: int,
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentActivityScore).where(
        StudentActivityScore.id == student_activity_score_id,
        StudentActivityScore.user_id == current_user.id
    )
    result = await db.execute(stmt)
    data = result.scalars().first()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ma'lumot topilmadi"
        )

    return data


# GET ALL
@student_activity_scores_router.get("/get_all")
async def get_all_student_activity_scores(
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentActivityScore).where(StudentActivityScore.user_id == current_user.id)
    result = await db.execute(stmt)
    all_data = result.scalars().all()
    return all_data


# UPDATE
@student_activity_scores_router.put("/update/{student_activity_score_id}")
async def update_student_activity_score(
    student_activity_score_id: int,
    reading_culture: UploadFile = File(None),
    five_initiatives: UploadFile = File(None),
    discipline_compliance: UploadFile = File(None),
    competition_achievements: UploadFile = File(None),
    attendance_punctuality: UploadFile = File(None),
    enlightenment_lessons: UploadFile = File(None),
    volunteering: UploadFile = File(None),
    cultural_visits: UploadFile = File(None),
    healthy_lifestyle: UploadFile = File(None),
    other_spiritual_activity: UploadFile = File(None),
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db),
):
    try:
        stmt = select(StudentActivityScore).where(
            StudentActivityScore.id == student_activity_score_id,
            StudentActivityScore.user_id == current_user.id
        )
        result = await db.execute(stmt)
        db_obj = result.scalars().first()

        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ma'lumot topilmadi"
            )

    

        # Update files if new ones are sent
        async def update_file_path(field_name: str, file: UploadFile):
            if file:
                path = await save_uploaded_file(file)
                setattr(db_obj, field_name, path)

        await update_file_path("reading_culture_path", reading_culture)
        await update_file_path("five_initiatives_path", five_initiatives)
        await update_file_path("discipline_compliance_path", discipline_compliance)
        await update_file_path("competition_achievements_path", competition_achievements)
        await update_file_path("attendance_punctuality_path", attendance_punctuality)
        await update_file_path("enlightenment_lessons_path", enlightenment_lessons)
        await update_file_path("volunteering_path", volunteering)
        await update_file_path("cultural_visits_path", cultural_visits)
        await update_file_path("healthy_lifestyle_path", healthy_lifestyle)
        await update_file_path("other_spiritual_activity_path", other_spiritual_activity)

        await db.commit()
        await db.refresh(db_obj)

        return {"message": "Ma'lumot yangilandi", "data": db_obj}

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bazaga yangilashda xatolik yuz berdi"
        )


# DELETE
@student_activity_scores_router.delete("/delete/{student_activity_score_id}")
async def delete_student_activity_score(
    student_activity_score_id: int,
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db),
):
    try:
        stmt = select(StudentActivityScore).where(
            StudentActivityScore.id == student_activity_score_id,
            StudentActivityScore.user_id == current_user.id
        )
        result = await db.execute(stmt)
        db_obj = result.scalars().first()

        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ma'lumot topilmadi"
            )

        await db.delete(db_obj)
        await db.commit()

        return {"detail": "Ma'lumot o'chirildi"}

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="O'chirishda xatolik yuz berdi"
        )



