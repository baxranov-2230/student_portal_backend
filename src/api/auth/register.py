from fastapi import APIRouter, Depends
from src.schemas.user import RegisterUser, AdminCreate
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base import get_db
from src.models.user import User, UserRole


register_router = APIRouter()


@register_router.post("/register")
async def register(user_item: RegisterUser, db: AsyncSession = Depends(get_db)):
    admin_data = AdminCreate(
        full_name=user_item.full_name,
        password=user_item.password,
        role=UserRole.admin.value,
    )
    new_admin = User(**admin_data.model_dump())
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return {"username": new_admin.full_name, "role": new_admin.role}
