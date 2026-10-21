import pygame

from config import SONG_END_CHECK_INTERVAL_MS


class MusicPlayer:
    def __init__(self, playlist):
        self.playlist = playlist
        self.current_song_index = 0
        self.paused = False
        self.auto_play = True

        self.on_song_change = None

        self.song_end = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.song_end)

    def play(self):

        song = self.get_current_song()

        if not song:
            return

        pygame.mixer.music.load(song.local_song_path)
        pygame.mixer.music.play()

        self.paused = False
        self._notify_song_change(song)

    def get_current_song(self):
        if not self.playlist.songs:
            return None

        return self.playlist.songs[self.current_song_index]

    def toggle_pause(self):
        if not self.playlist.songs:
            return

        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

        self.paused = not self.paused

    def next_song(self):
        if not self.playlist.songs:
            return

        self.current_song_index = (self.current_song_index + 1) % len(
            self.playlist.songs
        )
        self.play()

    def previous_song(self):
        if not self.playlist.songs:
            return

        self.current_song_index = (self.current_song_index - 1) % len(
            self.playlist.songs
        )
        self.play()

    def toggle_auto_play(self):
        self.auto_play = not self.auto_play

    def _notify_song_change(self, song):
        if self.on_song_change:
            self.on_song_change(song)

    def check_song_ended(self, root):
        for event in pygame.event.get():
            if event.type == self.song_end and self.auto_play:
                self.next_song()

        self.schedule_song_end_check(root)

    def schedule_song_end_check(self, root):
        root.after(
            SONG_END_CHECK_INTERVAL_MS,
            lambda: self.check_song_ended(root),
        )
