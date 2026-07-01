import numpy as np
import h5py
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from pathlib import Path

h5_file = Path("run.h5")
pixel_deg_motor = 0.921202100973
pixel_deg_azimuth = 0.688377359072
motor_center = 90

with h5py.File(h5_file, "r") as f:
    images = f["images"]
    angles = f["angles"]

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_title("Polar Wedge Map - One Patch per Image")
    ax.set_aspect("equal")
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.axis("off")

    patches = []
    colors = []

    for idx in range(len(images)):
        print(f"Placing image {idx}/{len(images)}")
        img = images[idx]

        #rotate image 90 degrees clockwise
        img = np.rot90(img, k=-1)

        motor_angle, azimuth_angle = angles[idx]

        #flip motor for second half
        if azimuth_angle < 90:
            motor = motor_angle
        else:
            motor = 180 - motor_angle

        motor_shifted = motor - motor_center

        mot_start = motor_shifted
        mot_end = mot_start + pixel_deg_azimuth
        az_start = azimuth_angle
        az_end = az_start + pixel_deg_motor

        #single intensity value per image, e.g. mean intensity
        img_mean = float(img.mean())

        #define the 4 corners of the patch
        corners_theta = [az_start, az_end, az_end, az_start]
        corners_r = [mot_start, mot_start, mot_end, mot_end]

        xs = [r * np.cos(np.deg2rad(t)) for r, t in zip(corners_r, corners_theta)]
        ys = [r * np.sin(np.deg2rad(t)) for r, t in zip(corners_r, corners_theta)]

        poly = Polygon(list(zip(xs, ys)), closed=True, edgecolor='none')
        patches.append(poly)
        colors.append(img_mean)

    colors = np.array(colors)
    colors_norm = (colors - colors.min()) / (colors.max() - colors.min() + 1e-9)  # avoid div bby 0

    collection = PatchCollection(patches, array=colors_norm, cmap='gray', edgecolor='none')
    collection.set_linewidth(0)
    ax.add_collection(collection)

    plt.tight_layout()
    plt.show()
