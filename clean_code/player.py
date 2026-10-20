
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from tkinter import filedialog

import pygame
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

# MP3 music-player

# -------------------- Configuration --------------------

@dataclass 
class AppConfig:
    title: str = "MP3 Music Player"
    geometry: str = "500x500"

# Button configuration, implemented default values from the original file
@dataclass
class ButtonConfig:
    text: str
    command: Callable[[], None] # Functionality
    bg: str = "AntiqueWhite1"
    width: int = 40
    row: int = 0
    column: int = 0
    pady: int = 2


@dataclass
class SongData:
    path: str # File path locally
    title: str = "Unknown title"
    artist: str = "Unknown artist"

    def __post_init__(self):
        try:
            metadata = EasyID3(self.path)
        except ID3NoHeaderError:
            return

        self.title = metadata.get("title", [self.title])[0]
        self.artist = metadata.get("artist", [self.artist])[0]

    def __str__(self):
        return f"{self.title} - {self.artist}" # Kept the str view from original file


# -------------------- Playlist --------------------

class PlaylistManager:
    def __init__(self, parent):
        self.songs = []
        self.text = tk.Text(
            parent,
            width=60,
            height=10,
            wrap=tk.WORD
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

        self.refresh()

    # Displays the playlist in the following format: (e.g)
    # 1. Title - Artist
    # 2. Title - Artist
    # ...
    def displayList(self):
        for number, song in enumerate(self.songs, start=1):
            self.text.insert(tk.END, f"{number}. {song}\n")

    # Updates the playlist displayed in the Tkinter text box
    def refresh(self):
        self.text.delete("1.0", tk.END)
        self.displayList()
        


# -------------------- Music Player --------------------

# Handles playing, pausing and other functionalities of a music-player
class MusicPlayer:
    def __init__(self, playlist):
        self.playlist = playlist # Playlist object
        self.song_index = 0 # The index of the currently selected song
        self.paused = False # Tracks whether playback is paused. Initially, it is not paused.
        self.auto_play = True # Determines whether the player automatically advances to the next song when the current song ends
        self.on_song_change = None # A placeholder for a function to call when the playing song changes. Initially, no function is assigned.

        self.song_end = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.song_end)

    def play(self):
        if not self.playlist.songs:
            return

        song = self.playlist.songs[self.song_index]
        pygame.mixer.music.load(song.path)
        pygame.mixer.music.play()
        self.paused = False
        self._notify_song_change()

    def toggle_pause(self):
        if not self.playlist.songs:
            return

        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

        self.paused = not self.paused

    def next(self):
        if not self.playlist.songs:
            return

        self.song_index = (self.song_index + 1) % len(self.playlist.songs)
        self.play()

    def previous(self):
        if not self.playlist.songs:
            return

        self.song_index = (self.song_index - 1) % len(self.playlist.songs)
        self.play()

    def toggle_auto_play(self):
        self.auto_play = not self.auto_play

    # Notify another component that the currently playing song has changed
    def _notify_song_change(self):
        if self.on_song_change:
            self.on_song_change()

    # Check if the current song has ended and automatic playback is enabled.
    # If so, play the next song
    def check_song_ended(self, root):
        for event in pygame.event.get():
            if event.type == self.song_end and self.auto_play:
                self.next()

        # schedules the check every 100 milliseconds
        root.after(100, lambda: self.check_song_ended(root))


# -------------------- Main Frame --------------------

# Build the (GUI) and connect its widgets to the playlist and music player
class FrameApp(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()

        self.create_components()
        self.create_buttons()
        self.layout_widgets()

        # Setting the "update_status" func to happen on song change
        self.player.on_song_change = self.update_status
        self.player.check_song_ended(root)

    def no_song_playing_display(self):
        # creates a label that initially displays "No song playing"
        self.status = tk.Label(
            self,
            text="No song playing",
            fg="black",
            font=("Helvetica", 12, "bold italic"),
            bg="ivory2"
        )
        
    
    # Creates the main objects and widgets used by the GUI
    def create_components(self):
        self.playlist = PlaylistManager(self)
        self.player = MusicPlayer(self.playlist)
        self.no_song_playing_display()

    # Defines the configuration for each button and returns a list of ButtonConfig objects
    def create_button_configs(self):
        return [
            ButtonConfig(
                text="ADD TO LIST",
                command=self.playlist.add_songs,
                row=0,
                column=0
            ),
            ButtonConfig(
                text="PLAY SONG",
                command=self.player.play,
                row=1,
                column=0
            ),
            ButtonConfig(
                text="PREVIOUS SONG",
                command=self.player.previous,
                row=2,
                column=0
            ),
            ButtonConfig(
                text="PAUSE/UNPAUSE",
                command=self.player.toggle_pause,
                row=3,
                column=0
            ),
            ButtonConfig(
                text="NEXT SONG",
                command=self.player.next,
                row=4,
                column=0
            ),
        ]

    # Creates the actual Tkinter buttons using the configurations returned by create_button_configs()
    def create_buttons(self):
        self.button_configs = self.create_button_configs()

        for config in self.button_configs:
            tk.Button(
                self,
                text=config.text,
                command=config.command,
                bg=config.bg,
                width=config.width
            ).grid(
                row=config.row,
                column=config.column,
                pady=config.pady
            )

    # Positions the status label and playlist text box beneath the buttons
    def layout_widgets(self):
        status_row = max(
            (button.row for button in self.button_configs),
            default=-1
        ) + 1

        self.status.grid(row=status_row, column=0, pady=10)
        self.playlist.text.grid(
            row=status_row + 1,
            column=0,
            pady=10
        )

    # Updates the status label to show the currently playing song
    def update_status(self):
        song = self.playlist.songs[self.player.song_index]
        self.status.config(text=f"Now playing: {song}")


# -------------------- Application Window --------------------

# initialize, launch, and shut down the application
class MusicPlayerApp:
    def __init__(self, config=None):
        pygame.init()

        self.config = config or AppConfig()
        self.root = tk.Tk()
        self.root.title(self.config.title)
        self.root.geometry(self.config.geometry)

        self.frame = FrameApp(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def run(self):
        self.root.mainloop()

    def close(self):
        pygame.mixer.music.stop()
        self.root.destroy()
        pygame.quit()


if __name__ == "__main__":
    MusicPlayerApp().run()
