from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.api import api_router 
import uvicorn



app = FastAPI()

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # Test uchun; keyin frontend URLni qo‘shing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=[
        "http://127.0.0.0.1:5500",
        "http://localhost:5173"
        # "http://localhost:5174",     
        # "http://localhost:5177",
        # "https://new.nsumt.uz",
    
    ],  # Разрешаем доступ с вашего фронтенда
    # allow_credentials=True,
    # allow_methods=["*"],  # Разрешаем все HTTP методы
    # allow_headers=["*"],  # Разрешаем все заголовки
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


