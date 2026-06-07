from Observer import Subject, Observer
from mutagen.easyid3 import EasyID3
import pygame
from tkinter.filedialog import *
from tkinter import *

class MusicPlayerModel(Subject):
    def __init__(self):
        self.current_song = ""
        self.play_list = []
        self.current_song_index = 0
        self.is_paused = True
        self.SONG_END = pygame.USEREVENT + 1

    def load_songs_into_playlist(self):
        try:
            directory = askopenfilenames()
            for song_dir in directory:
                print(song_dir)
                self.play_list.append(song_dir)
            self.notify_observers()
        except:
            pass

    def song_data_for_text(self, key, item):
        try:
            song = EasyID3(item)
            song_data = (str(key + 1) + ' : ' + song['title'][0] + ' - '
                            + song['artist'][0])
            return song_data
        except:
            pass
    
    def song_data_for_label(self):
        try:
            song = EasyID3(self.play_list[self.current_song])
            song_data = "Now playing: Nr:" + str(self.play_list + 1) + " " + \
                        str(song['title']) + " - " + str(song['artist'])
            return song_data
        except:
            pass
    
    def load_and_play_song(self):
        try:
            directory = self.play_list[self.current_song_index]
            pygame.mixer.music.load(directory)
            pygame.mixer.music.play(1, 0.0)
            pygame.mixer.music.set_endevent(self.SONG_END)
            self.is_paused = False
            self.notify_observers()
        except:
            pass

    def check_music(self):
        try:
            for event in pygame.event.get():
                if event.type == self.SONG_END:
                    self.next_song()
        except:
            pass

    def next_song(self):
        try: 
            self.current_song_index = (self.current_song_index + 1) % len(self.play_list)
            self.load_and_play_song()
        except:
            pass

    def previous_song(self):
        try: 
            self.current_song_index = (self.current_song_index - 1) % len(self.play_list)
            self.load_and_play_song()
        except:
            pass

