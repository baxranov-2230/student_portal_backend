from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db
from src.schemas.achievements import AchievementBase, AchievementUpdate
from src.utils.jwt_utils import get_user_from_token
from src.models.achievements import Achievement
from src.utils.main_crud import save_file, MainCrud
from datetime import date
from src.utils.auth import oauth2_scheme

achievement_router = APIRouter(prefix="/achievement")

main_crud = MainCrud(model=Achievement)


@achievement_router.post("/create")
async def create(
    type: str,
    award_date: date,
    title: str,
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    user_data = await get_user_from_token(db=db, token=token)
    saved_file_path = await save_file(file=file)
    achievement_data = AchievementBase(
        user_id=user_data.id,
        title=title,
        award_date=award_date,
        type=type,
        file_path=saved_file_path,
    )

    return await main_crud.create(db=db, obj_in=achievement_data)


@achievement_router.get("/get/{achievement_id}")
async def get_by_id(
    achievement_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    user_data = await get_user_from_token(db=db, token=token)
    return await main_crud.get(db=db, id=achievement_id, user_id=user_data.id)


@achievement_router.get("/get-all")
async def get_all(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    user_data = await get_user_from_token(db=db, token=token)
    return await main_crud.get_all(db=db, user_id=user_data.id)


@achievement_router.put("/update/{achievement_id}")
async def update(
    achievement_id: int,
    type: str | None = None,
    award_date: date | None = None,
    title: str | None = None,
    file: UploadFile = File(None),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if file:
        new_documation = await save_file(file=file)

        update_data = AchievementUpdate(
            type=type, title=title, award_date=award_date, file_path=new_documation
        )
    else:
        update_data = AchievementUpdate(
            type=type,
            title=title,
            award_date=award_date,
        )
    user_data = await get_user_from_token(db=db, token=token)
    return await main_crud.update(
        db=db, id=achievement_id, user_id=user_data.id, obj_in=update_data
    )


@achievement_router.delete("/delete/{achievement_id}")
async def delete(
    achievement_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    user_data = await get_user_from_token(db=db, token=token)
    await main_crud.delete(db=db, id=achievement_id, user_id=user_data.id)
    return {"message": "Delete successfuly"}
