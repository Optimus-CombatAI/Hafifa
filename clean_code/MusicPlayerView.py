import MusicPlayerModel
from mutagen.easyid3 import EasyID3
import pygame
from tkinter.filedialog import *
from tkinter import *

class MusicPlayerView(Frame):
    BUTTON_BG_COLOR = "AntiqueWhite1"
    BUTTON_WIDTH = 40
    BUTTON_LABELS = ["ADD TO LIST", "PLAY SONG", "PAUSE/UNPAUSE", "PREVIOUS SONG", "NEXT SONG"]
    
    LABEL_FG_COLOR = 'Black'
    LABEL_BG_COLOR = 'ivory2'
    LABEL_FONT = ('Helvetica 12 bold italic',10)

    def __init__(self,master,model: MusicPlayerModel):
        super(MusicPlayerView, self).__init__(master)
        self.model = model
        self.button_options = [("ADD TO LIST", model.add_songs_to_playlist), 
                          ("PLAY SONG", model.play_song), 
                          ("PAUSE/UNPAUSE", model.pause_or_unpause_song),
                          ("PREVIOUS SONG", model.previous_song),
                          ("NEXT SONG", model.next_song)]

        self.grid()
        buttons = []
        for i, button_option in enumerate(self.button_options):
            button = Button(self, text=button_option[0],command=button_option[1],bg=self.BUTTON_BACKGROUND_COLOR,width=self.BUTTON_WIDTH)
            buttons.append(button)
            button.grid(row=i, column=0)

        self.label = Label(self, fg=self.LABEL_FG_COLOR,font=self.LABEL_FONT,bg=self.LABEL_BG_COLOR)
        self.label.grid(row=6,column=0)

        self.text = Text(self,wrap=WORD,width=60)
        self.text.grid(row=8,column=0)
    
    def update(self):
        self.text.delete(0.0, END)
        for key, item in enumerate(self.model.playlist):
            self.text.insert(END, self.model.song_data_for_text(key, item) + '\n')
        self.label['text'] = self.model.song_data_for_label()