from abc import ABC, abstractmethod
from typing import List
from bs4 import BeautifulSoup


class HTMLParser(ABC):
    @abstractmethod
    def get_all_urls(self) -> List[str]:
        pass


class SoupHTMLParser(HTMLParser):
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def get_all_urls(self) -> List[str]:
        urls = set()

        for tag in self.soup.find_all(True):  # True = all tags
            href = tag.get('href')
            src = tag.get('src')
            if href:
                urls.add(href)
            if src:
                urls.add(src)

        return list(urls)
