import pygame
from mutagen.easyid3 import EasyID3
from tkinter import *
from tkinter.filedialog import askopenfilenames

pygame.init()
pygame.mixer.init()


class Player:
    def __init__(self):
        self.pausing = False
        self.playlist = []
        self.current_index = 0 # index of the song that playing
        self.SONG_END = pygame.USEREVENT + 1 # next song
    
    def add_song(self, path): 
        self.playlist.append(path)


    def play(self):
        if not self.playlist:
            return
        song_path = self.playlist[self.current_index] # take the path of the music
        pygame.mixer.music.load(song_path) 
        pygame.mixer.music.play() #do the music
        pygame.mixer.music.set_endevent(self.SONG_END) # when the music off send song_end
        self.pausing = False

    def toggle_pause(self):
        if self.pausing:
            pygame.mixer.music.unpause() #unpause  the music
            self.pausing = False
        else:
            pygame.mixer.music.pause()
            self.pausing = True

    def next_song(self):
        if not self.playlist:
            return
        self.current_index += 1
        if self.current_index == len(self.playlist): # check if is the last song of the list
            self.current_index = 0 # go back to the beginning of the list
        self.play() # play the music

    def previous_song(self):
        if not self.playlist:
            return
        self.current_index -= 1
        if self.current_index == -1:
            self.current_index = len(self.playlist)-1
        self.play()
        
    def get_current_song_info(self):
        if not self.playlist:
            return "No song playing"

        music_path = self.playlist[self.current_index]

        try:
            song = EasyID3(music_path)
            title = song.get("title", ["Unknown Title"])[0]
            artist = song.get("artist", ["Unknown Artist"])[0]
            return f"Now playing: {title} - {artist}"
        except:
        # fichier sans tag ID3
            file_name = music_path.split("/")[-1]
            return f"Now playing: {file_name}"


class FrameApp(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.player = Player()
        self.label = Label(self, text="", font=("Helvetica", 12))
        self.label.grid(row=0, column=0)
        self.text = Text(self, wrap=WORD, width=60, height=10, font=("Helvetica", 10))
        self.text.grid(row=1, column=0)
        self.btn_add = Button(self, text="ADD TO LIST", command=self.add_to_list)
        self.btn_add.grid(row=2, column=0)
        self.btn_play = Button(self, text="PLAY",command=self.play_song)
        self.btn_play.grid(row=3,column=0)
        self.btn_pause = Button(self, text="PAUSE", command=self.pause_song)
        self.btn_pause.grid(row=4, column=0)
        self.btn_next = Button(self,text="Next",command=self.next_song)
        self.btn_next.grid(row=5,column=0)
        self.btn_previous = Button(self,text="Previous",command=self.previous_song)
        self.btn_previous.grid(row=6,column=0)
        self.check_music()

    
    def add_to_list(self):
        files = askopenfilenames() # open the files
        for path in files:
            self.player.add_song(path)
        self.text.delete("1.0",END)
        for index, path in enumerate(self.player.playlist):

            try:
                song = EasyID3(path)
                title = song["title"][0]
                artist = song["artist"][0]
                self.text.insert(END, f"{index+1}. {title} - {artist}\n")
            except:
            
                self.text.insert(END, f"{index+1}. {path}\n")

    def play_song(self):
        self.player.play()
        info = self.player.get_current_song_info()
        self.label.config(text = info)

    def pause_song(self):
        self.player.toggle_pause()

    def next_song(self):
        self.player.next_song()
        info = self.player.get_current_song_info()
        self.label.config(text=info)

    def previous_song(self):
        self.player.previous_song()
        info = self.player.get_current_song_info()
        self.label.config(text=info)

    def check_music(self):
        for event in pygame.event.get():
            if event.type == self.player.SONG_END:
                self.player.next_song()
                info = self.player.get_current_song_info()
                self.label.config(text=info)
        self.after(200, self.check_music)
if __name__ == "__main__":
    root = Tk()
    app = FrameApp(root)
    app.pack()
    root.mainloop()


        
    

        
