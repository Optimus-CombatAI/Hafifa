from typing import TypedDict

from models.HtmlData import HtmlData


class DataSaveFormat(TypedDict):
    html: str
    resources: HtmlData
    screenshot: str
