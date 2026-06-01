from motors import Motor
from encoder import Encoder
import time
import signal

mo = Motor()
en = Encoder("4", "17", 'R', '5')
mo.enable()

def _standardQuit(signum, frame):
        mo.disable()
        en.stop()
        exit(0)
        
signal.signal(signal.SIGINT, _standardQuit)
speed = 0.0
past_position = 0.0
past_time = time.time()
current_time = time.time()
position = 0.0
while True:
#     for i in range (51):
#         i = i * 5
#         mo.setSpeed(i)
#         print("FAULT: ", mo.getFault())
       
#         print("Rot: ", en.read(), " Vel: ", en.getVelocity(), " Input: ", i)
#         time.sleep(0.05)
#     for i in range(51):
#         i = i * 5
#         mo.setSpeed(-1 * i)
#         print("FAULT: ", mo.getFault())
#         print("Rot: ", en.read(), " Vel: ", en.getVelocity(), " Input: ",-1 * i)
#         time.sleep(0.05)
    
    mo.setSpeed(100)
    print(en.read(), "   ", en.getVelocity())
    time.sleep(0.05)
    # position = en.read()
    # current_time = time.time()
    # speed = (float(position) - float(past_position)) / float(current_time - past_time)
    # mo.setSpeed(-255)
    # print("Rot: ", position, "Test Vel:", speed, " Vel: ", en.getVelocity())
    # past_position = position
    # past_time - current_time
    # time.sleep(0.5)