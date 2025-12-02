import asyncio
import base64
import json
from pathlib import Path
from typing import Tuple

from bs4 import BeautifulSoup
import tldextract
from playwright.async_api import async_playwright

from constants import DRIVER, URLS
from models.DataSaveFormat import DataSaveFormat
from models.HtmlData import HtmlData


async def get_page_data(url: str) -> Tuple[str, bytes]:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded")

        html_content = await page.content()
        screenshot_bytes = await page.screenshot(type="png")
        await browser.close()

        return html_content, screenshot_bytes


def store_url_data(folder_path: Path, data: DataSaveFormat) -> None:
    with open(f"{folder_path}/browse.json", "w") as file:
        json.dump(data, file, indent=4)


def get_folder_path(url: str) -> Path:
    domain = tldextract.extract(url).domain
    folder_path = Path(f"output/{domain}")

    return folder_path


def get_resources(html_content: str) -> HtmlData:
    html_soup = BeautifulSoup(html_content, "html.parser")

    imgs = [img.get("src") for img in html_soup.find_all("img") if img.get("src")]
    scripts = [script.get("src") for script in html_soup.find_all("script") if script.get("src")]
    links = [link.get("href") for link in html_soup.find_all("link") if link.get("href")]
    anchors = [href.get("href") for href in html_soup.find_all("a") if href.get("href")]

    return HtmlData(images=imgs, scripts=scripts, links=links, anchors=anchors)


async def get_info_from_url(url: str) -> None:
    html_content, screenshot_bytes = await get_page_data(url)
    resources = get_resources(html_content)

    folder_path = get_folder_path(url)

    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)

    img_path = f"{folder_path}/screenshot.png"

    with open(img_path, "wb") as f:
        f.write(screenshot_bytes)

    data_to_save = DataSaveFormat(
        html=BeautifulSoup(html_content, "html.parser").prettify(),
        resources=resources,
        screenshot=base64.b64encode(screenshot_bytes).decode('utf-8')
    )

    store_url_data(folder_path, data_to_save)


async def main() -> None:
    await asyncio.gather(*(get_info_from_url(url) for url in URLS))


if __name__ == '__main__':
    asyncio.run(main())

DRIVER.quit()
