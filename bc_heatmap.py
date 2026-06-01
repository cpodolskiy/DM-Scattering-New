import h5py
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

input_path = Path("/home/locsst/Documents/camera/array/full.h5")
output_path = Path("/home/locsst/Documents/camera/bc_mean_intensity_heatmap.png")

with h5py.File(input_path, "r") as f:
    images = f["images"]
    angles = f["angles"][:]

    motors = np.unique(angles[:, 0])
    azimuths = np.unique(angles[:, 1])

    motors.sort()
    azimuths.sort()

    intensity = np.full((len(azimuths), len(motors)), np.nan)

    for i, az in enumerate(azimuths):
        for j, motor in enumerate(motors):
            idx = np.where((angles[:, 1] == az) & (angles[:, 0] == motor))[0]
            if len(idx) > 0:
                img = images[idx[0]].astype(np.float32)
                background = np.percentile(img, 5)
                intensity[i, j] = img.mean() - background

# Optional: subtract approximate background
# background = np.nanmedian(intensity)
# intensity = intensity - background

fig, ax = plt.subplots(figsize=(10, 5))

im = ax.imshow(
    intensity,
    cmap="inferno",
    origin="lower",
    aspect="auto"
)

ax.set_xticks(np.arange(len(motors)))
ax.set_xticklabels([f"{m:.0f}°" for m in motors], rotation=45)

ax.set_yticks(np.arange(len(azimuths)))
ax.set_yticklabels([f"{az:.0f}°" for az in azimuths])

ax.set_xlabel("Camera / motor angle")
ax.set_ylabel("DM azimuth angle")
ax.set_title("Mean Scattering Intensity by Camera Angle and DM Azimuth")

cbar = plt.colorbar(im, ax=ax)
cbar.set_label("Background Corrected Mean intensity")

plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches="tight")
print(f"Saved heatmap to: {output_path}")