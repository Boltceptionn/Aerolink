import streamlit as st
import pygame
from simulator import run_simulation


st.set_page_config(
    page_title="AEROLINK Mission Control",
    page_icon="✈",
    layout="wide"
)


# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #080b0f;
    color: #e6edf3;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #e6edf3;
}

.aero-title {
    font-size: 34px;
    font-weight: 700;
    letter-spacing: 6px;
}

.aero-subtitle {
    color: #7f8c99;
    font-size: 11px;
    letter-spacing: 2px;
}

.aero-status {
    color: #35d07f;
    font-family: monospace;
    font-size: 12px;
    letter-spacing: 1px;
}

.section-title {
    color: #7f8c99;
    font-family: monospace;
    font-size: 11px;
    letter-spacing: 2px;
    margin-top: 12px;
    margin-bottom: 12px;
}

.telemetry {
    background: #0e141b;
    border: 1px solid #26313d;
    padding: 12px;
    margin-bottom: 8px;
}

.telemetry-label {
    color: #687582;
    font-family: monospace;
    font-size: 9px;
    letter-spacing: 1px;
}

.telemetry-value {
    color: #e6edf3;
    font-family: monospace;
    font-size: 19px;
    font-weight: bold;
    margin-top: 4px;
}

.footer {
    text-align: center;
    color: #46515c;
    font-family: monospace;
    font-size: 9px;
    letter-spacing: 2px;
    margin-top: 25px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="aero-title">AEROLINK</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="aero-subtitle">'
    'VIRTUAL FREE-SPACE OPTICAL COMMUNICATION TERMINAL'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="aero-status">● SYSTEM NOMINAL</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# MAIN LAYOUT
# ============================================================

left, center, right = st.columns(
    [1, 2.5, 1]
)


# ============================================================
# CONTROLS
# ============================================================

with left:

    st.markdown(
        '<div class="section-title">'
        'MISSION / CONFIGURATION'
        '</div>',
        unsafe_allow_html=True
    )

    target_speed = st.slider(
        "TARGET SPEED",
        1,
        10,
        5
    )

    camera_fov = st.slider(
        "CAMERA FOV",
        30,
        120,
        60
    )

    tracking_mode = st.selectbox(
        "TRACKING ALGORITHM",
        ["Ground Truth", "YOLO"]
    )

    start = st.button(
        "▶ START SIMULATION",
        use_container_width=True
    )

    reset = st.button(
        "↻ RESET",
        use_container_width=True
    )

    st.markdown(
        '<div class="telemetry">'
        '<div class="telemetry-label">MISSION MODE</div>'
        '<div class="telemetry-value">COARSE ALIGN</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# CAMERA
# ============================================================

with center:

    st.markdown(
        '<div class="section-title">'
        'SENSOR / VIRTUAL CAMERA FEED'
        '</div>',
        unsafe_allow_html=True
    )

    frame, error_x, error_y = run_simulation(
        target_speed=target_speed,
        tracking_mode=tracking_mode
    )

    frame = pygame.surfarray.array3d(frame)
    frame = frame.transpose(1, 0, 2)

    st.image(
        frame,
        use_container_width=True
    )


# ============================================================
# STATUS CALCULATION
# ============================================================

total_error = (
    error_x ** 2 +
    error_y ** 2
) ** 0.5


if total_error < 5:
    tracking_status = "ALIGNED"

elif total_error < 40:
    tracking_status = "ACQUIRING"

else:
    tracking_status = "SEARCHING"


# ============================================================
# TELEMETRY
# ============================================================

with right:

    st.markdown(
        '<div class="section-title">'
        'TELEMETRY / LIVE'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="telemetry">'
        f'<div class="telemetry-label">TRACKING MODE</div>'
        f'<div class="telemetry-value">{tracking_mode}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="telemetry">'
        f'<div class="telemetry-label">TARGET SPEED</div>'
        f'<div class="telemetry-value">{target_speed} PX/FRAME</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="telemetry">'
        f'<div class="telemetry-label">CAMERA FOV</div>'
        f'<div class="telemetry-value">{camera_fov}°</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="telemetry">'
        f'<div class="telemetry-label">HORIZONTAL ERROR</div>'
        f'<div class="telemetry-value">{error_x:+.1f} PX</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="telemetry">'
        f'<div class="telemetry-label">VERTICAL ERROR</div>'
        f'<div class="telemetry-value">{error_y:+.1f} PX</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="telemetry">'
        f'<div class="telemetry-label">TRACKING STATUS</div>'
        f'<div class="telemetry-value">{tracking_status}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ============================================================
# ALIGNMENT MONITOR
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">'
    'ALIGNMENT MONITOR'
    '</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)


with c1:
    st.metric(
        "TARGET",
        "DETECTED"
    )


with c2:
    st.metric(
        "PREDICTION",
        "READY"
    )


with c3:
    st.metric(
        "ALIGNMENT",
        tracking_status
    )


with c4:
    st.metric(
        "SYSTEM",
        "NOMINAL"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    'AEROLINK // VIRTUAL FSOC LABORATORY // COARSE ALIGNMENT'
    '</div>',
    unsafe_allow_html=True
)