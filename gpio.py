import lgpio as sbc
import pigpio

OUTPUT = pigpio.OUTPUT
INPUT = pigpio.INPUT

DOWN = pigpio.PUD_DOWN

class gpio:
    def __init__(self, state):
        self._state = state
        if self._state == 4:
            self._pi = pigpio.pi()
            if not self._pi.connected:
                raise IOError("Can't connect to pigpio")
        elif state == 5:
            self._handle = sbc.gpiochip_open(0)
            if self._handle < 0:
                raise IOError("Can't connect to gpiochip")
        else:
            raise IOError("ERROR IN STATE")
    
    def setMode(self, pin, IO):
        if self._state == 4:
            self._pi.set_mode(pin, IO)
        elif self._state == 5:
            if IO == pigpio.INPUT:#input
                sbc.gpio_claim_input(self._handle, pin)
            else:
                sbc.gpio_claim_output(self._handle, pin)
                
    
    def setPUD(self, pin, UD):
        if self._state == 4:
            self._pi.set_pull_up_down(pin, UD)
        elif self._state == 5:
            if UD == pigpio.PUD_DOWN:
                sbc.gpio_claim_output(self._handle, pin, IFlags=SET_PULL_DOWN)
            else:
                sbc.gpio_claim_output(self._handle, pin, IFlags=SET_PULL_UP)
    
    def read(self, pin):
        if self._state == 4:
            return self._pi.read(pin)
        elif self._state == 5:
            return sbc.gpio_read(self._handle, pin)
            
    def write(self, pin, level):
        if self._state == 4:
            self._pi.write(pin, level)
        elif self._state == 5:
            sbc.gpio_write(self._handle, pin, level)
    
    def writePWM(self, pin, speed):
        if self._state == 4:
            # self._pi.set_PWM_dutycycle(pin, pwm)
            self._pi.hardware_PWM(pin, 20000, int(speed * 6250 / 3))
        elif self._state == 5:
            sbc.tx_pwm(self._handle, pin, 20000, int(speed * 6250 / 3))#converts to percent