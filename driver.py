from encoder import encoder
from motors import Motor, stepper, MAX_SPEED
from PID import PID

motor = Motor(12, 24)
stepper = stepper(-1, -1, -1, -1, -1)
en = encoder("4", "17", 'R')
pid = PID(0.1, 0.01, motor, en)

motor.enable()
stepper.enable()
angel = 0.0

def offloadDone():#for testing purposes
    return True

for i in range(180):
    while (angel % 360) < 180:
        pid.driveAt(15)
        angel = en.readDeg
    while (angel % 360) < 270:
        pid.driveAt(10)
        angel = en.readDeg
    while not offloadDone():
        pid.driveAt(0)
    while (angel % 360) < 360:
        pid.driveAt(15)
        angel = en.readDeg
    stepper.fullStep()
    
en.stop()
pid.end()
motor.disable()
stepper.disable()
print("Al fin")

# from __future__ import print_function
# import time
# from dual_max14870_rpi import motors, MAX_SPEED
# import subprocess
# import threading
# import os
# import fcntl
# from encoder import encoder

# # Define a custom exception to raise if a fault is detected.

# en = encoder("16", "18", 'S')# change to 'R' for real encoder

# MAX_SPEED = 500

# class DriverFault(Exception):
#     pass

# def raiseIfFault():
#     if motors.getFault():
#         raise DriverFault
 
 
# # Set up sequences of motor speeds.
# test_forward_speeds = list(range(0, MAX_SPEED, 1)) + \
#   [MAX_SPEED] * 200 + list(range(MAX_SPEED, 0, -1)) + [0]

# test_reverse_speeds = list(range(0, -MAX_SPEED, -1)) + \
#   [-MAX_SPEED] * 200 + list(range(-MAX_SPEED, 0, 1)) + [0]


# try:
#     motors.setSpeeds(0, 0)

#     print("Motor 1 forward")
#     for s in test_forward_speeds:
#         motors.motor1.setSpeed(s)
#         raiseIfFault()
#         time.sleep(0.002)

#     print(en.read())
#     print("Motor 1 reverse")
#     for s in test_reverse_speeds:
#         motors.motor1.setSpeed(s)
#         raiseIfFault()
#         time.sleep(0.002)

   
#     print(en.read())
#     # Disable the drivers for half a second.
#     motors.disable()
#     time.sleep(0.5)
#     motors.enable()
    
#     print("finishing things up")

#     '''print("Motor 2 forward")
#     for s in test_forward_speeds:
#         motors.motor2.setSpeed(s)
#         raiseIfFault()
#         time.sleep(0.002)

#     print("Motor 2 reverse")
#     for s in test_reverse_speeds:
#         motors.motor2.setSpeed(s)
#         raiseIfFault()
#         time.sleep(0.002)'''

# except DriverFault:
#     print("Driver fault!")

# finally:
#     # Stop the motors, even if there is an exception
#     # or the user presses Ctrl+C to kill the process.
#     motors.forceStop()