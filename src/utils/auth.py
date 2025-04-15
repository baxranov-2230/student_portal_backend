from fastapi import HTTPException , status
from src.schemas.user import LoginRequest
import httpx
from src.core.config import settings
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from .main_crud import *

async def authenticate_user(credentials: LoginRequest)-> str:
    if not credentials.login or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login and password are required"
        )
    
    payload = {"login": credentials.login , "password": credentials.password}
    headers = {"Content-Type": "application/json",}
    async with httpx.AsyncClient() as client:
        api_response = await client.post(url=settings.HEMIS_LOGIN_URL , json=payload , headers=headers)
        api_response.raise_for_status()

        response_data = api_response.json()
        token = response_data.get("data" , {}).get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No token received from the authentication server"
            )
        
        return token
    
async def fetch_user_data(token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        user_response = await client.get(url=settings.HEMIS_USER , headers=headers)
        user_response.raise_for_status()
        return user_response.json().get("data" , {})
    
async def fetch_user_gpa(token: str) -> dict:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
             user_resposne = await client.get(url=settings.HEMIS_USER_GPA , headers=headers)
             user_resposne.raise_for_status()
             return user_resposne.json()
        
def map_user_data(api_data: dict) -> dict:
    user_data = {
            "first_name": api_data.get("first_name"),
            "last_name": api_data.get("second_name"),
            "third_name": api_data.get("third_name"),
            "full_name": api_data.get("full_name"),
            "student_id_number": api_data.get("student_id_number"),
            "image_path": api_data.get("image"),
            "birth_date": api_data.get("birth_date"),
            "passport_pin": api_data.get("passport_pin"),
            "passport_number": api_data.get("passport_number"),
            "phone": api_data.get("phone"),
            "gender": api_data.get("gender", {}).get("name"),
            "university": api_data.get("university"),
            "specialty": api_data.get("specialty", {}).get("name"),
            "studentStatus": api_data.get("studentStatus", {}).get("name"),
            "educationForm": api_data.get("educationForm", {}).get("name"),
            "educationType": api_data.get("educationType", {}).get("name"),
            "paymentForm": api_data.get("paymentForm", {}).get("name"),
            "group": api_data.get("group", {}).get("name"),
            "educationLang": api_data.get("educationLang", {}).get("name"),
            "faculty": api_data.get("faculty", {}).get("name"),
            "level": api_data.get("level", {}).get("name"),
            "semester": api_data.get("semester", {}).get("name"),
            "address": api_data.get("address"),
        }
    if user_data["birth_date"]:
        try:
            user_data["birth_date"] = datetime.fromtimestamp(user_data["birth_date"]).date()
        except (TypeError , ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='birth_date is missing in API response'
            )
    missing_fields = [key for key, value in user_data.items() if value is None]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Required fields missing in API response: {', '.join(missing_fields)}"
        )

    return user_data

def map_user_gpa(api_data)-> dict:
    data_list = api_data.get("data")
    if not data_list or not isinstance(data_list , list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API response does not contain valid data array"
        )
    data_item = data_list[0]

    try:
        gpa_value = data_item.get("gpa")
        mapped_data = {
            "gpa": float(gpa_value) if gpa_value is not None else None,
            "educationYear": data_item.get("educationYear", {}).get("name"),
            "subjects": data_item.get("subjects"),
            "level": data_item.get("level", {}).get("name"),
            "credit_sum": str(data_item.get("credit_sum")),
            "debt_subjects": data_item.get("debt_subjects")
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid GPA format: must be a valid number"
        )

    missing_fields = [field for field, value in mapped_data.items() if value is None]
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Required fields missing in API response: {', '.join(missing_fields)}"
        )
    return mapped_data


async def save_user_data_to_db(db: AsyncSession , user_data: dict):
    result = await get_user(db=db , username=user_data["student_id_number"])
    if result:
        return result
    
    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
    
async def save_user_gpa_to_db(db: AsyncSession , user_id: int, user_gpa: dict):
    result = await get_by_id(db=db , item_id=user_id)
    if result:
        return result
    new_user = UserGpa(user_id = user_id
     ,**user_gpa)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def fetch_subject(semester: int):
    url = f"{settings.HEMIS_USER_SUBJECT}?semester={semester}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
    

async def mapped_subject(api_data: dict) -> dict:
    pass