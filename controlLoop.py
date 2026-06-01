import time
from motors import Motor

class PID:#no kI term
    
    
    def __init__(self, kP, kD, motor):
        self._kP = kP
        self._kD = kD
        self._motor = motor
        self._velocity = 0.0
        self._motor.enable()
        self._pastE = [0, 0]# E, time
        self._setpoint = 0.0
        
    
    
    def _VFF(self):
        return (255 / 0.1) * self._setpoint 
        #return 50
        
    def driveAt(self, setpoint, velocity):#range of 0.1 to -0.05
        self._setpoint = setpoint
        self._velocity = velocity
        output = self._E()
        # if (output > 1):
        #     output = 1
        # elif (output < -1):
        #     output = -1
        self._motor.setSpeed(output)
        
        #print(output)
        
    def _E(self):
        
        try:
            P = (self._setpoint - self._velocity) / (self._setpoint)
            D = (P - self._pastE[0]) / (time.time() - self._pastE[1])
        except ZeroDivisionError:
            D = 0
            P = 0
        self._pastE = [P, time.time()]
        val = self._kP * P + self._kD * D + self._VFF()
        #print(f"output: {val:.5}, velocity: {vel:.5}")
        return val
    
    def end(self):
        self._motor.setNorm(0)
        self._motor.disable()
    
if __name__ == "__main__":
    m = Motor()
    #pid = PID(100, 1, m, e)
    pid = PID(90, 0.5, m)
    while True:
        pid.driveAt(0.03)
    #print(e.getVelocity())