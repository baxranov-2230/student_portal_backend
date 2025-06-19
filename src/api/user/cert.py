from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db
from src.schemas.cert import CertBase, CertUpdate
from datetime import date
from src.models.certs import Cert
from src.utils.jwt_utils import get_user_from_token
from src.utils.auth import oauth2_scheme
from src.utils.main_crud import MainCrud, save_file


cert_router = APIRouter(prefix="/cert")

main_crud = MainCrud(model=Cert)


@cert_router.post("/create")
async def create(
    language: str,
    certificate_type: str,
    level: str,
    series_and_number: str,
    date_of_issue: date,
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):

    user_data = await get_user_from_token(db=db, token=token)
    saved_file_path = await save_file(file=file)
    cert_data = CertBase(
        user_id=user_data.id,
        language=language,
        certificate_type=certificate_type,
        level=level,
        series_and_number=series_and_number,
        date_of_issue=date_of_issue,
        file_path=saved_file_path,
    )
    return await main_crud.create(db=db, obj_in=cert_data)


@cert_router.get("/get/{cert_id}")
async def get_by_id(
    cert_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    user_data = await get_user_from_token(db=db, token=token)
    return await main_crud.get(db=db, id=cert_id, user_id=user_data.id)


@cert_router.get("/get_all")
async def get_all(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    user_data = await get_user_from_token(db=db, token=token)
    return await main_crud.get_all(db=db, user_id=user_data.id)


@cert_router.put("/update/{cert_id}")
async def update(
    cert_id: int,
    language: str | None = None,
    certificate_type: str | None = None,
    level: str | None = None,
    series_and_number: str | None = None,
    date_of_issue: date | None = None,
    token: str = Depends(oauth2_scheme),
    file: UploadFile = File((None)),
    db: AsyncSession = Depends(get_db),
):
    if file:
        new_documation = await save_file(file=file)

        cert_data = CertUpdate(
            language=language,
            certificate_type=certificate_type,
            level=level,
            series_and_number=series_and_number,
            date_of_issue=date_of_issue,
            file_path=new_documation,
        )
    else:
        cert_data = CertUpdate(
            language=language,
            certificate_type=certificate_type,
            level=level,
            series_and_number=series_and_number,
            date_of_issue=date_of_issue,
        )
    user_data = await get_user_from_token(db=db, token=token)
    return await main_crud.update(
        db=db, id=cert_id, user_id=user_data.id, obj_in=cert_data
    )


@cert_router.delete("/delete/{cert_id}")
async def delete(
    cert_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):

    user_data = await get_user_from_token(db=db, token=token)
    await main_crud.delete(db=db, id=cert_id, user_id=user_data.id)

    return {"message": "Delete successfully"}
