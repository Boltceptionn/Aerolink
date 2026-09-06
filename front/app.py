import streamlit as st
import pygame
from simulator import run_simulation


st.set_page_config(
    page_title="AEROLINK Mission Control",
    page_icon="✈",
    layout="wide"
)


# ---------- Styling ----------
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f14;
        color: #e6edf3;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        max-width: 1500px;
    }

    .topbar {
        padding: 18px 22px;
        border: 1px solid #26313d;
        border-radius: 12px;
        background: #111821;
        margin-bottom: 18px;
    }

    .brand {
        font-size: 30px;
        font-weight: 700;
        letter-spacing: 3px;
    }

    .subtitle {
        color: #8b98a7;
        font-size: 13px;
        letter-spacing: 1px;
    }

    .status {
        color: #35d07f;
        font-weight: 600;
        letter-spacing: 1px;
    }

    .panel {
        background: #111821;
        border: 1px solid #26313d;
        border-radius: 12px;
        padding: 18px;
        min-height: 100%;
    }

    .panel-title {
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #9aa8b7;
        margin-bottom: 14px;
    }

    .telemetry-card {
        background: #0c1219;
        border: 1px solid #26313d;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }

    .telemetry-label {
        color: #7f8c99;
        font-size: 11px;
        letter-spacing: 1px;
    }

    .telemetry-value {
        font-size: 22px;
        font-weight: 600;
        margin-top: 3px;
    }

    .footer {
        text-align: center;
        color: #566270;
        font-size: 11px;
        margin-top: 18px;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)


# ---------- Header ----------
st.markdown("""
<div class="topbar">
    <div class="brand">AEROLINK</div>
    <div class="subtitle">
        VIRTUAL FSOC ALIGNMENT & TRACKING SYSTEM
    </div>
    <div style="margin-top:8px;" class="status">
        ● SYSTEM ONLINE
    </div>
</div>
""", unsafe_allow_html=True)


# ---------- Main Layout ----------
left, center, right = st.columns([1, 2.4, 1])


# ---------- Mission Controls ----------
with left:
    st.markdown(
        '<div class="panel-title">MISSION CONFIGURATION</div>',
        unsafe_allow_html=True
    )

    target_speed = st.slider(
        "Target Speed",
        min_value=1,
        max_value=10,
        value=5
    )

    camera_fov = st.slider(
        "Camera FOV",
        min_value=30,
        max_value=120,
        value=60
    )

    tracking_mode = st.selectbox(
        "Tracking Mode",
        ["Ground Truth", "YOLO"]
    )

    st.markdown("<br>", unsafe_allow_html=True)

    start = st.button(
        "▶  START SIMULATION",
        use_container_width=True
    )

    reset = st.button(
        "↻  RESET",
        use_container_width=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="telemetry-card">
        <div class="telemetry-label">MISSION MODE</div>
        <div class="telemetry-value">COARSE ALIGN</div>
    </div>
    """, unsafe_allow_html=True)


# ---------- Camera View ----------
with center:
    st.markdown(
        '<div class="panel-title">VIRTUAL CAMERA FEED</div>',
        unsafe_allow_html=True
    )

    frame = run_simulation(
        target_speed=target_speed,
        tracking_mode=tracking_mode
    )

    frame = frame.copy()
    frame = pygame.surfarray.array3d(frame)
    frame = frame.transpose(1, 0, 2)

    st.image(
        frame,
        caption="LIVE SIMULATION",
        use_container_width=True
    )


# ---------- Telemetry ----------
with right:
    st.markdown(
        '<div class="panel-title">LIVE TELEMETRY</div>',
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div class="telemetry-card">
        <div class="telemetry-label">TRACKING MODE</div>
        <div class="telemetry-value">{tracking_mode}</div>
    </div>

    <div class="telemetry-card">
        <div class="telemetry-label">TARGET SPEED</div>
        <div class="telemetry-value">{target_speed}</div>
    </div>

    <div class="telemetry-card">
        <div class="telemetry-label">CAMERA FOV</div>
        <div class="telemetry-value">{camera_fov}°</div>
    </div>

    <div class="telemetry-card">
        <div class="telemetry-label">HORIZONTAL ERROR</div>
        <div class="telemetry-value">0 px</div>
    </div>

    <div class="telemetry-card">
        <div class="telemetry-label">VERTICAL ERROR</div>
        <div class="telemetry-value">0 px</div>
    </div>

    <div class="telemetry-card">
        <div class="telemetry-label">TRACKING STATUS</div>
        <div class="telemetry-value" style="color:#35d07f;">
            {"ACTIVE" if start else "READY"}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------- Bottom Status ----------
st.divider()

st.markdown(
    '<div class="panel-title">ALIGNMENT MONITOR</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("TARGET", "DETECTED")

with c2:
    st.metric("PREDICTION", "READY")

with c3:
    st.metric("ALIGNMENT", "ACQUIRING")

with c4:
    st.metric("SYSTEM", "READY")


st.markdown(
    '<div class="footer">AEROLINK • VIRTUAL FSOC LABORATORY • COARSE ALIGNMENT</div>',
    unsafe_allow_html=True
)