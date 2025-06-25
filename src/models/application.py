from sqlalchemy import Column , String , Integer , Float , ForeignKey , DateTime
from sqlalchemy.orm import relationship
from src.core.base import Base
from datetime import datetime , timezone

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"))
    full_name = Column(String , nullable=True)
    student_id_number = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    group = Column(String, nullable=True)
    faculty = Column(String, nullable=True) 
    gpa = Column(Float , nullable=True)
    filepath = Column(String , nullable=True)
    reponse_file = Column(String , nullable=True)
    create_date = Column(DateTime , default=lambda: datetime.now(timezone.utc).replace( hour=0, minute=0, second=0, microsecond=0))

    user = relationship("User" , back_populates="application")

