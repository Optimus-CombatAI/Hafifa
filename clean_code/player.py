# from mutagen.easyid3 import EasyID3

import pygame
from tkinter.filedialog import *
from tkinter import *

import random
from dataclasses import dataclass
from pathlib import Path
from functools import wraps
import logging
import os
from dotenv import load_dotenv

load_dotenv("venv/.env")
pygame.init()

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

BUTTON_BG = 'AntiqueWhite1'
BUTTON_WIDTH = 40
SONG_END = pygame.USEREVENT + 1


def log_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.info(f"An error occurred in {func.__name__}: {e}")
    return wrapper


def get_random_artist() -> str:
    artists = ["Eminem", "JayZ", "2Pac", "Bob Dylan", "Madonna", "Rihanna", "Cher"]
    rand_artist = artists[random.randint(0, len(artists) - 1)]

    return rand_artist


def get_song_name(song_file_path: str) -> str:
    return Path(song_file_path).stem


def play_music(directory: str) -> None:
    pygame.mixer.music.load(directory)
    pygame.mixer.music.play(1, 0.0)
    pygame.mixer.music.set_endevent(SONG_END)


@dataclass
class Song:
    path: str
    title: str
    artist: str


class FrameApp(Frame):
    def __init__(self, master):
        super(FrameApp, self).__init__(master)
        self.grid()

        add_btn = Button(self, text="ADD TO LIST", command=self.add_songs_to_list, bg=BUTTON_BG, width=BUTTON_WIDTH)
        add_btn.grid(row=1, column=0)

        play_btn = Button(self, text="PLAY SONG", command=self.play_song, bg=BUTTON_BG, width=BUTTON_WIDTH)
        play_btn.grid(row=2, column=0)

        pause_btn = Button(self, text="PAUSE/UNPAUSE", command=self.pause_song, bg=BUTTON_BG, width=BUTTON_WIDTH)
        pause_btn.grid(row=3, column=0)

        prev_btn = Button(self, text="PREVIOUS SONG", command=self.play_prev_song, bg=BUTTON_BG, width=BUTTON_WIDTH)
        prev_btn.grid(row=4, column=0)

        next_btn = Button(self, text="NEXT SONG", command=self.play_next_song, bg=BUTTON_BG, width=BUTTON_WIDTH)
        next_btn.grid(row=5, column=0)

        self.message_label = Label(self, fg='Black', font=('Helvetica 12 bold italic', 10), bg='ivory2')
        self.message_label.grid(row=6, column=0)
        self.text_list = Text(self, wrap=WORD, width=60)
        self.text_list.grid(row=8, column=0)
        self.songs_list = list()
        self.pausing = False
        self.list_index = 0

    #################################################################################
    def append_songs(self, directory: tuple[str, ...]) -> None:
        for song_dir in directory:
            logging.info(song_dir)
            self.songs_list.append(Song(song_dir, get_song_name(song_dir), get_random_artist()))

    def add_to_text_list(self) -> None:
        for index, song in enumerate(self.songs_list):
            # song = EasyID3(item)
            song_data = f"{index + 1}: {song.title} - {song.artist}"
            self.text_list.insert(END, song_data + '\n')

    @log_exceptions
    def add_songs_to_list(self) -> None:
        directory = askopenfilenames()
        self.append_songs(directory)

        self.text_list.delete(0.0, END)
        self.add_to_text_list()

    #################################################################################
    @log_exceptions
    def get_song_data(self) -> str:
        song = self.songs_list[self.list_index]
        song_data = f"Now playing: Nr:{self.list_index + 1} {song.title} - {song.artist} "

        return song_data

    #################################################################################
    @log_exceptions
    def play_song(self) -> None:
        directory = self.songs_list[self.list_index].path
        play_music(directory)
        self.pausing = False
        self.message_label['text'] = self.get_song_data()

#################################################################################
    @log_exceptions
    def check_music(self) -> None:
        for event in pygame.event.get():
            if event.type == SONG_END:
                self.play_next_song()

#################################################################################
    @log_exceptions
    def pause_song(self) -> None:
        if self.pausing:
            pygame.mixer.music.unpause()
            self.pausing = False
        else:
            pygame.mixer.music.pause()
            self.pausing = True

#################################################################################
    @log_exceptions
    def get_next_song(self) -> int:
        return (self.list_index + 1) % len(self.songs_list)

    #################################################################################
    @log_exceptions
    def play_next_song(self) -> None:
        self.list_index = self.get_next_song()
        self.play_song()

    #################################################################################
    @log_exceptions
    def get_previous_song(self) -> int:
        return (self.list_index - 1) % len(self.songs_list)

    #################################################################################
    @log_exceptions
    def play_prev_song(self) -> None:
        self.list_index = self.get_previous_song()
        self.play_song()


#################################################################################
#################################################################################

SCREEN_DIMENSION = os.getenv("SCREEN_DIMENSION", "600x600")
APP_TITLE = os.getenv("APP_TITLE", "default app title")

window = Tk()
window.geometry(SCREEN_DIMENSION)
window.title(APP_TITLE)

#################################################################################
app = FrameApp(window)
#################################################################################
while True:
    # runs mainloop of program
    app.check_music()
    app.update()
