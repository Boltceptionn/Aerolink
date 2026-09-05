import os
import random
import shutil

# Use the same shuffle every time you run this script
random.seed(42)

# Where the images and labels are now
images_folder = os.path.join("dataset", "images")
labels_folder = os.path.join("dataset", "labels")

# Where train and val files should go
train_images = os.path.join(images_folder, "train")
val_images = os.path.join(images_folder, "val")
train_labels = os.path.join(labels_folder, "train")
val_labels = os.path.join(labels_folder, "val")

# Create the new folders if they do not exist yet
os.makedirs(train_images, exist_ok=True)
os.makedirs(val_images, exist_ok=True)
os.makedirs(train_labels, exist_ok=True)
os.makedirs(val_labels, exist_ok=True)

# Find image files in dataset/images (skip the train and val folders)
pairs = []
for name in os.listdir(images_folder):
    image_path = os.path.join(images_folder, name)
    if not os.path.isfile(image_path):
        continue
    if not name.endswith(".png"):
        continue

    # Matching label uses the same name, but with .txt
    label_name = name.replace(".png", ".txt")
    label_path = os.path.join(labels_folder, label_name)
    if os.path.isfile(label_path):
        pairs.append((name, label_name))

# Mix the pairs, then take 40 for train and 10 for val
random.shuffle(pairs)
train_pairs = pairs[:40]
val_pairs = pairs[40:50]


def move_pairs(pair_list, image_dest, label_dest):
    """Move each image and its matching label into the destination folders."""
    moved = 0
    for image_name, label_name in pair_list:
        shutil.move(
            os.path.join(images_folder, image_name),
            os.path.join(image_dest, image_name),
        )
        shutil.move(
            os.path.join(labels_folder, label_name),
            os.path.join(label_dest, label_name),
        )
        moved = moved + 1
    return moved


# Move the files (this does not delete them; they just change folders)
train_count = move_pairs(train_pairs, train_images, train_labels)
val_count = move_pairs(val_pairs, val_images, val_labels)

print("Train image+label pairs:", train_count)
print("Val image+label pairs:", val_count)
print("Train folders:", train_images, "and", train_labels)
print("Val folders:", val_images, "and", val_labels)
