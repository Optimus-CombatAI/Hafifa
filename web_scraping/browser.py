import os
import json
import asyncio
import base64
from typing import List
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup

from consts import INPUT_FILE, OUTPUT_DIR
from logger_config import logger


# ============================================================
#  READ URL FILE
# ============================================================
def read_urls(file_path: str) -> List[str]:
    """
    Read URL list from input file.
    Returns a clean list of non-empty URLs.
    """
    logger.info(f"Reading input file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        urls = [line.strip() for line in file if line.strip()]

    logger.debug(f"Found {len(urls)} URLs")

    return urls


# ============================================================
#  CREATE OUTPUT FOLDERS
# ============================================================
def create_output_folders(urls: List[str]) -> None:
    """
    Create output/url_N folders for each URL.
    """
    logger.info("Creating output folders...")

    os.makedirs(OUTPUT_DIR, exist_ok=True) #if already exist continue...

    for index in range(1, len(urls) + 1):
        folder = os.path.join(OUTPUT_DIR, f"url_{index}")
        os.makedirs(folder, exist_ok=True)

    logger.debug("Output folder structure created successfully.")


# ============================================================
#  FETCH HTML
# ============================================================
async def get_html(page: Page, url: str) -> str:
    """
    Load a web page and return its HTML content, prettified
    with BeautifulSoup (multi-line, indenté).
    """
    logger.debug(f"Loading HTML for: {url}")

    await page.goto(url, wait_until="domcontentloaded", timeout=120_000)#only HTML structure
    raw_html = await page.content()

    # Prettify HTML with BeautifulSoup
    soup = BeautifulSoup(raw_html, "html.parser")
    pretty_html = soup.prettify()

    logger.debug(f"HTML fetched for {url} (size={len(pretty_html)} chars)")
    return pretty_html


# ============================================================
#  FETCH RESOURCES
# ============================================================
async def get_resources(page: Page, url: str) -> List[str]:
    """
    Collect all resource URLs loaded by the page.
    """
    resources: List[str] = []
    logger.debug(f"Collecting resources for {url}")

    page.on("request", lambda req: resources.append(req.url))

    await page.goto(url, wait_until="domcontentloaded", timeout=120_000)#Reload the page to ensure a clean state and capture all initial network requests.

    logger.debug(f"Collected {len(resources)} resources for {url}")
    return resources


# ============================================================
#  SCREENSHOT
# ============================================================
async def take_screenshot(page: Page, output_path: str) -> str:
    """
    Take screenshot of the entire page.
    """
    logger.debug(f"Taking screenshot: {output_path}")

    await page.screenshot(path=output_path, full_page=True, timeout=120_000)

    logger.debug("Screenshot saved.")
    return output_path


# ============================================================
#  BASE64 ENCODE
# ============================================================
def encode_screenshot_to_base64(path: str) -> str:
    """
    Convert screenshot binary file to a base64 string.
    """
    logger.debug(f"Encoding screenshot to base64: {path}")

    with open(path, "rb") as image:
        encoded = base64.b64encode(image.read()).decode("utf-8")

    logger.debug("Screenshot converted to base64.")
    return encoded


# ============================================================
#  PROCESS ONE URL
# ============================================================
async def process_url(browser: Browser, url: str, index: int) -> None:
    """
    Process a single URL:
    - Fetch HTML (prettified)
    - Fetch resources
    - Take screenshot
    - Write browse.json
    """
    logger.info(f"Processing URL #{index}: {url}")

    folder = os.path.join(OUTPUT_DIR, f"url_{index}")
    screenshot_path = os.path.join(folder, "screenshot.png")
    json_path = os.path.join(folder, "browse.json")

    page = await browser.new_page()

    try:
        html = await get_html(page, url)
        resources = await get_resources(page, url)
        await take_screenshot(page, screenshot_path)
        screenshot_b64 = encode_screenshot_to_base64(screenshot_path)

        data = {
            "html": html,              
            "resources": resources,
            "screenshot": screenshot_b64,
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        logger.info(f"Finished URL #{index}")

    except Exception as e:
        logger.error(f"Error while processing {url}: {e}")

    finally:
        await page.close()


# ============================================================
#  ASYNC RUNNER
# ============================================================
async def run() -> None:
    """Main async runner for the scraper."""
    urls = read_urls(INPUT_FILE)
    create_output_folders(urls)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        tasks = [
            process_url(browser, url, index)
            for index, url in enumerate(urls, start=1)
        ]

        await asyncio.gather(*tasks)
        await browser.close()

    logger.info("All URLs processed successfully.")


# ============================================================
#  ENTRY POINT
# ============================================================
if __name__ == "__main__":
    asyncio.run(run())
