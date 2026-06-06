import json


class GhostRecorder:
    def __init__(self, filename):
        self.filename = filename
        self.positions = []
        self.saved = False

    def add_position(self, player):
        point = {
            "x": player.x,
            "y": player.y,
            "angle": player.angle
        }

        self.positions.append(point)

    def save(self):
        if self.saved:
            return

        if len(self.positions) == 0:
            print("Aucun point enregistré pour le fantôme.")
            return

        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(self.positions, file)

        self.saved = True
        print("Fantôme sauvegardé dans :", self.filename)