from fastapi import APIRouter 
from src.utils.jwt_utils import refresh_access_token

refresh_router = APIRouter()


@refresh_router.post("/refresh")
async def refresh(
    token: str
):
    tokens = await refresh_access_token(refresh_token=token)

    access_token=tokens.get('access_token')
    refresh_token=tokens.get('refresh_token')
    return {
        'access_token': access_token, 
        'refresh_token': refresh_token
        }
