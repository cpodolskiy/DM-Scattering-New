from motors import Motor
from encoder import Encoder
import time

if __name__ == "__main__":
    with Encoder(4, 17, "R", 5) as en:
        mo = Motor()
        mo.setSpeed(120)
        mo.enable()

        start = time.time()
        while True:
            rot = en.read_rotations()
            vel = en.read_velocity()
            t = time.time() - start
            print(f"Rot: {rot:.10} Vel: {vel:.10} Time: {t:.10}")
            time.sleep(0.5)
