from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from src.core.base import Base

class StudentActivityScore(Base):
    __tablename__ = "student_activity_scores"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Activity scores
    reading_culture = Column(String, default="0")
    five_initiatives = Column(String, default="0")
    academic_performance = Column(String, default="0")
    discipline_compliance = Column(String, default="0")
    competition_achievements = Column(String, default="0")
    attendance_punctuality = Column(String, default="0")
    enlightenment_lessons = Column(String, default="0")
    volunteering = Column(String, default="0")
    cultural_visits = Column(String, default="0")
    healthy_lifestyle = Column(String, default="0")
    other_spiritual_activity = Column(String, default="0")

    # File paths for uploaded files
    reading_culture_path = Column(String, nullable=True)
    five_initiatives_path = Column(String, nullable=True)
    academic_performance_path = Column(String, nullable=True)
    discipline_compliance_path = Column(String, nullable=True)
    competition_achievements_path = Column(String, nullable=True)
    attendance_punctuality_path = Column(String, nullable=True)
    enlightenment_lessons_path = Column(String, nullable=True)
    volunteering_path = Column(String, nullable=True)
    cultural_visits_path = Column(String, nullable=True)
    healthy_lifestyle_path = Column(String, nullable=True)
    other_spiritual_activity_path = Column(String, nullable=True)

    user = relationship("User", back_populates="activity_score")
