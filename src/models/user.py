from sqlalchemy import Column, Integer, String, Date, Enum as SqlEnum
from sqlalchemy.orm import relationship
from src.core.base import Base
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    manger = "manger"
    student = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=True) 
    last_name = Column(String, nullable=True) 
    third_name = Column(String, nullable=True) 
    full_name = Column(String, nullable=True)
    student_id_number = Column(String, nullable=True) 
    image_path = Column(String, nullable=True) 
    birth_date = Column(Date, nullable=True) 
    passport_pin = Column(String, nullable=True)
    passport_number = Column(String, nullable=True) 
    phone = Column(String, nullable=True)
    password = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    university = Column(String, nullable=True)
    specialty = Column(String, nullable=True)
    student_status = Column(String, nullable=True)
    education_form = Column(String, nullable=True)     # changed
    education_type = Column(String, nullable=True)     # changed
    payment_form = Column(String, nullable=True)       # changed
    group = Column(String, nullable=True)
    education_lang = Column(String, nullable=True)     # changed
    faculty = Column(String, nullable=True) 
    level = Column(String, nullable=True)
    semester = Column(String, nullable=True)
    address = Column(String, nullable=True)
    role = Column(SqlEnum(UserRole), default=UserRole.student)

    activity_score = relationship("StudentActivityScore", back_populates="user", uselist=False)
    attendances = relationship("UserAttendance", back_populates="user")
    cert = relationship("Cert", back_populates="user")
    achievement = relationship("Achievement", back_populates="user")
    research = relationship("Research", back_populates="user")
    subject = relationship("UserSubject", back_populates="user")
    gpa = relationship("UserGpa", back_populates="user", uselist=False)
    application = relationship("Application" , back_populates="user")
