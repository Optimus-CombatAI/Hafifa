from collections.abc import Callable
from dataclasses import dataclass

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

from config import (
    BUTTON_BG,
    BUTTON_PADY,
    BUTTON_WIDTH,
    LAYOUT_START_COLUMN,
    LAYOUT_START_ROW,
)


@dataclass
class SongData:
    local_song_path: str
    title: str = "Unknown title"
    artist: str = "Unknown artist"

    def __post_init__(self):
        try:
            metadata = EasyID3(self.local_song_path)
        except (ID3NoHeaderError, OSError, ValueError):
            return

        self.title = metadata.get("title", [self.title])[0]
        self.artist = metadata.get("artist", [self.artist])[0]

    def __str__(self):
        return f"{self.title} - {self.artist}"


@dataclass
class ButtonConfig:
    text_display: str
    functionality: Callable[[], None]
    bg: str = BUTTON_BG
    width: int = BUTTON_WIDTH
    row: int = LAYOUT_START_ROW
    column: int = LAYOUT_START_COLUMN
    pady: int = BUTTON_PADY
