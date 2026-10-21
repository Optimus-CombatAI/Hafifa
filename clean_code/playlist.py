import logging
import tkinter as tk
from tkinter import filedialog

from models import SongData

logger = logging.getLogger(__name__)


class PlaylistManager:
    def __init__(self):
        self.songs = []
        self.playlist_display = None

    def add_songs(self):
        paths = self.select_song_paths()
        added_count = self.add_songs_from_paths(paths)

        self.update_displayed_playlist()
        self.log_added_songs(added_count)

    def select_song_paths(self):
        return filedialog.askopenfilenames(
            title="Select MP3 files",
            filetypes=[("MP3 files", "*.mp3")],
        )

    def add_songs_from_paths(self, paths):
        added_count = 0

        for path in paths:
            if self.add_song_from_path(path):
                added_count += 1

        return added_count

    def add_song_from_path(self, path):
        try:
            song = SongData(path)
        except (OSError, ValueError) as error:
            logger.warning("Could not load song %s: %s", path, error)
            return False

        self.songs.append(song)
        return True

    def log_added_songs(self, added_count):
        if added_count:
            logger.info("Added %d song(s) to playlist", added_count)

    def display_list(self):
        for number, song in enumerate(self.songs, start=1):
            self.playlist_display.insert(
                tk.END,
                f"{number}. {song}\n",
            )

    def update_displayed_playlist(self):
        self.playlist_display.delete("1.0", tk.END)
        self.display_list()
