from pydantic import BaseModel

from src.models.rejected_row import RejectedRow


class UploadReport(BaseModel):
    saved_rows: int
    created_alerts: int
    rejected_rows: list[RejectedRow]
