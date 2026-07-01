import socket
import json

IP_LIST = {"pi" : "10.157.16.245", "raspberrypi" : "10.248.52.167", "shortcake" : "10.248.35.248", "ANY" : "0.0.0.0"}
TIMEOUT = socket.timeout
class skynet:
    
    def __init__(self, host, IP, port, sendIP=IP_LIST["shortcake"], sendPort=5560):
        self._host = host
        self._UDP_IP = IP
        self._UDP_Port = port
        self._sendIP = sendIP
        self._sendPort = sendPort
        self._steps = {'1' : 0, '2' : 0, '4' : 0, '8' : 0, 'D' : 0, '-1' : "A"}
        
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        if not self._host:
            self._sock.bind((self._UDP_IP, self._UDP_Port))
    
    def send(self, message):
        self._sock.sendto(message, (self._sendIP, self._sendPort))
        
    def receive(self, buffer):
        data, addr = self._sock.recvfrom(buffer)
        return data.decode()
    
    def updateSteps(self, full=0, half=0, quarter=0, eighth=0, direction=-1, other="A"):
        self._steps[1] += full
        self._steps[2] += half
        self._steps[4] += quarter
        self._steps[8] += eighth
        self._steps[-1] = other
        if direction != -1:
            self._steps['D'] == direction
    
    # def sendSteps(self):
    #     data = json.dumps(self._steps).encode('utf-8')
    #     self._sock.sendto(data, (self._UDP_IP, self._UDP_Port))
        
    def receiveSteps(self, buffer):
        data, addr = self._sock.recvfrom(buffer)
        newSteps = json.loads(data.decode())
        l = []
        for key, value in newSteps.items():
            if key == '-1':
                l.append((key, value))
                break
            elif key == 'D' and self._steps[key] != value:
                l.append((key, int(value)))
            elif self._steps[key] is not value:
                l.append((key, int(value) - int(self._steps[key])))
        self._steps = newSteps
        if l[0][0] == '-1' or l[0][1] < 2:
            message = b"OK"
        else:
            message = b"Not OK"
            print(f"WARNING: BAD MESSAGE: {l}")
        self._sock.sendto(message, (self._sendIP, self._sendPort))
        return l
    
    def getSteps(self):
        return self._steps
    
if __name__ == "__main__":
    sky = skynet(False, IP_LIST["ANY"], 5005)
    from gpio import gpio, OUTPUT
    g = gpio(4)
    g.setMode(4, OUTPUT)
    print("starting loop")
    while True:
        data = sky.recieve(1)
        if (data == "T"):
            print("running fan")
            g.write(4, 1)
        elif (data == "F"):
            print("stopping fan")
            g.write(4, 0)