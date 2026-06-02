import pygame
import math
import physics
import menu

WIDTH, HEIGHT = 1600, 980

# Index du menu (0=Rouge,1=Vert,2=Bleu,3=Jaune) → fichier image
VOITURES = {
    0: "F1.png",
    1: "F1.png",
    2: "F1_bleu.png",
    3: "F1.png",
}


def load_car(path="F1.png", scale=(40, 70)):
    surf = pygame.image.load(path).convert_alpha()
    orig_w, orig_h = surf.get_size()
    new_h = scale[1]
    new_w = int(new_h * (orig_w / orig_h))
    return pygame.transform.scale(surf, (new_w, new_h))


def load_track(path="Terrain_de_F1.png", screen_w=1600, screen_h=980):
    surf = pygame.image.load(path).convert()
    orig_w, orig_h = surf.get_size()
    scale = max(screen_w, screen_h) * 5 / max(orig_w, orig_h)
    return pygame.transform.scale(surf, (int(orig_w * scale), int(orig_h * scale)))


def draw_car(surface, car_surf, x, y, angle):
    degrees = -math.degrees(angle) - 90
    rotated = pygame.transform.rotate(car_surf, degrees)
    rect = rotated.get_rect(center=(int(x), int(y)))
    surface.blit(rotated, rect)

def draw_player_label(surface, text, x, y, color):
    font = pygame.font.SysFont(None, 28)
    label = font.render(text, True, color)
    rect = label.get_rect(center=(int(x), int(y - 55)))
    surface.blit(label, rect)

# ── Réglages communs ────────────────────────────────────────────
MAX_SPEED        = 750
STRAIGHT_ACCEL   = 450.0
TURN_SLOWDOWN    = 1.8
NATURAL_FRICTION = 0.985


def update_player(p, go_up, turn_left, turn_right, dt):
    """Met à jour un joueur (dict avec x, y, vx, vy, angle). Retourne le dict modifié."""
    turning = turn_left or turn_right

    if turn_left:
        p["angle"] -= physics.TURN_SPEED * dt
    if turn_right:
        p["angle"] += physics.TURN_SPEED * dt

    p["x"], p["y"], p["vx"], p["vy"], _ = physics.update_physics(
        p["x"], p["y"], p["vx"], p["vy"], p["angle"], go_up, dt
    )

    # Accélération bonus en ligne droite
    if go_up and not turning:
        p["vx"] += math.cos(p["angle"]) * STRAIGHT_ACCEL * dt
        p["vy"] += math.sin(p["angle"]) * STRAIGHT_ACCEL * dt

    # Ralentissement en virage
    if turning:
        if math.hypot(p["vx"], p["vy"]) > 0:
            f = max(0.0, 1.0 - TURN_SLOWDOWN * dt)
            p["vx"] *= f
            p["vy"] *= f

    # Frottement naturel
    if not go_up:
        p["vx"] *= NATURAL_FRICTION
        p["vy"] *= NATURAL_FRICTION

    # Vitesse max
    speed = math.hypot(p["vx"], p["vy"])
    if speed > MAX_SPEED:
        ratio = MAX_SPEED / speed
        p["vx"] *= ratio
        p["vy"] *= ratio

    return p


def game_loop(screen, clock, car1_surf, car2_surf):
    track_surf = load_track("Terrain_de_F1.png", WIDTH, HEIGHT)
    track_w, track_h = track_surf.get_size()

    # Deux joueurs, légèrement décalés au départ
    p1 = {"x": track_w / 2 - 280, "y": track_h / 2 +1375, "vx": 0.0, "vy": 0.0, "angle": 110.0}
    p2 = {"x": track_w / 2 - 225, "y": track_h / 2+1475, "vx": 0.0, "vy": 0.0, "angle": 110.0}

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"

        keys = pygame.key.get_pressed()

        # Joueur 1 : flèches
        update_player(p1, keys[pygame.K_UP], keys[pygame.K_LEFT], keys[pygame.K_RIGHT], dt)
        # Joueur 2 : ZQSD
        update_player(p2, keys[pygame.K_z], keys[pygame.K_q], keys[pygame.K_d], dt)

        # ── Caméra unique partagée : centrée sur le milieu des 2 voitures ──
        mid_x = (p1["x"] + p2["x"]) / 2
        mid_y = (p1["y"] + p2["y"]) / 2
        cam_x = max(0, min(track_w - WIDTH,  int(mid_x - WIDTH / 2)))
        cam_y = max(0, min(track_h - HEIGHT, int(mid_y - HEIGHT / 2)))
        screen_car1_x = p1["x"] - cam_x
        screen_car1_y = p1["y"] - cam_y

        screen_car2_x = p2["x"] - cam_x
        screen_car2_y = p2["y"] - cam_y
        # ── Rendu ──────────────────────────────────────────────────────
        screen.fill((34, 110, 45))
        screen.blit(track_surf, (0, 0), pygame.Rect(cam_x, cam_y, WIDTH, HEIGHT))

        draw_car(screen, car1_surf, p1["x"] - cam_x, p1["y"] - cam_y, p1["angle"])
        draw_car(screen, car2_surf, p2["x"] - cam_x, p2["y"] - cam_y, p2["angle"])
        draw_player_label(screen,"P1",screen_car1_x,screen_car1_y,(255,0,0))
        draw_player_label(screen,"P2",screen_car2_x,screen_car2_y,(0,120,255))
        pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("F1 Racing")
    clock = pygame.time.Clock()

    car1_surf = None
    car2_surf = None
    etat = "menu"

    while etat != "quit":
        if etat == "menu":
            action = menu.menu_principal(screen, clock)
            etat = "choix_p1" if action == "jouer" else "quit"

        elif etat == "choix_p1":
            choix = menu.selection_vehicule(screen, clock)
            if choix == "quit":
                etat = "quit"
            elif choix == "back":
                etat = "menu"
            else:
                car1_surf = load_car(VOITURES.get(choix, "F1.png"), scale=(40, 70))
                etat = "choix_p2"

        elif etat == "choix_p2":
            choix = menu.selection_vehicule(screen, clock)
            if choix == "quit":
                etat = "quit"
            elif choix == "back":
                etat = "choix_p1"   # retour au choix du P1
            else:
                car2_surf = load_car(VOITURES.get(choix, "F1.png"), scale=(40, 70))
                etat = "jeu"

        elif etat == "jeu":
            etat = game_loop(screen, clock, car1_surf, car2_surf)

            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
