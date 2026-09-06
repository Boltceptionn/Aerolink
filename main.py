import math
import numpy as np
import pygame
from ultralytics import YOLO

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

# Load the trained detector once (not inside the loop)
model = YOLO("runs/detect/train/weights/best.pt")
yolo_mode = False  # False = existing ground-truth tracking
yolo_every_n_frames = 10
yolo_gain = 0.0005  # small radians per pixel of horizontal error
frame_count = 0
error_x = 0.0
error_y = 0.0
yolo_found = False

clock = pygame.time.Clock()

running = True
while running:
    # Check events (keyboard, mouse, closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                pygame.image.save(screen, "frame.png")
            if event.key == pygame.K_m:
                yolo_mode = not yolo_mode

    frame_count = frame_count + 1

    # Move the circle
    circle_x = circle_x + speed_x
    circle_y = circle_y + speed_y

    # Bounce when the circle hits a wall
    if circle_x - circle_radius <= 0 or circle_x + circle_radius >= WIDTH:
        speed_x = -speed_x
    if circle_y - circle_radius <= 0 or circle_y + circle_radius >= HEIGHT:
        speed_y = -speed_y

    # Next position = current position + current speed
    predicted_x = circle_x + speed_x
    predicted_y = circle_y + speed_y

    # Save this frame's target position, then look at an older one (small delay)
    past_x.append(circle_x)
    past_y.append(circle_y)
    if len(past_x) > delay_frames:
        delayed_x = past_x.pop(0)
        delayed_y = past_y.pop(0)
    else:
        delayed_x = circle_x
        delayed_y = circle_y

    # Fill the background, then draw the circle (needed before YOLO sees the frame)
    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (circle_x, circle_y), circle_radius)

    # Run YOLO on the current window pixels, but only every N frames
    if frame_count % yolo_every_n_frames == 0:
        frame_rgb = np.transpose(pygame.surfarray.array3d(screen), (1, 0, 2)).copy()
        results = model(frame_rgb, verbose=False)
        result = results[0]
        yolo_found = False
        for box in result.boxes:
            class_id = int(box.cls[0])
            name = result.names[class_id]
            if name != "fsoc_target":
                continue
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            image_height, image_width = result.orig_shape
            camera_center_x = image_width / 2
            camera_center_y = image_height / 2
            error_x = center_x - camera_center_x
            error_y = center_y - camera_center_y
            yolo_found = True
            break

    if not yolo_mode:
        # Existing mode: point at the delayed ground-truth circle position
        dx = delayed_x - camera_x
        dy = delayed_y - camera_y
        target_angle = math.atan2(dy, dx)

        angle_diff = target_angle - camera_angle
        while angle_diff > math.pi:
            angle_diff = angle_diff - 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff = angle_diff + 2 * math.pi

        camera_angle = camera_angle + angle_diff * turn_speed
    else:
        # YOLO mode: pan only, using horizontal pixel error
        if yolo_found:
            camera_angle = camera_angle + yolo_gain * error_x

    # Tip of the arrow, using the camera's current pointing angle
    tip_x = camera_x + math.cos(camera_angle) * camera_marker_size
    tip_y = camera_y + math.sin(camera_angle) * camera_marker_size

    # Back corners of the arrow (a little left and right of the opposite direction)
    left_x = camera_x + math.cos(camera_angle + 2.5) * (camera_marker_size * 0.6)
    left_y = camera_y + math.sin(camera_angle + 2.5) * (camera_marker_size * 0.6)
    right_x = camera_x + math.cos(camera_angle - 2.5) * (camera_marker_size * 0.6)
    right_y = camera_y + math.sin(camera_angle - 2.5) * (camera_marker_size * 0.6)

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
    predicted_text = font.render(
        f"Predicted X: {predicted_x:.1f}   Predicted Y: {predicted_y:.1f}",
        True,
        BLACK,
    )
    if yolo_mode:
        mode_label = "Control: YOLO (press M to switch)"
    else:
        mode_label = "Control: ground truth (press M to switch)"
    mode_text = font.render(mode_label, True, BLACK)
    if yolo_found:
        error_text = font.render(
            f"YOLO alignment error: ({error_x:.1f}, {error_y:.1f})",
            True,
            BLACK,
        )
    else:
        error_text = font.render("YOLO alignment error: no fsoc_target", True, BLACK)
    screen.blit(target_text, (10, 10))
    screen.blit(angle_text, (10, 40))
    screen.blit(predicted_text, (10, 70))
    screen.blit(mode_text, (10, 100))
    screen.blit(error_text, (10, 130))

    # Show this frame on the screen
    pygame.display.flip()

    # Keep the game at 60 frames per second so movement is smooth
    clock.tick(60)

pygame.quit()
