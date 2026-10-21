import logging
import tkinter as tk

import pygame

from config import APP_GEOMETRY
from gui import GUIHandler

logger = logging.getLogger(__name__)


class MusicPlayerApp:
    def __init__(self):
        pygame.init()

        self.root = tk.Tk()
        self.root.title("MP3 Music Player")
        self.root.geometry(APP_GEOMETRY)

        self.gui = GUIHandler(self.root)

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        logger.info("Application initialized")

    def run(self):
        self.root.mainloop()

    def close(self):
        logger.info("Closing application")

        pygame.mixer.music.stop()
        self.root.destroy()
        pygame.quit()
