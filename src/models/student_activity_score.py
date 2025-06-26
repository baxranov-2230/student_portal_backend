from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from src.core.base import Base

class StudentActivityScore(Base):
    __tablename__ = "student_activity_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

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

    user = relationship("User", back_populates="activity_score")
