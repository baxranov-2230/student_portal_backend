from pydantic import BaseModel, ConfigDict
from datetime import date


class ResearchBase(BaseModel):
    user_id: int
    form: str
    pub_date: date
    title: str
    file_path: str


class ResearchResponse(ResearchBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ResearchUpdate(BaseModel):
    form: str | None = None
    pub_date: date | None = None
    title: str | None = None
    file_path: str | None = None
