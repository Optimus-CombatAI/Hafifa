import base64
from itertools import islice
import json
from pathlib import Path
import re
import threading

from html2image import Html2Image
import requests

### Constants ###
MAX_URLS = 10
APP_ROOT_PATH = Path(__file__).parent

class WebScraper:

    def __init__(self):
        self.urls_file = "urls.input"
        self.urls = []
        self.load_urls()
    
    def load_urls(self):
        file_path = APP_ROOT_PATH / self.urls_file

        try:
            with file_path.open() as input_file:
                for row in islice(input_file, MAX_URLS):
                    self.urls.append(row.strip())
        except Exception as ex:
            print(f"Error loading URL file: {ex}")

    def take_screenshot(self, url: str, directory: Path):
        try:
            html_to_image_converter = Html2Image(output_path=directory)
            # enforce consistent file name
            html_to_image_converter.screenshot(url=url, save_as="screenshot.png")
        except Exception as ex:
            print(f"Error taking screenshot of {url}: {ex}")

    def create_json(self, html: str, screenshot64: str, resources: list[str]):
        return {
            "html": html,
            "resources": resources,
            "screenshot": screenshot64
        }

    def save_json(self, data: dict, directory: Path):
        try:
            out_file = directory / "browse.json"
            
            with out_file.open("w", encoding="utf-8") as out_file:
                json.dump(data, out_file, ensure_ascii=False, indent=4)
                
        except Exception as ex:
            print(f"Error saving JSON file: {ex}")

    def extract_html_from_site(self, url: str) -> str:
        try:
            return requests.get(url).text
        
        except Exception as ex:
            print(f"Error fetching HTML from site{url}: {ex}")
            return ""

    def collect_resources(self, html: str) -> list[str]:
        return list(set(re.findall(r'(?:src|href)=["\'](.*?)["\']', html)))

    def encode_image(self, directory: Path) -> str:
        img_path = directory / "screenshot.png"

        try:
            with img_path.open("rb") as image:
                return base64.b64encode(image.read()).decode("utf-8")
        except Exception as ex:
            print(f"Error encoding screenshot in {directory}: {ex}")
            return ""
    
    def scrap(self, url: str, directory: Path):
        try:
            directory.mkdir(exist_ok=True)

            html = self.extract_html(url)
            resources = self.collect_resources(html)
            self.take_screenshot(url, directory)
            screenshot64 = self.encode_image(directory)

            json_data = self.create_json(html, screenshot64, resources)
            self.save_json(json_data, directory)

        except Exception as ex:
            print(f"Error scraping {url}: {ex}")


def main():
    scraper = WebScraper()
    out_root = scraper.root / "output"
    out_root.mkdir(exist_ok=True)

    threads = []

    for idx, url in enumerate(scraper.urls):
        path = out_root / f"url_{idx}"

        t = threading.Thread(target=scraper.scrap, args=(url, path))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
