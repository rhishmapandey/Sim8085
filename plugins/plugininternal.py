import socket
from ctypes import c_ubyte
from threading import Thread, Lock
# the socket recieves 3 bytes 
# 1st byte is 0 for in and 2 for out
# 2nd byte contains the port or the address
# 3nd byte finally contains the data

# to implement the plugin you will need to make inherit the PluginInternal as base class then 
# implement your own handle input and handle output functions
class PluginInternal:
    def __init__(self) -> None:
        self.isconnected = False
        self.wasconnected = False
        self.tbclamp:c_ubyte = c_ubyte()
        pass

    def establishconnection(self, port:int=6772) -> bool:
        self.sockserver:socket.socket = socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_STREAM)
        try:
            self.sockserver.bind((socket.gethostbyname("localhost"), port))
            self.sockserver.listen(1)
        except:
            print("plugininternal wasnot able to bind to the port")
            return False
        return True
    
    def tryconnect(self) -> bool:
        try:
            conn, addr = self.sockserver.accept()
            self.sockplug : socket.socket = conn
            # send the isrecieving signal
            if (not self.sendsignal(0, 0, 0)):
                return False
            self.isconnected = True
            self.wasconnected = True
        except:
            print("plugininternal tryconnect failed")
            return False
        return True

    def getclampedbyte(self, val:int) -> int:
        self.tbclamp.value = val
        return self.tbclamp.value

    def sendsignal(self, stype:int, saddr:int, sdata:int) -> bool:
        try:
            self.sockplug.send(bytes([stype, self.getclampedbyte(saddr), self.getclampedbyte(sdata)]))
        except:
            print("plugininteral sendsignal failed")
            self.isconnected = False
            return False
        return True

    def terminate(self):
        self.sockserver.close()
        if (self.wasconnected):
            self.eventthread.join()

    def tick(self) -> bool:
        try:
            rsdat = self.sockplug.recv(3)
            stype:int = rsdat[0]
            saddr:int = rsdat[1]
            sbyte:int = rsdat[2]
            if (stype == 0):
                print("plugininternal out signal recieved")
                self.handleout(saddr, sbyte)
            elif (stype == 1):
                print("plugininternal in signal recieved")
                self.handlein(saddr, sbyte)
            elif (stype == 0xff):
                print("plugininternal ignore signal recieved")
            else:
                print("plugininternal invalid signal recieved")
                return False
        except:
            print ("plugininternal error on tick")
            self.isconnected = False
            return False
        return True

    def __get__events(self):
        if (not self.isconnected):
            if (not self.tryconnect()):
                return
        print("plugininternal connection established!")
        while self.isconnected:
            self.tick()

    def run(self):
        self.eventthread = Thread(target=self.__get__events, args=())
        self.eventthread.start()
        return

    # implement these functions for your plugin
    def handlein(self, saddr:int, sbyte:int):
        pass
    
    def handleout(self, saddr:int, sbyte:int):
        pass
    