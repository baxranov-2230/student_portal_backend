from sqlalchemy import Column , String , Integer , ForeignKey
from src.core.base import Base
from sqlalchemy.orm import relationship

class UserAttendance(Base):
    __tablename__ = "user_attendances"

    id = Column(Integer , primary_key=True)
    user_id = Column(Integer , ForeignKey("users.id"))
    subject_name = Column(String , nullable=True)
    semester_name = Column(String , nullable=True)
    trainingType_name = Column(String , nullable=True)
    absent_on = Column(Integer , nullable=True)
    absent_off = Column(Integer , nullable=True)

    user = relationship("User", back_populates="attendances")