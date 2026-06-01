from motors import Motor
from controlLoop import PID
from encoder import Encoder
import time

mo = Motor()
en = Encoder("4", "17", 'R', '5')
# pid = PID(90, 0.5, mo)

start = time.time()
curr = start

# while curr - start < 20:
#     curr = time.time()
#     setpoint = 0.1
#     velocity = en.getVelocity()
#     pid.driveAt(setpoint, velocity)
# mo.enable()
# mo.setSpeed(420)

mo.setSpeed(120)
mo.enable()
position = en.read()

while position < 90:
    # pid.driveAt(0.1, en.getVelocity())
    position = en.read()
    velocity = en.getVelocity()
    curr = time.time()
    print(position)
    # print(f"position : {position:.10}, velocity: {velocity:.10}, time: {curr-start:.10}, fault: {mo.getFault()}")
    
# pid.end()