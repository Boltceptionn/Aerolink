from ultralytics import YOLO

# Our trained AEROLINK model (not the default yolov8n.pt)
model = YOLO("runs/detect/train-2/weights/best.pt")

# Look at the screenshot saved from the Pygame window
results = model("frame.png", save=False)
result = results[0]

# Print each object YOLO found
if len(result.boxes) == 0:
    print("No objects detected.")
else:
    print("YOLO detected:")
    for box in result.boxes:
        class_id = int(box.cls[0])
        name = result.names[class_id]
        confidence = float(box.conf[0])
        print(f"- {name} (confidence: {confidence:.2f})")
        if name == "fsoc_target":
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            print(f"Target center: ({center_x:.1f}, {center_y:.1f})")
            image_height, image_width = result.orig_shape
            camera_center_x = image_width / 2
            camera_center_y = image_height / 2
            error_x = center_x - camera_center_x
            error_y = center_y - camera_center_y
            print(f"Alignment error: ({error_x:.1f}, {error_y:.1f})")
