import pygame


def run_simulation(target_speed=5, tracking_mode="Ground Truth"):
    pygame.init()

    width = 640
    height = 480

    screen = pygame.Surface((width, height))
    screen.fill((255, 255, 255))

    target_x = width // 2 + target_speed * 10
    target_y = height // 2

    pygame.draw.circle(
        screen,
        (50, 120, 220),
        (target_x, target_y),
        60
    )

    pygame.quit()

    return screen