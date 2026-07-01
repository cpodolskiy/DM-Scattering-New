import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

#disable size limit
Image.MAX_IMAGE_PIXELS = None

#load
img_path = "reclongrungrid.png"
with Image.open(img_path) as img:
    #downsample by resizing
    img_small = img.resize((2000, 2000), resample=Image.BILINEAR)
    rect_img = np.array(img_small)

if rect_img.shape[0] > rect_img.shape[1]:
    rect_img = rect_img.T
print("Rect_img shape is: ", rect_img.shape)
azimuth_steps, motor_steps, _ = rect_img.shape
# azimuth_steps, motor_steps - rect_img.shape
rect_img = np.flip(rect_img, axis=1)
#polar mesh
theta = np.linspace(0, 2 * np.pi, azimuth_steps)
r = np.linspace(0, 1, motor_steps)
theta_grid, r_grid = np.meshgrid(theta, r, indexing='ij')

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))
c = ax.pcolormesh(theta_grid, r_grid, rect_img, shading='auto', cmap='gray')

ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_yticklabels([])
# plt.colorbar(c, ax=ax, label="Intensity")
plt.tight_layout()
# ax.axis('off')
output_path = "/home/locsst/Documents/camera/polarattempt.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0)

plt.show()
