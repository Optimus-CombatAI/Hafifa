
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from tkinter import filedialog

import pygame
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

# MP3 music-player

# -------------------- Configuration --------------------

SONG_END_CHECK_INTERVAL_MS = 100

PLAYLIST_TEXT_WIDTH = 60
PLAYLIST_TEXT_HEIGHT = 10
PLAYLIST_TEXT_WRAP = tk.WORD

BUTTON_BG = "AntiqueWhite1"
BUTTON_WIDTH = 40
BUTTON_PADY = 2

DEFAULT_ROW = 0
DEFAULT_COLUMN = 0
DEFAULT_PADY = 2

DEFAULT_TITLE = "MP3 Music Player"
DEFAULT_GEOMETRY = "500x500"

DEFAULT_LAYOUT_WIDGETS_PADY = 10

@dataclass 
class AppConfig:
    title: str = DEFAULT_TITLE
    geometry: str = DEFAULT_GEOMETRY

@dataclass
class ButtonConfig:
    button_display: str
    button_functionality: Callable[[], None] 
    bg: str = BUTTON_BG
    width: int = BUTTON_WIDTH
    row: int = DEFAULT_ROW
    column: int = DEFAULT_COLUMN
    pady: int = DEFAULT_PADY


@dataclass
class SongData:
    local_song_path: str 
    title: str = "Unknown title"
    artist: str = "Unknown artist"

    def __post_init__(self):
        try:
            metadata = EasyID3(self.local_song_path)
        except ID3NoHeaderError:
            return

        self.title = metadata.get("title", [self.title])[0]
        self.artist = metadata.get("artist", [self.artist])[0]

    def __str__(self):
        return f"{self.title} - {self.artist}" 


# -------------------- Playlist --------------------

class PlaylistManager:
    def __init__(self, parent):
        self.songs = []
        self.playlist_display = tk.Text(
            parent,
            width=PLAYLIST_TEXT_WIDTH,
            height=PLAYLIST_TEXT_HEIGHT,
            wrap=PLAYLIST_TEXT_WRAP
        )

    def add_songs(self):
        paths = filedialog.askopenfilenames(
            title="Select MP3 files",
            filetypes=[("MP3 files", "*.mp3")]
        )

        for path in paths:
            try:
                self.songs.append(SongData(path))
            except (OSError, ValueError):
                continue

        self.update_displayed_playlist()

    # Displays the playlist in the following format: (e.g)
    # 1. Title - Artist
    # 2. Title - Artist
    # ...
    def displayList(self):
        for number, song in enumerate(self.songs, start=1):
            self.playlist_display.insert(tk.END, f"{number}. {song}\n")

    def update_displayed_playlist(self):
        self.playlist_display.delete("1.0", tk.END)
        self.displayList()
        


# -------------------- Music Player --------------------

class MusicPlayer:
    def __init__(self, playlist):
        self.playlist = playlist 
        self.current_song_index = 0 
        self.playlist_paused = False 
        self.auto_play = True
        self.on_song_change = None 

        self.song_end = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.song_end)

    def play(self):
        if not self.playlist.songs:
            return

        song = self.playlist.songs[self.current_song_index]
        pygame.mixer.music.load(song.local_song_path)
        pygame.mixer.music.play()
        self.playlist_paused = False
        self._notify_song_change()

    def toggle_pause(self):
        if not self.playlist.songs:
            return

        if self.playlist_paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

        self.playlist_paused = not self.playlist_paused

    def next(self):
        if not self.playlist.songs:
            return

        self.current_song_index = (self.current_song_index + 1) % len(self.playlist.songs)
        self.play()

    def previous(self):
        if not self.playlist.songs:
            return

        self.current_song_index = (self.current_song_index - 1) % len(self.playlist.songs)
        self.play()

    def toggle_auto_play(self):
        self.auto_play = not self.auto_play

    
    def _notify_song_change(self):
        if self.on_song_change:
            self.on_song_change()

    def is_auto_play_enabled(self):
        return self.auto_play

    def play_next_song(self):
        if self.is_auto_play_enabled():
            self.next()
            self._notify_song_change()
    
    def check_song_ended(self, root):
        for event in pygame.event.get():
            if event.type == self.song_end:
                self.play_next_song()

        self.schedule_song_end_check(root)
        
    def schedule_song_end_check(self, root):
        root.after(SONG_END_CHECK_INTERVAL_MS, lambda: self.check_song_ended(root))


# -------------------- Main Frame --------------------

class GUI_Handler(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()

        self.create_components()
        self.create_buttons_from_configs()
        self.layout_widgets_below_buttons()

        self.player.on_song_change = self.update_current_song_display
        self.player.check_song_ended(root)

    def no_song_playing_display(self):
        self.status = tk.Label(
            self,
            text="No song playing",
            fg="black",
            font=("Helvetica", 12, "bold italic"),
            bg="ivory2"
        )
        
    
    def create_components(self):
        self.playlist = PlaylistManager(self)
        self.player = MusicPlayer(self.playlist)
        self.no_song_playing_display()

    def create_button_configs(self):
        return [
            ButtonConfig(
                button_display="ADD TO LIST",
                button_functionality=self.playlist.add_songs,
                row=0,
                column=0
            ),
            ButtonConfig(
                button_display="PLAY SONG",
                button_functionality=self.player.play,
                row=1,
                column=0
            ),
            ButtonConfig(
                button_display="PREVIOUS SONG",
                button_functionality=self.player.previous,
                row=2,
                column=0
            ),
            ButtonConfig(
                button_display="PAUSE/UNPAUSE",
                button_functionality=self.player.toggle_pause,
                row=3,
                column=0
            ),
            ButtonConfig(
                button_display="NEXT SONG",
                button_functionality=self.player.next,
                row=4,
                column=0
            ),
        ]

    def create_buttons_from_configs(self):
        self.button_configs = self.create_button_configs()

        for config in self.button_configs:
            tk.Button(
                self,
                text=config.button_display,
                command=config.button_functionality,
                bg=config.bg,
                width=config.width
            ).grid(
                row=config.row,
                column=config.column,
                pady=config.pady
            )

    def layout_widgets_below_buttons(self):
        status_row = max(
            (button.row for button in self.button_configs),
            default=-1
        ) + 1

        self.status.grid(row=status_row, column=DEFAULT_COLUMN, pady=DEFAULT_LAYOUT_WIDGETS_PADY)
        self.playlist.playlist_display.grid(
            row=status_row + 1,
            column=DEFAULT_COLUMN,
            pady=DEFAULT_LAYOUT_WIDGETS_PADY
        )

    def update_current_song_display(self):
        song = self.playlist.songs[self.player.current_song_index]
        self.status.config(text=f"Now playing: {song}")


# -------------------- Application Window --------------------

class MusicPlayerApp:
    def __init__(self, config=None):
        pygame.init()

        self.config = config or AppConfig()
        self.root = tk.Tk()
        self.root.title(self.config.title)
        self.root.geometry(self.config.geometry)

        self.frame = GUI_Handler(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def run(self):
        self.root.mainloop()

    def close(self):
        pygame.mixer.music.stop()
        self.root.destroy()
        pygame.quit()


if __name__ == "__main__":
    MusicPlayerApp().run()
