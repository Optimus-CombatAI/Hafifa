from src.input_reader import FileLineReader
from src.scraper import WebScraper
from consts import INPUT_FILE, SCREENSHOT_NAME

input = FileLineReader(INPUT_FILE)
urls = input.get_input()

for url in urls:
    scraper = WebScraper(url)
    result = scraper.scrape()
