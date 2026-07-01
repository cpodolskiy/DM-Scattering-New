import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2
from pathlib import Path

h5_path = Path("reclongrun.h5")

canvas_width_deg = 90 # canvas width in degrees
canvas_height_deg = 180 # canvas height in degrees
tile_width_deg = 0.921202100973 # actual angular degree size width
tile_height_deg = 0.688377359072 # actual angular degree size height
motor_step_deg = 0.6 # motor step size
azimuth_step_deg = 0.9 # azimuth step size

with h5py.File(h5_path, "r") as f:
    ds = f["rectangular_images"]
    az_steps, motor_steps, H, W = ds.shape
    print("Dataset shape:", ds.shape)

    fig, ax = plt.subplots(figsize=(4, 8))
    ax.set_xlim(0, canvas_width_deg)
    ax.set_ylim(0, canvas_height_deg)
    ax.set_aspect('equal')

    for az_idx in range(az_steps):
        print(f"Reading {az_idx} azimuth")
        for motor_idx in range(motor_steps):
            azimuth_deg = az_idx * azimuth_step_deg
            motor_deg = motor_idx * motor_step_deg
            rect = patches.Rectangle((motor_deg, azimuth_deg), tile_height_deg, tile_width_deg,
                                      linewidth=0.5, edgecolor=None, facecolor = None)
            ax.add_patch(rect)

    for az_idx in range(az_steps):
        print(f"Placing {az_idx} azimuth")
        for motor_idx in range(motor_steps):
            img = ds[az_idx, motor_idx]

            #normalize image for display
            img_f32 = img.astype(np.float32)
            img_f32 -= img_f32.min()
            if img_f32.max() > 0:
                img_f32 /= img_f32.max()
            img_u8 = (img_f32 * 255).astype(np.uint8)
            img_u8 = cv2.rotate(img_u8, cv2.ROTATE_90_CLOCKWISE)

            #resize to match image's angular size
            display_H = int(tile_height_deg * 400)
            display_W = int(tile_width_deg * 400)
            img_resized = cv2.resize(img_u8, (display_W, display_H))

            #compute degree placement
            motor_deg = motor_idx * motor_step_deg
            azimuth_deg = az_idx * azimuth_step_deg
            extent = [motor_deg, motor_deg + tile_height_deg,azimuth_deg, azimuth_deg + tile_width_deg]

            #put image over rectangle
            ax.imshow(img_resized, cmap='gray', extent=extent, origin='lower', aspect=1, zorder=1)
            
    ax.set_xlabel("Motor Angle (deg)")
    ax.set_ylabel("Azimuth Angle (deg)")
    ax.set_title("Actual Images on Grid")
    ax.grid(True)
    plt.tight_layout()

    # #hide all axis elements for saving image
    # ax.axis('off')

    output_path = Path("reclongrungrid.png")
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    print(f"Saved image-only plot to: {output_path}")

    plt.show()
