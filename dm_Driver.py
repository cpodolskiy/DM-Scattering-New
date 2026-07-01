from gpio import gpio, OUTPUT, INPUT, DOWN
import time
from datetime import datetime
from skynet import skynet, IP_LIST, TIMEOUT
import subprocess

class stepper(object):
    
    def __init__(self):
        
        self._pinEN = 14
        # self._pinStep = 14
        # self._pinDir = 2
        # self._pinMS1 = 4
        # self._pinMS2 = 14
        self._pinFault = 2 # was 4 but 4 is disconnected
        # self._pinIndex = self._pinFault#change for prod
        self._pinDir = 2
        self._pinStep = 3
        
        self._dir = 1
        self._position = 0.0
        self._pi = gpio(4)
        self.disable()
        self.setDir(1)
        
        self._enabled = False
        
        self._pi.setMode(self._pinEN, OUTPUT)
        self._pi.setMode(self._pinStep, OUTPUT)
        self._pi.setMode(self._pinDir, OUTPUT)
        # self._pi.setMode(self._pinMS1, OUTPUT)
        # self._pi.setMode(self._pinMS2, OUTPUT)
        self._pi.setMode(self._pinFault, INPUT)
        # self._pi.setMode(self._pinIndex, INPUT)
        # self._pi.setPUD(self._pinIndex, DOWN)
        self._pi.setPUD(self._pinFault, DOWN)
        
        # self._pi.setMode(4, OUTPUT)
        
        self._pi.write(self._pinStep, 0)
        self._pi.write(self._pinEN, 1)
        
    def _step(self, MS1, MS2):
        self._pi.write(self._pinStep, 1)
        # self._pi.write(self._pinMS1, MS1)
        # self._pi.write(self._pinMS2, MS2)
        time.sleep(0.001)
        self._pi.write(self._pinStep, 0)
        time.sleep(0.001)
        # just running the fan rn
        # self._pi.write(4, 1)
        # time.sleep(0.01)
        # self._pi.write(4, 0)
        
    def fullStep(self):
        # print("full step")
        self.halfStep()
        self.halfStep()
    def halfStep(self):
        # print("half step")
        self.quarterStep()
        self.quarterStep()
    def quarterStep(self):
        # print("quarter step")
        self.eighthStep()
        self.eighthStep()
    def eighthStep(self):
        # print("eighth step")
        if not self._enabled:
            return
        self._step(0, 0)
        if self._dir:
            self._position += 1.8 / 8.0
        else:
            self._position -= 1.8 / 8.0
            
    def enabled(self):
        return self._enabled
        
    def getFault(self):
        print(self._pi.read(self._pinFault))
        return not self._pi.read(self._pinFault)
    
    def getIndex(self):
        return self._pi.read(self._pinIndex)
    
    def setDir(self, dir):
        print(f'set direction to {dir}')
        self._dir = dir
        self._pi.write(self._pinDir, self._dir)
    def getDir(self):
        return self._dir
        
    def enable(self):
        # print('enable stepper')
        self._pi.write(self._pinEN, 0)
        self._enabled = True
    def disable(self):
        # print('disable stepper')
        self._pi.write(self._pinEN, 1)
        self._enabled = False
        
    def getPositionDeg(self):
        return self._position
    
    def _turnLEDON(self):
        subprocess.run(["sudo", "sh", "-c", f"echo 0 > /sys/class/leds/PWR/brightness"])
    
    def _turnLEDOFF(self):
        subprocess.run(["sudo", "sh", "-c", f"echo 255 > /sys/class/leds/PWR/brightness"])
        
    def _turnGreenLEDON(self):
        subprocess.run(["sudo", "sh", "-c", f"echo 255 > /sys/class/leds/ACT/brightness"])
    
    def _turnGreenLEDOFF(self):
        subprocess.run(["sudo", "sh", "-c", f"echo 0 > /sys/class/leds/ACT/brightness"])
    
    def confirmConnection(self):
        self._turnLEDON()
        time.sleep(0.5)
        self._turnLEDOFF()
        
    def castError(self):
        self._turnLEDON()
        self.disable()
        
    def end(self):
        self._turnLEDON()
        self.disable()
    
    def _signalPositionBinary(self):#best not to use
        mask = 256
        for i in range(8):
            output = int(self._position) & mask
            output >> (8 - i)
            mask = mask >> 1
            if output != 0:
                self._turnGreenLEDON()
                time.sleep(0.5)
                self._turnGreenLEDOFF()
            else:
                self._turnLEDON()
                time.sleep(0.5)
                self._turnLEDOFF()
                
    def signalPositionSimple(self):
        for i in range(int(self._position / 100)):
            self._turnGreenLEDON()
            self._turnLEDON()
            time.sleep(0.5)
            self._turnGreenLEDOFF()
            self._turnLEDOFF()
        for i in range(int((self._position % 100) / 10)):
            self._turnGreenLEDON()
            time.sleep(0.5)
            self._turnGreenLEDOFF()
        for i in range(int(self._position % 10)):
            self._turnLEDON()
            time.sleep(0.5)
            self._turnLEDOFF()
            
    
    def signalError(self):
        for i in range(3):
            self._turnLEDON()
            time.sleep(0.01)
            self._turnLEDOFF()
            time.sleep(0.01)
    
    def confirmPos(self, sky):
        # sky = skynet(True, IP_LIST["pi"], 5560)
        # sky.send(str(self._position).encode())
        sky.send(str(self._position).encode())

if __name__ == "__main__":
    
    # step = stepper()
    
    # step.confirmConnection()
    
    # print("Enable stepper")
    
    # step.enable()
    # step.setDir(1)
    
    # steps = 1
    # for i in range(steps):
    #     step.halfStep()
    #     time.sleep(0.005)

    # print("done")
    # step.disable()
      
    step = stepper()
    sky = skynet(False, IP_LIST["ANY"], 5005, IP_LIST["shortcake"], 5560)
    try:
        step.confirmConnection()
        t = {datetime.now().strftime("%H:%M:%S")}
        print(f"{t} Starting Loop")
        run = True

        while run:
            recv = sky.receiveSteps(100)
            # print(recv)
            t = datetime.now().strftime("%H:%M:%S")
            print(f"{t} {recv}, pos {step.getPositionDeg()}")
            
            # for some reason this always returns true
            # the data sheet says it should only return true if there is an error
            # right now this is commented out hoping there will be no issues    
            if step.getFault():
                print("Fault Triggered Exiting loop")
                step.end()
                run = False
                break
            
            for i in recv:
                if i[0] != '-1':
                    if i[1] > 1:
                        # step.signalError()
                        print(f"WARNING: {t} multiple {i[0]} steps at once ({i[1]})")
                match i[0]:
                    case '1':
                        print(f'full step {i[1]}')
                        for ii in range(i[1]):
                            step.fullStep()
                    case '2':
                        print(f'half step {i[1]}')
                        for ii in range(i[1]):
                            step.halfStep()
                    case '4':
                        print(f'quarter step {i[1]}')
                        for ii in range(i[1]):
                            step.quarterStep()
                    case '8':
                        print(f'eighth step {i[1]}')
                        for ii in range(i[1]):
                            step.eighthStep()
                    case 'D':
                        print(f'set direction to {i[1]}')
                        step.setDir(i[1])
                    case _:
                        print('here')
                        for ii in i[1]:
                            match ii:
                                case "E":
                                    step.enable()
                                    step.setDir(1)
                                case "N":
                                    step.end()
                                    run = False
                                    break
                                case "D":
                                    print('disable stepper')
                                    step.disable()
                                case "!":
                                    print('confirm connection')
                                    step.confirmConnection()
                                case "S":
                                    print('signal position')
                                    step.signalPositionSimple()
                                case "$":
                                    print('cast error')
                                    step.confirmPos(sky)
    except Exception as e:
        step.disable()
        step.end()
        print("Error occured stepper disabled successfully")
        print("Error message: ", e)
    finally:
        print(sky.getSteps())
