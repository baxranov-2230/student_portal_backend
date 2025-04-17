from fastapi import APIRouter
from .me import me_router
from .research import research_router
from .achievements import achievement_router
from .cert import cert_router
from .get_application import application_router


user_router = APIRouter(
    tags=["User"],
    prefix="/user"
)

user_router.include_router(me_router)
user_router.include_router(research_router)
user_router.include_router(cert_router)
user_router.include_router(achievement_router)
user_router.include_router(application_router)