from sqlalchemy.orm import Session
from models import RequestLog

class RequestLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_request_log(self, endpoint: str, request_data: dict, response_data: dict,
                         model: str = None, status_code: int = 200,
                         error_message: str = None, response_time_ms: float = None) -> RequestLog:
        db_log = RequestLog(
            endpoint=endpoint,
            request_data=request_data,
            response_data=response_data,
            model=model,
            status_code=status_code,
            error_message=error_message,
            response_time_ms=response_time_ms
        )
        self.db.add(db_log)
        self.db.commit()
        self.db.refresh(db_log)
        return db_log
