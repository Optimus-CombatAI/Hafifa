from src.input_reader import FileLineReader
from consts import INPUT_FILE

input = FileLineReader(INPUT_FILE)
urls = input.get_input()

for url in urls:
    print(url[:-1])
