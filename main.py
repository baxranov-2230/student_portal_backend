from fastapi import FastAPI, status
from starlette.requests import Request
from starlette.responses import JSONResponse
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from starlette.middleware.cors import CORSMiddleware
from src.api import api_router
import uvicorn


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # Test uchun; keyin frontend URLni qo‘shing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=[
        "http://grant.nsumt.uz",
        "https://grant.nsumt.uz",
        "http://localhost:5173",
        # "http://localhost:5174",
        # "http://localhost:5177",
        # "https://new.nsumt.uz",
    ],  # Разрешаем доступ с вашего фронтенда

)


@app.exception_handler(ExpiredSignatureError)
async def expired_signature_handler(request: Request, exc: ExpiredSignatureError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Token has expired"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(InvalidTokenError)
async def invalid_token_handler(request: Request, exc: InvalidTokenError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid token"},
        headers={"WWW-Authenticate": "Bearer"},
    )


app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
