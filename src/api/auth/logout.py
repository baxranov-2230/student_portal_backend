from fastapi import APIRouter , Request , Response


logout_router = APIRouter()


@logout_router.delete("/logout")
async def logout(request: Request , response :Response):
    token = request.cookies.get("access_token")

    if not token:
        return {"message": "No active session"}
    
    response.delete_cookie(key="access_token")

    return {"message": "Successfully logged out."}
