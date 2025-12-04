import json
import re
import base64
import requests
import threading
from pathlib import Path
from html2image import Html2Image


class WebScraper:

    def __init__(self, max_urls=10):
        self.urls_file = "urls.input"
        self.max_urls = max_urls

        # ABSOLUTE path to the directory where THIS FILE sits
        self.root = Path(__file__).parent

        self.urls = []
        self.load_urls()
    
    def load_urls(self):
        file_path = self.root / self.urls_file

        try:
            with file_path.open() as input_file:
                for i, row in enumerate(input_file):
                    if i >= self.max_urls:
                        break
                    self.urls.append(row.strip())
        except Exception as ex:
            print(f"Error loading URL file: {ex}")

    def take_screenshot(self, url: str, directory: Path):
        try:
            hti = Html2Image(output_path=directory)
            # enforce consistent file name
            hti.screenshot(url=url, save_as="screenshot.png")
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
            with out_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as ex:
            print(f"Error saving JSON file: {ex}")

    def extract_html(self, url: str) -> str:
        try:
            return requests.get(url).text
        except Exception as ex:
            print(f"Error fetching HTML from {url}: {ex}")
            return ""

    def collect_resources(self, html: str) -> list[str]:
        return list(set(re.findall(r'(?:src|href)=["\'](.*?)["\']', html)))

    def encode_image(self, directory: Path) -> str:
        img_path = directory / "screenshot.png"

        try:
            with img_path.open("rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
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
