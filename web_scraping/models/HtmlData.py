from typing import List
from pydantic import BaseModel


class HtmlData(BaseModel):
    images: List[str]
    scripts: List[str]
    links: List[str]
    anchors: List[str]
