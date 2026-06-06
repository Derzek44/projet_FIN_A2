import math


class PhysicsEngine:
    def __init__(self):
        self.friction = 0.985
        self.max_speed = 1000.0
        self.turn_speed = 3
        self.accel = 500.0

    def limit_speed(self, vx, vy, max_speed):
        speed = math.sqrt(vx**2 + vy**2)

        if speed == 0:
            return 0.0, 0.0

        if speed > max_speed:
            ratio = max_speed / speed
            vx = vx * ratio
            vy = vy * ratio

        return vx, vy

    def angle_from_velocity(self, vx, vy):
        if vx == 0 and vy == 0:
            return 0.0

        return math.atan2(vy, vx)

    def update_physics(self, x, y, vx, vy, angle_control, go_up, dt, off_track=False):
        if go_up:
            vx = vx + math.cos(angle_control) * self.accel * dt
            vy = vy + math.sin(angle_control) * self.accel * dt

        max_speed = self.max_speed

        if off_track:
            max_speed = max_speed * 0.4

        vx, vy = self.limit_speed(vx, vy, max_speed)

        x = x + vx * dt
        y = y + vy * dt

        vx = vx * self.friction
        vy = vy * self.friction

        angle_velocity = self.angle_from_velocity(vx, vy)

        return x, y, vx, vy, angle_velocity