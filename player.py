import math
import pygame


class Player:
    def __init__(self, x, y, angle, name, color):
        self.x = x
        self.y = y

        self.vx = 0.0
        self.vy = 0.0

        self.angle = angle

        self.name = name
        self.color = color

        self.trail = []

        self.max_speed = 1000
        self.straight_accel = 450
        self.turn_slowdown = 1.8
        self.natural_friction = 0.985

        self.next_checkpoint = 1
        self.laps = 0
        self.lap_start_time = pygame.time.get_ticks()
        self.finished = False

    def start_timer(self):
        self.lap_start_time = pygame.time.get_ticks()

    def add_point(self):
        point = (round(self.x), round(self.y), self.angle)

        if not self.trail or point != self.trail[-1]:
            self.trail.append(point)

        if len(self.trail) > 150:
            self.trail.pop(0)

    def get_speed(self):
        return math.sqrt(self.vx**2 + self.vy**2)

    def check_checkpoint(self, checkpoints):
        cp = checkpoints[self.next_checkpoint]

        if cp.collidepoint(self.x, self.y):
            if self.next_checkpoint == 0:
                self.laps = self.laps + 1
                self.lap_start_time = pygame.time.get_ticks()
                self.next_checkpoint = 1
            else:
                self.next_checkpoint = self.next_checkpoint + 1
                if self.next_checkpoint >= len(checkpoints):
                    self.next_checkpoint = 0

    def distance_to_next(self, checkpoints):
        cp = checkpoints[self.next_checkpoint]
        dx = self.x - cp.centerx
        dy = self.y - cp.centery
        return math.hypot(dx, dy)

    def race_score(self, checkpoints):
        nb = len(checkpoints)
        progression = self.laps * nb + self.next_checkpoint
        distance = self.distance_to_next(checkpoints)
        return progression * 100000 - distance

    def get_lap_time(self):
        return (pygame.time.get_ticks() - self.lap_start_time) / 1000

    def update(self, go_forward, turn_left, turn_right, dt, off_track, physics):
        turning = turn_left or turn_right

        if turn_left:
            self.angle = self.angle - physics.turn_speed * dt

        if turn_right:
            self.angle = self.angle + physics.turn_speed * dt

        result = physics.update_physics(
            self.x,
            self.y,
            self.vx,
            self.vy,
            self.angle,
            go_forward,
            dt,
            off_track
        )

        self.x = result[0]
        self.y = result[1]
        self.vx = result[2]
        self.vy = result[3]

        if go_forward and not turning:
            self.vx = self.vx + math.cos(self.angle) * self.straight_accel * dt
            self.vy = self.vy + math.sin(self.angle) * self.straight_accel * dt

        if turning:
            factor = 1.0 - self.turn_slowdown * dt

            if factor < 0:
                factor = 0

            self.vx = self.vx * factor
            self.vy = self.vy * factor

        if not go_forward:
            self.vx = self.vx * self.natural_friction
            self.vy = self.vy * self.natural_friction

        if off_track:
            self.vx = self.vx * 0.80
            self.vy = self.vy * 0.80

        speed = self.get_speed()

        if speed > self.max_speed:
            ratio = self.max_speed / speed
            self.vx = self.vx * ratio
            self.vy = self.vy * ratio

    def is_touching(self, other_player):
        dx = self.x - other_player.x
        dy = self.y - other_player.y

        distance = math.hypot(dx, dy)
        seuil = 55

        return distance < seuil

    def separate_from(self, other_player):
        dx = self.x - other_player.x
        dy = self.y - other_player.y

        distance = math.hypot(dx, dy)
        seuil = 55

        if distance > 0:
            nx = dx / distance
            ny = dy / distance

            overlap = seuil - distance

            self.x = self.x + nx * overlap
            self.y = self.y + ny * overlap

            other_player.x = other_player.x - nx * overlap
            other_player.y = other_player.y - ny * overlap
