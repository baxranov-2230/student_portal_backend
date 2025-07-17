from pydantic import BaseModel





class StudentActivityScoreUpdate(BaseModel):
    reading_culture : int | None = None
    academic_performance: int | None = None
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
    reading_culture: int  = 0
    five_initiatives: int  = 0
    academic_performance: int  = 0
    discipline_compliance: int  = 0
    competition_achievements: int  = 0
    attendance_punctuality: int  = 0
    enlightenment_lessons: int  = 0
    volunteering: int  = 0
    cultural_visits: int  = 0
    healthy_lifestyle: int  = 0
    other_spiritual_activity: int  = 0

class StudentActivityScoreResponse(StudentActivityScoreCreate):
    id: int
