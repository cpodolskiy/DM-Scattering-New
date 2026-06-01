import numpy as np
import matplotlib
matplotlib.use("Agg")   # avoids display / wayland issues
import matplotlib.pyplot as plt
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

img_path = "/home/locsst/Documents/camera/fullrec_clean.png"

with Image.open(img_path) as img:
    img = img.convert("L")   # keep as 2D intensity map
    img_small = img.resize((2000, 2000), resample=Image.BILINEAR)
    rect_img = np.array(img_small).astype(np.float32)

# normalize to 0–1
if rect_img.max() > rect_img.min():
    rect_img = (rect_img - rect_img.min()) / (rect_img.max() - rect_img.min())

if rect_img.shape[0] > rect_img.shape[1]:
    rect_img = rect_img.T

# flip horizontally so the right edge becomes the fold center
rect_img = np.fliplr(rect_img)

print("Rect img shape is:", rect_img.shape)

azimuth_steps, motor_steps = rect_img.shape

theta = np.linspace(0, 2 * np.pi, azimuth_steps)
r = np.linspace(0, 1, motor_steps)
theta_grid, r_grid = np.meshgrid(theta, r, indexing='ij')

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))

c = ax.pcolormesh(theta_grid, r_grid, rect_img, shading="auto", cmap="inferno")

ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_yticklabels([])

# optional colorbar for presentation
cbar = plt.colorbar(c, ax=ax, pad=0.08)
cbar.set_label("Relative Intensity")

plt.tight_layout()

output_path = "/home/locsst/Documents/camera/polarfull.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0)
print(f"Saved polar plot to: {output_path}")