import pygame
from settings import WIDTH, HEIGHT


class Track:
    def __init__(self, path):
        self.image = self.load_track(path)

    def load_track(self, path):
        track = pygame.image.load(path).convert()

        original_width, original_height = track.get_size()

        scale = max(WIDTH, HEIGHT) * 5 / max(original_width, original_height)

        new_width = int(original_width * scale)
        new_height = int(original_height * scale)

        track = pygame.transform.smoothscale(track, (new_width, new_height))

        return track

    def get_size(self):
        return self.image.get_size()

    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()

    def is_gray_pixel(self, x, y):
        x = int(x)
        y = int(y)

        if x < 0 or x >= self.get_width():
            return False

        if y < 0 or y >= self.get_height():
            return False

        r, g, b = self.image.get_at((x, y))[:3]

        gray_enough = abs(r - g) < 30 and abs(g - b) < 30 and abs(r - b) < 30
        brightness_ok = 50 < r < 230

        return gray_enough and brightness_ok

    def car_on_road(self, player):
        x = player.x
        y = player.y

        radius = 28

        points = [
            (x, y),
            (x + radius, y),
            (x - radius, y),
            (x, y + radius),
            (x, y - radius),
            (x + radius, y + radius),
            (x - radius, y + radius),
            (x + radius, y - radius),
            (x - radius, y - radius)
        ]

        road_points = 0

        for px, py in points:
            if self.is_gray_pixel(px, py):
                road_points = road_points + 1

        return road_points >= 2