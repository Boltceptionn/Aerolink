import pygame
import math
from ultralytics import YOLO


MODEL_PATH = "runs/detect/train-3/weights/best.pt"


def run_simulation(target_speed=5, tracking_mode="Ground Truth"):
    pygame.init()

    width = 640
    height = 480

    screen = pygame.Surface((width, height))
    screen.fill((255, 255, 255))

    # Target position
    target_x = width // 2 + target_speed * 20
    target_y = height // 2

    # Camera center
    camera_x = width // 2
    camera_y = height // 2

    # Draw target first so YOLO can see it
    pygame.draw.circle(
        screen,
        (50, 120, 220),
        (target_x, target_y),
        60
    )

    # YOLO tracking
    if tracking_mode == "YOLO":
        model = YOLO(MODEL_PATH)

        # Repeated detection and camera movement
        for _ in range(10):
            frame_rgb = pygame.surfarray.array3d(screen)
            frame_rgb = frame_rgb.transpose(1, 0, 2)

            results = model(
                frame_rgb,
                conf=0.1,
                verbose=False
            )

            if len(results[0].boxes) == 0:
                break

            # Pick highest-confidence detection
            best_box = results[0].boxes[
                results[0].boxes.conf.argmax()
            ]

            x1, y1, x2, y2 = best_box.xyxy[0].tolist()

            detected_x = (x1 + x2) / 2
            detected_y = (y1 + y2) / 2

            # Move camera toward detected target
            camera_x += (detected_x - camera_x) * 0.5
            camera_y += (detected_y - camera_y) * 0.5

    # Ground Truth tracking
    elif tracking_mode == "Ground Truth":
        camera_x += (target_x - camera_x) * 0.5
        camera_y += (target_y - camera_y) * 0.5

    # Tracking needle
    angle = math.atan2(
        target_y - camera_y,
        target_x - camera_x
    )

    needle_length = 70

    needle_x = camera_x + math.cos(angle) * needle_length
    needle_y = camera_y + math.sin(angle) * needle_length

    # Alignment line
    pygame.draw.line(
        screen,
        (180, 180, 180),
        (int(camera_x), int(camera_y)),
        (target_x, target_y),
        2
    )

    # Camera center
    pygame.draw.circle(
        screen,
        (35, 35, 35),
        (int(camera_x), int(camera_y)),
        6
    )

    # Needle
    pygame.draw.line(
        screen,
        (200, 50, 50),
        (int(camera_x), int(camera_y)),
        (int(needle_x), int(needle_y)),
        4
    )

    pygame.quit()

    error_x = target_x - camera_x
    error_y = target_y - camera_y

    return screen, error_x, error_y