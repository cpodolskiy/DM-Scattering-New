import numpy as np
import h5py
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from pathlib import Path

h5_file = Path("run.h5")
pixel_deg_motor = 0.921202100973  # actual pixel width
pixel_deg_azimuth = 0.688377359072
motor_center = 90
downsample = 45  # factor to reduce resolution for plotting
motor_step_taken = 0.6
azimuth_step_taken = 0.9

with h5py.File(h5_file, "r") as f:
    images = f["images"]
    angles = f["angles"]

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_title("Polar Wedge Map")
    ax.set_aspect("equal")
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.axis("off")

    patches = []
    colors = []

    for idx in range(len(images)):
        print(f"Placing image {idx}/{len(images)}")
        img = images[idx]
        motor_angle, azimuth_angle = angles[idx]
        img = np.rot90(img, k=-1) 
        #flip motor for second half
        if azimuth_angle < 90:
            motor = motor_angle
        else:
            motor = 180 - motor_angle

        #position based on motor_step_taken, size based on pixel_deg_motor
        motor_shifted = motor - motor_center
        motor_position_idx = round(motor_shifted / motor_step_taken)
        mot_start = motor_position_idx * motor_step_taken
        mot_end = mot_start + pixel_deg_azimuth  # size remains the actual motor pixel width

        az_start = azimuth_angle
        az_end = az_start + pixel_deg_motor

        #downsample for display
        img = img[::downsample, ::downsample].astype(np.float32)
        img -= img.min()
        if img.max() > 0:
            img /= img.max()

        h, w = img.shape
        theta_vals = np.linspace(az_start, az_end, h)
        r_vals = np.linspace(mot_start, mot_end, w)

        thetas, rs = np.meshgrid(theta_vals, r_vals, indexing='ij')

        xs = rs * np.cos(np.deg2rad(thetas))
        ys = rs * np.sin(np.deg2rad(thetas))

        #one patch per downsampled pixel
        for i in range(h - 1):
            for j in range(w - 1):
                poly = Polygon([(xs[i, j], ys[i, j]), (xs[i+1, j], ys[i+1, j]),
                                (xs[i+1, j+1], ys[i+1, j+1]), (xs[i, j+1], ys[i, j+1])], closed=True, edgecolor='None', linewidth=0) # type: ignore
                patches.append(poly)
                colors.append(img[i, j])

        #orientation outlines
        top_poly = [(xs[0, 0], ys[0, 0]), (xs[0, -1], ys[0, -1])]
        right_poly = [(xs[0, -1], ys[0, -1]), (xs[-1, -1], ys[-1, -1])]
        ax.plot(*zip(*top_poly), color='None', lw=0)
        ax.plot(*zip(*right_poly), color='None', lw=0)

    collection = PatchCollection(patches, array=np.array(colors), cmap='gray', edgecolor='none', antialiaseds=False)
    collection.set_linewidth(0)
    ax.add_collection(collection)

    plt.tight_layout()
    plt.show()
