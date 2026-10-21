from mutagen.easyid3 import EasyID3
from tkinter.filedialog import *
from tkinter import *
import pygame

pygame.init()

# Crée les cinq boutons et reçoit les clics de l'utilisateur.
class ControlsFrame(Frame):
    def __init__(self, master, player, display):
        super().__init__(master)

        self.player = player
        self.display = display
        self.grid(row=0, column=0)

        buttons = [
            {"text": "PLAY SONG", "command": self.play_song, "row": 2},
            {"text": "PREVIOUS SONG", "command": self.player.play_previous_song, "row": 4},
            {"text": "PAUSE/UNPAUSE", "command": self.player.toggle_pause, "row": 3},
            {"text": "NEXT SONG", "command": self.player.play_next_song, "row": 5},
            {"text": "ADD TO LIST", "command": self.add_songs, "row": 1}
        ]

        for button in buttons:
            btn = Button(
                self,
                text=button["text"],
                command=button["command"],
                bg='AntiqueWhite1',
                width=40
            )
            btn.grid(row=button["row"], column=0)

    def play_song(self):
        self.player.play_song()
        self.display.current_song_label["text"] = self.player.get_current_song_info()

    def add_songs(self):
        directory = askopenfilenames()

        for song_dir in directory:
            print(song_dir)
            self.player.playlist.append(song_dir)

        self.display.playlist_text.delete(0.0, END)

        for key, item in enumerate(self.player.playlist):
            song = EasyID3(item)
            song_data = (str(key + 1) + ' : ' + song['title'][0]
                         + ' - ' + song['artist'][0])
            self.display.playlist_text.insert(END, song_data + '\n')


# Contient les widgets qui affichent les informations.
class DisplayFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=1, column=0)
        self.current_song_label = Label(
            self,
            fg='Black',
            font=('Helvetica 12 bold italic', 10),
            bg='ivory2'
        )
        self.current_song_label.grid(row=0, column=0)

        self.playlist_text = Text(self, wrap=WORD, width=60)
        self.playlist_text.grid(row=1, column=0)


# Contient l'état musical et les opérations de lecture.
class MusicPlayer:
    def __init__(self):
        self.playlist = []
        self.is_paused = False
        self.current_song_index = 0
        self.SONG_END = pygame.USEREVENT + 1

    def get_next_song_index(self):
        if self.current_song_index + 2 <= len(self.playlist):
            return self.current_song_index + 1
        else:
            return 0

    def get_previous_song_index(self):
        if self.current_song_index - 1 >= 0:
            return self.current_song_index - 1
        else:
            return len(self.playlist) - 1

    def play_song(self):
        directory = self.playlist[self.current_song_index]
        pygame.mixer.music.load(directory)
        pygame.mixer.music.play(1, 0.0)
        pygame.mixer.music.set_endevent(self.SONG_END)
        self.is_paused = False

    def toggle_pause(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            pygame.mixer.music.pause()
            self.is_paused = True

    def play_previous_song(self):
        self.current_song_index = self.get_previous_song_index()
        self.play_song()

    def play_next_song(self):
        self.current_song_index = self.get_next_song_index()
        self.play_song()

    def check_song_end(self):
        for event in pygame.event.get():
            if event.type == self.SONG_END:
                self.play_next_song()

    def get_current_song_info(self):
        song = EasyID3(self.playlist[self.current_song_index])
        song_data = "Now playing: Nr:" + str(self.current_song_index + 1) + " " + \
                    str(song['title']) + " - " + str(song['artist'])
        return song_data


#################################################################################

window = Tk()
window.geometry("500x500")
window.title("MP3 Music Player")

player = MusicPlayer()
display = DisplayFrame(window)
app = ControlsFrame(window, player, display)

while True:
    player.check_song_end()
    app.update()