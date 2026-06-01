import numpy as np
import h5py
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from pathlib import Path

h5_file = Path("/home/locsst/Documents/camera/array/monoattempt.h5")
pixel_deg_motor = 0.921202100973
pixel_deg_azimuth = 0.688377359072
motor_center = 90

with h5py.File(h5_file, "r") as f:
    images = f["images"]
    angles = f["angles"]

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_title("Polar Map")
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
    colors_norm = (colors - colors.min()) / (colors.max() - colors.min() + 1e-9)  # avoid div0

    collection = PatchCollection(patches, array=colors_norm, cmap='gray', edgecolor='none')
    collection.set_linewidth(0)
    ax.add_collection(collection)

    plt.tight_layout()
    plt.show()


# import numpy as np
# import h5py
# import matplotlib.pyplot as plt
# from matplotlib.patches import Polygon
# from matplotlib.collections import PatchCollection
# from matplotlib.lines import Line2D
# import matplotlib.patches as mpatches
# from pathlib import Path

# h5_file = Path("/home/locsst/Documents/camera/array/monotestlong.h5")
# pixel_deg_motor = 0.757185810663
# pixel_deg_azimuth = 0.567892973939
# motor_center = 90
# azimuth_split = 90  # fold line for azimuth

# azimuth_rotation = -90

# with h5py.File(h5_file, "r") as f:
#     images = f["images"]
#     angles = f["angles"]

#     fig, ax = plt.subplots(figsize=(12, 12))
#     ax.set_title("Polar Map - Averaged")
#     ax.set_aspect("equal")

#     ax.set_xlim(-100, 100)
#     ax.set_ylim(-100, 100)
#     # ax.grid(True, linestyle=':', color='gray', alpha=0.5)

#     patches = []
#     colors = []

#     n_images = len(images)
#     for idx in range(n_images):
#         print(f"Placing image {idx+1}/{n_images}")
#         img = images[idx]
#         motor_angle, azimuth_angle = angles[idx]

#         #rotate azimuth angles so 0° is at top
#         azimuth_angle_rotated = (azimuth_angle + azimuth_rotation) % 360
#         #bowtie format for images    
#         if azimuth_angle_rotated < azimuth_split:
#             motor = motor_angle
#         else:
#             motor = 180 - motor_angle

#         motor_shifted = motor - motor_center
#         motor_step_actual = 0.75
#         motor_position_idx = round((motor_angle - motor_center) / motor_step_actual)
#         mot_start = motor_position_idx * motor_step_actual
#         mot_end = mot_start + pixel_deg_motor
#         az_start = azimuth_angle_rotated
#         az_end = az_start + pixel_deg_azimuth
#         img_norm = (img - img.min()) / (img.max() - img.min() + 1e-9)
#         img_mean = float(img_norm.mean())

#         corners_theta = [az_start, az_end, az_end, az_start]
#         corners_r = [mot_start, mot_start, mot_end, mot_end]

#         xs = [r * np.cos(np.deg2rad(t)) for r, t in zip(corners_r, corners_theta)]
#         ys = [r * np.sin(np.deg2rad(t)) for r, t in zip(corners_r, corners_theta)]

#         poly = Polygon(list(zip(xs, ys)), closed=True, edgecolor='none')
#         patches.append(poly)
#         colors.append(img_mean)

#     colors = np.array(colors)
#     colors_norm = (colors - colors.min()) / (colors.max() - colors.min() + 1e-9)

#     collection = PatchCollection(patches, array=colors_norm, cmap='gray', edgecolor='none')
#     collection.set_linewidth(0)
#     ax.add_collection(collection)
#     ax.axis("off")
#     plt.tight_layout()
#     output_path = Path("/home/locsst/Documents/camera/images/avgpolartestlong")
#     plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
#     plt.show()

#     # motor_angles = [0, 45, 90, 135, 180]
#     # azimuth_angles = [0, 45, 90, 135, 180]

#     # def draw_motor_arc(radius, az_start_deg, az_end_deg, **kwargs):
#     #     pass
#         # arc = mpatches.Arc((0, 0), 2*abs(radius), 2*abs(radius), angle=0,
#         #                    theta1=az_start_deg, theta2=az_end_deg, **kwargs)
#         # ax.add_patch(arc)
#         # mid_az = (az_start_deg + az_end_deg) / 2

#         #flip motor label radius sign as before
#         # if az_start_deg >= azimuth_split:
#         #     label_radius = -radius
#         # else:
#         #     label_radius = radius

#         # label_x = label_radius * np.cos(np.deg2rad(mid_az))
#         # label_y = label_radius * np.sin(np.deg2rad(mid_az))

#         #flip label_y to flip top/bottom motor labels
#         # label_y = -label_y

#         # ax.text(label_x, label_y, f'Motor {int(radius + motor_center)}°', color='green', fontsize=9, ha='center', va='center')

#     # for m in motor_angles:
#     #     radius_left = m - motor_center
#     #     radius_right = (180 - m) - motor_center

#     #     draw_motor_arc(radius_left, 0, azimuth_split, color='lightgreen', linestyle='--', linewidth=0.8)
#     #     draw_motor_arc(radius_right, azimuth_split, 180, color='lightgreen', linestyle='--', linewidth=0.8)

#     # min_radius = min([m - motor_center for m in motor_angles])
#     # max_radius = max([m - motor_center for m in motor_angles])

#     # for az in azimuth_angles:
#     #     #shift labels so 0 is at the top, counterclockwise
#     #     az_label_angle = (az - 270) % 360

#     #     x0 = min_radius * np.cos(np.deg2rad(az_label_angle))
#     #     y0 = min_radius * np.sin(np.deg2rad(az_label_angle))
#     #     x1 = max_radius * np.cos(np.deg2rad(az_label_angle))
#     #     y1 = max_radius * np.sin(np.deg2rad(az_label_angle))
#     #     ax.plot([x0, x1], [y0, y1], color='lightblue', linestyle='--', linewidth=0.8)

#     #     label_x = max_radius * np.cos(np.deg2rad(az_label_angle))
#     #     label_y = max_radius * np.sin(np.deg2rad(az_label_angle))
#     #     ax.text(label_x, label_y, f'Az {az}°', color='blue', fontsize=9, ha='center', va='center')


#     # legend_elements = [Line2D([0], [0], color='lightgreen', lw=2, linestyle='--', label='Motor arcs'),
#     #                    Line2D([0], [0], color='lightblue', lw=2, linestyle='--', label='Azimuth spokes'),]
#     # ax.legend(handles=legend_elements, loc='upper right')

#     # plt.tight_layout()
#     # plt.show()