import os
import json
import time
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver


def create_output_dir(directory="output"):
    if not os.path.exists(directory):
        os.mkdir(directory)


def get_urls_from_file(input_file="input/urls.input"):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} does not exist")

    with open(input_file, "r") as file:
        return file.read().splitlines()


def initialize_driver():
    return webdriver.Chrome()


def get_html_content(driver):
    return driver.page_source


def get_resources(driver):
    resources = set()
    for resource in driver.execute_script("return window.performance.getEntriesByType('resource')"):
        resources.add(resource['name'])
    return list(resources)


def save_screenshot_png(driver, output_path):
    screenshot_path = os.path.join(output_path, "screenshot.png")
    driver.save_screenshot(screenshot_path)


def get_screenshot_base64(driver):
    return driver.get_screenshot_as_base64()


def save_browse_data(output_path, browse_data):
    browse_json_path = os.path.join(output_path, "browse.json")
    with open(browse_json_path, "w") as file:
        json.dump(browse_data, file, indent=4)


def browse_url(url, url_index):
    output_path = f"output/url_{url_index + 1}"
    os.makedirs(output_path, exist_ok=True)

    driver = initialize_driver()

    try:
        driver.get(url)
        time.sleep(3)

        html_content = get_html_content(driver)
        resources = get_resources(driver)
        save_screenshot_png(driver, output_path)
        screenshot_base64 = get_screenshot_base64(driver)

        browse_data = {
            "html": html_content,
            "resources": resources,
            "screenshot": screenshot_base64
        }

        save_browse_data(output_path, browse_data)
    finally:
        driver.quit()


def process_urls(urls):
    with ThreadPoolExecutor() as executor:
        for index, url in enumerate(urls):
            executor.submit(browse_url, url, index)


def main():
    create_output_dir()
    urls = get_urls_from_file()
    process_urls(urls)


if __name__ == '__main__':
    main()
