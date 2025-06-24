from pydantic import BaseModel 
from datetime import date

class SearchBase(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    student_id_number: str | None = None
    faculty: str | None = None



