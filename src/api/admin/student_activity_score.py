from fastapi import APIRouter , Depends , HTTPException , status
from src.utils.auth import RoleChecker
from src.models import User , StudentActivityScore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.student_activity_scores import StudentActivityScoreUpdate
from sqlalchemy.exc import SQLAlchemyError
from src.core.base import get_db

student_activity_scores_router = APIRouter()




@student_activity_scores_router.get("/get_by_id/{student_activity_score_id}")
async def student_activity_scores_create(
    student_activity_score_id: int,
    current_user: User = Depends(RoleChecker("admin")),
    db : AsyncSession = Depends(get_db)
):
    stmt = select(StudentActivityScore).where(StudentActivityScore.user_id == current_user.id , StudentActivityScore.id == student_activity_score_id)
    result = await db.execute(stmt)
    user_data = result.scalars().first()
    if user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student activity score"
        )
    return user_data



@student_activity_scores_router.get("/get_all")
async def student_activity_scores_create(
    current_user: User = Depends(RoleChecker("admin")),
    db : AsyncSession = Depends(get_db)
):
    stmt = select(StudentActivityScore).where(StudentActivityScore.user_id == current_user.id)
    result = await db.execute(stmt)
    user_data = result.scalars().all()
    if user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student activity score"
        )
    return user_data



@student_activity_scores_router.put("/update/{student_activity_score_id}")
async def student_activity_scores_create(
    student_activity_score_id: int,
    obj_in: StudentActivityScoreUpdate,
    current_user: User = Depends(RoleChecker("admin")),
    db : AsyncSession = Depends(get_db)
):
        try:
            stmt = select(StudentActivityScore).where(StudentActivityScore.id == student_activity_score_id)
            result = await db.execute(stmt)
            db_obj = result.scalars().first()
            if not db_obj:
                return None
            for key, value in obj_in.model_dump(exclude_unset=True).items():
                if value is None or value == "" or value == "string":
                    continue
                setattr(db_obj, key, value)
            await db.commit()
            return db_obj
        except SQLAlchemyError as e:
            await db.rollback()
            raise e



@student_activity_scores_router.delete("/delete{student_activity_score_id}")
async def student_activity_scores_create():
    return



