from pydantic import BaseModel


class RejectedRow(BaseModel):
    line_number: int
    reason: str
