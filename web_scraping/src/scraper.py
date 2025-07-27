from src.html_extractor import RequestsHTMLExtractor
from src.html_parser import SoupHTMLParser
from src.screenshot import HTMLWebShotEngine
from consts import SCREENSHOT_NAME, OUTPUT_PATH
from pathlib import Path


class WebScraper:
    def __init__(self, url: str, extractor=RequestsHTMLExtractor,
                 url_parser=SoupHTMLParser, screenshot_engine=HTMLWebShotEngine):
        self.url = url
        self.extractor = extractor(url)
        self.url_parser = url_parser
        self.screenshot_engine = screenshot_engine()

    def scrape(self):
        save_path: Path = self.__create_output_path()

        result = dict()
        result['html'] = self.extractor.get_html()
        result['resources'] = self.url_parser(result['html']).get_all_urls()
        self.screenshot = self.screenshot_engine.take_screenshot(
            self.url, save_path / SCREENSHOT_NAME)

        self.__save_output(result)

        return result

    def __create_output_path(self) -> Path:
        fixed_url = self.__fix_path_name_of_url(self.url)
        path = Path(f"{OUTPUT_PATH}/{fixed_url}")
        path.mkdir(parents=True, exist_ok=True)

        return Path(path)

    def __save_output(self, output: dict):
        pass

    @staticmethod
    def __fix_path_name_of_url(url: str) -> str:
        """
            this function takes the http://url and only given the url
            this is done becuase the // is a folder so its interfiring
        """
        return url.split('https://')[-1].split('http://')[-1]
