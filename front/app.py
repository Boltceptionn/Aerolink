import streamlit as st

st.set_page_config(
    page_title="AEROLINK",
    page_icon="✈",
    layout="wide"
)

st.title("AEROLINK")
st.caption("Virtual FSOC Alignment & Tracking System")

st.divider()

# Left panel: controls
left, center, right = st.columns([1, 2, 1])

with left:
    st.subheader("Mission Controls")

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

    start = st.button(
        "Start Simulation",
        use_container_width=True
    )

with center:
    st.subheader("Virtual Camera View")

    st.image(
        "frame.png",
        caption="Virtual Camera Feed",
        use_container_width=True
    )
with right:
    st.subheader("Telemetry")

    st.metric("Tracking Mode", tracking_mode)
    st.metric("Target Speed", target_speed)
    st.metric("Camera FOV", f"{camera_fov}°")

    if start:
        st.success("Simulation started")
    else:
        st.info("System ready")

st.divider()

st.subheader("Alignment Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Horizontal Error", "0 px")

with col2:
    st.metric("Vertical Error", "0 px")

with col3:
    st.metric("System Status", "READY")