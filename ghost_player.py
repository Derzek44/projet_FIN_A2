import json
import os
from player import Player


class GhostPlayer(Player):
    def __init__(self, x, y, angle, name, color, ghost_file):
        super().__init__(x, y, angle, name, color)

        self.ghost_file = ghost_file
        self.positions = []
        self.index = 0

        self.load_ghost()

    def load_ghost(self):
        if not os.path.exists(self.ghost_file):
            print("Aucun fichier fantôme trouvé :", self.ghost_file)
            self.positions = []
            return

        with open(self.ghost_file, "r", encoding="utf-8") as file:
            self.positions = json.load(file)

        print("Fantôme chargé :", self.ghost_file)

    def update_from_record(self, dt):
        if len(self.positions) == 0:
            self.vx = 0
            self.vy = 0
            return

        if self.index >= len(self.positions):
            self.vx = 0
            self.vy = 0
            return

        old_x = self.x
        old_y = self.y

        point = self.positions[self.index]

        self.x = point["x"]
        self.y = point["y"]
        self.angle = point["angle"]

        if dt > 0:
            self.vx = (self.x - old_x) / dt
            self.vy = (self.y - old_y) / dt

        self.index = self.index + 1

    def has_record(self):
        return len(self.positions) > 0