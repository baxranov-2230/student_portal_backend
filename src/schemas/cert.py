from pydantic import BaseModel, ConfigDict
from datetime import date


class CertBase(BaseModel):
    user_id: int
    language: str
    certificate_type: str
    level: str
    series_and_number: str
    date_of_issue: date
    file_path: str


class CertResponse(CertBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CertUpdate(BaseModel):
    lenguage: str | None = None
    certificate_type: str | None = None
    level: str | None = None
    series_and_number: str | None = None
    date_of_issue: date | None = None
    file_path: str | None = None
