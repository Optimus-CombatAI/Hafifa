import MusicPlayerModel
import MusicPlayerView
import pygame
from tkinter import *

pygame.init()

window = Tk()
window.geometry("500x500")
window.title("MP3 Music Player")
#################################################################################
model = MusicPlayerModel()
app = MusicPlayerView(window, model)
#################################################################################
while True:
    # runs mainloop of program
    model.check_music()
    app.update()