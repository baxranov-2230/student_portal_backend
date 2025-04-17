from fastapi import APIRouter , Depends , UploadFile , File , Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db
from src.schemas.cert import CertBase , CertUpdate
from datetime import date
from src.models.certs import Cert
from src.utils.jwt_utils import decode_token 
from src.utils.main_crud import MainCrud , save_file


cert_router = APIRouter(
    prefix="/cert"
)

main_crud = MainCrud(model=Cert)


@cert_router.post("/create")
async def create(
    request : Request,
    language: str ,
    certificate_type: str,
    level: str,
    series_and_number: str,
    date_of_issue: date,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    saved_file_path = await save_file(file=file)
    cert_data = CertBase(
        user_id=user_data.id,
        language=language,
        certificate_type=certificate_type,
        level=level,
        series_and_number=series_and_number,
        date_of_issue=date_of_issue,
        file_path=saved_file_path
    )
    return await main_crud.create(db=db , obj_in=cert_data)


@cert_router.get('/get/{id}')
async def get_by_id(
    id: int,
    request: Request,
    db:AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    return await main_crud.get(db=db , id=id , user_id=user_data.id)

@cert_router.get("/get-all")
async def get_all(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    return await main_crud.get_all(db=db , user_id=user_data.id)

@cert_router.put("/update/{id}")
async def update(
    id: int,
    language: str  | None = None,
    certificate_type: str | None = None,
    level: str | None = None,
    series_and_number: str | None = None,
    date_of_issue: date | None = None,
    file: UploadFile = File((None)),
    db: AsyncSession = Depends(get_db)
):
    if file:
        new_documation = await save_file(file=file)

        cert_data = CertUpdate(
            language=language,
            certificate_type=certificate_type,
            level=level,
            series_and_number=series_and_number,
            date_of_issue=date_of_issue,
            file_path=new_documation
        )
    else:
        cert_data = CertUpdate(
            language=language,
            certificate_type=certificate_type,
            level=level,
            series_and_number=series_and_number,
            date_of_issue=date_of_issue,
        )
    return await main_crud.update(db=db , id=id , obj_in=cert_data)

@cert_router.delete("/delete/{id}")
async def delete(
    id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    response = request.cookies.get("jwt_token")
    user_data = await decode_token(db=db , token=response)
    await main_crud.delete(db=db , id=id , user_id=user_data.id)

    return {"message": "Delete successfully"}

    