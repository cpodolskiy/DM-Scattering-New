from encoder import Encoder
from motors import Motor
from motors import stepper
from PyQt5 import QtWidgets, QtCore, QtGui
import sys, time, cv2, queue, gc, multiprocessing, json

class MotorApp(QtWidgets.QWidget):

    def __init__(self):
        self.m = Motor()
        self.en = Encoder("4", "17", 'R', '5')
        self.m.enable
        super().__init__()
        self.setWindowTitle("Motor App")
        self.resize(828,560)
        layout = QtWidgets.QFormLayout(self)
        

        #self.folder_in = QtWidgets.QLineEdit("array")
        #self.base_in = QtWidgets.QLineEdit("capture")
        
        self.clockwise_btn = QtWidgets.QPushButton("Rotate Clockwise")
        self.clockwise_btn.setStyleSheet("background-color : lightblue")
        self.clockwise_btn.clicked.connect(self.rotateClockwise)

        self.counter_btn = QtWidgets.QPushButton("Rotate Counter-Clockwise")
        self.counter_btn.setStyleSheet("background-color : lightgreen")
        self.counter_btn.clicked.connect(self.rotateCounterClockwise)

        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.stop_btn.setStyleSheet("background-color : lightgreen")
        self.stop_btn.clicked.connect(self.stopRotate)

        #self.image_preview = QtWidgets.QLabel("Preview")
        #self.image_preview.setFixedHeight(364)
        #self.image_preview.setAlignment(QtCore.Qt.AlignCenter) #type:ignore
        layout.addRow(self.clockwise_btn)
        layout.addRow(self.counter_btn)
        layout.addRow(self.stop_btn)
        self.display_timer = QtCore.QTimer()
        self.display_timer.start(500)
    def rotateClockwise(self):
        self.m.setSpeed(-100);
    def rotateCounterClockwise(self):
        self.m.setSpeed(100);
    def stopRotate(self):
        self.m.setSpeed(0)
    def stop(self):
        try:
            if self.m:
                self.m.setSpeed(0)
                self.m.disable()
                #self.log("Motor disabled.")
        except Exception as e:
            #self.log(f"Motor disable error: {e}")
            return
        try:
            if self.en:
                self.en.stop()
                #self.log("Encoder stopped.")
        except Exception as e:
            #self.log(f"Encoder stop error: {e}")
            return
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
        win = MotorApp()
        win.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        win.stop()