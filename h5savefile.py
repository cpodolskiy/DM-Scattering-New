import numpy as np
import h5py
from pathlib import Path

data_root = Path("array") #folder where all files are
image_shape = (1088, 1456) 
pixel_deg_motor = 0.921202100973 # angular resolution based on distance
pixel_deg_azimuth = 0.688377359072

output_path = data_root / "monolongrun.h5"

#HDF5 file with expandable datasets
with h5py.File(output_path, "w") as f:
    img_ds = f.create_dataset("images", shape=(0, *image_shape), maxshape=(None, *image_shape), dtype=np.uint16, compression="gzip", chunks=(1, *image_shape))

    angle_ds = f.create_dataset("angles", shape=(0, 2), maxshape=(None, 2), dtype=np.float32,  compression="gzip", chunks=(1, 2))

    idx = 0
    for folder in sorted(data_root.glob("longrun_*")): #folder name for the images
        azimuth = float(folder.name.split("_")[1])
        for file in sorted(folder.glob("*.raw")):
            motor = float(file.stem.split("_")[2])
            raw = np.fromfile(file, dtype=np.uint16).reshape(1088, 1472)
            raw = raw[:, :1456]
            if raw.size != np.prod(image_shape):
                print(f"skipping {file.name}: wrong size ({raw.size})")
                continue

            print(f"Working on {file.name}")

            #resize datasets to hold one more entry
            img_ds.resize(idx + 1, axis=0)
            angle_ds.resize(idx + 1, axis=0)

            #store image and angles directly to disk instead of in RAM
            img_ds[idx] = raw
            angle_ds[idx] = [motor, azimuth]
            idx += 1

print(f"Saved {idx} images and angles to: {output_path}")
