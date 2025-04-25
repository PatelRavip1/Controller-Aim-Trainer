import pygame
import random
import math
import time

# --- Init ---
pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    print("No joystick connected!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Custom Aim Trainer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

WHITE, RED, BLACK, BLUE = (255, 255, 255), (255, 0, 0), (0, 0, 0), (0, 0, 255)

# --- Choose Aiming Stick (only reads axis) ---
def choose_stick():
    screen.fill(WHITE)
    msg = font.render(" Move the stick you want to use for AIMING", True, BLACK)
    screen.blit(msg, (80, HEIGHT // 2 - 20))
    pygame.display.flip()

    pygame.event.clear()

    while True:
        pygame.event.pump()
        for axis in range(joystick.get_numaxes()):
            val = joystick.get_axis(axis)
            
            # Skip known trigger axes (usually axis 4 & 5), or if resting value is already non-zero
            if axis in [4, 5] or abs(val) < 0.5:
                continue
            
            # Confirm it's a valid X axis (even number) and paired with the next Y axis
            if axis % 2 == 0 and axis + 1 < joystick.get_numaxes():
                y_val = joystick.get_axis(axis + 1)
                if abs(y_val) > 0.2:  # Some movement on Y too
                    return axis, axis + 1


# --- Choose Shooting Button/Trigger (only reads button/axis) ---
def choose_button():
    screen.fill(WHITE)
    msg = font.render(" Press the BUTTON or TRIGGER you want for SHOOTING", True, BLACK)
    screen.blit(msg, (40, HEIGHT // 2 - 20))
    pygame.display.flip()

    pygame.event.clear()  # Clear previous inputs

    while True:
        pygame.event.pump()
        # Buttons
        for btn in range(joystick.get_numbuttons()):
            if joystick.get_button(btn):
                return 'button', btn
        # Triggers (axis)
        for axis in range(joystick.get_numaxes()):
            val = joystick.get_axis(axis)
            if val > 0.8:
                return 'axis', axis

# --- Game Setup ---
x_axis_index, y_axis_index = choose_stick()
trigger_type, trigger_index = choose_button()

target_radius = 30
target_pos = [random.randint(target_radius, WIDTH - target_radius),
              random.randint(target_radius, HEIGHT - target_radius)]
crosshair_x, crosshair_y = WIDTH // 2, HEIGHT // 2
crosshair_radius = 10
score = 0
hit_times = []
last_hit_time = time.time()

# --- Game Loop ---
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Aiming with chosen stick
    x_axis = joystick.get_axis(x_axis_index)
    y_axis = joystick.get_axis(y_axis_index)
    crosshair_x += int(x_axis * 10)
    crosshair_y += int(y_axis * 10)
    crosshair_x = max(0, min(WIDTH, crosshair_x))
    crosshair_y = max(0, min(HEIGHT, crosshair_y))

    # Shooting with chosen button/trigger
    shoot = False
    if trigger_type == 'button':
        shoot = joystick.get_button(trigger_index)
    elif trigger_type == 'axis':
        shoot = joystick.get_axis(trigger_index) > 0.8

    if shoot:
        dist = math.hypot(crosshair_x - target_pos[0], crosshair_y - target_pos[1])
        if dist < target_radius:
            score += 1
            current_time = time.time()
            hit_times.append(current_time - last_hit_time)
            last_hit_time = current_time
            target_pos = [random.randint(target_radius, WIDTH - target_radius),
                          random.randint(target_radius, HEIGHT - target_radius)]
            pygame.time.wait(200)  # debounce

    # Draw elements
    pygame.draw.circle(screen, RED, target_pos, target_radius)
    pygame.draw.circle(screen, BLUE, (crosshair_x, crosshair_y), crosshair_radius)

    # Score and timing
    screen.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))
    if hit_times:
        avg_time = sum(hit_times) / len(hit_times)
        screen.blit(font.render(f"Avg Time: {avg_time:.2f}s", True, BLACK), (WIDTH - 250, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
