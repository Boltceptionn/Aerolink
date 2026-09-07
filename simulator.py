import pygame
import math
import random
import streamlit as st
from ultralytics import YOLO


MODEL_PATH = "runs/detect/train-3/weights/best.pt"

_yolo_model_cache = None


@st.cache_resource(show_spinner=False)
def _load_yolo_cached(model_path):
    return YOLO(model_path)


def get_yolo_model(model_path=MODEL_PATH):
    """Returns a cached YOLO model instance so weights are not reloaded every frame."""
    global _yolo_model_cache
    if _yolo_model_cache is None:
        try:
            _yolo_model_cache = _load_yolo_cached(model_path)
        except Exception:
            _yolo_model_cache = YOLO(model_path)
    return _yolo_model_cache


def reset_simulation_state(
    width=640,
    height=480,
    target_speed=5,
    initial_position="Standard (+80px)"
):
    """Resets persistent simulation and alignment telemetry state."""
    st.session_state.camera_x = width // 2
    st.session_state.camera_y = height // 2

    if initial_position == "Center (0px)":
        st.session_state.target_x = width // 2
        st.session_state.target_y = height // 2
    elif initial_position == "Far Off-Axis (+180px)":
        st.session_state.target_x = width // 2 + 180
        st.session_state.target_y = height // 2 + 60
    elif initial_position == "High Elevation (-120px)":
        st.session_state.target_x = width // 2 + 50
        st.session_state.target_y = height // 2 - 120
    else:  # "Standard (+80px)"
        st.session_state.target_x = width // 2 + 80
        st.session_state.target_y = height // 2

    st.session_state.velocity_x = target_speed * 0.8
    st.session_state.velocity_y = target_speed * 0.35
    st.session_state.previous_target_x = st.session_state.target_x
    st.session_state.previous_target_y = st.session_state.target_y
    st.session_state.last_detected_x = st.session_state.target_x
    st.session_state.last_detected_y = st.session_state.target_y
    st.session_state.yolo_found = False
    st.session_state.yolo_confidence = 0.0
    st.session_state.total_error = math.sqrt(
        (st.session_state.target_x - st.session_state.camera_x) ** 2 +
        (st.session_state.target_y - st.session_state.camera_y) ** 2
    )
    st.session_state.error_x = st.session_state.target_x - st.session_state.camera_x
    st.session_state.error_y = st.session_state.target_y - st.session_state.camera_y
    st.session_state.alignment_status = "SEARCHING"
    st.session_state.error_history = []
    st.session_state.error_history_x = []
    st.session_state.error_history_y = []
    st.session_state.confidence_history = []
    st.session_state.acquisition_time = None
    st.session_state.acquisition_status = "STANDBY"
    st.session_state.sim_step = 0


def run_simulation(
    target_speed=5,
    tracking_mode="Ground Truth",
    trajectory="Linear Bounce",
    camera_fov=60,
    detection_noise=0.0,
    prediction_horizon=8,
    controller_gain=0.5
):

    if not pygame.get_init():
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
    tracking_color = (0, 229, 255)
    alert_color = (239, 68, 68)

    # --------------------------------------------------------
    # Sensor grid
    # --------------------------------------------------------

    for x in range(0, width, 40):
        pygame.draw.line(screen, grid_color, (x, 0), (x, height), 1)

    for y in range(0, height, 40):
        pygame.draw.line(screen, grid_color, (0, y), (width, y), 1)

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

    # Maintain velocity magnitude matching user target_speed
    sign_vx = 1.0 if st.session_state.velocity_x >= 0 else -1.0
    sign_vy = 1.0 if st.session_state.velocity_y >= 0 else -1.0
    velocity_x = sign_vx * abs(target_speed * 0.8)
    velocity_y = sign_vy * abs(target_speed * 0.35)

    target_radius = 45

    # --------------------------------------------------------
    # Target Motion / Trajectory Profile
    # --------------------------------------------------------

    st.session_state.sim_step = st.session_state.get("sim_step", 0) + 1
    step = st.session_state.sim_step

    if trajectory == "Sinusoidal Wave":
        target_x += velocity_x
        target_y = (height // 2) + math.sin(step * 0.08 * (target_speed / 5.0)) * (height * 0.32)
        if target_x > width - target_radius:
            target_x = width - target_radius
            velocity_x = -abs(velocity_x)
        elif target_x < target_radius:
            target_x = target_radius
            velocity_x = abs(velocity_x)

    elif trajectory == "Figure-8 Orbit":
        scale_x = (width // 2) - target_radius - 20
        scale_y = (height // 2) - target_radius - 20
        t = step * 0.04 * (target_speed / 5.0)
        target_x = (width // 2) + math.sin(t) * scale_x
        target_y = (height // 2) + math.sin(2 * t) * scale_y * 0.65

    elif trajectory == "Maneuvering":
        if step % 20 == 0:
            angle = ((step * 47) % 360) * (math.pi / 180.0)
            velocity_x = math.cos(angle) * target_speed
            velocity_y = math.sin(angle) * target_speed
        target_x += velocity_x
        target_y += velocity_y
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

    else:  # "Linear Bounce"
        target_x += velocity_x
        target_y += velocity_y
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
    # Optical Sensor Aperture / Camera FOV Ring
    # --------------------------------------------------------

    aperture_radius = int((camera_fov / 60.0) * 140)
    pygame.draw.circle(
        screen,
        (20, 36, 48),
        (int(camera_x), int(camera_y)),
        aperture_radius,
        1
    )

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

        model = get_yolo_model(MODEL_PATH)

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

            x1, y1, x2, y2 = best_box.xyxy[0].tolist()

            yolo_confidence = float(best_box.conf[0])
            yolo_found = True

            detected_x = (x1 + x2) / 2
            detected_y = (y1 + y2) / 2
            st.session_state.last_detected_x = detected_x
            st.session_state.last_detected_y = detected_y
        else:
            yolo_found = False
            if "last_detected_x" in st.session_state:
                detected_x = st.session_state.last_detected_x
                detected_y = st.session_state.last_detected_y

    # --------------------------------------------------------
    # Detection Noise Injection
    # --------------------------------------------------------

    if detection_noise > 0.0:
        detected_x += random.gauss(0, detection_noise)
        detected_y += random.gauss(0, detection_noise)

    # --------------------------------------------------------
    # Estimate target velocity
    # --------------------------------------------------------

    if "previous_target_x" not in st.session_state:
        st.session_state.previous_target_x = detected_x

    if "previous_target_y" not in st.session_state:
        st.session_state.previous_target_y = detected_y

    estimated_velocity_x = detected_x - st.session_state.previous_target_x
    estimated_velocity_y = detected_y - st.session_state.previous_target_y

    st.session_state.previous_target_x = detected_x
    st.session_state.previous_target_y = detected_y

    # --------------------------------------------------------
    # Predict future target position
    # --------------------------------------------------------

    predicted_x = detected_x + estimated_velocity_x * prediction_horizon
    predicted_y = detected_y + estimated_velocity_y * prediction_horizon

    # Keep prediction inside camera frame
    predicted_x = max(0, min(width, predicted_x))
    predicted_y = max(0, min(height, predicted_y))

    # --------------------------------------------------------
    # Proportional alignment controller
    # --------------------------------------------------------

    pointing_error_x = predicted_x - camera_x
    pointing_error_y = predicted_y - camera_y

    kp = controller_gain

    camera_x += kp * pointing_error_x
    camera_y += kp * pointing_error_y

    # --------------------------------------------------------
    # Save camera state
    # --------------------------------------------------------

    st.session_state.camera_x = camera_x
    st.session_state.camera_y = camera_y

    # --------------------------------------------------------
    # Alignment error & 4-State Machine
    # --------------------------------------------------------

    error_x = target_x - camera_x
    error_y = target_y - camera_y

    total_error = math.sqrt(error_x ** 2 + error_y ** 2)

    if total_error < 5:
        alignment_status = "LOCKED"
    elif total_error < 25:
        alignment_status = "ACQUIRING"
    elif total_error < 70 and (tracking_mode == "Ground Truth" or yolo_found):
        alignment_status = "TRACKING"
    else:
        alignment_status = "SEARCHING"

    st.session_state.total_error = total_error
    st.session_state.error_x = error_x
    st.session_state.error_y = error_y
    st.session_state.alignment_status = alignment_status
    st.session_state.yolo_found = yolo_found
    st.session_state.yolo_confidence = yolo_confidence
    st.session_state.detected_x = detected_x
    st.session_state.detected_y = detected_y
    st.session_state.predicted_x = predicted_x
    st.session_state.predicted_y = predicted_y
    st.session_state.estimated_velocity_x = estimated_velocity_x
    st.session_state.estimated_velocity_y = estimated_velocity_y

    # --------------------------------------------------------
    # Draw prediction point & vector
    # --------------------------------------------------------

    pygame.draw.circle(
        screen,
        prediction_color,
        (int(predicted_x), int(predicted_y)),
        7,
        2
    )

    pygame.draw.line(
        screen,
        prediction_color,
        (int(detected_x), int(detected_y)),
        (int(predicted_x), int(predicted_y)),
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
        (box_left, box_top, box_size, box_size),
        2
    )

    # --------------------------------------------------------
    # Camera crosshair
    # --------------------------------------------------------

    cx = int(camera_x)
    cy = int(camera_y)
    crosshair_size = 18

    pygame.draw.line(screen, hud_color, (cx - crosshair_size, cy), (cx + crosshair_size, cy), 2)
    pygame.draw.line(screen, hud_color, (cx, cy - crosshair_size), (cx, cy + crosshair_size), 2)
    pygame.draw.circle(screen, hud_color, (cx, cy), 4, 1)

    # --------------------------------------------------------
    # Alignment vector & Tracking needle
    # --------------------------------------------------------

    pygame.draw.line(
        screen,
        error_color,
        (cx, cy),
        (int(target_x), int(target_y)),
        2
    )

    angle = math.atan2(target_y - camera_y, target_x - camera_x)
    needle_length = 70
    needle_x = camera_x + math.cos(angle) * needle_length
    needle_y = camera_y + math.sin(angle) * needle_length

    pygame.draw.line(screen, (230, 80, 80), (cx, cy), (int(needle_x), int(needle_y)), 3)

    # --------------------------------------------------------
    # Fonts & HUD overlays
    # --------------------------------------------------------

    font = pygame.font.Font(None, 20)
    small_font = pygame.font.Font(None, 16)

    # Top-left telemetry
    labels = [
        "SENSOR: VIRTUAL OPTICAL CAM-01",
        f"FOV: {camera_fov} DEG | APERTURE OK",
        f"TRAJECTORY: {trajectory.upper()}",
    ]

    for i, text in enumerate(labels):
        surface = small_font.render(text, True, text_color)
        screen.blit(surface, (18, 16 + i * 18))

    # Top-right telemetry
    mode_text = f"TRACKING: {tracking_mode.upper()}"
    surface = small_font.render(mode_text, True, hud_color)
    screen.blit(surface, (430, 16))

    status_text = f"STATUS: {alignment_status}"
    if alignment_status == "LOCKED":
        status_color = hud_color
    elif alignment_status == "ACQUIRING":
        status_color = error_color
    elif alignment_status == "TRACKING":
        status_color = tracking_color
    else:
        status_color = alert_color

    surface = small_font.render(status_text, True, status_color)
    screen.blit(surface, (430, 35))

    # Target label
    target_label = "TARGET"
    if yolo_found:
        target_label += f"  CONF {yolo_confidence:.2f}"

    surface = small_font.render(target_label, True, hud_color)
    screen.blit(surface, (box_left, box_top - 20))

    # Prediction label
    prediction_label = f"PRED (H={prediction_horizon})"
    surface = small_font.render(prediction_label, True, prediction_color)
    screen.blit(surface, (int(predicted_x) + 10, int(predicted_y) - 10))

    # Bottom-left telemetry
    error_lines = [
        f"ERR X: {error_x:+.1f} PX",
        f"ERR Y: {error_y:+.1f} PX",
        f"TOTAL: {total_error:.1f} PX",
    ]

    for i, text in enumerate(error_lines):
        surface = font.render(text, True, text_color)
        screen.blit(surface, (18, height - 70 + i * 18))

    # Prediction telemetry
    prediction_text = f"LEAD HORIZON: {prediction_horizon} FRAMES | KP: {kp:.2f}"
    surface = small_font.render(prediction_text, True, prediction_color)
    screen.blit(surface, (340, height - 43))

    # Optical channel active
    optical_text = "● FSOC COARSE BEAM CHANNEL"
    surface = small_font.render(optical_text, True, hud_color if alignment_status in ["LOCKED", "ACQUIRING"] else error_color)
    screen.blit(surface, (400, height - 25))

    return screen, error_x, error_y