from src.input_reader import FileLineReader
from src.html_extractor import RequestsHTMLExtractor
from src.html_parser import SoupHTMLParser
from src.screenshot import HTML2ImageScreenShotEngine, HTMLWebShotEngine
from consts import INPUT_FILE, SCREENSHOT_NAME

input = FileLineReader(INPUT_FILE)
urls = input.get_input()
screenshot_engine = HTMLWebShotEngine()

for url in urls:
    extractor = RequestsHTMLExtractor(url)
    html_content = extractor.get_html()
    urls = SoupHTMLParser(html_content).get_all_urls()
    screenshot = screenshot_engine.take_screenshot(url, SCREENSHOT_NAME)
    print(f'{url}: \n{html_content}\nlinks: {urls}, screenshot: {screenshot}')
