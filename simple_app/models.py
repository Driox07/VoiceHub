from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from simple_app.database import Base

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    pth_file = Column(String(500), nullable=False)
    index_file = Column(String(500), nullable=False)
    technology = Column(String(50), nullable=False, default="RVMPE")
    epochs = Column(Integer, nullable=False)
    language = Column(String(50), nullable=False)
