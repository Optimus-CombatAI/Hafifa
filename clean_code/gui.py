import tkinter as tk

from config import (
    LAYOUT_START_COLUMN,
    LAYOUT_START_ROW,
    LAYOUT_WIDGETS_PADY,
    PLAYLIST_TEXT_HEIGHT,
    PLAYLIST_TEXT_WIDTH,
)
from models import ButtonConfig
from player import MusicPlayer
from playlist import PlaylistManager


class GUIHandler:
    def __init__(self, root):
        self.root = root
        self.buttons = []

        self.create_playlist_manager()
        self.create_music_player()
        self.create_components()
        self.arrange_components()

        self.player.on_song_change = self.update_current_song_display
        self.player.schedule_song_end_check(root)

    def create_playlist_manager(self):
        self.playlist = PlaylistManager()

    def create_music_player(self):
        self.player = MusicPlayer(self.playlist)

    def create_components(self):
        self.create_playlist_display()
        self.create_status_label()
        self.create_buttons()

    def create_playlist_display(self):
        self.playlist_display = tk.Text(
            self.root,
            width=PLAYLIST_TEXT_WIDTH,
            height=PLAYLIST_TEXT_HEIGHT,
            wrap=tk.WORD,
        )
        self.playlist.playlist_display = self.playlist_display

    def create_status_label(self):
        self.status_label = tk.Label(
            self.root,
            text="No song playing",
        )

    def create_button_configs(self):
        return [
            ButtonConfig("ADD TO LIST", self.playlist.add_songs),
            ButtonConfig("PLAY SONG", self.player.play),
            ButtonConfig("PREVIOUS SONG", self.player.previous_song),
            ButtonConfig("PAUSE/UNPAUSE", self.player.toggle_pause),
            ButtonConfig("NEXT SONG", self.player.next_song),
            ButtonConfig("AUTO PLAY: ON", self.toggle_auto_play),
        ]

    def create_buttons(self):
        self.buttons = []

        for config in self.create_button_configs():
            button = tk.Button(
                self.root,
                text=config.text_display,
                command=config.functionality,
                bg=config.bg,
                width=config.width,
            )
            self.buttons.append((button, config))

    def arrange_components(self):
        current_row = LAYOUT_START_ROW

        current_row = self.arrange_buttons(current_row)
        current_row = self.arrange_status_label(current_row)
        self.arrange_playlist_display(current_row)

    def arrange_buttons(self, row):
        current_row = row

        for button, config in self.buttons:
            button.grid(
                row=current_row,
                column=LAYOUT_START_COLUMN + config.column,
                pady=config.pady,
            )
            current_row += 1

        return current_row

    def arrange_status_label(self, row):
        self.status_label.grid(
            row=row,
            column=LAYOUT_START_COLUMN,
            pady=LAYOUT_WIDGETS_PADY,
        )

        return row + 1

    def arrange_playlist_display(self, row):
        self.playlist_display.grid(
            row=row,
            column=LAYOUT_START_COLUMN,
            pady=LAYOUT_WIDGETS_PADY,
        )

    def update_current_song_display(self, song):
        self.status_label.config(text=str(song))

    def toggle_auto_play(self):
        self.player.toggle_auto_play()
        self.update_auto_play_button()

    def update_auto_play_button(self):
        state = "ON" if self.player.auto_play else "OFF"

        button = self.get_button_by_functionality(self.toggle_auto_play)
        button.config(text=f"AUTO PLAY: {state}")

    def get_button_by_functionality(self, functionality):
        for button, config in self.buttons:
            if config.functionality == functionality:
                return button

        raise ValueError(f"No button found for functionality: {functionality.__name__}")
