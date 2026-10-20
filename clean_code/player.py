from abc import ABC, abstractmethod
import os
from mutagen.easyid3 import EasyID3
import pygame
from tkinter import *
from tkinter.filedialog import askopenfilenames


#################################################################################
class MusicPlayer:

    def __init__(self):
        pygame.mixer.init()
        self.song_list = []
        self.list_index = 0
        self.paused = False
        self.playing = False

    def add_songs(self, files):
        for f in files:
            self.song_list.append(f)

    def get_song_name(self, path):
        try:
            tags = EasyID3(path)
            return tags['title'][0] + ' - ' + tags['artist'][0]
        except Exception:
            return os.path.basename(path)

    def play(self):
        if len(self.song_list) == 0:
            return
        pygame.mixer.music.load(self.song_list[self.list_index])
        pygame.mixer.music.play()
        self.playing = True
        self.paused = False

    def pause_unpause(self):
        if not self.playing:
            return
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            pygame.mixer.music.pause()
            self.paused = True

    def next_song(self):
        if len(self.song_list) == 0:
            return
        # the % brings us back to 0 after the last song
        self.list_index = (self.list_index + 1) % len(self.song_list)
        self.play()

    def previous_song(self):
        if len(self.song_list) == 0:
            return
        self.list_index = (self.list_index - 1) % len(self.song_list)
        self.play()

    def check_song_end(self):
        # called every half second, goes to the next song when this one is over
        if self.playing and not self.paused and not pygame.mixer.music.get_busy():
            self.next_song()

    def now_playing_text(self):
        if not self.playing:
            return ""
        name = self.get_song_name(self.song_list[self.list_index])
        return "Now playing: Nr:" + str(self.list_index + 1) + " " + name


#################################################################################
class AbstractButton(ABC):

    def __init__(self, frame, player, text, row):
        self.frame = frame
        self.player = player
        self.button = Button(frame, text=text, width=40, bg='AntiqueWhite1',
                             command=self.click)
        self.button.grid(row=row, column=0)

    def click(self):
        self.on_click()
        self.frame.update_label()
        self.frame.update_list()

    @abstractmethod
    def on_click(self):
        pass


class AddSongButton(AbstractButton):

    def on_click(self):
        files = askopenfilenames(filetypes=[("MP3 files", "*.mp3")])
        self.player.add_songs(files)


class PlayButton(AbstractButton):

    def on_click(self):
        self.player.play()


class PauseUnpauseButton(AbstractButton):

    def on_click(self):
        self.player.pause_unpause()


class PreviousSongButton(AbstractButton):

    def on_click(self):
        self.player.previous_song()


class NextSongButton(AbstractButton):

    def on_click(self):
        self.player.next_song()



#################################################################################
class FrameApp(Frame):

    def __init__(self, master):
        super().__init__(master)
        self.grid()
        self.player = MusicPlayer()

        AddSongButton(self, self.player, "ADD TO LIST", 1)
        PlayButton(self, self.player, "PLAY SONG", 2)
        PauseUnpauseButton(self, self.player, "PAUSE/UNPAUSE", 3)
        PreviousSongButton(self, self.player, "PREVIOUS SONG", 4)
        NextSongButton(self, self.player, "NEXT SONG", 5)

        self.label1 = Label(self, fg='Black', bg='ivory2',
                            font=('Helvetica', 10, 'bold italic'))
        self.label1.grid(row=6, column=0)

        self.text1 = Text(self, wrap=WORD, width=60)
        self.text1.grid(row=7, column=0)

        self.check_music()

    def update_label(self):
        self.label1['text'] = self.player.now_playing_text()

    def update_list(self):
        self.text1.delete('1.0', END)
        number = 1
        for path in self.player.song_list:
            self.text1.insert(END, str(number) + ' : ' + self.player.get_song_name(path) + '\n')
            number += 1

    def check_music(self):
        self.player.check_song_end()
        self.update_label()
        self.after(500, self.check_music)


#################################################################################
window = Tk()
window.geometry("500x500")
window.title("MP3 Music Player")
app = FrameApp(window)
window.mainloop()
