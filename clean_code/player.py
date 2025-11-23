# from mutagen.easyid3 import EasyID3

import pygame
from tkinter.filedialog import *
from tkinter import *

import random
from dataclasses import dataclass
from pathlib import Path

import logging


pygame.init()

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

BUTTON_BG = 'AntiqueWhite1'
BUTTON_WIDTH = 40


def get_random_artist() -> str:
    artists = ["Eminem", "JayZ", "2Pac", "Bob Dylan", "Madonna", "Rihanna", "Cher"]
    rand_artist = artists[random.randint(0, len(artists) - 1)]

    return rand_artist


def get_song_name(song_file_path) -> str:

    return Path(song_file_path).stem


def play_music(directory, song_end):
    pygame.mixer.music.load(directory)
    pygame.mixer.music.play(1, 0.0)
    pygame.mixer.music.set_endevent(song_end)


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
        self.song_end = pygame.USEREVENT + 1  # TODO: should be lower case? Doesn't change through the runtime

    #################################################################################
    def add_songs_to_list(self):
        try:
            directory = askopenfilenames()

            for song_dir in directory:
                logging.info(song_dir)
                self.songs_list.append(Song(song_dir, get_song_name(song_dir), get_random_artist()))

            self.text_list.delete(0.0, END)

            for index, song in enumerate(self.songs_list):
                # song = EasyID3(item)
                song_data = f"{index + 1}: {song.title} - {song.artist}"
                self.text_list.insert(END, song_data + '\n')

        except Exception as e:
            logging.info(f"an error occurred:{e}")

    #################################################################################
    def get_song_data(self):
        try:
            song = self.songs_list[self.list_index]
            song_data = f"Now playing: Nr:{self.list_index + 1} {song.title} - {song.artist} "

            return song_data

        except Exception as e:
            logging.info(f"an error occurred:{e}")

    #################################################################################
    def play_song(self):
        try:
            directory = self.songs_list[app.list_index].path
            play_music(directory, self.song_end)
            self.pausing = False
            self.message_label['text'] = self.get_song_data()

        except Exception as e:
            logging.info(f"an error occurred:{e}")

#################################################################################
    def check_music(self):
        try:

            for event in pygame.event.get():
                if event.type == self.song_end:
                    self.play_next_song()

        except Exception as e:
            logging.info(f"an error occurred:{e}")

#################################################################################
    def pause_song(self):
        try:
            if self.pausing:
                pygame.mixer.music.unpause()
                self.pausing = False
            else:
                pygame.mixer.music.pause()
                self.pausing = True

        except Exception as e:
            logging.info(f"an error occurred:{e}")

#################################################################################
    def get_next_song(self):
        try:

            return (self.list_index + 1) % len(self.songs_list)

        except Exception as e:
            logging.info(f"an error occurred:{e}")

    #################################################################################
    def play_next_song(self):
        try:
            self.list_index = self.get_next_song()
            self.play_song()

        except Exception as e:
            logging.info(f"an error occurred:{e}")

    #################################################################################
    def get_previous_song(self):
        try:

            return (self.list_index - 1) % len(self.songs_list)

        except Exception as e:
            logging.info(f"an error occurred:{e}")

    #################################################################################
    def play_prev_song(self):
        try:
            self.list_index = self.get_previous_song()
            self.play_song()

        except Exception as e:
            logging.info(f"an error occurred:{e}")

# TODO: seems redundant all the exceptions. Is there more efficient way to write handle exceptions?


#################################################################################
#################################################################################

SCREEN_DIMENSION = "500x500"
APP_TITLE = "MP3 Music Player"

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
