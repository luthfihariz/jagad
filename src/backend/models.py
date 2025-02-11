from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from database import Base
import datetime

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, index=True)
    request_data = Column(JSON)
    response_data = Column(JSON)
    model = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    status_code = Column(Integer)
    error_message = Column(String, nullable=True)
    response_time_ms = Column(Float)
