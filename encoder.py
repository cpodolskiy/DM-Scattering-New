import time
import ctypes
import pathlib
import subprocess
from motors import Motor

class Encoder:
    def __init__(self, pinA: int, pinB: int, RS: str, state: int):
        base = pathlib.Path(__file__).resolve().parent

        # Load shared library
        so_path = base / "Encoder.so"
        self._lib = ctypes.CDLL(str(so_path))
        self._lib.readPosition.restype = ctypes.c_double
        self._lib.readVelocity.restype = ctypes.c_double

        # Launch encoder executable
        exe_path = base / "Encoder"
        self._proc = subprocess.Popen(
            [str(exe_path), str(pinA), str(pinB), str(RS), str(state)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        time.sleep(0.05)
        if self._proc.poll() is not None:
            raise RuntimeError(f"Encoder exited immediately (rc={self._proc.returncode})")
    

    def read(self):#in rotations
        val = float(self._lib.readPosition())
        #print("POS: ", val)
        return val
    
    def readRad(self):
        return float(self.read()) * 6.283
    
    def readDeg(self):
        return float(self.read()) * 360
    
    def resetLogs(self):
        os.remove(r"/home/nick/LoCSST_DM/Logging.txt")
        
    def getVelocity(self):
        val = float(self._lib.readVelocity())
        #print("VEL: ", val)
        return val

    
    def _getStepperPos(self):#just an estimate since they are two independent systems
        t_1 = time.time() - self._startTime
        v = self._velocity
        #v = 0.25
        t_2 = 180 / v
        p = t_1 / t_2
        return math.floor(p * 180)
        
        
    def stop(self):
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self._proc.kill()
    
    def __exit__(self, exc_type, exc, tb):
        self.stop()


    def _standardQuit(self, signum, frame):
        self._running = False
        if self._p1.pid == None:
            raise RuntimeError("PID not found")
        os.kill(self._p1.pid, signal.SIGTERM)
        self._p1.join()
        for proc in psutil.process_iter():
            if proc.name() == self._procname:
                proc.kill()
        exit(0)


if __name__ == "__main__":
    en = Encoder(4, 17, 'R', 5)
    mo = Motor()
    start = time.time()
    rotation = 0.0
    velocity = 0.0
    time_diff = 0.0
    mo.setSpeed(120)
    mo.enable()
    try:
        while True:
            rotation = en.read()
            velocity = en.getVelocity()
            time_diff = time.time() - start
            print(f"Rot: {rotation:.10} Vel: {velocity:.10} Time: {time_diff:.10}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Ctrl+C detected")
    finally:
        en.stop()