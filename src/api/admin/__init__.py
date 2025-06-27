from fastapi import APIRouter
from .application import application_router
from .count import count_router
from .student_activity_score import student_activity_scores_router


admin_router = APIRouter(tags=["Admin"], prefix="/admin")


admin_router.include_router(application_router)
admin_router.include_router(student_activity_scores_router)
admin_router.include_router(count_router)