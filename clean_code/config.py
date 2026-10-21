import os

from dotenv import load_dotenv

load_dotenv()


APP_GEOMETRY = os.getenv("APP_GEOMETRY", "500x500")

SONG_END_CHECK_INTERVAL_MS = int(os.getenv("SONG_END_CHECK_INTERVAL_MS", "100"))

PLAYLIST_TEXT_WIDTH = int(os.getenv("PLAYLIST_TEXT_WIDTH", "60"))

PLAYLIST_TEXT_HEIGHT = int(os.getenv("PLAYLIST_TEXT_HEIGHT", "10"))

LAYOUT_START_ROW = int(os.getenv("LAYOUT_START_ROW", "0"))

LAYOUT_START_COLUMN = int(os.getenv("LAYOUT_START_COLUMN", "0"))

BUTTON_BG = os.getenv("BUTTON_BG", "AntiqueWhite1")
BUTTON_WIDTH = int(os.getenv("BUTTON_WIDTH", "40"))
BUTTON_PADY = int(os.getenv("BUTTON_PADY", "2"))

LAYOUT_WIDGETS_PADY = int(os.getenv("LAYOUT_WIDGETS_PADY", "10"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
