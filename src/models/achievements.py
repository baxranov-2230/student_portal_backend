from sqlalchemy import Column , String , Integer , Date , ForeignKey
from sqlalchemy.orm import relationship
from src.core.base import Base


class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer , primary_key=True)
    user_id = Column(Integer , ForeignKey("users.id"))
    type = Column(String(50) , nullable=False)
    award_date = Column(Date , nullable=False)
    title = Column(String(100), nullable=False)
    file_path = Column(String , nullable=False)


    user = relationship("User" , back_populates="achievement")



    def __repr__(self):
        return (
            f"Achievement(id={self.id!r}, title={self.title!r}, "
            f"type={self.type!r}, award_date={self.award_date!r}, "
            f"file={self.file_path!r})"
        )