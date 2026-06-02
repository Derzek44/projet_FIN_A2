
import pygame
import math
import numpy as np
import physics


TRACK_SCALE = 1.0 


def load_car(path="F1.png", scale=(20, 35)):
    surf = pygame.image.load(path).convert_alpha()
    arr = pygame.surfarray.pixels3d(surf)
    alpha = pygame.surfarray.pixels_alpha(surf)
    del arr, alpha
    orig_w, orig_h = surf.get_size()
    new_h = scale[1]
    new_w = int(new_h * (orig_w / orig_h))
    surf = pygame.transform.scale(surf, (new_w, new_h))
    return surf


def load_track(path="Terrain_de_F1.png", screen_w=900, screen_h=600):
    surf = pygame.image.load(path).convert()
    orig_w, orig_h = surf.get_size()
    # Mise à l'échelle pour que le circuit rentre dans la fenêtre × 1.5
    # (on garde de la marge pour le scroll caméra)
    scale = max(screen_w, screen_h) * 3 / max(orig_w, orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    surf = pygame.transform.scale(surf, (new_w, new_h))
    return surf


def draw_car(surface, car_surf, x, y, angle):
    degrees = -math.degrees(angle) - 90
    rotated = pygame.transform.rotate(car_surf, degrees)
    rect = rotated.get_rect(center=(int(x), int(y)))
    surface.blit(rotated, rect)


def main():
    pygame.init()
    WIDTH, HEIGHT = 900, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("F1 - Simulation inertielle")
    clock = pygame.time.Clock()

    car_surf  = load_car("F1.png", scale=(40, 70))
    track_surf = load_track("Terrain_de_F1.png", WIDTH, HEIGHT)
    track_w, track_h = track_surf.get_size()

    # Position de départ : milieu du circuit
    car_x = track_w / 2
    car_y = track_h / 2
    vx, vy = 0.0, 0.0
    angle_control = 0.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            angle_control -= physics.TURN_SPEED * dt
        if keys[pygame.K_RIGHT]:
            angle_control += physics.TURN_SPEED * dt
        go_up = keys[pygame.K_UP]

        car_x, car_y, vx, vy, _ = physics.update_physics(
            car_x, car_y, vx, vy, angle_control, go_up, dt
        )

        # ── Caméra centrée sur la voiture ──────────────────────────────
        cam_x = int(car_x - WIDTH  / 2)
        cam_y = int(car_y - HEIGHT / 2)
        # Clamp pour ne pas dépasser les bords du circuit
        cam_x = max(0, min(track_w - WIDTH,  cam_x))
        cam_y = max(0, min(track_h - HEIGHT, cam_y))
    
        # ── Rendu ──────────────────────────────────────────────────────
        # Découpe la portion visible du circuit
        visible_rect = pygame.Rect(cam_x, cam_y, WIDTH, HEIGHT)
        screen.blit(track_surf, (0, 0), visible_rect)

        # Coordonnées de la voiture à l'écran
        screen_car_x = car_x - cam_x
        screen_car_y = car_y - cam_y
        draw_car(screen, car_surf, screen_car_x, screen_car_y, angle_control)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()