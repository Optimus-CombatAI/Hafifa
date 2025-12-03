import pygame
from tkinter import *
from tkinter.filedialog import askopenfilenames
from mutagen.easyid3 import EasyID3


class MusicPlayer(Frame):

    def __init__(self, master):
        super().__init__(master)
        pygame.init()

        self.song_list = []
        self.current_index = 0
        self.is_paused = False
        self.SONG_END = pygame.USEREVENT + 1

        self.build_ui()
        self.grid()

    def create_button(self, text, command, row):
        button = Button(
            self,
            text=text,
            command=command,
            width=40,
            bg='AntiqueWhite1'
        )
        button.grid(row=row, column=0, pady=2)
        return button

    def build_ui(self):
        self.create_button("Add Songs", self.add_songs, row=0)
        self.create_button("Play", self.play_current_song, row=1)
        self.create_button("Pause / Unpause", self.toggle_pause, row=2)
        self.create_button("Previous", self.play_previous, row=3)
        self.create_button("Next", self.play_next, row=4)

        self.now_playing_label = Label(
            self,
            fg='black',
            bg='ivory2',
            font=('Helvetica', 10, 'bold italic')
        )
        self.now_playing_label.grid(row=5, column=0, pady=4)
        self.song_textbox = Text(self, wrap=WORD, width=60)
        self.song_textbox.grid(row=6, column=0, pady=4)

    
    def add_songs(self):
        try:
            files = askopenfilenames()
            if not files:
                return

            self.song_list.extend(files)
            self.refresh_song_list_display()

        except Exception as e:
            print("Error adding songs:", e)

    def refresh_song_list_display(self):
        self.song_textbox.delete(1.0, END)

        for idx, path in enumerate(self.song_list):
            try:
                tag = EasyID3(path)
                line = f"{idx + 1}: {tag['title'][0]} - {tag['artist'][0]}"
            except Exception:
                line = f"{idx + 1}: {path}"

            self.song_textbox.insert(END, line + "\n")

    def play_current_song(self):
        try:
            if not self.song_list:
                return

            song_path = self.song_list[self.current_index]
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            pygame.mixer.music.set_endevent(self.SONG_END)
            self.is_paused = False
            self.update_now_playing()

        except Exception as e:
            print("Error playing song:", e)

    def update_now_playing(self):
        try:
            tag = EasyID3(self.song_list[self.current_index])
            text = f"Now playing: {tag['title'][0]} - {tag['artist'][0]}"
        except Exception:
            text = f"Now playing: {self.song_list[self.current_index]}"

        self.now_playing_label.config(text=text)

    def toggle_pause(self):
        try:
            if self.is_paused:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()
            self.is_paused = not self.is_paused
        except Exception as e:
            print("Pause error:", e)

    def play_next(self):
        if not self.song_list:
            return
        self.current_index = (self.current_index + 1) % len(self.song_list)
        self.play_current_song()

    def play_previous(self):
        if not self.song_list:
            return
        self.current_index = (self.current_index - 1) % len(self.song_list)
        self.play_current_song()

    def check_music_events(self):
        """Check pygame events for song ending."""
        try:
            for event in pygame.event.get():
                if event.type == self.SONG_END:
                    self.play_next()
        except Exception as e:
            print("Event error:", e)


##### Main #####

if __name__ == "__main__":
    window = Tk()
    window.title("MP3 Music Player")
    window.geometry("500x600")

    player = MusicPlayer(window)

    while True:
        # runs mainloop of program
        player.check_music_events()
        player.update()
