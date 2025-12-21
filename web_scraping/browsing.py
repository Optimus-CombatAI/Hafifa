import asyncio
import base64
import json
import re
from itertools import islice
from pathlib import Path

import aiohttp
from html2image import Html2Image

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
            with file_path.open() as urls_file:
                for row in islice(urls_file, MAX_URLS):
                    self.urls.append(row.strip())
        
        except Exception as ex:
            print(f"Error loading URL file: {ex}")
            
    def take_screenshot(self, url: str, directory: Path):
        try:
            html_to_image_converter = Html2Image(output_path=directory)
            html_to_image_converter.screenshot(url=url, save_as="screenshot.png")
        
        except Exception as ex:
            print(f"Error taking screenshot of {url}: {ex}")
        
    async def extract_html_from_site(self, session, url: str) -> str:
        async with session.get(url) as response:
            return await response.text()

    def collect_resources(self, html: str) -> list[str]:
        return list(set(re.findall(r'(?:src|href)=["\'](.*?)["\']', html)))


    def encode_image(self, directory: Path) -> str:
        image_path = directory / "screenshot.png"
        with image_path.open("rb") as img:
            return base64.b64encode(img.read()).decode("utf-8")

    def save_json(self, data: dict, directory: Path):
        out_file = directory / "browse.json"
        with out_file.open("w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)

    async def scrape(self, session, url: str, directory: Path):
        directory.mkdir(exist_ok=True)

        html = await self.extract_html_from_site(session, url)
        resources = self.collect_resources(html)

        self.take_screenshot(url, directory)
        screenshot64 = self.encode_image(directory)

        self.save_json({
            "html": html,
            "resources": resources,
            "screenshot": screenshot64
        }, directory)


async def main():
    scraper = WebScraper()
    out_root = APP_ROOT_PATH / "output"
    out_root.mkdir(exist_ok=True)

    async with aiohttp.ClientSession() as session:
        tasks = []

        for idx, url in enumerate(scraper.urls):
            path = out_root / f"url_{idx}"
            tasks.append(scraper.scrape(session, url, path))

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
