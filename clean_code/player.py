# from mutagen.easyid3 import EasyID3

import pygame
from tkinter.filedialog import *
from tkinter import *

import random
from dataclasses import dataclass
from typing import Dict

pygame.init()

BUTTON_BG = 'AntiqueWhite1'
BUTTON_WIDTH = 40


def get_random_artist() -> str:
    artist = ["Eminem", "JayZ", "2Pac", "Bob Dylan", "Madonna", "Rihanna", "Cher"]
    rand_artist = artist[random.randint(0, len(artist) - 1)]
    return rand_artist


def get_song_name(file_path) -> str:
    len_file_type = len(".mp3")
    return file_path.split("/")[-1][:-len_file_type]


@dataclass
class Song:
    song_path: str
    song_metadata: Dict[str, str]


class FrameApp(Frame):
    def __init__(self, master):
        super(FrameApp, self).__init__(master)
        self.grid()
        play_btn = Button(self, text="PLAY SONG", command=play_song, bg=BUTTON_BG, width=BUTTON_WIDTH)
        play_btn.grid(row=2, column=0)
        prev_btn = Button(self, text="PREVIOUS SONG", command=play_prev_song, bg=BUTTON_BG, width=BUTTON_WIDTH)
        prev_btn.grid(row=4, column=0)
        pause_btn = Button(self, text="PAUSE/UNPAUSE", command=pause_song, bg=BUTTON_BG, width=BUTTON_WIDTH)
        pause_btn.grid(row=3, column=0)
        next_btn = Button(self, text="NEXT SONG", command=play_next_song, bg=BUTTON_BG, width=BUTTON_WIDTH)
        next_btn.grid(row=5, column=0)
        add_btn = Button(self, text="ADD TO LIST", command=add_songs_to_list, bg=BUTTON_BG, width=BUTTON_WIDTH)
        add_btn.grid(row=1, column=0)

        self.message_label = Label(self, fg='Black', font=('Helvetica 12 bold italic', 10), bg='ivory2')
        self.message_label.grid(row=6, column=0)
        self.text_list = Text(self, wrap=WORD, width=60)
        self.text_list.grid(row=8, column=0)
        self.songs_list = list()
        self.pausing = False
        self.list_index = 0
        self.SONG_END = pygame.USEREVENT + 1


#################################################################################
def add_songs_to_list():
    try:
        app.text_list.delete(0.0, END)
        directory = askopenfilenames()
        for song_dir in directory:
            print(song_dir)
            song_metadata = {'title': get_song_name(song_dir), 'artist': get_random_artist()}
            app.songs_list.append(Song(song_dir, song_metadata))

        for key, item in enumerate(app.songs_list):
            # song = EasyID3(item)
            song = app.songs_list[key]
            song_data = (str(key + 1) + ' : ' + song.song_metadata['title'] + ' - ' + song.song_metadata['artist'])
            app.text_list.insert(END, song_data + '\n')

    except:
        print("an error occurred")


#################################################################################
def get_song_data():
    try:
        song = app.songs_list[app.list_index]
        song_data = f"Now playing: {song.song_metadata['title']} - {song.song_metadata['artist']} " \
                    f"Nr:{str(app.list_index + 1)} "
        return song_data

    except:
        print("failed to get song data")


#################################################################################
def play_song():
    try:
        directory = app.songs_list[app.list_index].song_path
        pygame.mixer.music.load(directory)
        pygame.mixer.music.play(1, 0.0)
        pygame.mixer.music.set_endevent(app.SONG_END)
        app.pausing = False
        app.message_label['text'] = get_song_data()

    except:
        print("play song btn")


#################################################################################
def check_music():
    try:
        for event in pygame.event.get():
            if event.type == app.SONG_END:
                play_next_song()

    except:
        print("failed to check song")


#################################################################################
def pause_song():
    try:
        if app.pausing:
            pygame.mixer.music.unpause()
            app.pausing = False
        else:
            pygame.mixer.music.pause()
            app.pausing = True

    except:
        print("pause/unpause btn")


#################################################################################
def get_next_song():
    try:
        return (app.list_index + 1) % len(app.songs_list)
        """if app.list_index + 1 < len(app.songs_list):
            return app.list_index + 1
        else:
            return 0"""
    except:
        print("failed next song")


#################################################################################
def play_next_song():
    try:
        app.list_index = get_next_song()
        play_song()

    except:
        print("failed next song")


#################################################################################
def get_previous_song():
    try:
        return (app.list_index - 1) % len(app.songs_list)

        """if app.list_index - 1 >= 0:
            return app.list_index - 1
        else:
            return len(app.songs_list) - 1"""
    except:
        print("failed to previous song")


#################################################################################
def play_prev_song():
    try:
        app.list_index = get_previous_song()
        play_song()

    except:
        print("prev song btn")


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
    check_music()
    app.update()
