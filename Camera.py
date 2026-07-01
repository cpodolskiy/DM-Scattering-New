#!/bin/bash
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
import sys, time, cv2, queue, gc, multiprocessing, json
from pathlib import Path
from picamera2 import Picamera2
from multiprocessing import Process, JoinableQueue
from typing import SupportsFloat as Numeric
from encoder import Encoder
from motors import Motor
from motors import stepper

class SaveWorker(Process):
    def __init__(self, save_queue, display_queue):
        super().__init__()
        self.save_queue = save_queue
        self.display_queue = display_queue
        self.daemon = True

    def run(self):
        idx = 0
        while True:
            item = self.save_queue.get()
            if item is None:
                break
            fname, buffer_bytes = item
            with open(str(fname) + ".raw", "wb") as f:
                f.write(buffer_bytes)

            if idx % 5 == 0: #show preview every 5th frame only
                
                print("Sending an image")
                sys.stdout.flush()
                try:
                    self.display_queue.put_nowait(buffer_bytes)
                except Exception as e:
                    print(f"Preview error: {e}")  #drop frame if any error occurs

            idx += 1
            self.save_queue.task_done()

class CameraWorker(QtCore.QThread):
    progress = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal(float)

    def __init__(self, cam, folder_base:str, base_name:str, motor_step:Numeric, azimuth_step:Numeric, metadata:dict, display_queue,motor, encoder, stepper): # , pid): #
        super().__init__()
        self.cam = cam
        self.folder_base = Path(folder_base)
        # self.folder_base = Path(r"/media/locsst/USB SKY/mapping")
        self.base_name = base_name
        self.motor_step = motor_step
        self.azimuth_step = azimuth_step
        self.metadata = metadata
        print("Metadata is : ", self.metadata)
        self.display_queue = display_queue
        self.total_frames = int(180.0 / float(motor_step))
        self._stop = False
        self.interval = 6.0 / self.total_frames
        self.target_angles = list(np.arange(0, 180.0 + 0.01, float(motor_step)))
        # self.total_iterations = list(np.arange(0, 180.0 + 0.01, float(azimuth_step)))
        # self.total_frames = len(self.target_angles)
        #self.target_angles = [float(i) * float(motor_step) for i in range(self.total_frames)]
        self.total_iterations = [i * float(azimuth_step) for i in range(int(180.0 / float(azimuth_step)))]
        self.motor = motor
        self.encoder = encoder
        self.stepper = stepper

    def circular_error(self, current_angle, target_angle):
        """
        Signed shortest difference between current_angle and target_angle.
        Both angles are in degrees.
        Result is in range [-180, 180].
        """
        return ((current_angle - target_angle + 180.0) % 360.0) - 180.0
    
    def wait_for_angle(self, target_angle, tolerance=0.0675):
        """
        Wait until encoder reaches target angle, using circular 0/360 logic.
        """
        target_angle = target_angle % 360.0

        while not self._stop:
            degree = self.encoder.readDeg() % 360.0
            err = self.circular_error(degree, target_angle)

            if abs(err) < tolerance:
                return degree

            time.sleep(0.0005)

        return None
    
    def wait_for_local_angle(self, target_local_angle, row_zero_angle, tolerance=0.0675):
        """
        Wait until the camera reaches target_local_angle measured relative
        to the starting angle of this row.

        Example:
        If row_zero_angle = 359.66 deg, then raw 359.66 deg is local 0 deg,
        raw 0.16 deg is local 0.50 deg, etc.
        """
        target_local_angle = target_local_angle % 360.0
        row_zero_angle = row_zero_angle % 360.0

        while not self._stop:
            raw_degree = self.encoder.readDeg() % 360.0
            local_degree = (raw_degree - row_zero_angle) % 360.0

            err = self.circular_error(local_degree, target_local_angle)

            if abs(err) < tolerance:
                return raw_degree, local_degree

            time.sleep(0.0005)

        return None, None
    
    def return_to_corrected_start(self, start_angle):
        """
        Continue camera rotation until it reaches the corrected start angle
        for the next cycle. This allows starts like -0.27 deg to be treated
        as 359.73 deg.
        """
        start_angle = start_angle % 360.0

        self.progress.emit(
            f"Returning camera to corrected start angle: {start_angle:.3f} deg"
        )

        self.motor.setSpeed(100)

        while not self._stop:
            degree = self.encoder.readDeg() % 360.0
            err = self.circular_error(degree, start_angle)

            if abs(err) < 0.10:
                break

            time.sleep(0.001)

        self.motor.setSpeed(0)
        time.sleep(0.05)

        self.progress.emit(
            f"Camera reached corrected start angle. Encoder = {self.encoder.readDeg() % 360.0:.3f} deg"
        )

    def run(self):
        if not self.cam.started:
            # cfg = self.cam.create_video_configuration(raw={"format": "SRGGB12", "size": (2028, 1520)}, controls ={"AeEnable": False, "AwbEnable": False, 
            #                                                 "ExposureTime": self.metadata.get("ExposureTime"), "AnalogueGain": self.metadata.get("AnalogueGain"),
            #                                                 "FrameRate": 40.01, "ScalerCrop": (0, 0, 4056, 3040)})
            cfg = self.cam.create_video_configuration(raw={"format": "R10", "size": self.cam.sensor_resolution}, controls={ "AeEnable": False,
                                                            "ExposureTime": self.metadata.get("ExposureTime"), "AnalogueGain": self.metadata.get("AnalogueGain"),
                                                            "FrameRate": 30.0, #"FrameRate": 60.38, 
                                                            "ScalerCrop": (0, 0, 1456, 1088)})

            self.cam.configure(cfg)
            self.cam.start()
            time.sleep(1)

        Path(self.folder_base).mkdir(parents=True, exist_ok=True)
        meta_path = self.folder_base/"meta_data.json"
        with open(meta_path, "w") as f:
            json.dump(self.metadata, f, indent=2)
        save_queue = JoinableQueue(maxsize=self.total_frames)
        save_worker = SaveWorker(save_queue, self.display_queue)
        save_worker.start()

        
        time.sleep(2) #warm up
        t0 = time.monotonic()

        # One master encoder log for the whole experiment
        encoder_log_path = self.folder_base / "encoder_log.csv"

        with open(encoder_log_path, "w") as encoder_log:
            encoder_log.write(
        "filename,folder,azimuth,commanded_angle,local_encoder_angle,"
        "raw_encoder_angle,row_zero_angle,angle_error,time_seconds\n"
            )

        DRIFT_RATE_PER_CYCLE = 0.07 # 0.09 deg per cycle

        try:
            self.motor.setSpeed(100)
            for cycle_idx, i in enumerate(self.total_iterations):  # desired DM / azimuth angle

                if self._stop:
                    break

                # Move DM BEFORE capturing this azimuth folder
                self.progress.emit(f"Preparing DM for azimuth {i:.2f} deg")
                self.progress.emit(f"Stepper angle before move: {self.stepper.getLocalPosition():.3f}")

                # In this setup, positive azimuth corresponds to negative local stepper angle.
                # This moves from current local position toward target local position = -i.
                delta_to_move = i + self.stepper.getLocalPosition()

                if abs(delta_to_move) > 0.2:
                    self.stepper.degreeStep(delta_to_move)

                self.progress.emit(f"Stepper angle after move: {self.stepper.getLocalPosition():.3f}")
                self.progress.emit(f"Capturing azimuth folder: {i:.2f} deg")

                folder = self.folder_base / f"{self.base_name}_{i:06.2f}"
                folder.mkdir(parents=True, exist_ok=True)

                frame_idx = 0

                cumulative_drift = cycle_idx * DRIFT_RATE_PER_CYCLE

                # The current physical encoder position is the zero for this row.
                # For row 0, it should be near 0.
                # For later rows, it may be near 359.xx, but we still call it local 0.
                row_zero_angle = self.encoder.readDeg() % 360.0

                self.progress.emit(
                    f"Row zero set at raw encoder angle: {row_zero_angle:.3f} deg"
                )

                # Start camera rotation for this azimuth row
                self.motor.setSpeed(100)

                for j in self.target_angles:

                    if self._stop:
                        break

                    raw_degree, local_degree = self.wait_for_local_angle(j, row_zero_angle)

                    if raw_degree is None:
                        break

                    # while True:
                    #     degree = self.encoder.readDeg()
                    #     if abs(degree - corrected_target_angle) < 0.0675:
                    #         break

                    self.motor.setSpeed(100)

                    raw_data = self.cam.capture_buffer("raw").data
                    buffer_bytes = bytes(raw_data)
                    raw_array = np.frombuffer(buffer_bytes, dtype=np.uint16)

                    try:
                        raw_image = raw_array.reshape((1088, 1472))
                        raw_image = raw_image[:, :1456]

                        mean_intensity = raw_image.mean()
                        max_intensity = raw_image.max()
                        min_intensity = raw_image.min()
                        flux = raw_image.sum()

                        saturation_pixels = np.sum(raw_image > 65000)
                        saturation_percent = 100.0 * saturation_pixels / raw_image.size

                    except Exception:
                        mean_intensity = -1
                        max_intensity = -1
                        min_intensity = -1
                        flux = -1
                        saturation_percent = -1
                    fname = folder / f"{self.base_name}_{i:06.2f}_{j:06.2f}"
                    # fname = folder / f"{self.base_name}_{i:06.2f}_{degree:06.2f}"
                    #fname = folder / f"{self.base_name}_{i:06.2f}_{local_degree:06.2f}"
                    angle_error = self.circular_error(local_degree, j)
                    elapsed_time = time.monotonic() - t0

                    with open(encoder_log_path, "a") as encoder_log:
                        encoder_log.write(
                            f"{fname.name},"
                            f"{folder.name},"
                            f"{i:.6f},"
                            f"{j:.6f},"
                            f"{local_degree:.6f},"
                            f"{raw_degree:.6f},"
                            f"{row_zero_angle:.6f},"
                            f"{angle_error:.6f},"
                            f"{elapsed_time:.6f}\n"
                        )
                    for _ in range(10):
                        try:
                            save_queue.put((fname, buffer_bytes))
                            break
                        except queue.Full:
                            continue

                    # if j % 6 == 0:
                    #     self.progress.emit(
                    #         f"Captured {fname.name}, Expected Angle: {j}, "
                    #         f"Actual Angle: {degree:.3f}, Time: {(time.monotonic() - t0):03.2f}"
                    #     )
                    self.progress.emit(
                        f"Captured {fname.name}, Expected Angle: {j:.1f}, "
                        f"Local Angle: {local_degree:.3f}, "
                        f"Raw Encoder: {raw_degree:.3f}, "
                        f"Row Zero: {row_zero_angle:.3f}, "
                        f"Mean: {mean_intensity:.1f}, Max: {max_intensity:.0f}, "
                        f"Sat: {saturation_percent:.3f}%, "
                        f"Flux: {flux:.0f}, "
                        f"Time: {(time.monotonic() - t0):03.2f}"
                    )
                    frame_idx += 1

                # After finishing this 0-to-180 camera scan,
                # return the camera to the corrected start angle for the NEXT row.
                next_cycle_idx = cycle_idx + 1

                if next_cycle_idx < len(self.total_iterations):
                    next_cumulative_drift = next_cycle_idx * DRIFT_RATE_PER_CYCLE
                    next_start_angle = (0.0 - next_cumulative_drift) % 360.0

                    self.return_to_corrected_start(next_start_angle)

                self.progress.emit("Saving files")
                save_queue.join()

        finally:
            save_queue.put(None)
            save_worker.join()
            self.cam.stop()
            self.motor.setSpeed(0)
            print("Disabled motor")
            # self.encoder.stop()
            # print("Stopped encoder")
            self.stepper.disable()
            print("Stopped stepper")
            self.finished.emit((time.monotonic() - t0)/60)
            gc.collect()

    def stop(self):
        self._stop = True
        self.motor.disable()
        self.encoder.stop()

class CalibrateDialog(QtWidgets.QDialog):
    def __init__(self, cam, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calibrating Camera")
        self.setFixedSize(300,200)
        self.label = QtWidgets.QLabel("Calibrating...\nPlease wait.", self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.cam = cam
        self.exposure = None
        self.gain = None

        QtCore.QTimer.singleShot(100, self.calibrate)

    def calibrate(self):
        self.cam.stop()
        cfg = self.cam.create_still_configuration(raw={"format":"R10", "size": self.cam.sensor_resolution}, controls={"AeEnable": 1})
        self.cam.configure(cfg)
        self.cam.start()
        time.sleep(2)

        two = self.cam.capture_array("raw")
        metadata = self.cam.capture_metadata()
        self.cam.stop()

        self.exposure = int(metadata.get("ExposureTime", 1000))
        self.gain = float(metadata.get("AnalogueGain", 1.0))
        self.accept()

class CaptureApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Capture")
        self.cam = Picamera2()
        self.resize(828,560)
        self.display_queue = multiprocessing.Queue(maxsize = 10)
        layout = QtWidgets.QFormLayout(self)
        self.motor = Motor()
        self.en = Encoder("4", "17", 'R', '5')
        self.motor.enable()
        self.step = stepper()
        self.step.enable()

        self.folder_in = QtWidgets.QLineEdit("array")
        self.base_in = QtWidgets.QLineEdit("capture")
        self.motor_step = QtWidgets.QDoubleSpinBox(maximum=180.0, minimum=0.01, value=0.5) # type: ignore
        self.azimuth_step = QtWidgets.QDoubleSpinBox(maximum=360.0, minimum=0.01, value=10.0) # type: ignore
        self.exp_in = QtWidgets.QSpinBox(maximum=674181621, value=60) # type: ignore
        self.gain_in = QtWidgets.QDoubleSpinBox(value=2.0) # type: ignore
        self.status = QtWidgets.QTextEdit(readOnly=True) # type: ignore
        self.calibrate_btn = QtWidgets.QPushButton("Calibrate Settings")
        self.calibrate_btn.setStyleSheet("background-color : lightblue")
        self.calibrate_btn.clicked.connect(self.calibrate_camera)
        self.start_btn = QtWidgets.QPushButton("Start Capture")
        self.start_btn.setStyleSheet("background-color : lightgreen")
        self.start_btn.clicked.connect(self.start_capture)

        self.image_preview = QtWidgets.QLabel("Preview")
        self.image_preview.setFixedHeight(364)
        self.image_preview.setAlignment(QtCore.Qt.AlignCenter) #type:ignore

        layout.addRow("Save Folder:", self.folder_in)
        layout.addRow("Base Filename:", self.base_in)
        layout.addRow("Motor Step (deg):", self.motor_step)
        layout.addRow("Azimuth Step (deg):", self.azimuth_step)
        layout.addRow("Exposure (µs):", self.exp_in)
        layout.addRow("Gain:", self.gain_in)
        layout.addRow(self.calibrate_btn)
        layout.addRow(self.start_btn)
        layout.addRow(self.image_preview)
        layout.addRow(self.status)

        self.display_timer = QtCore.QTimer()
        self.display_timer.timeout.connect(self.update_preview)
        self.display_timer.start(500)

    def log(self, msg):
        self.status.append(msg)

    def calibrate_camera(self) -> None:
        try:
            dialog = CalibrateDialog(self.cam, self)
            if dialog.exec_():
                if dialog.exposure is None or dialog.gain is None:
                    raise RuntimeError("Calibration values not found")

                self.exp_in.setValue(dialog.exposure)
                self.gain_in.setValue(dialog.gain)
                self.log(f"Calibrated: Exposure = {dialog.exposure} µs, Gain = {dialog.gain:.2f}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Calibration Error", str(e))

    def start_capture(self):
        self.status.clear()
        self.start_btn.setEnabled(False)
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.log("Stopping previous capture thread...")
            self.worker.stop()
            self.worker.wait()
        user_inputs = {"ExposureTime": self.exp_in.value(),"AnalogueGain": self.gain_in.value()}
        self.worker = CameraWorker(self.cam, self.folder_in.text(), self.base_in.text(),
                                   self.motor_step.value(), self.azimuth_step.value(), user_inputs, self.display_queue, self.motor, self.en, self.step)
        self.worker.progress.connect(self.log)
        #self.worker.finished.connect(lambda s: self.log(f"Done in {s:.2f} sec"))
        self.worker.finished.connect(lambda s: (self.log(f"Done in {s:.2f} minutes"), self.start_btn.setEnabled(True))) #type:ignore
        self.worker.start()
        self.log("Capture started...")

    def update_preview(self):
        if not self.display_queue.empty():
            latest = None
            while not self.display_queue.empty():
                latest = self.display_queue.get_nowait()
            if latest:
                # print("Opening an image")
                try:
                    raw_array = np.frombuffer(latest, dtype=np.uint16)
                    width, height = 1472, 1088
                    expected_pixels = width * height
                    if raw_array.size != expected_pixels:
                        print(f"Unexpected image size: got {raw_array.size}, expected {expected_pixels}")
                        return
                    raw_image = raw_array.reshape((height, width))
                    preview_image = raw_image[:, :1456]
                    norm = (preview_image - preview_image.min()) / (preview_image.max() - preview_image.min())
                    norm8 = (norm*255).astype(np.uint8)
                    qimage = QtGui.QImage(norm8.data, norm8.shape[1], norm8.shape[0],norm8.strides[0], QtGui.QImage.Format_Grayscale8)
                    pixmap = QtGui.QPixmap.fromImage(qimage)
                    print("Attempting to rotate")
                    rotation_matrix = QtGui.QTransform()
                    rotation_matrix.rotate(90)
                    print("Rotating")
                    pixmap = pixmap.transformed(rotation_matrix)
                    self.image_preview.setPixmap(pixmap.scaled(272, 364))
                    # self.image_preview.setPixmap(pixmap.scaled(364, 272))
                except Exception as e:
                    print("Preview fallback error:", e)

    def stop(self):
        self.log("Stopping system...")
        # try:
        #     if hasattr(self, 'worker') and self.worker.isRunning():
        #         self.log("Stopping capture thread...")
        #         self.worker.stop()
        #         self.worker.wait()
        # except Exception as e:
        #     self.log(f"Error stopping worker: {e}")

        try:
            if self.motor:
                self.motor.setSpeed(0)
                self.motor.disable()
                self.log("Motor disabled.")
        except Exception as e:
            self.log(f"Motor disable error: {e}")

        try:
            if self.en:
                self.en.stop()
                self.log("Encoder stopped.")
        except Exception as e:
            self.log(f"Encoder stop error: {e}")

        try:
            if self.cam and self.cam.started:
                self.cam.stop()
                self.log("Camera stopped.")
        except Exception as e:
            self.log(f"Camera stop error: {e}")


    def closeEvent(self, event: QtGui.QCloseEvent): #type:ignore
        try:
            self.stop()
        except Exception as e:
            print("Error during stop():", e)

        event.accept()
        print("Application closed")

if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        win = CaptureApp()
        win.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        win.stop()
