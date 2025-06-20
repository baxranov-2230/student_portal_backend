from fastapi import APIRouter
from .me import me_router
from .research import research_router
from .achievements import achievement_router
from .cert import cert_router
from .application import application_router

user_router = APIRouter(prefix="/user")

user_router.include_router(me_router , tags=["User"])
user_router.include_router(research_router , tags=["User"])
user_router.include_router(cert_router , tags=["User"])
user_router.include_router(achievement_router , tags=["User"])
user_router.include_router(application_router , tags=["Application"])
