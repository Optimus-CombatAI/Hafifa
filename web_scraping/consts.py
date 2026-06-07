import os

PAGE_TIMEOUT_MS = int(os.getenv("PAGE_TIMEOUT_MS", "120000"))
INPUT_FILE = "input/urls.input"
OUTPUT_DIR = "output"
SCREENSHOT_PATH_NAME = "screenshot.png"
JSON_PATH_NAME = "browse.json"