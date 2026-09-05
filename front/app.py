import streamlit as st

st.title("AEROLINK")
st.subheader("Virtual FSOC Alignment Simulator")

st.write("Simulation Controls")

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

start = st.button("Start Simulation")

st.write("Target Speed:", target_speed)
st.write("Camera FOV:", camera_fov)

if start:
    st.success("Simulation started!")

st.subheader("Virtual Camera View")
st.image(
    "frame.png", 
    caption="Current virtual camera frame"
    )

?