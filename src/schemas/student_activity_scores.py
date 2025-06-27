from pydantic import BaseModel


class StudentActivityScoreUpdate(BaseModel):
    reading_culture : str | None = None
    five_initiatives : str | None = None
    academic_performance : str | None = None
    discipline_compliance : str | None = None
    competition_achievements : str | None = None
    attendance_punctuality : str | None = None
    enlightenment_lessons : str | None = None
    volunteering : str | None = None
    cultural_visits : str | None = None
    healthy_lifestyle : str | None = None
    other_spiritual_activity : str | None = None




class StudentActivityScoreCreate(BaseModel):
    reading_culture: str = "0"
    five_initiatives: str = "0"
    academic_performance: str = "0"
    discipline_compliance: str = "0"
    competition_achievements: str = "0"
    attendance_punctuality: str = "0"
    enlightenment_lessons: str = "0"
    volunteering: str = "0"
    cultural_visits: str = "0"
    healthy_lifestyle: str = "0"
    other_spiritual_activity: str = "0"

class StudentActivityScoreResponse(StudentActivityScoreCreate):
    id: int