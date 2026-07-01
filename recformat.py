import numpy as np
import h5py
from pathlib import Path

input_path = Path("monolongrun.h5")
output_path = Path("reclongrun.h5")

with h5py.File(input_path, "r") as f_in:
    angles = f_in["angles"][:]
    num_images = f_in["images"].shape[0]
    H, W = f_in["images"].shape[1:]

    azimuths = np.unique(angles[:, 1])
    motor_angles = np.unique(angles[:, 0])
    azimuths.sort()
    motor_angles.sort()

    mid_az = np.median(azimuths)
    azimuths_top = azimuths[azimuths <= mid_az]
    azimuths_bot = azimuths[azimuths > mid_az]
    motor_top = motor_angles[motor_angles <= 90]
    motor_bot = motor_angles[motor_angles >= 90][::-1]

    max_cols = max(len(motor_top), len(motor_bot))
    num_rows = len(azimuths)

    with h5py.File(output_path, "w") as f_out:
        dset_imgs = f_out.create_dataset("rectangular_images", shape=(num_rows, max_cols, H, W), dtype=np.uint16, compression="gzip", chunks=(1, 1, H, W),)
        dset_motor = f_out.create_dataset("motor_angles_per_row", shape=(num_rows, max_cols), dtype=np.float32, compression="gzip")
        f_out.create_dataset("azimuths", data=azimuths)

        #initialize motor matrix with -1
        dset_motor[...] = -1

        #fill top half
        for i, az in enumerate(azimuths_top):
            for j, m in enumerate(motor_top):
                match_idx = np.where((angles[:, 0] == m) & (angles[:, 1] == az))[0]
                if len(match_idx) > 0:
                    print(f"Saving {m}")
                    idx = match_idx[0]
                    dset_imgs[i, j] = f_in["images"][idx]
                    dset_motor[i, j] = m

        #fill bottom half
        for i, az in enumerate(azimuths_bot, start=len(azimuths_top)):
            for j, m in enumerate(motor_bot):
                match_idx = np.where((angles[:, 0] == m) & (angles[:, 1] == az))[0]
                if len(match_idx) > 0:
                    print(f"Saving {m}")
                    idx = match_idx[0]
                    dset_imgs[i, j] = f_in["images"][idx]
                    dset_motor[i, j] = m

print(f"Rectangular HDF5 saved to: {output_path}")
