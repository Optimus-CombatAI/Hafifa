import os
import pygame
import logging
from pathlib import Path
from mutagen.easyid3 import EasyID3
from tkinter import *
from tkinter.filedialog import askopenfilenames

pygame.init()
pygame.mixer.init()

logging.basicConfig(level=logging.INFO)

SONG_END = pygame.USEREVENT + 1  # constant


def requires_playlist(func):
    def wrapper(self, *args, **kwargs):
        if not self.playlist:
            logging.info("Cannot execute %s: playlist is empty.", func.__name__)
            return

        return func(self, *args, **kwargs)

    return wrapper


class Player:
    def __init__(self):
        self.pausing = False
        self.playlist: list[str] = []
        self.current_index = 0

    def add_song(self, path: str) -> None:
        self.playlist.append(path)

    @requires_playlist
    def play(self):
        song_path = self.playlist[self.current_index]

        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(1, 0.0)  # same behavior as old code
        pygame.mixer.music.set_endevent(SONG_END)

        self.pausing = False

    def toggle_pause(self):
        if self.pausing:
            pygame.mixer.music.unpause()
            self.pausing = False

        else:
            pygame.mixer.music.pause()
            self.pausing = True

    @requires_playlist
    def next_song(self):
        self.current_index += 1

        if self.current_index >= len(self.playlist):
            self.current_index = 0

        self.play()

    @requires_playlist
    def previous_song(self):
        self.current_index -= 1

        if self.current_index < 0:
            self.current_index = len(self.playlist) - 1

        self.play()

    def get_current_song_info(self) -> str:
        if not self.playlist:
            return "No song playing"

        music_path = self.playlist[self.current_index]

        try:
            song = EasyID3(music_path)
            title = song.get("title", ["Unknown Title"])[0]
            artist = song.get("artist", ["Unknown Artist"])[0]

            return f"Now playing: {title} - {artist}"
        
        except Exception as e:
            logging.error("Error reading ID3 tags for %s: %s", music_path, e)
            file_name = Path(music_path).name

            return f"Now playing: {file_name}"


class FrameApp(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.player = Player()
        self.grid()  # same logic as old code

        # LABEL (same font + bg as old)
        self.label = Label(self, fg="Black",
                           font=("Helvetica 12 bold italic", 10),
                           bg="ivory2")
        self.label.grid(row=6, column=0)

        # TEXT (same width)
        self.text = Text(self, wrap=WORD, width=60)
        self.text.grid(row=8, column=0)

        # BUTTONS — EXACT same style as old project
        self.btn_add = Button(self, text="ADD TO LIST",
                              command=self.add_to_list,
                              bg="AntiqueWhite1",
                              width=40)
        self.btn_add.grid(row=1, column=0)

        self.btn_play = Button(self, text="PLAY SONG",
                               command=self.play_song,
                               bg="AntiqueWhite1",
                               width=40)
        self.btn_play.grid(row=2, column=0)

        self.btn_pause = Button(self, text="PAUSE/UNPAUSE",
                                command=self.pause_song,
                                bg="AntiqueWhite1",
                                width=40)
        self.btn_pause.grid(row=3, column=0)

        self.btn_previous = Button(self, text="PREVIOUS SONG",
                                   command=self.previous_song,
                                   bg="AntiqueWhite1",
                                   width=40)
        self.btn_previous.grid(row=4, column=0)

        self.btn_next = Button(self, text="NEXT SONG",
                               command=self.next_song,
                               bg="AntiqueWhite1",
                               width=40)
        self.btn_next.grid(row=5, column=0)

        self.check_music()

    def add_to_list(self):
        files = askopenfilenames()

        for path in files:
            self.player.add_song(path)

        self.text.delete("1.0", END)

        for index, path in enumerate(self.player.playlist):

            try:
                song = EasyID3(path)
                title = song.get("title", ["Unknown Title"])[0]
                artist = song.get("artist", ["Unknown Artist"])[0]

                self.text.insert(END, f"{index+1}. {title} - {artist}\n")

            except Exception as e:
                logging.error("Error reading ID3 tags for %s: %s", path, e)
                self.text.insert(END, f"{index+1}. {Path(path).name}\n")


    def update_label(self):
        self.label.config(text=self.player.get_current_song_info())

    def play_song(self):
        self.player.play()
        self.update_label()

    def pause_song(self):
        self.player.toggle_pause()

    def next_song(self):
        self.player.next_song()
        self.update_label()

    def previous_song(self):
        self.player.previous_song()
        self.update_label()

    def check_music(self):
        for event in pygame.event.get():
            if event.type == SONG_END:
                self.player.next_song()
                self.update_label()

        self.after(200, self.check_music)


if __name__ == "__main__":
    WINDOW_SIZE = os.environ.get("WINDOW_SIZE", "500x500")
    WINDOW_TITLE = os.environ.get("WINDOW_TITLE", "MP3 Music Player")

    root = Tk()
    root.geometry(WINDOW_SIZE)
    root.title(WINDOW_TITLE)
    app = FrameApp(root)
    root.mainloop()
