
import asyncio
import base64
import json
import os

from dataclasses import asdict, dataclass
from functools import partial

from playwright.async_api import Browser, Page, Request, TimeoutError, Error, async_playwright

MAX_CONCURRENT_TASKS = 5
PAGE_WAIT_TIMEOUT_MS = 8000


@dataclass
class PageData:
    """Store the HTML, resources, and screenshot of a scraped page."""
    html: str
    resources: list[str]
    screenshot: str


def collect_request(request: Request, resources: list[str]) -> None:
    """Add the URL of a network request to the resources list."""
    resources.append(request.url)


def encode_screenshot(screenshot: bytes) -> str:
    """Convert screenshot bytes into a Base64 string."""
    return base64.b64encode(screenshot).decode("utf-8")


async def take_screenshot(page: Page, url_index: int) -> bytes:
    """Take a screenshot and save it to the corresponding output folder."""
    return await page.screenshot(path=f"output/url_{url_index}/screenshot.png")


async def get_html(page: Page) -> str:
    """Return the HTML content of the page."""
    return await page.content()


def get_resources(page: Page) -> list[str]:
    """Register a listener to collect network requests during page loading."""
    resources = []
    page.on("request", partial(collect_request, resources=resources))
    return resources


async def scrape_url(url_index: int, url: str, navigator: Browser, semaphore: asyncio.Semaphore) -> None:
    """Scrape a URL and save its HTML, requested resources, and screenshot."""
    async with semaphore:
        print(f"Starting to scrape {url}")
        os.makedirs(f"output/url_{url_index}", exist_ok=True)

        context = await navigator.new_context()

        try:
            page = await context.new_page()

            resources = get_resources(page)

            try:
                await page.goto(url, wait_until="domcontentloaded")
            except TimeoutError:
                print(f"Timeout while loading {url}")
                return

            await page.wait_for_timeout(PAGE_WAIT_TIMEOUT_MS)

            screenshot = await take_screenshot(page, url_index)
            img_in_str = encode_screenshot(screenshot)

            html = await get_html(page)

            data = PageData(
                html=html,
                resources=resources,
                screenshot=img_in_str
            )

            with open(f"output/url_{url_index}/browse.json", "w", encoding="utf-8") as file:
                json.dump(asdict(data), file)

            print(f"{url}: {len(resources)} resources")

        except Error as error:
            print(f"Playwright error while scraping {url}: {error}")

        except OSError as error:
            print(f"File error while scraping {url}: {error}")

        finally:
            await context.close()


async def main() -> None:
    """Read input URLs and run scraping tasks concurrently."""
    play = await async_playwright().start()

    try:
        navigator = await play.chromium.launch(headless=False)

        try:
            with open("input/urls.input", "r") as file:
                content = file.readlines()

            urls = []

            for line in content:
                line = line.strip()

                if line != "":
                    urls.append(line)

            semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

            tasks = []

            for i, url in enumerate(urls, start=1):
                tasks.append(scrape_url(i, url, navigator, semaphore))

            await asyncio.gather(*tasks)

        finally:
            await navigator.close()

    finally:
        await play.stop()


asyncio.run(main())
