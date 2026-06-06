import pygame


class SoundManager:
    def __init__(self):
        self.engine_sound = self.load_engine_sound()
        self.engine_channel = pygame.mixer.Channel(0)
        self.engine_is_playing = False

        self.min_volume = 0.15
        self.max_volume = 1.0
        self.max_speed_for_sound = 1000

    def load_engine_sound(self):
        try:
            sound = pygame.mixer.Sound("moteur_f1.mp3")
            sound.set_volume(0.5)
            return sound
        except:
            print("Le fichier moteur_f1.mp3 est introuvable ou illisible.")
            return None

    def update_engine_sound(self, speed):
        if self.engine_sound is None:
            return

        if speed < 5:
            self.stop_engine()
            return

        volume_ratio = speed / self.max_speed_for_sound

        if volume_ratio > 1:
            volume_ratio = 1

        if volume_ratio < 0:
            volume_ratio = 0

        volume = self.min_volume + volume_ratio * (self.max_volume - self.min_volume)

        self.engine_sound.set_volume(volume)

        if not self.engine_is_playing:
            self.engine_channel.play(self.engine_sound, loops=-1)
            self.engine_is_playing = True

    def stop_engine(self):
        self.engine_channel.stop()
        self.engine_is_playing = False