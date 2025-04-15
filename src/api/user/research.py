from fastapi import APIRouter , Depends , UploadFile , File , Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db
from src.schemas.research import ResearchBase , ResearchUpdate 
from datetime import date
from src.utils.main_crud import MainCrud , save_file 
from src.utils.jwt_utils import decode_token
from src.models.research import Research


research_router = APIRouter(
    prefix="/research"
)

main_crud = MainCrud(model=Research)

@research_router.post("/create")
async def create(
    request: Request,
    form: str,
    pub_date: date,
    title: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    saved_file_path = await save_file(file=file)
    research_data = ResearchBase(
        user_id=user_data.id,
        title=title,
        form=form,
        pub_date=pub_date,
        file_path=saved_file_path,
    )

    return await main_crud.create(db=db , obj_in=research_data)
    

@research_router.get('/get/{id}')
async def get_by_id(
    id: int,
    request: Request,
    db:AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    return await main_crud.get(db=db , id=id , user_id=user_data.id)

@research_router.get("/get-all")
async def get_all(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    return await main_crud.get_all(db=db , user_id=user_data.id)

@research_router.put("/update/{id}")
async def update(
    id: int,
    form: str | None = None,
    pub_date: date | None = None,
    title: str | None = None,
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    if file:
        new_documantion = await save_file(file=file)

        research_data = ResearchUpdate(
            form=form,
            pub_date=pub_date,
            title=title,
            file_path=new_documantion
        )
    else:
        research_data = ResearchUpdate(
            form=form,
            pub_date=pub_date,
            title=title,
        )
    return await main_crud.update(db=db , id=id , obj_in=research_data)

@research_router.delete("/delete/{id}")
async def delete(
    id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    await main_crud.delete(db=db , id=id , user_id=user_data.id)
    return {"message": "Delete successfully"}