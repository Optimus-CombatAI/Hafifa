from typing import List, TypedDict


class HtmlData(TypedDict):
    images: List[str]
    scripts: List[str]
    links: List[str]
    anchors: List[str]
