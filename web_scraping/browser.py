from src.input_reader import FileLineReader
from src.html_extractor import RequestsHTMLExtractor
from consts import INPUT_FILE

input = FileLineReader(INPUT_FILE)
urls = input.get_input()

for url in urls:
    extractor = RequestsHTMLExtractor(url)
    print(f'{url}: {extractor.get_html()}')
