import pygame
import math

from settings import WIDTH, HEIGHT, FPS
from physics_engine import PhysicsEngine
from player import Player
from ghost_player import GhostPlayer
from ghost_recorder import GhostRecorder
from track import Track
from camera import Camera
from race_lights import RaceLights


TOURS_POUR_GAGNER = 3


class Game:
    def __init__(self, screen, clock, car1, car2, sound_manager, mode, ghost_file=None):
        self.screen = screen
        self.clock = clock

        self.car1 = car1
        self.car2 = car2

        self.sound_manager = sound_manager
        self.mode = mode
        self.ghost_file = ghost_file

        self.physics = PhysicsEngine()
        self.track = Track("Terrain_de_F1.png")

        self.trace_img = pygame.image.load("trace_pneu.png").convert_alpha()
        self.trace_img = pygame.transform.scale(self.trace_img, (20, 20))

        track_width, track_height = self.track.get_size()

        centres = [
            (3629, 3692),
            (2740, 3693), (2397, 3077), (1850, 2734), (918, 2495),
            (1272, 1093), (2666, 1112), (3890, 1408), (2888, 1675),
            (1944, 2033), (2717, 2755), (3827, 3193), (4888, 2820),
            (5186, 2000), (5680, 989), (6217, 1221), (5856, 2064),
            (6566, 2465), (7351, 2681), (7351, 3406), (6813, 3707),
            (5337, 3700),
        ]
        taille = 350
        self.checkpoints = []
        for cx, cy in centres:
            rect = pygame.Rect(cx - taille // 2, cy - taille // 2, taille, taille)
            self.checkpoints.append(rect)

        if self.mode == "record":
            player1_x = track_width / 2 - 225
            player1_y = track_height / 2 + 1475
        else:
            player1_x = track_width / 2 - 280
            player1_y = track_height / 2 + 1375

        self.player1 = Player(
            x=player1_x,
            y=player1_y,
            angle=math.radians(180),
            name="Joueur 1",
            color=(255, 70, 70)
        )

        if self.mode == "ghost":
            self.player2 = GhostPlayer(
                x=track_width / 2 - 225,
                y=track_height / 2 + 1475,
                angle=math.radians(180),
                name="Fantôme",
                color=(70, 140, 255),
                ghost_file=self.ghost_file
            )
        else:
            if self.mode == "human":
                player2_name = "Joueur 2"
            else:
                player2_name = "Enregistrement"

            self.player2 = Player(
                x=track_width / 2 - 225,
                y=track_height / 2 + 1475,
                angle=math.radians(180),
                name=player2_name,
                color=(70, 140, 255)
            )

        self.left_view = pygame.Rect(0, 0, WIDTH // 2, HEIGHT)
        self.right_view = pygame.Rect(WIDTH // 2, 0, WIDTH // 2, HEIGHT)
        self.full_view = pygame.Rect(0, 0, WIDTH, HEIGHT)

        self.race_lights = RaceLights()

        self.recorder = None
        if self.mode == "record":
            self.recorder = GhostRecorder(self.ghost_file)

        self.timer_started = False
        self.winner = None          # le Player gagnant
        self.race_over = False

    def draw_text_center(self, surface, text, x, y, size, color):
        font = pygame.font.SysFont("arial", size, bold=True)
        label = font.render(text, True, color)
        rect = label.get_rect(center=(int(x), int(y)))
        surface.blit(label, rect)

    def draw_hud_box(self, view, text, x, y, w, h, text_color, bg_color):
        fond = pygame.Surface((w, h), pygame.SRCALPHA)
        fond.fill(bg_color)
        view.blit(fond, (x, y))
        pygame.draw.rect(view, (255, 255, 255), pygame.Rect(x, y, w, h), 2, border_radius=8)
        self.draw_text_center(view, text, x + w // 2, y + h // 2, 28, text_color)

    def get_position(self, player, other_player):
        if player.race_score(self.checkpoints) >= other_player.race_score(self.checkpoints):
            return "1er"
        else:
            return "2e"

    def draw_lap_time(self, view, player):
        temps = player.get_lap_time()
        text = "Tour : " + str(round(temps, 1)) + " s"

        rect_w, rect_h = 200, 50
        x = view.get_width() - rect_w - 20
        y = 20

        fond = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
        fond.fill((0, 0, 0, 150))
        view.blit(fond, (x, y))
        pygame.draw.rect(view, (255, 255, 255), pygame.Rect(x, y, rect_w, rect_h), 2, border_radius=8)
        self.draw_text_center(view, text, x + rect_w // 2, y + rect_h // 2, 26, (255, 255, 255))

    def draw_trail(self, view, player, camera_x, camera_y):
        for px, py, pangle in player.trail:
            screen_x = px - camera_x
            screen_y = py - camera_y
            degrees = -math.degrees(pangle) - 90
            rotated = pygame.transform.rotate(self.trace_img, degrees)
            rect = rotated.get_rect(center=(screen_x, screen_y))
            view.blit(rotated, rect)

    def draw_player_view(self, view_rect, player, player_car, other_player=None, other_car=None):
        track_width, track_height = self.track.get_size()

        view = self.screen.subsurface(view_rect)

        camera = Camera(view_rect.width, view_rect.height)
        camera_x, camera_y = camera.get_position(player, track_width, track_height)

        view.fill((34, 110, 45))

        visible_rect = pygame.Rect(camera_x, camera_y, view_rect.width, view_rect.height)
        view.blit(self.track.image, (0, 0), visible_rect)

        self.draw_trail(view, player, camera_x, camera_y)
        if other_player is not None:
            self.draw_trail(view, other_player, camera_x, camera_y)

        player_screen_x = player.x - camera_x
        player_screen_y = player.y - camera_y

        if other_player is not None and other_car is not None:
            other_screen_x = other_player.x - camera_x
            other_screen_y = other_player.y - camera_y
            if -100 < other_screen_x < view_rect.width + 100 and -100 < other_screen_y < view_rect.height + 100:
                other_car.draw(view, other_screen_x, other_screen_y, other_player.angle)

        player_car.draw(view, player_screen_x, player_screen_y, player.angle)

        self.draw_text_center(view, player.name, player_screen_x, player_screen_y - 60, 24, player.color)

        # HUD tours (en haut à gauche, encadré)
        self.draw_hud_box(
            view,
            "TOUR " + str(player.laps + 1) + " / " + str(TOURS_POUR_GAGNER),
            20, 20, 200, 50,
            (255, 255, 255), (0, 0, 0, 150)
        )

        # HUD position (gros badge doré/argenté)
        if other_player is not None:
            position = self.get_position(player, other_player)
            if position == "1er":
                badge_color = (255, 215, 0)      # or
            else:
                badge_color = (200, 200, 210)    # argent
            self.draw_hud_box(
                view,
                position,
                20, 85, 110, 60,
                (20, 20, 20), badge_color + (230,) if len(badge_color) == 3 else badge_color
            )

        self.draw_lap_time(view, player)

        if self.mode == "record":
            self.draw_text_center(view, "MODE ENREGISTREMENT - ESC POUR SAUVEGARDER",
                                  view_rect.width // 2, 110, 30, (255, 220, 80))

        if self.mode == "ghost":
            if isinstance(self.player2, GhostPlayer):
                if not self.player2.has_record():
                    self.draw_text_center(view, "AUCUN FANTÔME ENREGISTRÉ POUR CETTE VOITURE",
                                          view_rect.width // 2, 110, 26, (255, 80, 80))

    def draw_end_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.mode == "human":
            # Deux joueurs : on dit qui gagne
            titre = self.winner.name + " GAGNE !"
            self.draw_text_center(self.screen, titre, WIDTH // 2, HEIGHT // 2 - 60, 90, (255, 215, 0))
        else:
            # ghost / record : le joueur 1 est le héros
            if self.winner is self.player1:
                self.draw_text_center(self.screen, "GAGNÉ !", WIDTH // 2, HEIGHT // 2 - 60, 100, (80, 230, 120))
            else:
                self.draw_text_center(self.screen, "PERDU", WIDTH // 2, HEIGHT // 2 - 60, 100, (230, 80, 80))

        self.draw_text_center(self.screen, "Appuie sur ÉCHAP pour revenir au menu",
                              WIDTH // 2, HEIGHT // 2 + 60, 36, (240, 240, 240))
        pygame.display.flip()

    def save_record_if_needed(self):
        if self.recorder is not None:
            self.recorder.save()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.sound_manager.stop_engine()
                self.save_record_if_needed()
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.sound_manager.stop_engine()
                    self.save_record_if_needed()
                    return "menu"
        return "continue"

    def check_winner(self):
        if self.player1.laps >= TOURS_POUR_GAGNER:
            self.winner = self.player1
            self.race_over = True
        elif (self.mode == "human" or self.mode == "ghost") and self.player2.laps >= TOURS_POUR_GAGNER:
            self.winner = self.player2
            self.race_over = True

    def update_players(self, dt):
        keys = pygame.key.get_pressed()

        race_started = self.race_lights.race_started()

        # Démarre le chrono des joueurs au feu vert (une seule fois)
        if race_started and not self.timer_started:
            self.player1.start_timer()
            self.player2.start_timer()
            self.timer_started = True

        player1_off_track = not self.track.car_on_road(self.player1)
        player2_off_track = not self.track.car_on_road(self.player2)

        if race_started:
            player1_forward = keys[pygame.K_UP]
            player1_left = keys[pygame.K_LEFT]
            player1_right = keys[pygame.K_RIGHT]

            if self.mode == "human":
                player2_forward = keys[pygame.K_z]
                player2_left = keys[pygame.K_q]
                player2_right = keys[pygame.K_d]
            else:
                player2_forward = False
                player2_left = False
                player2_right = False
        else:
            player1_forward = False
            player1_left = False
            player1_right = False
            player2_forward = False
            player2_left = False
            player2_right = False

        self.player1.update(player1_forward, player1_left, player1_right, dt, player1_off_track, self.physics)

        if self.mode == "ghost":
            if race_started:
                self.player2.update_from_record(dt)
        elif self.mode == "human":
            self.player2.update(player2_forward, player2_left, player2_right, dt, player2_off_track, self.physics)
        elif self.mode == "record":
            pass

        if race_started:
            self.player1.check_checkpoint(self.checkpoints)
            if self.mode == "human" or self.mode == "ghost":
                self.player2.check_checkpoint(self.checkpoints)
            self.check_winner()

        speed1 = self.player1.get_speed()
        speed2 = self.player2.get_speed()
        biggest_speed = max(speed1, speed2)

        if race_started:
            self.sound_manager.update_engine_sound(biggest_speed)
        else:
            self.sound_manager.stop_engine()

        if race_started:
            self.player1.add_point()
            if self.mode == "human" or self.mode == "ghost":
                self.player2.add_point()
            if self.mode == "record":
                self.recorder.add_position(self.player1)

        if self.mode == "human" or self.mode == "ghost":
            if self.player1.is_touching(self.player2):
                self.player1.separate_from(self.player2)

    def draw(self):
        self.screen.fill((0, 0, 0))

        if self.mode == "record":
            self.draw_player_view(self.full_view, self.player1, self.car1)
        else:
            self.draw_player_view(self.left_view, self.player1, self.car1, self.player2, self.car2)
            self.draw_player_view(self.right_view, self.player2, self.car2, self.player1, self.car1)
            pygame.draw.line(self.screen, (0, 0, 0), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 6)

        self.race_lights.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            action = self.handle_events()
            if action != "continue":
                return action

            if self.race_over:
                # La course est finie : on stoppe le moteur et on affiche l'écran de fin
                self.sound_manager.stop_engine()
                self.save_record_if_needed()
                self.draw_end_screen()
            else:
                self.update_players(dt)
                self.draw()
