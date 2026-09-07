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
    prediction_color = (180, 100, 255)

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
    # Persistent camera state
    # --------------------------------------------------------

    if "camera_x" not in st.session_state:
        st.session_state.camera_x = width // 2

    if "camera_y" not in st.session_state:
        st.session_state.camera_y = height // 2

    camera_x = st.session_state.camera_x
    camera_y = st.session_state.camera_y

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

    # Keep movement direction while allowing speed changes
    velocity_x = (
        abs(target_speed * 0.8)
        if st.session_state.velocity_x >= 0
        else -abs(target_speed * 0.8)
    )

    velocity_y = (
        abs(target_speed * 0.35)
        if st.session_state.velocity_y >= 0
        else -abs(target_speed * 0.35)
    )

    target_radius = 45

    # --------------------------------------------------------
    # Move target
    # --------------------------------------------------------

    target_x += velocity_x
    target_y += velocity_y

    # --------------------------------------------------------
    # Bounce from boundaries
    # --------------------------------------------------------

    if target_x > width - target_radius:

        target_x = width - target_radius
        velocity_x = -abs(velocity_x)

    elif target_x < target_radius:

        target_x = target_radius
        velocity_x = abs(velocity_x)

    if target_y > height - target_radius:

        target_y = height - target_radius
        velocity_y = -abs(velocity_y)

    elif target_y < target_radius:

        target_y = target_radius
        velocity_y = abs(velocity_y)

    # Save target state
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

    # --------------------------------------------------------
    # Detection variables
    # --------------------------------------------------------

    yolo_confidence = 0.0
    yolo_found = False

    detected_x = target_x
    detected_y = target_y

    # --------------------------------------------------------
    # YOLO detection
    # --------------------------------------------------------

    if tracking_mode == "YOLO":

        model = YOLO(MODEL_PATH)

        frame_rgb = pygame.surfarray.array3d(screen)
        frame_rgb = frame_rgb.transpose(1, 0, 2)

        results = model(
            frame_rgb,
            conf=0.1,
            verbose=False
        )

        if len(results[0].boxes) > 0:

            best_index = results[0].boxes.conf.argmax()
            best_box = results[0].boxes[best_index]

            x1, y1, x2, y2 = (
                best_box.xyxy[0].tolist()
            )

            yolo_confidence = float(
                best_box.conf[0]
            )

            yolo_found = True

            detected_x = (x1 + x2) / 2
            detected_y = (y1 + y2) / 2

    # --------------------------------------------------------
    # Estimate target velocity
    # --------------------------------------------------------

    if "previous_target_x" not in st.session_state:
        st.session_state.previous_target_x = detected_x

    if "previous_target_y" not in st.session_state:
        st.session_state.previous_target_y = detected_y

    estimated_velocity_x = (
        detected_x -
        st.session_state.previous_target_x
    )

    estimated_velocity_y = (
        detected_y -
        st.session_state.previous_target_y
    )

    st.session_state.previous_target_x = detected_x
    st.session_state.previous_target_y = detected_y

    # --------------------------------------------------------
    # Predict future target position
    # --------------------------------------------------------

    prediction_horizon = 8

    predicted_x = (
        detected_x +
        estimated_velocity_x *
        prediction_horizon
    )

    predicted_y = (
        detected_y +
        estimated_velocity_y *
        prediction_horizon
    )

    # Keep prediction inside camera frame
    predicted_x = max(
        0,
        min(width, predicted_x)
    )

    predicted_y = max(
        0,
        min(height, predicted_y)
    )

    # --------------------------------------------------------
    # Proportional alignment controller
    # --------------------------------------------------------

    pointing_error_x = predicted_x - camera_x
    pointing_error_y = predicted_y - camera_y

    kp = 0.5

    if tracking_mode == "YOLO":

        camera_x += kp * pointing_error_x
        camera_y += kp * pointing_error_y

    elif tracking_mode == "Ground Truth":

        camera_x += kp * pointing_error_x
        camera_y += kp * pointing_error_y

    # --------------------------------------------------------
    # Save camera state
    # --------------------------------------------------------

    st.session_state.camera_x = camera_x
    st.session_state.camera_y = camera_y

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
    # Draw prediction point
    # --------------------------------------------------------

    pygame.draw.circle(
        screen,
        prediction_color,
        (
            int(predicted_x),
            int(predicted_y)
        ),
        7,
        2
    )

    # Prediction vector
    pygame.draw.line(
        screen,
        prediction_color,
        (
            int(detected_x),
            int(detected_y)
        ),
        (
            int(predicted_x),
            int(predicted_y)
        ),
        2
    )

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

    # Prediction label
    prediction_label = "PREDICTED POSITION"

    surface = small_font.render(
        prediction_label,
        True,
        prediction_color
    )

    screen.blit(
        surface,
        (
            int(predicted_x) + 10,
            int(predicted_y) - 10
        )
    )

    # --------------------------------------------------------
    # Bottom-left telemetry
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
    # Prediction telemetry
    # --------------------------------------------------------

    prediction_text = (
        f"PREDICTION HORIZON: "
        f"{prediction_horizon} FRAMES"
    )

    surface = small_font.render(
        prediction_text,
        True,
        prediction_color
    )

    screen.blit(
        surface,
        (
            380,
            height - 43
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