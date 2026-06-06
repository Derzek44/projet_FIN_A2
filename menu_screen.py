import pygame

from settings import NOIR, BLANC, GRIS, JAUNE, VERT, BLEU, ROUGE
from button import Button


class MenuScreen:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock

    def draw_text(self, text, font, color, x, y):
        image_texte = font.render(text, True, color)
        rect = image_texte.get_rect()
        rect.center = (x, y)
        self.screen.blit(image_texte, rect)

    def load_car_image(self, path):
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (120, 180))
        return image

    def draw_car_choice(self, rect, car_name, car_image, font):
        pygame.draw.rect(self.screen, GRIS, rect)
        pygame.draw.rect(self.screen, BLANC, rect, 3)

        image_rect = car_image.get_rect()
        image_rect.center = (rect.centerx, rect.y + 100)
        self.screen.blit(car_image, image_rect)

        self.draw_text(car_name, font, BLANC, rect.centerx, rect.y + 210)

    def menu_principal(self):
        W, H = self.screen.get_size()

        title_font = pygame.font.SysFont("arial", 80)
        button_font = pygame.font.SysFont("arial", 40)

        bouton_jouer = Button(
            W // 2 - 150,
            H // 2,
            300,
            80,
            "JOUER",
            VERT,
            button_font
        )

        bouton_quitter = Button(
            W // 2 - 150,
            H // 2 + 110,
            300,
            80,
            "QUITTER",
            GRIS,
            button_font
        )

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                if bouton_jouer.is_clicked(event):
                    return "jouer"

                if bouton_quitter.is_clicked(event):
                    return "quit"

            self.screen.fill(NOIR)

            self.draw_text(
                "F1 RACING",
                title_font,
                JAUNE,
                W // 2,
                H // 2 - 170
            )

            bouton_jouer.draw(self.screen)
            bouton_quitter.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

    def selection_mode(self):
        W, H = self.screen.get_size()

        title_font = pygame.font.SysFont("arial", 65)
        text_font = pygame.font.SysFont("arial", 28)
        button_font = pygame.font.SysFont("arial", 34)

        bouton_humain = Button(
            W // 2 - 250,
            H // 2 - 30,
            500,
            80,
            "1V1 CONTRE HUMAIN",
            BLEU,
            button_font
        )

        bouton_fantome = Button(
            W // 2 - 250,
            H // 2 + 90,
            500,
            80,
            "1V1 CONTRE FANTÔME",
            ROUGE,
            button_font
        )

        bouton_retour = Button(
            40,
            40,
            180,
            60,
            "RETOUR",
            GRIS,
            text_font
        )

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "back"

                if bouton_humain.is_clicked(event):
                    return "human"

                if bouton_fantome.is_clicked(event):
                    return "ghost"

                if bouton_retour.is_clicked(event):
                    return "back"

            self.screen.fill(NOIR)

            self.draw_text(
                "CHOIX DU MODE",
                title_font,
                JAUNE,
                W // 2,
                140
            )

            self.draw_text(
                "Choisis ton mode de jeu",
                text_font,
                BLANC,
                W // 2,
                220
            )

            bouton_humain.draw(self.screen)
            bouton_fantome.draw(self.screen)
            bouton_retour.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

    def selection_vehicule(self, player_number, cars):
        W, H = self.screen.get_size()

        title_font = pygame.font.SysFont("arial", 60)
        text_font = pygame.font.SysFont("arial", 30)

        car_images = []

        for car in cars:
            image = self.load_car_image(car["image"])
            car_images.append(image)

        card_width = 220
        card_height = 260
        gap = 40

        total_width = len(cars) * card_width + (len(cars) - 1) * gap
        start_x = (W - total_width) // 2
        start_y = H // 2 - 80

        card_rects = []

        for i in range(len(cars)):
            x = start_x + i * (card_width + gap)
            rect = pygame.Rect(x, start_y, card_width, card_height)
            card_rects.append(rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "back"

                for i in range(len(card_rects)):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if card_rects[i].collidepoint(event.pos):
                            return i

            self.screen.fill(NOIR)

            self.draw_text(
                "JOUEUR " + str(player_number),
                title_font,
                JAUNE,
                W // 2,
                80
            )

            self.draw_text(
                "Choisis ta voiture",
                text_font,
                BLANC,
                W // 2,
                140
            )

            for i in range(len(cars)):
                self.draw_car_choice(
                    card_rects[i],
                    cars[i]["name"],
                    car_images[i],
                    text_font
                )

            pygame.display.flip()
            self.clock.tick(60)

    def selection_vehicule_fantome(self, cars):
        W, H = self.screen.get_size()

        title_font = pygame.font.SysFont("arial", 60)
        text_font = pygame.font.SysFont("arial", 30)

        car_images = []

        for car in cars:
            image = self.load_car_image(car["image"])
            car_images.append(image)

        card_width = 220
        card_height = 260
        gap = 40

        total_width = len(cars) * card_width + (len(cars) - 1) * gap
        start_x = (W - total_width) // 2
        start_y = H // 2 - 80

        card_rects = []

        for i in range(len(cars)):
            x = start_x + i * (card_width + gap)
            rect = pygame.Rect(x, start_y, card_width, card_height)
            card_rects.append(rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "back"

                for i in range(len(card_rects)):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if card_rects[i].collidepoint(event.pos):
                            return i

            self.screen.fill(NOIR)

            self.draw_text(
                "FANTÔME",
                title_font,
                JAUNE,
                W // 2,
                80
            )

            self.draw_text(
                "Choisis la voiture du fantôme",
                text_font,
                BLANC,
                W // 2,
                140
            )

            for i in range(len(cars)):
                self.draw_car_choice(
                    card_rects[i],
                    cars[i]["name"],
                    car_images[i],
                    text_font
                )

            pygame.display.flip()
            self.clock.tick(60)