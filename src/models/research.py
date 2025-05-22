from sqlalchemy import Column, String, Integer, Date, ForeignKey
from src.core.base import Base
from sqlalchemy.orm import relationship


class Research(Base):
    __tablename__ = "researchs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    form = Column(String, nullable=False)
    pub_date = Column(Date, nullable=False)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    user = relationship("User", back_populates="research")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, title={self.title}, pub_date={self.pub_date})>"
