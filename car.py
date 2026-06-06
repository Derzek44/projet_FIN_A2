import pygame
import math


class Car:
    def __init__(self, image_path):
        self.image = self.load_car(image_path)

    def load_car(self, path):
        car = pygame.image.load(path).convert_alpha()

        original_width, original_height = car.get_size()

        new_height = 70
        new_width = int(new_height * original_width / original_height)

        car = pygame.transform.smoothscale(car, (new_width, new_height))

        return car

    def draw(self, surface, x, y, angle):
        degrees = -math.degrees(angle) - 90
        rotated = pygame.transform.rotate(self.image, degrees)
        rect = rotated.get_rect(center=(int(x), int(y)))
        surface.blit(rotated, rect)