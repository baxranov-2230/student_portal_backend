from fastapi import APIRouter , Depends , HTTPException , status
from src.utils.auth import RoleChecker
from src.models import User , StudentActivityScore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.student_activity_scores import StudentActivityScoreUpdate
from sqlalchemy.exc import SQLAlchemyError
from src.schemas.student_activity_scores import StudentActivityScoreCreate 
from src.core.base import get_db

student_activity_scores_router = APIRouter(
    prefix="/student_activity_scores"
)


@student_activity_scores_router.post("/create")
async def create_student_activity_scores(
    current_user: User = Depends(RoleChecker("student")),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentActivityScore).where(StudentActivityScore.user_id == current_user.id)
    result = await db.execute(stmt)
    user_data = result.scalars().first()
    if user_data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu allaqachon yaratilgan"
        )
    new_activity = StudentActivityScore(
        user_id = current_user.id,
        reading_culture = "0",
        five_initiatives = "0",
        academic_performance = "0",
        discipline_compliance = "0",
        competition_achievements = "0",
        attendance_punctuality = "0",
        enlightenment_lessons = "0",
        volunteering = "0",
        cultural_visits = "0",
        healthy_lifestyle = "0",
        other_spiritual_activity = "0",
    )
    db.add(new_activity)
    await db.commit()
    await db.refresh(new_activity)
    return new_activity

@student_activity_scores_router.get("/get_by_id/{student_activity_score_id}")
async def get_student_activity_score_by_id(
    student_activity_score_id: int,
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentActivityScore).where(
        StudentActivityScore.user_id == current_user.id,
        StudentActivityScore.id == student_activity_score_id
    )
    result = await db.execute(stmt)
    user_data = result.scalars().first()

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student activity score not found"
        )

    return user_data



@student_activity_scores_router.get("/get_all")
async def get_all_student_activity_scores(
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentActivityScore).where(StudentActivityScore.user_id == current_user.id)
    result = await db.execute(stmt)
    user_data = result.scalars().all()

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No student activity scores found"
        )

    return user_data



@student_activity_scores_router.put("/update/{student_activity_score_id}")
async def update_student_activity_score(
    student_activity_score_id: int,
    obj_in: StudentActivityScoreUpdate,
    current_user: User = Depends(RoleChecker("admin")),
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
                detail="Student activity score not found"
            )

        for key, value in obj_in.model_dump(exclude_unset=True).items():
            if value in [None, "", "string"]:
                continue
            setattr(db_obj, key, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating"
        )



@student_activity_scores_router.delete("/delete/{student_activity_score_id}")
async def delete_student_activity_score(
    student_activity_score_id: int,
    current_user: User = Depends(RoleChecker("admin")),
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
                detail="Student activity score not found"
            )

        await db.delete(db_obj)
        await db.commit()
        return {"detail": "Student activity score deleted successfully"}

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete student activity score"
        )



