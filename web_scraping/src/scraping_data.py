from pathlib import Path
from pydantic import BaseModel
from typing import List
from base64 import b64encode


class ScrapingData(BaseModel):
    html: str = None
    resources: List[str] = None
    screenshot: str = None

    def set_screenshot(self, screenshot_path: Path):
        with open(screenshot_path, 'rb') as file:
            self.screenshot = str(b64encode(file.read()))
