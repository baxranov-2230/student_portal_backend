from sqlalchemy import Column, Integer, String, Date, ForeignKey
from src.core.base import Base
from sqlalchemy.orm import relationship


class Cert(Base):
    __tablename__ = "certs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    language = Column(String(50), nullable=False)
    certificate_type = Column(String(50), nullable=False)
    level = Column(String(10), nullable=False)
    series_and_number = Column(String(50), nullable=False)
    date_of_issue = Column(Date, nullable=False)
    file_path = Column(String(255))

    user = relationship("User", back_populates="cert")

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(id={self.id}, language={self.language}, "
            f"certificate_type={self.certificate_type}, date_of_issue={self.date_of_issue})>"
        )
