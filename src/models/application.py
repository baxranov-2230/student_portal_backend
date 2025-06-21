from sqlalchemy import Column , String , Integer , Float , ForeignKey
from sqlalchemy.orm import relationship
from src.core.base import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"))
    first_name = Column(String , nullable=True)
    last_name = Column(String , nullable=True)
    third_name = Column(String , nullable=True)
    student_id_number = Column(String, nullable=True)
    image_path = Column(String, nullable=True) 
    group = Column(String, nullable=True)
    faculty = Column(String, nullable=True) 
    gpa = Column(Float , nullable=True)

    user = relationship("User" , back_populates="application")

