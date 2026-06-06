import pygame
from settings import BLANC


class Button:
    def __init__(self, x, y, width, height, text, color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = font

    def draw_text(self, screen, text, color, x, y):
        image_texte = self.font.render(text, True, color)
        rect = image_texte.get_rect()
        rect.center = (x, y)
        screen.blit(image_texte, rect)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLANC, self.rect, 3)

        self.draw_text(
            screen,
            self.text,
            BLANC,
            self.rect.centerx,
            self.rect.centery
        )

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True

        return False