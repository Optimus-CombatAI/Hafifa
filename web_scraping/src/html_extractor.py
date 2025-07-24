from abc import ABC, abstractmethod
from requests import get


class HTML_EXTRACTOR(ABC):
    @abstractmethod
    def get_html(self) -> str:
        pass


class RequestsHTMLExtractor(HTML_EXTRACTOR):
    def __init__(self, url: str):
        self.url = url

    def get_html(self) -> str:
        request = get(self.url)
        return request.text
