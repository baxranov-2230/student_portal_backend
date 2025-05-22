from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.core.base import Base


class UserSubject(Base):
    __tablename__ = "user_subjects"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_name = Column(String, nullable=False)
    grade = Column(Integer, nullable=False)
    semester_code = Column(Integer, nullable=False)

    user = relationship("User", back_populates="subject")
