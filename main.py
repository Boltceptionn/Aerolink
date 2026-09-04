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

# Circle position, size, and how far it moves each frame
circle_x = WIDTH // 2
circle_y = HEIGHT // 2
circle_radius = 60
speed_x = 3
speed_y = 2

# Camera marker: a fixed spot in the window (it does not move yet)
camera_x = WIDTH // 2
camera_y = HEIGHT // 2
camera_marker_size = 16

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

    # Fill the background, then draw the circle on top
    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (circle_x, circle_y), circle_radius)

    # Draw the camera marker as a red plus sign (it stays in the same place)
    pygame.draw.line(
        screen,
        RED,
        (camera_x - camera_marker_size, camera_y),
        (camera_x + camera_marker_size, camera_y),
        3,
    )
    pygame.draw.line(
        screen,
        RED,
        (camera_x, camera_y - camera_marker_size),
        (camera_x, camera_y + camera_marker_size),
        3,
    )

    # Show this frame on the screen
    pygame.display.flip()

    # Keep the game at 60 frames per second so movement is smooth
    clock.tick(60)

pygame.quit()
