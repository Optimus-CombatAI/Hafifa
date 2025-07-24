from src.input_reader import FileLineReader
from src.html_extractor import RequestsHTMLExtractor
from src.html_parser import SoupHTMLParser
from consts import INPUT_FILE

input = FileLineReader(INPUT_FILE)
urls = input.get_input()

for url in urls:
    extractor = RequestsHTMLExtractor(url)
    html_content = extractor.get_html()
    urls = SoupHTMLParser(html_content).get_all_urls()
    print(f'{url}: \n{html_content}\nlinks: {urls}')
