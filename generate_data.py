import os
import random
import pygame

pygame.init()

# Same window size, colors, and circle as main.py
WIDTH = 640
HEIGHT = 480
WHITE = (255, 255, 255)
BLUE = (50, 120, 220)
circle_radius = 60

# Folders for the images and YOLO labels
folder = os.path.join("dataset", "images")
labels_folder = os.path.join("dataset", "labels")
os.makedirs(folder, exist_ok=True)
os.makedirs(labels_folder, exist_ok=True)

# Draw on a surface (no game window needed)
surface = pygame.Surface((WIDTH, HEIGHT))

how_many = 50

for i in range(how_many):
    # Keep the whole circle inside the image
    x = random.randint(circle_radius, WIDTH - circle_radius)
    y = random.randint(circle_radius, HEIGHT - circle_radius)

    surface.fill(WHITE)
    pygame.draw.circle(surface, BLUE, (x, y), circle_radius)

    filename = os.path.join(folder, f"target_{i:03d}.png")
    pygame.image.save(surface, filename)

    # YOLO label: class x_center y_center width height (all between 0 and 1)
    # Class 0 is our blue target. The box is the square around the circle.
    box_width = (circle_radius * 2) / WIDTH
    box_height = (circle_radius * 2) / HEIGHT
    x_center = x / WIDTH
    y_center = y / HEIGHT
    label_filename = os.path.join(labels_folder, f"target_{i:03d}.txt")
    with open(label_filename, "w") as label_file:
        label_file.write(f"0 {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")

    print(f"Saved {filename}")

pygame.quit()
print("Done. Saved", how_many, "images in", folder)
print("Done. Saved", how_many, "labels in", labels_folder)
