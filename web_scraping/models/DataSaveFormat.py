from pydantic import BaseModel

from models.HtmlData import HtmlData


class DataSaveFormat(BaseModel):
    html: str
    resources: HtmlData
    screenshot: str
