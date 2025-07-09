from fastapi import APIRouter
from .me import me_router
# from .research import research_router
# from .achievements import achievement_router
# from .cert import cert_router
from .application import application_router
from .student_activity_score import student_activity_scores_router

user_router = APIRouter(
    prefix="/user",
    tags=["User"]
    )

user_router.include_router(me_router)
# user_router.include_router(research_router , tags=["User"])
# user_router.include_router(cert_router , tags=["User"])
# user_router.include_router(achievement_router , tags=["User"])
user_router.include_router(application_router)
user_router.include_router(student_activity_scores_router)
