from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db
from src.schemas.research import ResearchBase, ResearchUpdate
from datetime import date
from src.utils.main_crud import MainCrud, save_file
from src.utils.jwt_utils import get_user_from_token
from src.utils.auth import oauth2_scheme
from src.models.research import Research


research_router = APIRouter(prefix="/research")

main_crud = MainCrud(model=Research)


@research_router.post("/create")
async def create(
    form: str,
    pub_date: date,
    title: str,
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):

    user_data = await get_user_from_token(db=db, token=token)
    saved_file_path = await save_file(file=file)
    research_data = ResearchBase(
        user_id=user_data.id,
        title=title,
        form=form,
        pub_date=pub_date,
        file_path=saved_file_path,
    )

    return await main_crud.create(db=db, obj_in=research_data)


@research_router.get("/get/{research_id}")
async def get_by_id(
    research_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):

    user_data = await get_user_from_token(db=db, token=token)
    return await main_crud.get(db=db, id=research_id, user_id=user_data.id)


@research_router.get("/get_all")
async def get_all(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):

    user_data = await get_user_from_token(db=db, token=token)
    return await main_crud.get_all(db=db, user_id=user_data.id)


@research_router.put("/update/{research_id}")
async def update(
    research_id: int,
    form: str | None = None,
    pub_date: date | None = None,
    title: str | None = None,
    file: UploadFile = File(None),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if file:
        new_documantion = await save_file(file=file)

        research_data = ResearchUpdate(
            form=form, pub_date=pub_date, title=title, file_path=new_documantion
        )
    else:
        research_data = ResearchUpdate(
            form=form,
            pub_date=pub_date,
            title=title,
        )
    user_data = await get_user_from_token(db=db, token=token)
    return await main_crud.update(
        db=db, id=research_id, user_id=user_data.id, obj_in=research_data
    )


@research_router.delete("/delete/{research_id}")
async def delete(
    research_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):

    user_data = await get_user_from_token(db=db, token=token)
    await main_crud.delete(db=db, id=research_id, user_id=user_data.id)
    return {"message": "Delete successfully"}
