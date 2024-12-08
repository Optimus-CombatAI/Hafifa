from mutagen.easyid3 import EasyID3
import pygame
from tkinter.filedialog import askopenfilenames
from tkinter import Tk, Frame, Button, Label, Text, WORD


class MusicPlayer(Frame):
    BUTTON_BG_COLOR = 'AntiqueWhite1'
    LABEL_BG_COLOR = 'ivory2'
    FONT_STYLE = ('Helvetica 12 bold italic', 10)

    def __init__(self, master):
        super().__init__(master)
        self.grid()

        self.list_of_songs = []
        self.paused = False
        self.current_song_index = 0
        self.SONG_END = pygame.USEREVENT + 1

        self.song_info_label = None
        self.song_list_text = None

        self.create_widgets()

    def create_widgets(self):
        self.create_buttons()
        self.create_song_info_label()
        self.create_song_list_text()

    def create_buttons(self):
        BUTTONS = [
            ("ADD TO LIST", self.add_songs_to_list, 1),
            ("PLAY SONG", self.play_song, 2),
            ("PAUSE/UNPAUSE", self.toggle_pause, 3),
            ("PREVIOUS SONG", self.play_previous_song, 4),
            ("NEXT SONG", self.play_next_song, 5),
        ]

        for text, command, row in BUTTONS:
            self.create_button(text, command, row)

    def create_button(self, text, command, row):
        Button(self, text=text, command=command, bg=self.BUTTON_BG_COLOR, width=40).grid(row=row, column=0)

    def create_song_info_label(self):
        self.song_info_label = Label(self, fg='Black', font=self.FONT_STYLE, bg=self.LABEL_BG_COLOR)
        self.song_info_label.grid(row=6, column=0)

    def create_song_list_text(self):
        self.song_list_text = Text(self, wrap=WORD, width=60)
        self.song_list_text.grid(row=8, column=0)

    def add_songs_to_list(self):
        selected_files = askopenfilenames()
        self.list_of_songs.extend(selected_files)
        self.update_song_list_text()

    def update_song_list_text(self):
        self.song_list_text.delete(0.0, 'end')

        for index, song_file in enumerate(self.list_of_songs, start=1):
            self.song_list_text.insert('end', f"{index}: {self.get_song_data(song_file)}\n")

    @staticmethod
    def get_song_data(song_file):
        try:
            song = EasyID3(song_file)
            title = song.get('title', ['Unknown'])[0]
            artist = song.get('artist', ['Unknown'])[0]
            return f"{title} - {artist}"
        except Exception as error:
            print(f"Could not get song data {error}")
            return "Unknown Song"

    def play_song(self):
        if self.list_of_songs:
            try:
                current_song = self.list_of_songs[self.current_song_index]
                pygame.mixer.music.load(current_song)
                pygame.mixer.music.play(1, 0.0)
                pygame.mixer.music.set_endevent(self.SONG_END)
                self.paused = False
                self.song_info_label.config(text=self.get_current_song_info())
            except Exception as error:
                print(f"Error playing song: {error}")

    def toggle_pause(self):
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.paused = not self.paused

    def get_current_song_info(self):
        song_data = self.get_song_data(self.list_of_songs[self.current_song_index])
        return f"Now playing: Nr: {self.current_song_index + 1} {song_data}"

    def play_next_song(self):
        self.change_song_index(1)
        self.play_song()

    def play_previous_song(self):
        self.change_song_index(-1)
        self.play_song()

    def change_song_index(self, direction):
        # direction: 1 for next song, -1 for previous song
        self.current_song_index = (self.current_song_index + direction) % len(self.list_of_songs)

    def check_music(self):
        for event in pygame.event.get():
            if event.type == self.SONG_END:
                self.play_next_song()


def main():
    pygame.init()
    window = Tk()
    window.geometry("500x500")
    window.title("MP3 Music Player")

    app = MusicPlayer(window)
    window.protocol("WM_DELETE_WINDOW", window.quit)

    while True:
        app.check_music()
        app.update()


if __name__ == "__main__":
    main()
