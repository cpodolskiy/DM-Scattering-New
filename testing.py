# import sys
# import numpy as np
# from PyQt5 import QtWidgets, QtGui, QtCore
# from picamera2 import Picamera2
# import cv2

# class PreviewWindow(QtWidgets.QWidget):
#     def __init__(self, raw_bytes, raw_width, raw_height, rgb_array):
#         super().__init__()
#         self.setWindowTitle("Raw10 and Preview Side-by-Side")
#         self.resize(1600, 600)

#         raw = np.frombuffer(raw_bytes, dtype=np.uint16).reshape((raw_height, 1472))
#         #raw = np.frombuffer(raw_bytes, dtype=np.uint16)[:raw_height * raw_width].reshape((raw_height, raw_width))
#         norm_raw = ((raw / 1023) * 255).astype(np.uint8)
#         resized_raw = cv2.resize(norm_raw, (780, 544))
#         qimg_raw = QtGui.QImage(resized_raw.data, resized_raw.shape[1], resized_raw.shape[0], resized_raw.strides[0], QtGui.QImage.Format_Grayscale8)
#         pix_raw = QtGui.QPixmap.fromImage(qimg_raw)

#         rgb_resized = cv2.resize(rgb_array, (780, 544))
#         #rgb_resized = cv2.cvtColor(rgb_resized, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB for Qt
#         h, w, ch = rgb_resized.shape
#         bytes_per_line = ch * w
#         qimg_rgb = QtGui.QImage(rgb_resized.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
#         pix_rgb = QtGui.QPixmap.fromImage(qimg_rgb)

#         layout = QtWidgets.QHBoxLayout()
        
#         label_raw = QtWidgets.QLabel()
#         label_raw.setPixmap(pix_raw)
#         label_raw.setAlignment(QtCore.Qt.AlignCenter)
#         layout.addWidget(label_raw)

#         label_rgb = QtWidgets.QLabel()
#         label_rgb.setPixmap(pix_rgb)
#         label_rgb.setAlignment(QtCore.Qt.AlignCenter)
#         layout.addWidget(label_rgb)

#         self.setLayout(layout)

# def main():
#     raw_width, raw_height = 1456, 1088

#     app = QtWidgets.QApplication(sys.argv)
#     cam = Picamera2()

#     config = cam.create_still_configuration(
#         raw={"format": "R10", "size": cam.sensor_resolution},
#         main={"size": cam.sensor_resolution})
#     cam.configure(config)
#     cam.start()

#     request = cam.capture_request()
#     raw_bytes = request.make_buffer("raw").data
#     rgb_array = request.make_array("main")  # Get RGB preview as numpy array
#     request.release()
#     cam.stop()

#     window = PreviewWindow(raw_bytes, raw_width, raw_height, rgb_array)
#     window.show()
#     sys.exit(app.exec_())

# if __name__ == "__main__":
#     main()



# from picamera2 import Picamera2
# import cv2
# import time
# import numpy as np

# def main():
#     picam2 = Picamera2()
#     config = picam2.create_preview_configuration(raw = {"format": "R10", "size": picam2.sensor_resolution}, controls={"AeEnable": 1})# main={"format": "RGB888", "size": (640, 480)})
#     picam2.configure(config)
#     picam2.start()

#     start_time = time.time()
#     while time.time() - start_time < 1000:  
#         frame = picam2.capture_array("raw")
#         image_shape = [1088, 1472]
#         dtype = np.uint16
#         frame = np.frombuffer(frame, dtype=dtype).reshape(image_shape)
#         frame = frame[:, :1456]
#         # print(frame.size, "size")
#         # print(frame.shape, "shape")
#         # print(frame.max(), "max") 
#         # print(picam2.capture_metadata())
#         cv2.imshow("Live Preview", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'): 
#             break

#     picam2.stop()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()

# from pathlib import Path
# import numpy as np
# import matplotlib.pyplot as plt
# import cv2

# folder = Path(r"/home/locsst/Documents/camera/array/timetrial_000.0")  
# image_shape = (1088, 1472)        
# dtype = np.uint16          

# raw_files = sorted(folder.glob("*.raw"))
# if not raw_files:
#     print("No .raw files found.")
#     exit()

# print(f"Found {len(raw_files)} files.")

# i = 0
# fig, ax = plt.subplots()

# def show_image(index):
#     arr = np.fromfile(raw_files[index], dtype=dtype).reshape(image_shape)
    
#     ax.imshow(arr, cmap="gray") 
#     ax.set_title(raw_files[index].name)
#     fig.canvas.draw()

# def on_key(event):
#     global i
#     if event.key == 'right' or event.key == ' ':
#         i = (i + 1) % len(raw_files)
#     elif event.key == 'left':
#         i = (i - 1) % len(raw_files)
#     elif event.key == 'escape':
#         plt.close()
#         return
#     show_image(i)

# fig.canvas.mpl_connect('key_press_event', on_key)
# show_image(i)
# plt.show()


# from picamera2 import Picamera2
# import numpy as np
# import matplotlib.pyplot as plt
# import time

# def main():
#     cam = Picamera2()
#     config = cam.create_video_configuration(raw={"format": "R10", "size": (1456, 1088)})
#     cam.configure(config)
#     cam.start()
#     time.sleep(1)

#     array = cam.capture_array("raw")
#     array = array[:, ::2]
#     array = array[:, :1456]
#     print(array.max(), array.min(), array.mean())

#     buf = cam.capture_buffer("raw").data
#     raw_array = np.frombuffer(buf, dtype=np.uint16).reshape(1088, 1472)
#     buffer = raw_array[:, :1456]
#     print(buffer.max(), buffer.min(), buffer.mean())

#     plt.figure(figsize=(10,5))
#     plt.subplot(1,2,1)
#     plt.imshow(array, cmap="gray")
#     plt.title("array")

#     plt.subplot(1,2,2)
#     plt.imshow(buffer, cmap = "gray")
#     plt.title("buffer")
#     plt.tight_layout()
#     plt.show()

# if __name__ == "__main__":
#     main()


# from picamera2 import Picamera2
# import numpy as np
# import matplotlib.pyplot as plt
# import time

# def main():
#     cam = Picamera2()
#     width, height = 1472, 1088
#     config = cam.create_video_configuration(raw={"format": "R10", "size": (width, height)})
#     cam.configure(config)
#     cam.start()
#     time.sleep(1)

#     array = cam.capture_array("raw")
#     array = array[:, 1::2]
#     array = array[:, :1456]
#     print("array shape:", array.shape, array.dtype)
#     print("array max, min, mean:", array.max(), array.min(), array.mean())

#     buf = cam.capture_buffer("raw").data
#     buffer = np.frombuffer(buf, dtype=np.uint16).reshape(height, width)
#     buffer = buffer[:, :1456]
#     print("buffer shape:", buffer.shape, buffer.dtype)
#     print("buffer max, min, mean:", buffer.max(), buffer.min(), buffer.mean())

#     config2 = cam.create_still_configuration(main={"format": "RGB888", "size": (width, height)})
#     main = cam.switch_mode_and_capture_array(config2, "main")
#     print("main:", main.shape, main.dtype)
#     print("main size: ", main.size, main.shape)

#     plt.figure(figsize=(10, 5))
#     plt.subplot(1, 3, 1)
#     plt.imshow(array, cmap="gray")
#     plt.title("capture_array")

#     plt.subplot(1, 3, 2)
#     plt.imshow(buffer, cmap="gray")
#     plt.title("capture_buffer")

#     plt.subplot(1,3,3)
#     plt.imshow(main, cmap="gray")
#     plt.title("main")

#     plt.tight_layout()
#     plt.show()

# if __name__ == "__main__":
#     main()

#####################
# from picamera2 import Picamera2
# import cv2
# import numpy as np
# import time

# def main():
#     cam = Picamera2()
#     width, height = 1472, 1088

#     #configure camera: RAW buffer + main
#     config = cam.create_video_configuration(
#         raw={"format": "R10", "size": (width, height)},
#         main={"format": "RGB888", "size": (width, height)},
#         controls={"AeEnable": 1, "FrameRate": 60.38})
#     cam.configure(config)
#     cam.start()
#     time.sleep(1)

#     preview_height = 500  # common preview height for both streams

#     while True:
#         #RAW buffer (mono)
#         buf = cam.capture_buffer("raw").data
#         buffer = np.frombuffer(buf, dtype=np.uint16).reshape(height, width)[:, :1456]
#         buffer_disp = ((buffer - buffer.min()) / (buffer.max() - buffer.min() + 1e-9) * 255).astype(np.uint8)
#         preview_buffer = cv2.resize(buffer_disp, (int(buffer_disp.shape[1] * preview_height / buffer_disp.shape[0]), preview_height), interpolation=cv2.INTER_NEAREST)

#         #main 
#         main_frame = cam.capture_array("main")
#         preview_main = cv2.resize(main_frame, (int(main_frame.shape[1] * preview_height / main_frame.shape[0]), preview_height), interpolation=cv2.INTER_NEAREST)
#         preview_main_gray = cv2.cvtColor(preview_main, cv2.COLOR_RGB2GRAY)

#         combined = np.hstack([preview_buffer, preview_main_gray])

#         cv2.imshow("Live Preview: RAW | Main (Gray)", combined)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cam.stop()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()


# from picamera2 import Picamera2
# import cv2
# import numpy as np
# import time

# def main():
#     cam = Picamera2()
#     width, height = 1472, 1088

#     # Video configuration: capture RAW buffer and RGB main
#     config = cam.create_video_configuration(
#         raw={"format": "R10", "size": (width, height)},
#         main={"format": "RGB888", "size": (width, height)},
#         controls={"AeEnable": 1})
#     cam.configure(config)
#     cam.start()
#     time.sleep(1)

#     preview_height = 300  # common height for both previews

#     while True:
#         # RAW buffer
#         buf = cam.capture_buffer("raw").data
#         buffer = np.frombuffer(buf, dtype=np.uint16).reshape(height, width)[:, :1456]
#         buffer_disp = ((buffer - buffer.min()) / (buffer.max() - buffer.min() + 1e-9) * 255).astype(np.uint8)
#         preview_buffer = cv2.resize(buffer_disp, (int(buffer_disp.shape[1] * preview_height / buffer_disp.shape[0]), preview_height), interpolation=cv2.INTER_NEAREST)
#         preview_buffer = cv2.cvtColor(preview_buffer, cv2.COLOR_GRAY2BGR)
#         # Add title
#         # cv2.putText(preview_buffer, "RAW Buffer", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

#         # RGB main
#         main_frame = cam.capture_array("main")
#         preview_main = cv2.resize(main_frame, (int(main_frame.shape[1] * preview_height / main_frame.shape[0]), preview_height), interpolation=cv2.INTER_NEAREST)
#         # Add title
#         # cv2.putText(preview_main, "Main RGB", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

#         # Stack horizontally
#         combined = np.hstack([preview_buffer, preview_main])

#         cv2.imshow("Live Preview: Buffer , Main", combined)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cam.stop()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()




###################### Real time Image Viewer #################
# from picamera2 import Picamera2
# import cv2
# import time
# import numpy as np

# def main():
#     picam2 = Picamera2()
    
#     # Configure RAW10 capture (camera converts to 16-bit)
#     config = picam2.create_still_configuration(
#         raw={"format": "R10", "size": picam2.sensor_resolution},
#         controls={ "AeEnable": False, "FrameRate": 60.38, "ScalerCrop": (0, 0, 1456, 1088)})
#     picam2.configure(config)
#     picam2.start()

#     start_time = time.time()
#     while time.time() - start_time < 1000:
#         # Proper way to get raw sensor data
#         frame = picam2.capture_buffer("raw").data
#         frame = bytes(frame)   #already 16-bit, aligned, cropped
#         # Crop if needed
#         frame = np.frombuffer(frame, dtype=np.uint16)  # interpret bytes as 16-bit integers
#         frame = frame.reshape((1088, 1472)) 
#         frame = frame[:, :1456]

#         # Optional: downsample for smaller preview window
#         preview_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

#         # Display raw values directly
#         cv2.imshow("Live RAW Preview", preview_frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     picam2.stop()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()


############## Loading images ###########3
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

folder = Path("/home/locsst/Documents/camera/array/full_112.50")
image_shape = [1088, 1472]
dtype = np.uint16

raw_files = sorted(folder.glob("*.raw"))
if not raw_files:
    print("No raw files found")
    exit()

print(f"Found {len(raw_files)} files")

i = 0
fig, ax = plt.subplots(figsize=(10, 8))

def show_image(index):
    ax.clear()
    
    # Read and process image
    arr = np.fromfile(raw_files[index], dtype=dtype).reshape(image_shape)
    arr = arr[:, :1456]
    
    # Rotate and flip to get correct orientation
    arr_rotated = np.rot90(arr, 3)  # Rotate 270 degrees
    arr_rotated = np.flipud(arr_rotated)  # Flip to move y-axis
    
    ax.imshow(arr_rotated, cmap="gray")
    ax.set_title(raw_files[index].name)
    plt.draw()

def on_key(event):
    global i
    if event.key == 'right' or event.key == ' ':
        i = (i + 1) % len(raw_files)
    elif event.key == 'left':
        i = (i - 1) % len(raw_files)
    elif event.key == 'escape':
        plt.close()
        return
    show_image(i)

fig.canvas.mpl_connect('key_press_event', on_key)
show_image(i)
plt.tight_layout()
plt.show()