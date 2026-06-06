import pygame
from settings import WIDTH


class RaceLights:
    def __init__(self):
        self.start_time = pygame.time.get_ticks()

    def get_elapsed_time(self):
        return (pygame.time.get_ticks() - self.start_time) / 1000

    def draw(self, screen):
        elapsed_time = self.get_elapsed_time()

        if elapsed_time >= 8:
            return True

        light_radius = 35
        gap = 95

        total_width = 5 * light_radius * 2 + 4 * gap
        start_x = WIDTH // 2 - total_width // 2 + light_radius
        y = 120

        race_started = elapsed_time >= 5

        for i in range(5):
            x = start_x + i * (light_radius * 2 + gap)

            pygame.draw.circle(screen, (15, 15, 15), (x, y), light_radius + 10)

            if race_started:
                color = (0, 220, 80)
            else:
                if elapsed_time >= i + 1:
                    color = (220, 0, 0)
                else:
                    color = (65, 0, 0)

            pygame.draw.circle(screen, color, (x, y), light_radius)

        return race_started

    def race_started(self):
        elapsed_time = self.get_elapsed_time()
        return elapsed_time >= 5