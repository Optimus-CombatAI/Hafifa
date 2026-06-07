import os
import json
import asyncio
import base64
from typing import List
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup

from consts import INPUT_FILE, OUTPUT_DIR, PAGE_TIMEOUT_MS,SCREENSHOT_PATH_NAME,JSON_PATH_NAME
from logger_config import logger


def read_non_empty_lines(file_path: str) -> List[str]:
    
    logger.info(f"Reading text file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    logger.debug(f"Found {len(lines)} non-empty lines")

    return lines


async def navigate_page(page: Page, url: str) -> None:
    
    logger.debug(f"Navigating to: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)


def create_output_folders(urls: List[str]) -> None:
    """
    Create output/url_N folders for each URL.
    """
    logger.info("Creating output folders...")

    os.makedirs(OUTPUT_DIR, exist_ok=True) 

    for index in range(1, len(urls) + 1):
        folder = os.path.join(OUTPUT_DIR, f"url_{index}")
        os.makedirs(folder, exist_ok=True)

    logger.debug("Output folder structure created successfully.")



async def get_html(page: Page, url: str) -> str:
    """
    Load a web page and return its HTML content, prettified
    with BeautifulSoup (multi-line, indenté).
    """
    logger.debug(f"Loading HTML for: {url}")

    await navigate_page(page,url)
    raw_html = await page.content()

    prettified_html = BeautifulSoup(raw_html, "html.parser").prettify()


    logger.debug(f"HTML fetched for {url} (size={len(prettified_html)} chars)")

    return prettified_html



async def get_resources(page: Page, url: str) -> List[str]:
    """
    Collect all resource URLs loaded by the page.
    """
    logger.debug(f"Collecting resources for {url}")
    resources: List[str] = []

    page.on("request", lambda req: resources.append(req.url))

    await navigate_page(page,url)

    logger.debug(f"Collected {len(resources)} resources for {url}")

    return resources



async def take_screenshot(page: Page, output_path: str) -> str:
    """
    Take screenshot of the entire page.
    """
    logger.debug(f"Taking screenshot: {output_path}")

    await page.screenshot(path=output_path, full_page=True, timeout=PAGE_TIMEOUT_MS)

    logger.debug("Screenshot saved.")

    return output_path



def encode_screenshot_to_base64(path: str) -> str:
    """
    Convert screenshot binary file to a base64 string.
    """
    logger.debug(f"Encoding screenshot to base64: {path}")

    with open(path, "rb") as image:
        encoded = base64.b64encode(image.read()).decode("utf-8")

    logger.debug("Screenshot converted to base64.")

    return encoded



async def process_url(browser: Browser, url: str, output_folder: str) -> None:
    """
    Process a single URL:
    - Fetch HTML (prettified)
    - Fetch resources
    - Take screenshot
    - Write browse.json

    Args:
        browser (Browser): Playwright browser instance.
        url (str): URL to scrape.
        output_folder (str): Already-built folder path where output files will be stored.
    """
    logger.info(f"Processing URL: {url}")

    screenshot_path = os.path.join(output_folder, SCREENSHOT_PATH_NAME)
    json_path = os.path.join(output_folder, JSON_PATH_NAME)

    page = await browser.new_page()

    try:
        html = await get_html(page, url)
        resources = await get_resources(page, url)
        await take_screenshot(page, screenshot_path)
        screenshot_encoded_to_b64 = encode_screenshot_to_base64(screenshot_path)

        data = {
            "html": html,
            "resources": resources,
            "screenshot": screenshot_encoded_to_b64,
        }

        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

        logger.info(f"Finished processing: {url}")

    except Exception as e:
        logger.error(f"Error while processing {url}: {e}")

    finally:
        await page.close()




async def run() -> None:   
    urls = read_non_empty_lines(INPUT_FILE)
    create_output_folders(urls)

    async with async_playwright() as playwright:
        async with await playwright.chromium.launch(headless=True) as browser:

            tasks = [
                process_url(
                    browser,
                    url,
                    os.path.join(OUTPUT_DIR, f"url_{index}")
                )
                for index, url in enumerate(urls, start=1)
            ]

            await asyncio.gather(*tasks)

    logger.info("All URLs processed successfully.")




if __name__ == "__main__":
    asyncio.run(run())
