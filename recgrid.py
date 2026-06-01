import h5py
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2
from pathlib import Path

h5_path = Path("/home/locsst/Documents/camera/array/fullrec.h5")

clean_output_path = Path("/home/locsst/Documents/camera/fullrec_clean.png")
labeled_output_path = Path("/home/locsst/Documents/camera/fullrec_labeled.png")

# Coarse test settings
motor_step_deg = 10
azimuth_step_deg = 90

tile_width_deg = azimuth_step_deg
tile_height_deg = motor_step_deg


def draw_recgrid(make_labeled=False):
    with h5py.File(h5_path, "r") as f:
        ds = f["rectangular_images"]
        motor_matrix = f["motor_angles_per_row"][:]

        az_steps, motor_steps, H, W = ds.shape
        print("Dataset shape:", ds.shape)
        print("Motor angle matrix:")
        print(motor_matrix)

        # canvas_width_deg = motor_steps * motor_step_deg
        # canvas_height_deg = az_steps * azimuth_step_deg
        canvas_width_deg = 90 # canvas width in degrees
        canvas_height_deg = 180 # canvas height in degrees
        

        # Global normalization across all images
        global_min = float(ds[:].min())
        global_max = float(ds[:].max())
        print("Global min:", global_min)
        print("Global max:", global_max)

        if make_labeled:
            fig, ax = plt.subplots(figsize=(7, 10))
        else:
            fig, ax = plt.subplots(figsize=(7, 10))

        ax.set_xlim(0, canvas_width_deg)
        ax.set_ylim(0, canvas_height_deg)
        ax.set_aspect("equal")

        for az_idx in range(az_steps):
            print(f"Placing azimuth row {az_idx}")
            for motor_idx in range(motor_steps):
                img = ds[az_idx, motor_idx].astype(np.float32)

                if motor_matrix[az_idx, motor_idx] < 0:
                    continue

                if global_max > global_min:
                    img = (img - global_min) / (global_max - global_min)
                else:
                    img = img * 0

                img_u8 = np.clip(img * 255, 0, 255).astype(np.uint8)
                img_u8 = cv2.rotate(img_u8, cv2.ROTATE_90_CLOCKWISE)

                display_H = max(1, int(tile_width_deg * 20))
                display_W = max(1, int(tile_height_deg * 20))
                img_resized = cv2.resize(img_u8, (display_W, display_H))

                x0 = motor_idx * motor_step_deg
                y0 = az_idx * azimuth_step_deg

                extent = [
                    x0,
                    x0 + tile_height_deg,
                    y0,
                    y0 + tile_width_deg
                ]

                ax.imshow(
                    img_resized,
                    cmap="gray",
                    extent=extent,
                    origin="lower",
                    aspect="auto",
                    vmin=0,
                    vmax=255,
                    zorder=1
                )

                if make_labeled:
                    rect = patches.Rectangle(
                        (x0, y0),
                        tile_height_deg,
                        tile_width_deg,
                        linewidth=0.8,
                        edgecolor="white",
                        facecolor="none",
                        alpha=0.5,
                        zorder=2
                    )
                    ax.add_patch(rect)

                    # ax.text(
                    #     x0 + tile_height_deg / 2,
                    #     y0 + tile_width_deg / 2,
                    #     f"M={motor_matrix[az_idx, motor_idx]:.0f}°",
                    #     color="white",
                    #     fontsize=8,
                    #     ha="center",
                    #     va="center",
                    #     bbox=dict(facecolor="black", alpha=0.35, edgecolor="none")
                    # )

        if make_labeled:
            ax.set_xlabel("Folded motor / camera-angle coordinate (degrees)", fontsize=12)
            ax.set_ylabel("Azimuth / DM step angle (degrees)", fontsize=12)
            ax.set_title("Rectangular Stitched Scattering Intensity Map", fontsize=14)

            ax.set_xticks(np.arange(0, canvas_width_deg + 1, motor_step_deg))
            ax.set_yticks(np.arange(0, canvas_height_deg + 1, azimuth_step_deg))
            ax.grid(True, alpha=0.25)

            ax.text(
                0.02,
                0.98,
                "10° motor step, 90° azimuth step",
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=10,
                bbox=dict(facecolor="white", alpha=0.75, edgecolor="none")
            )

            plt.tight_layout()
            plt.savefig(labeled_output_path, dpi=300, bbox_inches="tight")
            print(f"Saved labeled rectangular plot to: {labeled_output_path}")

        else:
            ax.axis("off")
            plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
            plt.savefig(clean_output_path, dpi=300, bbox_inches="tight", pad_inches=0)
            print(f"Saved clean rectangular plot to: {clean_output_path}")

        plt.close(fig)


# Save clean version for polar.py
draw_recgrid(make_labeled=False)

# Save labeled version for explanation/presentation
draw_recgrid(make_labeled=True)