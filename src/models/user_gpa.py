from sqlalchemy import Column, String, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from src.core.base import Base


class UserGpa(Base):
    __tablename__ = "user_gpas"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gpa = Column(Float, nullable=False)
    educationYear = Column(String, nullable=False)
    subjects = Column(Integer, nullable=False)
    level = Column(String, nullable=False)
    credit_sum = Column(String, nullable=False)
    debt_subjects = Column(Integer, nullable=False)

    user = relationship("User", back_populates="gpa")
