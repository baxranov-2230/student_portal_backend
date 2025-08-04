from fastapi import HTTPException, status
from src.schemas.user import LoginRequest
import httpx
from src.core.config import settings
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from src.models.user_subject import UserSubject
from .main_crud import get_user , get_by_field
from src.models.user import User 
from sqlalchemy import select
from src.models.user_gpa import UserGpa
from typing import Dict, Any, List
import jwt
from typing import Callable
from fastapi import Depends
from src.core.base import get_db
from src.models.user_attendance import UserAttendance





oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
)


async def authenticate_user(credentials: LoginRequest) -> str:
    username = credentials.username.strip()
    password = credentials.password.strip()

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login and password are required",
        )

    try:
        login = int(username)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login must be a valid integer",
        )

    payload = {"login": login, "password": password}
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            api_response = await client.post(
                url=settings.HEMIS_LOGIN_URL, json=payload, headers=headers
            )
            api_response.raise_for_status()

            response_data = api_response.json()
            token = response_data.get("data", {}).get("token")

            if not token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No token received from the authentication server",
                )

            return token

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials",
            )
        else:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Authentication server error: {e.response.text}",
            )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is unavailable",
        )


async def authenticate_admin(credentials: LoginRequest, db: AsyncSession):
    stmt = select(User).where(
        User.full_name == credentials.username, User.password == credentials.password
    )
    result = await db.execute(stmt)
    user_data = result.scalars().first()

    if user_data:
        return user_data
    if not user_data:
        return None


async def fetch_user_data(token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        user_response = await client.get(url=settings.HEMIS_USER, headers=headers)
        user_response.raise_for_status()
        return user_response.json().get("data", {})


async def fetch_user_gpa(token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        user_resposne = await client.get(url=settings.HEMIS_USER_GPA, headers=headers)
        user_resposne.raise_for_status()
        return user_resposne.json()


async def fetch_subject(semester: int, token: str):
    url = f"{settings.HEMIS_USER_SUBJECT}?semester={semester}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)
        response.raise_for_status()
        return response.json()

async def fetch_attendance(semester_code: int, token: str):
    subject_id = 0
    params = {"subject": subject_id, "semester": semester_code}
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
            response = await client.get(url=settings.HEMIS_USER_ATTENDANCE, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
             

def map_user_data(api_data: dict) -> dict:
    print(api_data)
    
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
        "student_status": api_data.get("studentStatus", {}).get("name"),
        "education_form": api_data.get("educationForm", {}).get("name"),
        "education_type": api_data.get("educationType", {}).get("name"),
        "payment_form": api_data.get("paymentForm", {}).get("name"),
        "group": api_data.get("group", {}).get("name"),
        "education_lang": api_data.get("educationLang", {}).get("name"),
        "faculty": api_data.get("faculty", {}).get("name"),
        "level": api_data.get("level", {}).get("name"),
        "semester": api_data.get("semester", {}).get("name"),
        "address": api_data.get("address"),
        "gpa": str(api_data.get("avg_gpa"))
    }

    if user_data["birth_date"]:
        try:
            user_data["birth_date"] = datetime.fromtimestamp(
                user_data["birth_date"]
            ).date()
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="birth_date is invalid in API response",
            )

    OPTIONAL_FIELDS = {"passport_pin", "passport_number"}
    missing_fields = [
        key for key, value in user_data.items()
        if value is None and key not in OPTIONAL_FIELDS
    ]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Required fields missing in API response: {', '.join(missing_fields)}",
        )

    return user_data


def map_user_gpa(api_data) -> list[dict]:
    data_list = api_data.get("data")
    if not data_list or not isinstance(data_list, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API response does not contain valid data array",
        )

    mapped_results = []
    for data_item in data_list:
        try:
            gpa_value = data_item.get("gpa")
            mapped_data = {
                "gpa": float(gpa_value) if gpa_value is not None else None,
                "educationYear": data_item.get("educationYear", {}).get("name"),
                "subjects": data_item.get("subjects"),
                "level": data_item.get("level", {}).get("name"),
                "credit_sum": str(data_item.get("credit_sum")),
                "debt_subjects": data_item.get("debt_subjects"),
            }
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GPA format: must be a valid number",
            )

        missing_fields = [field for field, value in mapped_data.items() if value is None]
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Required fields missing in API response: {', '.join(missing_fields)}",
            )
        
        mapped_results.append(mapped_data)

    return mapped_results



def map_subject_grades(api_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    data = api_data.get("data", [])
    result = []
    for item in data:
        subject_name = item.get("curriculumSubject", {}).get("subject", {}).get("name")
        grade = item.get("overallScore", {}).get("grade")
        semester_code = item.get("_semester", 0)

        if subject_name is None or grade is None or semester_code == 0:
            continue

        subject_data = {
            "subject_name": subject_name,
            "grade": grade,
            "semester_code": semester_code,
        }
        result.append(subject_data)
    return result

def map_attendance_records(api_data: Dict[str, Any]) -> list[Dict[str, Any]]:
    data = api_data.get("data", [])
    result = []

    for item in data:
        mapped = {
            "subject_name": item["subject"]["name"],
            "semester_name": item["semester"]["name"],
            "trainingType_name": item["trainingType"]["name"],
            "absent_on": item["absent_on"],
            "absent_off": item["absent_off"],
        }
        result.append(mapped)

    return result

async def save_attendance_to_db(
    db: AsyncSession, user_attendance: list[Dict[str, Any]], user_id: int
):
    try:
        existing = await db.execute(
            select(UserAttendance).where(UserAttendance.user_id == user_id)
        )
        existing = existing.scalars().all()

        existing_keys = {
            (item.subject_name, item.semester_name, item.trainingType_name)
            for item in existing
        }

        db_items = []
        for item in user_attendance:
            key = (item["subject_name"], item["semester_name"], item["trainingType_name"])
            if key not in existing_keys:
                db_items.append(
                    UserAttendance(
                        user_id=user_id,
                        subject_name=item["subject_name"],
                        semester_name=item["semester_name"],
                        trainingType_name=item["trainingType_name"],
                        absent_on=item["absent_on"],
                        absent_off=item["absent_off"],
                    )
                )

        if db_items:
            db.add_all(db_items)
            await db.commit()

            for item in db_items:
                await db.refresh(item)

    except Exception as e:
        await db.rollback()
        raise Exception(f"Failed to save attendance: {str(e)}")

async def save_user_data_to_db(db: AsyncSession, user_data: dict):
    result = await get_user(db=db, username=user_data["student_id_number"])
    if result:
        return result

    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def save_user_gpa_to_db(db: AsyncSession, user_id: int, user_gpa_list: list[dict]):
    saved_records = []
    for user_gpa in user_gpa_list:
        new_user = UserGpa(user_id=user_id, **user_gpa)
        db.add(new_user)
        saved_records.append(new_user)

    await db.commit()
    for user in saved_records:
        await db.refresh(user)
    return saved_records


async def save_user_subject_to_db(
    db: AsyncSession, user_subjects: List[dict], user_id: int
):
    try:
        existing_subjects = await db.execute(
            select(UserSubject).where(UserSubject.user_id == user_id)
        )
        existing_subjects = existing_subjects.scalars().all()

        existing_subject_keys = {
            (subject.subject_name, subject.semester_code)
            for subject in existing_subjects
        }

        db_items = []
        for item in user_subjects:
            subject_name = item["subject_name"]
            subject_grade = item["grade"]
            semester_code = int(item["semester_code"])

            if subject_grade == 0:
                continue

            if (subject_name, semester_code) not in existing_subject_keys:
                db_items.append(
                    UserSubject(
                        user_id=user_id,
                        subject_name=subject_name,
                        grade=item["grade"],
                        semester_code=semester_code,
                    )
                )
            else:
                return existing_subjects

        if db_items:
            db.add_all(db_items)
            await db.commit()

            for item in db_items:
                await db.refresh(item)

    except ValueError as e:
        await db.rollback()
        raise Exception(f"Invalid semester_code value: {str(e)}")

    except Exception as e:
        await db.rollback()
        raise Exception(f"Failed to save subjects: {str(e)}")


def check_semester(semestr: str):
    match semestr:
        case "1-semestr":
            return 11
        case "2-semestr":
            return 12
        case "3-semestr":
            return 13
        case "4-semestr":
            return 14
        case "5-semestr":
            return 15
        case "6-semestr":
            return 16
        case "7-semestr":
            return 17
        case "8-semestr":
            return 18


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username not found in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_data = await get_by_field(db=db , model=User , field_name="full_name" , field_value=username)

        if user_data:
            return user_data
        
        user = await get_user(db=db, username=username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def RoleChecker(valid_roles: str | List[str]) -> Callable:
    async def _role_checker(user: User = Depends(get_current_user)):
        roles = [valid_roles] if isinstance(valid_roles, str) else valid_roles
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' not allowed",
            )
        return user

    return _role_checker





