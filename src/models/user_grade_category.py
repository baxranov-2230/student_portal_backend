from sqlalchemy import Column , String , Integer
from sqlalchemy.orm import relationship
from src.core.base import Base

class UserGradeCategory(Base):
    __tablename__ = "user_grade_gategorys"

    id = Column(Integer, primary_key=True)
    