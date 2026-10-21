from playwright.sync_api import sync_playwright
import os
import json
import base64
from pathlib import Path

def main():
    with open("input/urls.input", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"Found {len(urls)} urls")

    os.makedirs("output", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for i, url in enumerate(urls, start=1):
            print(f"\nProcessing {url} ...")

            folder = Path("output") / f"url_{i}"
            folder.mkdir(exist_ok=True)

            page = browser.new_page()

            resources = []

            def handle_request(request):
                resources.append(request.url)

            page.on("request", handle_request)

            try:
                page.goto(url, wait_until="networkidle", timeout=60000)

                html = page.content()

                screenshot_path = folder / "screenshot.png"
                page.screenshot(path=str(screenshot_path), full_page=True)

                with open(screenshot_path, "rb") as img_file:
                    screenshot_b64 = base64.b64encode(img_file.read()).decode("utf-8")

                data = {
                    "html": html,
                    "resources": resources,
                    "screenshot": screenshot_b64
                }

                with open(folder / "browse.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                print(f"Finished url_{i}")

            except Exception as e:
                print(f"Error with {url}: {e}")

            finally:
                page.close()

        browser.close()

    print("\nAll done!")

if __name__ == "__main__":
    main()