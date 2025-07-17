from pydantic import BaseModel





class StudentActivityScoreUpdate(BaseModel):
    reading_culture : int | None = None
    five_initiatives : int | None = None
    discipline_compliance : int | None = None
    competition_achievements : int | None = None
    attendance_punctuality : int | None = None
    enlightenment_lessons : int | None = None
    volunteering : int | None = None
    cultural_visits : int | None = None
    healthy_lifestyle : int | None = None
    other_spiritual_activity : int | None = None




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
