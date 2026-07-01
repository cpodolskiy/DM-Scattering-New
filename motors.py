import pigpio
import threading
import time
from gpio import gpio
from skynet import skynet, IP_LIST, TIMEOUT

# _pi = pigpio.pi()

# if not _pi.connected:
#     print("ERROR")
#     raise IOError("Can't connect to pigpio")

MAX_SPEED = 480



class Motor(object):
   

    def __init__(self):
        
        self._pin_nEN = 3
        self._pin_nFAULT = 27
        self._pin_M1PWM = 18
        self._pin_M1DIR = 2
        # _pi.set_mode(self._pin_nEN, pigpio.OUTPUT)
        # _pi.set_mode(self._pin_nFAULT, pigpio.INPUT)
        # _pi.set_mode(self._pin_M1DIR, pigpio.OUTPUT)
        # _pi.set_mode(self._pin_M1PWM, pigpio.OUTPUT)
        
        # _pi.set_pull_up_down(self._pin_nFAULT, pigpio.PUD_UP)
        self._gpio = gpio(5)
        self._gpio.setMode(self._pin_nEN, pigpio.OUTPUT)
        self._gpio.setMode(self._pin_nFAULT, pigpio.INPUT)
        self._gpio.setMode(self._pin_M1DIR, pigpio.OUTPUT)
        self._gpio.setMode(self._pin_M1PWM, pigpio.OUTPUT)
        
        self._gpio.setPUD(self._pin_nFAULT, pigpio.PUD_UP)
    def getFault(self):
        # return not _pi.read(self._pin_nFAULT)
        return False

    def enable(self):
        # _pi.write(self._pin_nEN, 0)
        self._gpio.write(self._pin_nEN, 0)

    def disable(self):
        # _pi.write(self._pin_nEN, 1)
        self._gpio.write(self._pin_nEN, 1)
        
    def setNorm(self, speed):
        self.setSpeed(speed * MAX_SPEED)


    def setSpeed(self, speed):
        if speed < 0:
            speed = -speed
            dir_value = 1
        else:
            dir_value = 0

        if speed > MAX_SPEED:
            speed = MAX_SPEED
        
        # _pi.write(self._pin_M1DIR, dir_value)
        # _pi.set_PWM_dutycycle(self._pin_M1PWM, speed)
        #_pi.hardware_PWM(self.pwm_pin, 20000, int(speed * 6250 / 3))
        # 20 kHz PWM, duty cycle in range 0-1000000 as expected by pigpio
        self._gpio.write(self._pin_M1DIR, dir_value)
        self._gpio.writePWM(self._pin_M1PWM, speed)
        
    
class stepper(object):
    
    def __init__(self):
        self._position = 0.0
        self._dir = 0
        from skynet import skynet, IP_LIST
        # self._sky = skynet(True, IP_LIST["raspberrypi"], 5005, sim=False)
        self._sky = skynet(
            host=True,
            IP=IP_LIST["raspberrypi"],  # <-- destination Pi (stepper driver)
            port=5005,                  # <-- destination command port
            sim=False,
            receiveIP=IP_LIST["ANY"],   # <-- bind on all interfaces
            receivePort=5560            # <-- controller listens here for replies
        )

    
    def enable(self):
        # self._sky.send(b"E")
        self._sky.updateSteps(other=["E"])
        self._sky.sendSteps()
    def disable(self):
        # self.sky.send(b"D")
        self._sky.updateSteps(other=["D"])
        self._sky.sendSteps()
    
    def setDir(self, direction):
        self._dir = direction
        # self._sky.send(b"C")
        self._sky.updateSteps(direction=self._dir)
        self._sky.sendSteps()
    
    def fullStep(self):
        #self._sky.send(b"1")
        self._sky.updateSteps(full=1)
        rval = self._sky.sendSteps()
        if self._dir:
            self._position += 1.8
        else:
            self._position -= 1.8
        return rval
        
    def halfStep(self):
        # self._sky.send(b"2")
        self._sky.updateSteps(half=1)
        rval = self._sky.sendSteps()
        if self._dir:
            self._position += 1.8 / 2
        else:
            self._position -= 1.8 / 2
        return rval
            
    def quarterStep(self):
        # self._sky.send(b"4")
        self._sky.updateSteps(quarter=1)
        rval = self._sky.sendSteps()
        if self._dir:
            self._position += 1.8 / 4
        else:
            self._position -= 1.8 / 4
        return rval
            
    def eighthStep(self):
        # self._sky.send(b"8")
        self._sky.updateSteps(eighth=1)
        rval = self._sky.sendSteps()
        if self._dir:
            self._position += 1.8 / 8 
        else:
            self._position -= 1.8 / 8
        return rval
        
    def customStep(self, f=0, h=0, q=0, e=0, dir_value=-1, o=["A"]):
        if dir_value != -1:
            self._dir = dir_value
        self._sky.updateSteps(full=f, half=h, quarter=q, eighth=e, direction=self._dir, other=o)
        rval = self._sky.sendSteps()
        if self._dir:
            self._position += 1.8 * (f + (h / 2) + (q / 4) + (e / 8))
        else:
            self._position -= 1.8 * (f + (h / 2) + (q / 4) + (e / 8))
        return rval
    
    def degreeStep(self, degrees):
        _f = int (degrees / 1.8)
        _h = int ((degrees - (_f * 1.8)) / (1.8 / 2))
        _q = int ((degrees - (_f * 1.8 + _h * (1.8 / 2))) / (1.8 / 4))
        _e = int ((degrees - (_f * 1.8 + _h * (1.8 / 2) + _q * (1.8 / 4))) / (1.8 / 8))

        self.customStep(f=_f, h=_h, q=_q, e=_e, dir_value=0)

    def getLocalPosition(self):
        return self._position
    
    def signalPosition(self):
        # self._sky.send(b"S")
        self._sky.updateSteps(other=["S"])
        return self._sky.sendSteps()
    
    def confirmConnection(self):
        # self._sky.send(b"!")
        self._sky.updateSteps(other=["!"])
        self._sky.sendSteps()
        
    def getRemotePosition(self):
        # sky = skynet(False, IP_LIST["ANY"], 5560)
        for i in range(5):
            # self._sky.send(b"$")
            self._sky.updateSteps(other=["$"])
            self._sky.sendSteps()
            try:
                pos = float(self._sky.receive(10))
                break
            except (TIMEOUT, ValueError):
                print("timeout occured in motors.py")
                pos = -99
        return pos

    def confirmPos(self):
        pos = self.getRemotePosition()
        return abs(pos - self._position) < 0.2
    
    def resetPos(self):
        self._position = self.getRemotePosition()
    
    def end(self):
        # self._sky.send(b"N")
        self._sky.updateSteps(other=["N"])
        self._sky.sendSteps()
        


# if (__name__ == "__main__"):
#     motor = Motor()
#     motor.enable()
    
#     while True:
#         # for i in range(MAX_SPEED):
#         #     motor.setSpeed(i)
#         #     time.sleep(0.05)
#         #     print(motor.getFault())
#         #     print(i)
#         # for i in range(MAX_SPEED):
#         #     motor.setSpeed(-1 * i)
#         #     time.sleep(0.05)
#         #     print(motor.getFault())
#         #     print(-1 * i)
#         motor.setSpeed(MAX_SPEED)
#     motor.disable()
    
    
if __name__ == "__main__" and False:
    step = stepper()
    print("starting")
    print("Confirming connection")
    step.confirmConnection()
    step.setDir(1)
    time.sleep(0.5)
    step.enable()
    print("full step")
    for i in range(10):
        if not step.fullStep():
            print("STEP NOT SENT")
        time.sleep(0.01)
    step.setDir(0)
    # print(step.confirmPos())
    time.sleep(1)
    print("half step")
    for i in range(10):
        if not step.halfStep():
            print("STEP NOT SENT")
        time.sleep(0.01)
    step.setDir(1)
    time.sleep(1)
    # print(step.confirmPos())
    print("quarter step")
    for i in range(10):
        if not step.quarterStep():
            print("STEP NOT SENT")
        time.sleep(0.01)
    step.setDir(0)
    # print(step.confirmPos())
    time.sleep(1)
    print("eighth step")
    for i in range(10):
        if not step.eighthStep():
            print("STEP NOT SENT")
        time.sleep(0.01)
    print("Confirming Position, expecting True")
    print(step.confirmPos())
    print("Signaling position")
    step.signalPosition()
    # step = stepper()
    # while not step.confirmPos():
    #     step.fullStep()
    #     print(f"pos remote: {step.getPositionDeg()}")
    #     time.sleep(0.01)
    # print(step.getPositionDeg())
    # time.sleep(1)
    # step.signalPosition()
    time.sleep(1)
    print(f"sending error at {step.getLocalPosition()}, expecting False")
    rval = step.customStep(f=2)
    print(rval)
    print(f"sending normal at {step.getLocalPosition()}")
    rval = step.fullStep()
    print(rval)
    print(f"sending custom steps at {step.getLocalPosition()}")
    stepConfirmation = step.customStep(f=1, h=1, q=1, e=1)
    time.sleep(0.05)
    positionConfirmation = step.confirmPos()
    print(f"step signal {stepConfirmation}, Position Confirmation {positionConfirmation}, Local {step.getLocalPosition()}, Remote {step.getRemotePosition()}")
    print("sending many alternatives")
    step.customStep(o=["E", "D"])
    print("Ending")
    step.end()
    print("Al fin")

if __name__ == "__main__":
    step = stepper()
    step.enable()
    pos = step.getRemotePosition()
    print(pos)
    step.setDir(True)
    while pos <= 180:
        pos = step.getLocalPosition()
        print(pos)
        if not (step.eighthStep()):
            print("Step not sent")
        time.sleep(0.01)
    step.setDir(False)
    pos = step.getRemotePosition()
    while pos >= 0:
        pos = step.getLocalPosition()
        print(pos)
        if not (step.eighthStep()):
            print("Step not sent")
        time.sleep(0.05)
    step.disable()
    # step.end()