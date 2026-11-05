import datetime
from typing import Self

from pydantic import BaseModel, model_validator


class DateRangeQuery(BaseModel):
    start_date: datetime.date
    end_date: datetime.date

    @model_validator(mode="after")
    def _require_start_not_after_end(self) -> Self:
        if self.start_date > self.end_date:
            raise ValueError(f"start_date {self.start_date} is after end_date {self.end_date}")

        return self
