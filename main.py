import pygame
import math
import physics
import menu

WIDTH = 1600
HEIGHT = 980
FPS = 60

CARS = [
    {"name": "Rouge", "image": "F1_rouge.png", "color": (220, 50, 50)},
    {"name": "Bleu", "image": "F1_bleu.png", "color": (50, 100, 230)},
    {"name": "noir", "image": "F1_noir.png", "color": (50, 180, 90)},
    {"name": "orange", "image": "F1_orange.png", "color": (230, 200, 50)}
]
trace_img = None
MAX_SPEED = 1000
STRAIGHT_ACCEL = 450
TURN_SLOWDOWN = 1.8
NATURAL_FRICTION = 0.985

def load_car(path):
    car = pygame.image.load(path).convert_alpha()
    original_width, original_height = car.get_size()
    new_height = 70
    new_width = int(new_height * original_width / original_height)
    car = pygame.transform.smoothscale(car, (new_width, new_height))
    return car

def load_track():
    track = pygame.image.load("Terrain_de_F1.png").convert()
    original_width, original_height = track.get_size()
    scale = max(WIDTH, HEIGHT) * 5 / max(original_width, original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    track = pygame.transform.smoothscale(track, (new_width, new_height))
    return track


def create_player(x, y, angle):
    player = {
        "x": x,
        "y": y,
        "vx": 0.0,
        "vy": 0.0,
        "angle": angle,
        "trail": [],
    }
    return player

def draw_car(surface, car_image, x, y, angle):
    degrees = -math.degrees(angle) - 90
    rotated = pygame.transform.rotate(car_image, degrees)
    rect = rotated.get_rect(center=(int(x), int(y)))
    surface.blit(rotated, rect)

def voitures_en_contact(player1, player2):
    dx = player1["x"] - player2["x"]
    dy = player1["y"] - player2["y"]
    distance = math.hypot(dx, dy)
    seuil = 55
    return distance < seuil

def add_point(player):
    pt = (round(player["x"]), round(player["y"]), player["angle"])
    if not player["trail"] or pt != player["trail"][-1]:
        player["trail"].append(pt)
    if len(player["trail"]) > 150:
        player["trail"].pop(0)

def draw_text_center(surface, text, x, y, size, color):
    font = pygame.font.SysFont("arial", size, bold=True)
    label = font.render(text, True, color)
    rect = label.get_rect(center=(int(x), int(y)))
    surface.blit(label, rect)

def draw_speed(surface, player, player_name, color):
    speed = math.sqrt(player["vx"]**2 + player["vy"]**2)
    text = player_name + "  |  Vitesse : " + str(int(speed))
    draw_text_center(surface, text, 190, 35, 28, color)

def draw_start_lights(screen, elapsed_time):
    """
    Affiche un départ type F1.
    Après 8 secondes, les feux disparaissent.
    """
    # Après 8 secondes, on n'affiche plus les feux
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

def is_gray_pixel(track, x, y):
    x = int(x)
    y = int(y)
    if x < 0 or x >= track.get_width():
        return False
    if y < 0 or y >= track.get_height():
        return False
    r, g, b = track.get_at((x, y))[:3]
    gray_enough = abs(r - g) < 30 and abs(g - b) < 30 and abs(r - b) < 30
    brightness_ok = 50 < r < 230
    return gray_enough and brightness_ok

def car_on_road(track, player):
    x = player["x"]
    y = player["y"]
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
        if is_gray_pixel(track, px, py):
            road_points = road_points + 1
    return road_points >= 2

def update_player(player, go_forward, turn_left, turn_right, dt, off_track):
    turning = turn_left or turn_right
    if turn_left:
        player["angle"] = player["angle"] - physics.TURN_SPEED * dt
    if turn_right:
        player["angle"] = player["angle"] + physics.TURN_SPEED * dt
    result = physics.update_physics(
        player["x"],
        player["y"],
        player["vx"],
        player["vy"],
        player["angle"],
        go_forward,
        dt,
        off_track
    )
    player["x"] = result[0]
    player["y"] = result[1]
    player["vx"] = result[2]
    player["vy"] = result[3]
    if go_forward and not turning:
        player["vx"] = player["vx"] + math.cos(player["angle"]) * STRAIGHT_ACCEL * dt
        player["vy"] = player["vy"] + math.sin(player["angle"]) * STRAIGHT_ACCEL * dt
    if turning:
        factor = 1.0 - TURN_SLOWDOWN * dt
        if factor < 0:
            factor = 0
        player["vx"] = player["vx"] * factor
        player["vy"] = player["vy"] * factor
    if not go_forward:
        player["vx"] = player["vx"] * NATURAL_FRICTION
        player["vy"] = player["vy"] * NATURAL_FRICTION
    if off_track:
        player["vx"] = player["vx"] * 0.80
        player["vy"] = player["vy"] * 0.80
    speed = math.sqrt(player["vx"]**2 + player["vy"]**2)
    if speed > MAX_SPEED:
        ratio = MAX_SPEED / speed
        player["vx"] = player["vx"] * ratio
        player["vy"] = player["vy"] * ratio

def get_camera_for_player(player, track_width, track_height, view_width, view_height):
    camera_x = int(player["x"] - view_width / 2)
    camera_y = int(player["y"] - view_height / 2)
    if camera_x < 0:
        camera_x = 0
    if camera_y < 0:
        camera_y = 0
    if camera_x > track_width - view_width:
        camera_x = track_width - view_width
    if camera_y > track_height - view_height:
        camera_y = track_height - view_height
    return camera_x, camera_y


def draw_player_view(screen, view_rect, track, player, player_car, other_player, other_car, player_name, player_color):
    track_width, track_height = track.get_size()
    view = screen.subsurface(view_rect)
    view_width = view_rect.width
    view_height = view_rect.height
    camera_x, camera_y = get_camera_for_player(
        player, track_width, track_height, view_width, view_height
    )
    view.fill((34, 110, 45))
    visible_rect = pygame.Rect(camera_x, camera_y, view_width, view_height)
    view.blit(track, (0, 0), visible_rect)

    # Traînée du joueur principal
    for i, (px, py, pangle) in enumerate(player["trail"]):
        screen_x = px - camera_x
        screen_y = py - camera_y
        degrees = -math.degrees(pangle) - 90
        rotated = pygame.transform.rotate(trace_img, degrees)
        rect = rotated.get_rect(center=(screen_x, screen_y))
        view.blit(rotated, rect)

    # Traînée de l'autre joueur
    for i, (px, py, pangle) in enumerate(other_player["trail"]):
        screen_x = px - camera_x
        screen_y = py - camera_y
        degrees = -math.degrees(pangle) - 90
        rotated = pygame.transform.rotate(trace_img, degrees)
        rect = rotated.get_rect(center=(screen_x, screen_y))
        view.blit(rotated, rect)

    player_screen_x = player["x"] - camera_x
    player_screen_y = player["y"] - camera_y
    other_screen_x = other_player["x"] - camera_x
    other_screen_y = other_player["y"] - camera_y
    if -100 < other_screen_x < view_width + 100 and -100 < other_screen_y < view_height + 100:
        draw_car(view, other_car, other_screen_x, other_screen_y, other_player["angle"])
    draw_car(view, player_car, player_screen_x, player_screen_y, player["angle"])
    draw_text_center(view, player_name, player_screen_x, player_screen_y - 60, 24, player_color)
    draw_speed(view, player, player_name, player_color)

def game_loop(screen, clock, car1_image, car2_image):
    track = load_track()
    track_width, track_height = track.get_size()
    player1 = create_player(
        x=track_width / 2 - 280,
        y=track_height / 2 + 1375,
        angle=math.radians(180)
    )
    player2 = create_player(
        x=track_width / 2 - 225,
        y=track_height / 2 + 1475,
        angle=math.radians(180)
    )
    right_view = pygame.Rect(0, 0, WIDTH // 2, HEIGHT)
    left_view = pygame.Rect(WIDTH // 2, 0, WIDTH // 2, HEIGHT)

    # Début du décompte
    start_time = pygame.time.get_ticks()

    while True:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
        keys = pygame.key.get_pressed()

        # Temps écoulé depuis le début de la course
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
        race_started = elapsed_time >= 5

        player1_off_track = not car_on_road(track, player1)
        player2_off_track = not car_on_road(track, player2)

        # Tant que les feux ne sont pas verts, les joueurs ne peuvent pas bouger
        if race_started:
            player1_forward = keys[pygame.K_UP]
            player1_left = keys[pygame.K_LEFT]
            player1_right = keys[pygame.K_RIGHT]
            player2_forward = keys[pygame.K_z]
            player2_left = keys[pygame.K_q]
            player2_right = keys[pygame.K_d]
        else:
            player1_forward = False
            player1_left = False
            player1_right = False
            player2_forward = False
            player2_left = False
            player2_right = False

        update_player(player1, player1_forward, player1_left, player1_right, dt, player1_off_track)
        update_player(player2, player2_forward, player2_left, player2_right, dt, player2_off_track)

        # On n'enregistre la traînée qu'une fois la course lancée
        if race_started:
            add_point(player1)
            add_point(player2)

        screen.fill((0, 0, 0))
        draw_player_view(
            screen, left_view, track,
            player1, car1_image, player2, car2_image,
            "Joueur 1", (255, 70, 70)
        )
        draw_player_view(
            screen, right_view, track,
            player2, car2_image, player1, car1_image,
            "Joueur 2", (70, 140, 255)
        )

        # Collision entre les deux voitures
        if voitures_en_contact(player1, player2):
            dx = player1["x"] - player2["x"]
            dy = player1["y"] - player2["y"]
            distance = math.hypot(dx, dy)
            seuil = 55
            if distance > 0:
                nx = dx / distance
                ny = dy / distance
                overlap = seuil - distance
                player1["x"] += nx * overlap
                player1["y"] += ny * overlap
                player2["x"] -= nx * overlap
                player2["y"] -= ny * overlap

        pygame.draw.line(screen, (0, 0, 0), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 6)

        # Feux de départ par-dessus les deux écrans
        draw_start_lights(screen, elapsed_time)

        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    global trace_img
    trace_img = pygame.image.load("trace_pneu.png").convert_alpha()
    trace_img = pygame.transform.scale(trace_img, (20, 20))
    pygame.display.set_caption("F1 Racing")
    clock = pygame.time.Clock()
    running = True
    while running:
        action = menu.menu_principal(screen, clock)
        if action == "quit":
            running = False
        elif action == "jouer":
            choice1 = menu.selection_vehicule(screen, clock, 1, CARS)
            if choice1 == "quit":
                running = False
            elif choice1 == "back":
                pass
            else:
                car1_image = load_car(CARS[choice1]["image"])
                choice2 = menu.selection_vehicule(screen, clock, 2, CARS)
                if choice2 == "quit":
                    running = False
                elif choice2 == "back":
                    pass
                else:
                    car2_image = load_car(CARS[choice2]["image"])
                    result = game_loop(screen, clock, car1_image, car2_image)
                    if result == "quit":
                        running = False
    pygame.quit()

if __name__ == "__main__":
    main()
