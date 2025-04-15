from pydantic import BaseModel , ConfigDict
from datetime import datetime , date


class AchievementBase(BaseModel):
    user_id: int
    type: str
    award_date: date
    title: str
    file_path: str


class AchievementResposne(AchievementBase):
    id: int

    model_config = ConfigDict(from_attributes=True)



class AchievementUpdate(BaseModel):
    type: str | None = None
    award_date: date | None = None
    title: str | None = None
    file_path: str | None = None