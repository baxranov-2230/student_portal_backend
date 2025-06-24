from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class ApplicationCreateResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    student_id_number: str
    image_path: str | None
    group: str
    faculty: str
    gpa: float
    filepath: Optional[str] = None
    create_date: datetime
    reponse_file: Optional[str] = None



class ApplicationDeleteResponse(BaseModel):
    message: str

class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    student_id_number: str
    image_path: str | None
    group: str
    faculty: str
    gpa: float
    filepath: Optional[str] = None
    create_date: datetime
    reponse_file: Optional[str] = None