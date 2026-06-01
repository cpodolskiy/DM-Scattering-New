import h5py
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cv2
from pathlib import Path

# ============================================================
# USER PATHS
# ============================================================
input_path = Path("/home/locsst/Documents/camera/array/full.h5")

output_global = Path("/home/locsst/Documents/camera/direct_recgrid_global.png")
output_per_image = Path("/home/locsst/Documents/camera/direct_recgrid_per_image.png")


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def normalize_image(img, global_min=None, global_max=None, mode="global"):
    """
    mode = "global"    -> all images use the same intensity scale.
                          Best for comparing brightness between angles.
    mode = "per_image" -> each image is stretched separately.
                          Best for seeing texture inside each image.
    """
    img = img.astype(np.float32)

    if mode == "global":
        if global_max is not None and global_min is not None and global_max > global_min:
            img = (img - global_min) / (global_max - global_min)
        else:
            img = img * 0

    elif mode == "per_image":
        img_min = img.min()
        img_max = img.max()
        if img_max > img_min:
            img = (img - img_min) / (img_max - img_min)
        else:
            img = img * 0

    img_u8 = np.clip(img * 255, 0, 255).astype(np.uint8)

    # Match the same orientation used in your other scripts
    img_u8 = cv2.rotate(img_u8, cv2.ROTATE_90_CLOCKWISE)

    return img_u8


def make_direct_montage(mode, output_path):
    with h5py.File(input_path, "r") as f:
        images = f["images"]
        angles = f["angles"][:]

        # Motor angle is column coordinate
        motors = np.unique(angles[:, 0])
        motors.sort()

        # Azimuth angle is row coordinate
        azimuths = np.unique(angles[:, 1])
        azimuths.sort()

        n_rows = len(azimuths)
        n_cols = len(motors)

        print("Azimuth values:", azimuths)
        print("Motor values:", motors)
        print(f"Direct montage size: {n_rows} rows × {n_cols} columns = {n_rows * n_cols} positions")

        # Create lookup table using rounded angles to avoid floating-point mismatch
        angle_to_index = {}
        for k, (motor, az) in enumerate(angles):
            key = (round(float(az), 3), round(float(motor), 3))
            angle_to_index[key] = k

        # Global normalization values
        # Use true min/max for direct raw comparison.
        global_min = float(images[:].min())
        global_max = float(images[:].max())

        print("Global min:", global_min)
        print("Global max:", global_max)

        # Display highest azimuth at the top, lowest at bottom
        azimuths_display = azimuths[::-1]

        fig, axes = plt.subplots(
            n_rows,
            n_cols,
            figsize=(2.1 * n_cols, 2.0 * n_rows),
            squeeze=False
        )

        for row_idx, az in enumerate(azimuths_display):
            for col_idx, motor in enumerate(motors):
                ax = axes[row_idx, col_idx]

                key = (round(float(az), 3), round(float(motor), 3))

                if key in angle_to_index:
                    img_index = angle_to_index[key]
                    img = images[img_index]

                    img_display = normalize_image(
                        img,
                        global_min=global_min,
                        global_max=global_max,
                        mode=mode
                    )

                    ax.imshow(img_display, cmap="gray", vmin=0, vmax=255)
                else:
                    # Missing image position
                    ax.set_facecolor("lightgray")
                    ax.text(
                        0.5,
                        0.5,
                        "Missing",
                        ha="center",
                        va="center",
                        fontsize=9,
                        transform=ax.transAxes
                    )

                ax.set_xticks([])
                ax.set_yticks([])

                # Column titles: motor/camera angle
                if row_idx == 0:
                    ax.set_title(f"{motor:.0f}°", fontsize=10)

                # Row labels: DM azimuth angle
                if col_idx == 0:
                    ax.set_ylabel(f"{az:.0f}°", fontsize=11, rotation=0, labelpad=28, va="center")

                # Add a thin border around each cell
                for spine in ax.spines.values():
                    spine.set_visible(True)
                    spine.set_linewidth(0.8)
                    spine.set_color("white")

        fig.suptitle(
            f"Direct Rectangular Scan Map: All Captured Images ({mode} normalization)",
            fontsize=16,
            y=0.98
        )

        fig.text(0.5, 0.04, "Camera / motor angle", ha="center", fontsize=13)
        fig.text(0.02, 0.5, "DM azimuth angle", va="center", rotation="vertical", fontsize=13)

        plt.tight_layout(rect=[0.04, 0.06, 1.0, 0.94])
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

        print(f"Saved: {output_path}")


# ============================================================
# MAKE BOTH VERSIONS
# ============================================================

# Best for comparing actual brightness between angles
make_direct_montage(mode="global", output_path=output_global)

# Best for seeing image texture in each cell
make_direct_montage(mode="per_image", output_path=output_per_image)