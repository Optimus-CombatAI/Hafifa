from src.html_extractor import RequestsHTMLExtractor
from src.html_parser import SoupHTMLParser
from src.screenshot import HTMLWebShotEngine
from consts import SCREENSHOT_NAME


class WebScraper:
    def __init__(self, url: str, extractor=RequestsHTMLExtractor,
                 url_parser=SoupHTMLParser, screenshot_engine=HTMLWebShotEngine):
        self.url = url
        self.extractor = extractor(url)
        self.url_parser = url_parser
        self.screenshot_engine = screenshot_engine()

    def scrape(self):
        result = dict()
        result['html'] = self.extractor.get_html()
        result['resources'] = self.url_parser(result['html']).get_all_urls()
        self.screenshot = self.screenshot_engine.take_screenshot(
            self.url, SCREENSHOT_NAME)

        return result
