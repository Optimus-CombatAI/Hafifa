import pygame
from tkinter import *
from tkinter.filedialog import askopenfilenames
from mutagen.easyid3 import EasyID3

class MusicPlayer(Frame):
    def __init__(self, master):
        super().__init__(master)
        pygame.init()

        self.songs_list = []
        self.current_playing_song_index = 0
        self.is_paused = False
        self.SONG_END = pygame.USEREVENT + 1

        self.build_ui()
        self.grid()

    def create_button(self, text: str, command: callable, row: int) -> Button:
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

            self.songs_list.extend(files)
            self.refresh_songs_list_display()

        except Exception as e:
            print("Error adding songs:", e)

    def refresh_songs_list_display(self):
        self.song_textbox.delete(1.0, END)

        for idx, path in enumerate(self.songs_list):
            try:
                audio_metadata = EasyID3(path)
                display_text = f"{idx + 1}: {audio_metadata['title'][0]} - {audio_metadata['artist'][0]}"
                self.song_textbox.insert(END, display_text + "\n")
            except Exception:
                print(f"Error with the file: {path}")

    def play_current_song(self):
        try:
            if not self.songs_list:
                return

            song_path = self.songs_list[self.current_playing_song_index]
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            pygame.mixer.music.set_endevent(self.SONG_END)
            self.is_paused = False
            self.update_now_playing()

        except Exception as e:
            print("Error playing song:", e)

    def update_now_playing(self):
        audio_metadata = EasyID3(self.songs_list[self.current_playing_song_index])
        text = f"Now playing: {audio_metadata['title'][0]} - {audio_metadata['artist'][0]}"
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
        if not self.songs_list:
            return
        self.current_playing_song_index = (self.current_playing_song_index + 1) % len(self.songs_list)
        self.play_current_song()

    def play_previous(self):
        if not self.songs_list:
            return
        self.current_playing_song_index = (self.current_playing_song_index - 1) % len(self.songs_list)
        self.play_current_song()

    def check_music_events(self):
        """Check pygame events for song ending."""
        for event in pygame.event.get():
                if event.type == self.SONG_END:
                    self.play_next()

if __name__ == "__main__":
    window = Tk()
    window.title("MP3 Music Player")
    window.geometry("500x600")

    player = MusicPlayer(window)

    while True:
        player.check_music_events()
        player.update()
