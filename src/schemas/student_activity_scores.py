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