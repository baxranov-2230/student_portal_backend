from fastapi import APIRouter , Depends
from src.utils.auth import oauth2_scheme

refresh_router = APIRouter()


@refresh_router.post("/refresh")
async def refresh(
    token: str = Depends(oauth2_scheme)
):
    token = None
    return {"message": "Sometimes not work"}