from ultralytics import YOLO

# Small pretrained model (YOLO downloads this file the first time you run it)
model = YOLO("yolov8n.pt")

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
