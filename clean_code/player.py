from mutagen.easyid3 import EasyID3
from tkinter.filedialog import *
from tkinter import *
import pygame
from dataclasses import dataclass
from typing import Callable

# Window configuration
WINDOW_SIZE = "500x500"
WINDOW_TITLE = "MP3 Music Player"

# Button configuration
BUTTON_WIDTH = 40
BUTTON_BG_COLOR = "AntiqueWhite1"

# Display configuration
PLAYLIST_WIDTH = 60
SONG_LABEL_BG_COLOR = "ivory2"
SONG_LABEL_FG_COLOR = "Black"
SONG_LABEL_FONT = ("Helvetica 12 bold italic", 10)

# Pygame configuration
SONG_END_EVENT = pygame.USEREVENT + 1

pygame.init()


@dataclass
class ButtonConfig:
    """Store the configuration of a control button."""

    text: str
    command: Callable[[], None]
    row: int


class Controls(Frame):
    """Manage the music player controls and user interactions."""

    def __init__(self, master, player, display) -> None:
        """Initialize the control buttons and their associated actions."""
        super().__init__(master)

        self.player = player
        self.display = display
        self.grid(row=0, column=0)
        self._create_buttons()

    def _create_buttons(self) -> None:
        """Create and position the music player control buttons."""
        buttons = [
            ButtonConfig(text="PLAY SONG", command=self.play_song, row=2),
            ButtonConfig(text="PREVIOUS SONG", command=self.play_previous_song, row=4),
            ButtonConfig(text="PAUSE/UNPAUSE", command=self.player.toggle_pause, row=3),
            ButtonConfig(text="NEXT SONG", command=self.play_next_song, row=5),
            ButtonConfig(text="ADD TO LIST", command=self.add_songs, row=1)
        ]

        for button in buttons:
            btn = Button(
                self,
                text=button.text,
                command=button.command,
                bg=BUTTON_BG_COLOR,
                width=BUTTON_WIDTH
            )
            btn.grid(row=button.row, column=0)

    def _refresh_current_song(self) -> None:
        """Refresh the current song display."""
        self.display.update_current_song(self.player.get_current_song_info())

    def play_song(self) -> None:
        """Play the selected song and update the display."""
        self.player.play_song()
        self._refresh_current_song()

    def add_songs(self) -> None:
        """Add selected songs to the playlist and refresh its display."""
        directory = askopenfilenames()

        for song_dir in directory:
            print(song_dir)
            self.player.add_song(song_dir)

        self.display.update_playlist(self.player.playlist)

    def play_next_song(self) -> None:
        """Play the next song and update the display."""
        self.player.play_next_song()
        self._refresh_current_song()

    def play_previous_song(self) -> None:
        """Play the previous song and update the display."""
        self.player.play_previous_song()
        self._refresh_current_song()


class DisplayFrame(Frame):
    """Display the current song information and the playlist."""

    def __init__(self, master) -> None:
        """Initialize and arrange the song label and playlist widgets."""
        super().__init__(master)
        self.grid(row=1, column=0)
        self.current_song_label = Label(
            self,
            fg=SONG_LABEL_FG_COLOR,
            font=SONG_LABEL_FONT,
            bg=SONG_LABEL_BG_COLOR
        )
        self.current_song_label.grid(row=0, column=0)

        self.playlist_text = Text(self, wrap=WORD, width=PLAYLIST_WIDTH)
        self.playlist_text.grid(row=1, column=0)

    def update_playlist(self, songs: list[str]) -> None:
        """Refresh the displayed playlist."""
        self.playlist_text.delete(0.0, END)

        for index, item in enumerate(songs):
            song = EasyID3(item)
            song_data = self._format_song(song, index)
            self.playlist_text.insert(END, song_data + '\n')

    @staticmethod
    def _format_song(song: EasyID3, index: int) -> str:
        """Format a song's index, title, and artist for playlist display."""
        return f"{index + 1} : {song['title'][0]} - {song['artist'][0]}"

    def update_current_song(self, song_info: str) -> None:
        """Update the displayed current song information."""
        self.current_song_label["text"] = song_info


class MusicPlayer:
    """Manage the playlist, playback controls, and current song state."""

    def __init__(self) -> None:
        """Initialize the playlist, playback state, and song-end event."""
        self.playlist = []
        self.is_paused = False
        self.current_song_index = 0
        self.SONG_END = SONG_END_EVENT

    def get_next_song_index(self) -> int:
        """Return the next song index, wrapping to the first song if needed."""
        if self.current_song_index + 2 <= len(self.playlist):
            return self.current_song_index + 1
        else:
            return 0

    def get_previous_song_index(self) -> int:
        """Return the previous song index, wrapping to the last song if needed."""
        if self.current_song_index - 1 >= 0:
            return self.current_song_index - 1
        else:
            return len(self.playlist) - 1

    def play_song(self) -> None:
        """Load and play the current song, resetting the pause state."""
        directory = self.playlist[self.current_song_index]
        pygame.mixer.music.load(directory)
        pygame.mixer.music.play(1, 0.0)
        pygame.mixer.music.set_endevent(self.SONG_END)
        self.is_paused = False

    def toggle_pause(self) -> None:
        """Toggle between paused and playing states."""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            pygame.mixer.music.pause()
            self.is_paused = True

    def play_previous_song(self) -> None:
        """Switch to the previous song and start playing it."""
        self.current_song_index = self.get_previous_song_index()
        self.play_song()

    def play_next_song(self) -> None:
        """Switch to the next song and start playing it."""
        self.current_song_index = self.get_next_song_index()
        self.play_song()

    def check_song_end(self) -> None:
        """Check for song-end events and automatically play the next song."""
        for event in pygame.event.get():
            if event.type == self.SONG_END:
                self.play_next_song()

    def get_current_song_info(self) -> str:
        """Return the current song's number, title, and artist as a string."""
        song = EasyID3(self.playlist[self.current_song_index])

        return (f"Now playing: Nr:{self.current_song_index + 1} "
                f"{song['title'][0]} - {song['artist'][0]}")

    def add_song(self, song_dir: str) -> None:
        """Add a song to the playlist."""
        self.playlist.append(song_dir)


window = Tk()
window.geometry(WINDOW_SIZE)
window.title(WINDOW_TITLE)

player = MusicPlayer()
display = DisplayFrame(window)
app = Controls(window, player, display)

while True:
    previous_index = player.current_song_index

    player.check_song_end()

    if player.current_song_index != previous_index:
        display.update_current_song(player.get_current_song_info())

    app.update()
