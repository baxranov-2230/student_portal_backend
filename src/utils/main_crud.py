from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import User
from src.exception.base_exception import main_exeption , not_found
from typing import TypeVar, Generic, List , Type
from pydantic import BaseModel
from typing import Any
import os
from fastapi import UploadFile

ModelType = TypeVar("ModelType", bound=BaseModel)
SchemaType = TypeVar("SchemaType")


class MainCrud(Generic[ModelType, SchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int, user_id: int) -> ModelType:
        result = await db.execute(
            select(self.model).where(
                (self.model.id == id) & (self.model.user_id == user_id)
            )
        )
        db_obj = result.scalars().first()
        if not db_obj:
            raise await not_found("user")
        return db_obj

    async def get_all(self, user_id: int, db: AsyncSession) -> List[ModelType]:
        result = await db.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: SchemaType) -> ModelType:
        try:
            db_obj = self.model(**obj_in.model_dump())
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await db.rollback()
            raise await main_exeption(e)

    async def update(
        self, db: AsyncSession, id: int, user_id: int, obj_in: SchemaType
    ) -> ModelType:
        try:
            db_obj = await self.get(db=db, id=id, user_id=user_id)
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value in {None, "", "string"}:
                    continue
                setattr(db_obj, field, value)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await db.rollback()
            raise await main_exeption(e)

    async def delete(self, db: AsyncSession, id: int, user_id: int) -> None:
        db_obj = await self.get(db=db, id=id, user_id=user_id)
        await db.delete(db_obj)
        await db.commit()


async def get_user(db: AsyncSession, username: str):
    stmst = select(User).where(User.student_id_number == username)
    excute = await db.execute(stmst)
    return excute.scalars().first()


async def get_by_field(db: AsyncSession, model, field_name: str, field_value: Any):
    if not hasattr(model, field_name):
        raise ValueError(f"Field '{field_name}' does not exist on model {model.__name__}")
    query = select(model).where(getattr(model, field_name) == field_value)
    scalars = await db.scalars(query)
    return scalars.first()
    


async def save_file(file: UploadFile) -> str:
    """Save an uploaded file to the 'uploads' directory and return its path."""
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return file_path
    except Exception as e:
        raise ValueError(f"Failed to save file: {str(e)}")
    finally:
        await file.close()
