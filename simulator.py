import pygame
import math
import streamlit as st
from ultralytics import YOLO


MODEL_PATH = "runs/detect/train-3/weights/best.pt"


def run_simulation(target_speed=5, tracking_mode="Ground Truth"):

    pygame.init()

    width = 640
    height = 480

    screen = pygame.Surface((width, height))
    screen.fill((5, 9, 13))

    # --------------------------------------------------------
    # Colors
    # --------------------------------------------------------

    grid_color = (25, 38, 48)
    target_color = (35, 120, 240)
    hud_color = (80, 230, 170)
    text_color = (180, 195, 205)
    error_color = (230, 170, 70)

    # --------------------------------------------------------
    # Sensor grid
    # --------------------------------------------------------

    for x in range(0, width, 40):
        pygame.draw.line(
            screen,
            grid_color,
            (x, 0),
            (x, height),
            1
        )

    for y in range(0, height, 40):
        pygame.draw.line(
            screen,
            grid_color,
            (0, y),
            (width, y),
            1
        )

    # --------------------------------------------------------
    # Camera center
    # --------------------------------------------------------

    camera_x = width // 2
    camera_y = height // 2

    # --------------------------------------------------------
    # Persistent target state
    # --------------------------------------------------------

    if "target_x" not in st.session_state:
        st.session_state.target_x = width // 2 + 80

    if "target_y" not in st.session_state:
        st.session_state.target_y = height // 2

    if "velocity_x" not in st.session_state:
        st.session_state.velocity_x = target_speed * 0.8

    if "velocity_y" not in st.session_state:
        st.session_state.velocity_y = target_speed * 0.35

    target_x = st.session_state.target_x
    target_y = st.session_state.target_y

    velocity_x = target_speed * 0.8
    velocity_y = target_speed * 0.35

    target_radius = 45

    # --------------------------------------------------------
    # Move target
    # --------------------------------------------------------

    target_x += velocity_x
    target_y += velocity_y

    # --------------------------------------------------------
    # Bounce from sensor boundaries
    # --------------------------------------------------------

    if target_x > width - target_radius or target_x < target_radius:
        velocity_x *= -1
        target_x = max(
            target_radius,
            min(width - target_radius, target_x)
        )

    if target_y > height - target_radius or target_y < target_radius:
        velocity_y *= -1
        target_y = max(
            target_radius,
            min(height - target_radius, target_y)
        )

    # Save state for the next Streamlit rerun
    st.session_state.target_x = target_x
    st.session_state.target_y = target_y
    st.session_state.velocity_x = velocity_x
    st.session_state.velocity_y = velocity_y

    # --------------------------------------------------------
    # Draw target
    # --------------------------------------------------------

    pygame.draw.circle(
        screen,
        target_color,
        (int(target_x), int(target_y)),
        target_radius
    )

    yolo_confidence = 0.0
    yolo_found = False

    detected_x = target_x
    detected_y = target_y

    # --------------------------------------------------------
    # YOLO tracking
    # --------------------------------------------------------

    if tracking_mode == "YOLO":

        model = YOLO(MODEL_PATH)

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

            best_index = results[0].boxes.conf.argmax()
            best_box = results[0].boxes[best_index]

            x1, y1, x2, y2 = best_box.xyxy[0].tolist()

            yolo_confidence = float(best_box.conf[0])
            yolo_found = True

            detected_x = (x1 + x2) / 2
            detected_y = (y1 + y2) / 2

            camera_x += (
                detected_x - camera_x
            ) * 0.5

            camera_y += (
                detected_y - camera_y
            ) * 0.5

    # --------------------------------------------------------
    # Ground Truth tracking
    # --------------------------------------------------------

    elif tracking_mode == "Ground Truth":

        camera_x += (
            target_x - camera_x
        ) * 0.5

        camera_y += (
            target_y - camera_y
        ) * 0.5

    # --------------------------------------------------------
    # Alignment error
    # --------------------------------------------------------

    error_x = target_x - camera_x
    error_y = target_y - camera_y

    total_error = math.sqrt(
        error_x ** 2 +
        error_y ** 2
    )

    if total_error < 5:
        alignment_status = "ALIGNED"

    elif total_error < 40:
        alignment_status = "ACQUIRING"

    else:
        alignment_status = "SEARCHING"

    # --------------------------------------------------------
    # Target bounding box
    # --------------------------------------------------------

    box_left = int(target_x - target_radius)
    box_top = int(target_y - target_radius)
    box_size = target_radius * 2

    pygame.draw.rect(
        screen,
        hud_color,
        (
            box_left,
            box_top,
            box_size,
            box_size
        ),
        2
    )

    # --------------------------------------------------------
    # Camera crosshair
    # --------------------------------------------------------

    cx = int(camera_x)
    cy = int(camera_y)

    crosshair_size = 18

    pygame.draw.line(
        screen,
        hud_color,
        (
            cx - crosshair_size,
            cy
        ),
        (
            cx + crosshair_size,
            cy
        ),
        2
    )

    pygame.draw.line(
        screen,
        hud_color,
        (
            cx,
            cy - crosshair_size
        ),
        (
            cx,
            cy + crosshair_size
        ),
        2
    )

    pygame.draw.circle(
        screen,
        hud_color,
        (cx, cy),
        4,
        1
    )

    # --------------------------------------------------------
    # Alignment vector
    # --------------------------------------------------------

    pygame.draw.line(
        screen,
        error_color,
        (cx, cy),
        (
            int(target_x),
            int(target_y)
        ),
        2
    )

    # --------------------------------------------------------
    # Tracking needle
    # --------------------------------------------------------

    angle = math.atan2(
        target_y - camera_y,
        target_x - camera_x
    )

    needle_length = 70

    needle_x = (
        camera_x +
        math.cos(angle) *
        needle_length
    )

    needle_y = (
        camera_y +
        math.sin(angle) *
        needle_length
    )

    pygame.draw.line(
        screen,
        (230, 80, 80),
        (cx, cy),
        (
            int(needle_x),
            int(needle_y)
        ),
        3
    )

    # --------------------------------------------------------
    # Fonts
    # --------------------------------------------------------

    font = pygame.font.Font(None, 20)
    small_font = pygame.font.Font(None, 16)

    # --------------------------------------------------------
    # Top-left telemetry
    # --------------------------------------------------------

    labels = [
        "SENSOR CAM-01",
        "FOV 60 DEG",
        "VIRTUAL OPTICAL CHANNEL",
    ]

    for i, text in enumerate(labels):

        surface = small_font.render(
            text,
            True,
            text_color
        )

        screen.blit(
            surface,
            (
                18,
                16 + i * 18
            )
        )

    # --------------------------------------------------------
    # Top-right telemetry
    # --------------------------------------------------------

    mode_text = (
        f"TRACKING: "
        f"{tracking_mode.upper()}"
    )

    surface = small_font.render(
        mode_text,
        True,
        hud_color
    )

    screen.blit(
        surface,
        (430, 16)
    )

    status_text = (
        f"STATUS: "
        f"{alignment_status}"
    )

    surface = small_font.render(
        status_text,
        True,
        hud_color
        if alignment_status == "ALIGNED"
        else error_color
    )

    screen.blit(
        surface,
        (430, 35)
    )

    # --------------------------------------------------------
    # Target label
    # --------------------------------------------------------

    target_label = "TARGET"

    if yolo_found:
        target_label += (
            f"  CONF "
            f"{yolo_confidence:.2f}"
        )

    surface = small_font.render(
        target_label,
        True,
        hud_color
    )

    screen.blit(
        surface,
        (
            box_left,
            box_top - 20
        )
    )

    # --------------------------------------------------------
    # Bottom-left error telemetry
    # --------------------------------------------------------

    error_lines = [
        f"ERROR X: {error_x:+.2f} PX",
        f"ERROR Y: {error_y:+.2f} PX",
        f"TOTAL ERROR: {total_error:.2f} PX",
    ]

    for i, text in enumerate(error_lines):

        surface = font.render(
            text,
            True,
            text_color
        )

        screen.blit(
            surface,
            (
                18,
                height - 70 + i * 18
            )
        )

    # --------------------------------------------------------
    # Optical status
    # --------------------------------------------------------

    optical_text = (
        "● OPTICAL CHANNEL ACTIVE"
    )

    surface = small_font.render(
        optical_text,
        True,
        hud_color
    )

    screen.blit(
        surface,
        (
            420,
            height - 25
        )
    )

    pygame.quit()

    return screen, error_x, error_y