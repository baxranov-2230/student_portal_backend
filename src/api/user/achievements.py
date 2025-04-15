from fastapi import APIRouter , Depends , UploadFile , File , Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db
from src.schemas.achievements import AchievementBase , AchievementUpdate
from src.utils.jwt_utils import decode_token
from src.models.achievements import Achievement
from src.utils.main_crud import save_file , MainCrud
from datetime import date


achievement_router = APIRouter(
    prefix="/achievement"
)

main_crud = MainCrud(model=Achievement)

@achievement_router.post("/create")
async def create(
    request: Request,
    type: str,
    award_date: date,
    title: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    saved_file_path = await save_file(file=file)
    achievement_data = AchievementBase(
        user_id=user_data.id,
        title=title,
        award_date=award_date,
        type=type,
        file_path=saved_file_path
    )

    return await main_crud.create(db=db , obj_in=achievement_data)


@achievement_router.get('/get/{id}')
async def get_by_id(
    id: int,
    request: Request,
    db:AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    return await main_crud.get(db=db , id=id , user_id=user_data.id)


@achievement_router.get("/get-all")
async def get_all(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    return await main_crud.get_all(db=db , user_id=user_data.id)

@achievement_router.put("/update/{id}")
async def update(
    id: int,
    type: str| None = None,
    award_date: date | None = None,
    title: str | None = None,
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    if file:
        new_documation = await save_file(file=file)
    
        update_data = AchievementUpdate(
                type=type,
                title=title,
                award_date=award_date,
                file_path=new_documation
            )
    else:
        update_data = AchievementUpdate(
                type=type,
                title=title,
                award_date=award_date,
            )
    return await main_crud.update(db=db , id=id , obj_in=update_data)

@achievement_router.delete("/delete/{id}")
async def delete(
    id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    await main_crud.delete(db=db , id=id , user_id=user_data.id)
    return {"message": "Delete successfuly"}