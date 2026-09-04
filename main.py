import math
import pygame

# Start pygame (this sets up the window, drawing, and events)
pygame.init()

# Window size in pixels (width, height)
WIDTH = 640
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My First Circle")

# Colors are (red, green, blue) values from 0 to 255
WHITE = (255, 255, 255)
BLUE = (50, 120, 220)
RED = (200, 50, 50)
BLACK = (0, 0, 0)

# Font for the numbers on the screen
font = pygame.font.Font(None, 28)

# Circle position, size, and how far it moves each frame
circle_x = WIDTH // 2
circle_y = HEIGHT // 2
circle_radius = 60
speed_x = 3
speed_y = 2

# Camera marker: stays in one place, and turns smoothly toward the circle
camera_x = WIDTH // 2
camera_y = HEIGHT // 2
camera_marker_size = 24
camera_angle = 0
turn_speed = 0.08  # how much of the remaining turn we do each frame (0 to 1)

# Remember old target positions so the camera looks a little late
delay_frames = 18
past_x = []
past_y = []

clock = pygame.time.Clock()

running = True
while running:
    # Check events (keyboard, mouse, closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the circle
    circle_x = circle_x + speed_x
    circle_y = circle_y + speed_y

    # Bounce when the circle hits a wall
    if circle_x - circle_radius <= 0 or circle_x + circle_radius >= WIDTH:
        speed_x = -speed_x
    if circle_y - circle_radius <= 0 or circle_y + circle_radius >= HEIGHT:
        speed_y = -speed_y

    # Save this frame's target position, then look at an older one (small delay)
    past_x.append(circle_x)
    past_y.append(circle_y)
    if len(past_x) > delay_frames:
        delayed_x = past_x.pop(0)
        delayed_y = past_y.pop(0)
    else:
        delayed_x = circle_x
        delayed_y = circle_y

    # The direction we want to point (at the delayed target position)
    dx = delayed_x - camera_x
    dy = delayed_y - camera_y
    target_angle = math.atan2(dy, dx)

    # How far we still need to turn
    angle_diff = target_angle - camera_angle

    # Keep the difference between -pi and pi so we turn the short way
    while angle_diff > math.pi:
        angle_diff = angle_diff - 2 * math.pi
    while angle_diff < -math.pi:
        angle_diff = angle_diff + 2 * math.pi

    # Turn a fraction of the way each frame (smooth follow, not an instant snap)
    camera_angle = camera_angle + angle_diff * turn_speed

    # Tip of the arrow, using the camera's current pointing angle
    tip_x = camera_x + math.cos(camera_angle) * camera_marker_size
    tip_y = camera_y + math.sin(camera_angle) * camera_marker_size

    # Back corners of the arrow (a little left and right of the opposite direction)
    left_x = camera_x + math.cos(camera_angle + 2.5) * (camera_marker_size * 0.6)
    left_y = camera_y + math.sin(camera_angle + 2.5) * (camera_marker_size * 0.6)
    right_x = camera_x + math.cos(camera_angle - 2.5) * (camera_marker_size * 0.6)
    right_y = camera_y + math.sin(camera_angle - 2.5) * (camera_marker_size * 0.6)

    # Fill the background, then draw the circle on top
    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (circle_x, circle_y), circle_radius)

    # Draw the camera marker as a red arrow (position stays fixed)
    pygame.draw.polygon(
        screen,
        RED,
        [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)],
    )

    # Show the target position and the camera's pointing angle
    angle_degrees = math.degrees(camera_angle)
    target_text = font.render(
        f"Target X: {circle_x:.1f}   Target Y: {circle_y:.1f}",
        True,
        BLACK,
    )
    angle_text = font.render(
        f"Camera angle: {angle_degrees:.1f} degrees",
        True,
        BLACK,
    )
    screen.blit(target_text, (10, 10))
    screen.blit(angle_text, (10, 40))

    # Show this frame on the screen
    pygame.display.flip()

    # Keep the game at 60 frames per second so movement is smooth
    clock.tick(60)

pygame.quit()
