from pathlib import Path
from html2image import Html2Image
from abc import ABC, abstractmethod
from htmlwebshot import WebShot


class ScreenShotHTML(ABC):
    @abstractmethod
    def take_screenshot(self, source: str, output_path: str):
        pass


class HTML2ImageScreenShotEngine(ScreenShotHTML):
    def __init__(self):
        self.hti = Html2Image()

    def take_screenshot(self, source: str, output_path: Path):
        self.hti.screenshot(html_file=source, save_as=output_path)


class HTMLWebShotEngine(ScreenShotHTML):
    def __init__(self):
        self.shot = WebShot()
        self.shot.flags = ["--quiet",
                           "--enable-javascript", "--no-stop-slow-scripts"]

    def take_screenshot(self, source: str, output_path: Path):
        return self.shot.create_pic(url=source, output=output_path)
