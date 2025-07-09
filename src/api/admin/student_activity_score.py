from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.schemas.student_activity_scores import StudentActivityScoreUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.auth import RoleChecker
from src.models import User, StudentActivityScore
from src.core.base import get_db
from sqlalchemy.exc import SQLAlchemyError

student_activity_scores_router = APIRouter(prefix="/student_activity_scores")


@student_activity_scores_router.post("/create", status_code=status.HTTP_200_OK)
async def create_or_update_student_activity_scores(
    student_activity: StudentActivityScoreUpdate,
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Check if score already exists for this student
        stmt = select(StudentActivityScore).where(StudentActivityScore.user_id == student_activity.student_id)
        result = await db.execute(stmt)
        existing_score = result.scalar_one_or_none()

        if existing_score:
            # Update existing record
            for field, value in student_activity.model_dump(exclude_unset=True).items():
                setattr(existing_score, field, value)
            await db.commit()
            await db.refresh(existing_score)
            return {"detail": "Student activity score updated", "data": existing_score}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@student_activity_scores_router.get("/get_by_id/{student_activity_score_id}")
async def get_student_activity_score_by_id(
    student_activity_score_id: int,
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db)
):
    return 



@student_activity_scores_router.get("/get_all")
async def get_all_student_activity_scores(
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db)
):
    return 



@student_activity_scores_router.put("/update/{student_activity_score_id}")
async def update_student_activity_score(
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db),
):
    return
 



@student_activity_scores_router.delete("/delete/{student_activity_score_id}")
async def delete_student_activity_score(
    student_activity_score_id: int,
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db),
):
    return
