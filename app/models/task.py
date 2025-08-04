# app/models/task.py
from sqlalchemy import Column, String, DateTime, JSON, Integer, Float
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
class Base(DeclarativeBase):
    pass
class TaskStatus(Base):
    __tablename__ = "task_status"
    
    id = Column(Integer, primary_key=True, index=True)
    celery_task_id = Column(String, index=True, nullable=True)
    status = Column(String, default="PENDING")
    progress = Column(Float, default=0.0)
    request_config = Column(JSON, nullable=False)
    result = Column(JSON, nullable=True)
    errors = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None