import requests
from bs4 import BeautifulSoup
import lxml
import schedule
import pyautogui
import base64
import tldextract
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from constants import URLS, DRIVER
from pathlib import Path
import asyncio


def get_page_data(url: str) -> tuple[str, bytes]:
    DRIVER.get(url)
    WebDriverWait(DRIVER, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

    html_content = DRIVER.page_source
    screenshot_bytes = DRIVER.get_screenshot_as_png()

    return html_content, screenshot_bytes


def store_url_data(folder_path: Path, data: dict) -> None:
    with open(f"{folder_path}/browse.json", "w") as file:
        json.dump(data, file, indent=4)


def get_folder_path(url: str) -> Path:
    domain = tldextract.extract(url).domain
    folder_path = Path(f"output/{domain}")

    return folder_path


def get_resources(html_content: str) -> dict:
    html_soup = BeautifulSoup(html_content, "html.parser")  # parse it

    imgs = [img.get("src") for img in html_soup.find_all("img") if img.get("src")]
    scripts = [script.get("src") for script in html_soup.find_all("script") if script.get("src")]
    links = [link.get("href") for link in html_soup.find_all("link") if link.get("href")]
    anchors = [a.get("href") for a in html_soup.find_all("a") if a.get("href")]

    return {"images": imgs, "scripts": scripts, "links": links, "anchors": anchors}


async def handle_url(url: str) -> None:
    # print(url)
    html_content, screenshot_bytes = get_page_data(url)
    resources = get_resources(html_content)

    folder_path = get_folder_path(url)
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)

    img_path = f"{folder_path}/screenshot.png"

    with open(img_path, "wb") as f:
        f.write(screenshot_bytes)
    
    data_to_save = {
        "html": BeautifulSoup(html_content, "html.parser").prettify(),
        "resources": resources,
        "screenshot": base64.b64encode(screenshot_bytes).decode('utf-8')
    }

    store_url_data(folder_path, data_to_save)


async def main() -> None:
    await asyncio.gather(*(handle_url(url) for url in URLS))


if __name__ == '__main__':
    asyncio.run(main())

DRIVER.quit()
