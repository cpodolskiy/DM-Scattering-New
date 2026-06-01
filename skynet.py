import socket
import json


IP_LIST = {"pi" : "10.157.16.245", "raspberrypi" : "10.248.52.167", "shortcake" : "10.248.35.248", "ANY" : "0.0.0.0"}
#pi and raspberry pi are the two pi 4s, shortcake is the pi 5, and ANY will let it recieve from any IP
TIMEOUT = socket.timeout

class skynet:
    
    def __init__(self, host, IP, port, sim=False, receiveIP=IP_LIST["ANY"], receivePort=5560):
        self._host = host
        self._UDP_IP = IP
        self._UDP_Port = port
        
        self._receiveIP = receiveIP
        self._receivePort = receivePort
        
        self._steps = {1 : 0, 2 : 0, 4 : 0, 8 : 0, 'D' : 0, -1 : ["A"]}
        
        if not sim:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
            # if not self._host:
            self._sock.settimeout(1)
            self._sock.bind((self._receiveIP, self._receivePort))
        self._sim = sim
    
    def send(self, message):
        if not self._sim:
            self._sock.sendto(message, (self._UDP_IP, self._UDP_Port))
        else:
            print(f"pretending to send data: {message}")
        
    def receive(self, buffer):
        if not self._sim:
            data, addr = self._sock.recvfrom(buffer)
            return data.decode()
        else:
            return "in sim"
        
    def updateSteps(self, full=0, half=0, quarter=0, eighth=0, direction=-1, other=["A"]):
        self._steps[1] += full
        self._steps[2] += half
        self._steps[4] += quarter
        self._steps[8] += eighth
        if direction != -1:
            self._steps['D'] = direction
        self._steps[-1] = other
        
    def sendSteps(self):
        data = json.dumps(self._steps).encode('utf-8')
       
        for i in range(5):
            try:
                self._sock.sendto(data, (self._UDP_IP, self._UDP_Port))
                message = self.receive(10)#could add logging here
                return message == "OK"
            except TIMEOUT:
                print("timeout occured in skynet.py")
                #print(self._UDP_IP)
                #print(self._UDP_Port)
        return False
    def receiveSteps(self, buffer):
        data, addr = self._sock.recvfrom(buffer)
        newSteps = json.loads(data.decode())
        l = []
        for key, value in self._steps.items():
            if newSteps[key] is not value:
                l.append((key, value - newSteps))
        self._steps = newSteps
        return l
    
if __name__ == "__main__":
    sky = skynet(True, IP_LIST["raspberrypi"], 5005)
    import time
    print("starting loop")
    count = 1
    while True:
        count += 1
        if count % 2 == 1:
            sky.send(b"T")
        else:
            sky.send(b"F")

# recieving code example   
# if __name__ == "__main__":
#     sky = skynet(False, IP_LIST["ANY"], 5005)
#     from gpio import gpio, OUTPUT
#     g = gpio(4)
#     g.setMode(4, OUTPUT)
#     print("starting loop")
#     while True:
#         data = sky.recieve(1)
#         if (data == "T"):
#             print("running fan")
#             g.write(4, 1)
#         elif (data == "F"):
#             print("stopping fan")
#             g.write(4, 0)C