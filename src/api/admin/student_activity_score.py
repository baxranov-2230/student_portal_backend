from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.student_activity_scores import StudentActivityScoreUpdate
from src.utils.auth import RoleChecker
from src.models import User, StudentActivityScore, Application
from src.core.base import get_db
from openpyxl import Workbook
from fastapi.responses import StreamingResponse
from io import BytesIO


student_activity_scores_router = APIRouter(prefix="/student_activity_scores")

@student_activity_scores_router.post("/grant_type")
async def grant_type(
    user_id: int,
    grant_type: str, 
    _: User = Depends(RoleChecker(["manager", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Application).where(Application.user_id == user_id)
    result = await db.execute(stmt)
    application_data = result.scalars().first()

    if not application_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    application_data.grant_type = grant_type 
    db.add(application_data)
    await db.commit()
    await db.refresh(application_data)

    return {"message": "Successfully updated grant type"}

@student_activity_scores_router.patch("/give_grade/{user_id}" , tags=["Manager"])
async def give_grade(
    user_id: int,
    grade_data: StudentActivityScoreUpdate,
    _: User = Depends(RoleChecker(["manager","admin"])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentActivityScore).where(StudentActivityScore.user_id == user_id)
    result = await db.execute(stmt)
    activity_score = result.scalars().first()

    if not activity_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"StudentActivityScore with ID {user_id} not found"
        )

    # Update only fields that are not None
    for field, value in grade_data.model_dump(exclude_unset=True).items():
        setattr(activity_score, field, value)

    try:
        await db.commit()
        await db.refresh(activity_score)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update grade: {str(e)}"
        )

    return activity_score


@student_activity_scores_router.get("/get_by_id/{user_id}" , tags=["Manager"])
async def get_activity_by_id(
    user_id: int,
    _: User = Depends(RoleChecker(["manager","admin"])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentActivityScore).where(StudentActivityScore.user_id == user_id)
    result = await db.execute(stmt)
    user_data = result.scalars().first()
    
    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity score not found")
    
    return user_data

@student_activity_scores_router.get("/get_all" , tags=["Manager"])
async def get_all_activity_scores(
    _: User = Depends(RoleChecker(["manager","admin"])),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentActivityScore)
    result = await db.execute(stmt)
    all_data = result.scalars().all()
    
    return all_data


@student_activity_scores_router.get("/download_excel/")
async def download_user_info(
    current_user: User = Depends(RoleChecker("admin")),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(StudentActivityScore)
        .options(
            selectinload(StudentActivityScore.user)
            .selectinload(User.application)  # nested loading
        )
    )
    result = await db.execute(stmt)
    activity_scores = result.scalars().all()

    # Create Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Student Activity Scores"

    # Write header row
    ws.append([
        "Score ID",
        "Full Name",
        "Group",
        "Specialty",
        "GPA",
        "Student ID Number",
        "Education Type",
    ])

    # Write data rows
    for score in activity_scores:
        user = score.user
        application = user.application if user else None
        if user and application:
            ws.append([
                score.id,
                user.full_name,
                user.group,
                user.specialty,
                application[0].gpa,
                user.student_id_number,
                user.educationType,
            ])

    # Save to memory
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    # Return Excel file
    return StreamingResponse(
        file_stream,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": "attachment; filename=student_activity_scores.xlsx"}
    )

