import math

FRICTION = 0.985
MAX_SPEED = 1000.0
TURN_SPEED = 3
ACCEL = 500.0


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


def update_physics(x, y, vx, vy, angle_control, go_up, dt, off_track=False):

    if go_up:
        vx += math.cos(angle_control) * ACCEL * dt
        vy += math.sin(angle_control) * ACCEL * dt

    max_speed = MAX_SPEED
    if off_track:
        max_speed *= 0.4 
    vx, vy = limit_speed(vx, vy, max_speed)
    x += vx * dt
    y += vy * dt
    vx*= FRICTION
    vy *= FRICTION
    angle_velocity = angle_from_velocity(vx, vy)

    return x, y, vx, vy, angle_velocity
