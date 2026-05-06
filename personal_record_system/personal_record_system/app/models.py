from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from .db import Base


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    source = Column(String, nullable=False, default="google_contacts")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
