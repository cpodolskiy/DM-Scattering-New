import h5py
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

input_path = Path("/home/locsst/Documents/camera/array/full.h5")
output_path = Path("/home/locsst/Documents/camera/bc_mean_intensity_heatmap_staticbeam.png")

def process_with_master_background(input_path, output_path):
    with h5py.File(input_path, "r") as f:
        angles = f["angles"][:]
        images_dataset = f["images"]

        motors = np.sort(np.unique(angles[:, 0]))
        azimuths = np.sort(np.unique(angles[:, 1]))

        motor_to_idx = {val: idx for idx, val in enumerate(motors)}
        azimuth_to_idx = {val: idx for idx, val in enumerate(azimuths)}

        intensity = np.full((len(azimuths), len(motors)), np.nan)

        # 1. Compute Master Background (Pixel-by-pixel 5th percentile across time)
        print("Computing master background image...")
        # Stack or stream data to find the lowest intensity baseline for each pixel
        # Adjust chunk size if your dataset is extremely large
        all_images = images_dataset[:].astype(np.float32)
        master_background = np.percentile(all_images, 5, axis=0)

        # 2. Process images using the Master Background
        print("Processing images and subtracting stray light...")
        for idx, (motor, az) in enumerate(angles):
            if motor in motor_to_idx and az in azimuth_to_idx:
                i = azimuth_to_idx[az]
                j = motor_to_idx[motor]

                # Subtract master background pixel-by-pixel
                img_corrected = (
                    images_dataset[idx].astype(np.float32)
                    - master_background
                )

                # Store the mean of the corrected scattering signal
                intensity[i, j] = np.mean(img_corrected)

    # 3. Plotting with corrected label tweaks
    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(
        intensity, cmap="inferno", origin="lower", aspect="auto"
    )

    ax.set_xticks(np.arange(len(motors)))
    ax.set_xticklabels([f"{m:.0f}°" for m in motors], rotation=45)
    ax.set_yticks(np.arange(len(azimuths)))
    ax.set_yticklabels([f"{az:.0f}°" for az in azimuths])

    ax.set_xlabel("Camera / motor angle")
    ax.set_ylabel("DM azimuth angle")

    # Updated Label Tweaks
    ax.set_title(
        "Master-Background Corrected Mean Scattering Intensity"
    )
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Corrected Intensity (Signal - Master Background)")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved master-corrected heatmap to: {output_path}")
