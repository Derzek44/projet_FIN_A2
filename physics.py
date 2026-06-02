import math

FRICTION = 0.98
MAX_SPEED = 350.0
ANGLE_BLEND = 0.15
TURN_SPEED = 2.5
ACCEL = 300.0

def limit_speed(vx, vy, max_speed):
    speed = math.sqrt(vx**2 + vy**2)
    if speed == 0:
        return 0.0, 0.0
    if speed > max_speed:
        ratio = max_speed / speed
        vx *= ratio
        vy *= ratio
    return vx, vy

def angle_from_velocity(vx, vy):
    if vx == 0 and vy == 0:
        return 0.0
    return math.atan2(vy, vx)

def lerp_angle(a, b, t):
    diff = (b - a + math.pi) % (2 * math.pi) - math.pi
    return a + diff * t

def update_physics(x, y, vx, vy, angle_control, go_up, dt):
    if go_up:
        vx += math.cos(angle_control) * ACCEL * dt
        vy += math.sin(angle_control) * ACCEL * dt
    vx, vy = limit_speed(vx, vy, MAX_SPEED)
    x += vx * dt
    y += vy * dt
    vx *= FRICTION
    vy *= FRICTION
    angle_velocity = angle_from_velocity(vx, vy)
    return x, y, vx, vy, angle_velocity
