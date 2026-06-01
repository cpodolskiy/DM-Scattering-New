import h5py
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

input_path = Path("/home/locsst/Documents/camera/array/full.h5")
output_path = Path("/home/locsst/Documents/camera/intensity_vs_camera_angle.png")

with h5py.File(input_path, "r") as f:
    images = f["images"]
    angles = f["angles"][:]

    motors = np.unique(angles[:, 0])
    azimuths = np.unique(angles[:, 1])

    motors.sort()
    azimuths.sort()

    fig, ax = plt.subplots(figsize=(9, 5))

    for az in azimuths:
        y = []
        for motor in motors:
            idx = np.where((angles[:, 1] == az) & (angles[:, 0] == motor))[0]
            if len(idx) > 0:
                img = images[idx[0]].astype(np.float32)
                y.append(img.mean())
            else:
                y.append(np.nan)

        ax.plot(motors, y, marker="o", label=f"Azimuth {az:.0f}°")

ax.set_xlabel("Camera / motor angle")
ax.set_ylabel("Mean raw intensity")
ax.set_title("Measured Intensity vs Camera Angle")
ax.legend(title="DM azimuth")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches="tight")
print(f"Saved line plot to: {output_path}")