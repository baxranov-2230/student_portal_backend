from pydantic import BaseModel

class ExelDataBase(BaseModel):
    full_name: str
    specialty: str
    group: str
    student_id_number: str
    gpa: float

