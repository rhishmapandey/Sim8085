import socket
from ctypes import c_ubyte
# the socket recieves 3 bytes 
# 1st byte is 0 for in and 2 for out
# 2nd byte contains the port or the address
# 3nd byte finally contains the data

class PluginExternal:
    def __init__(self) -> None:
        self.isconnected = False
        self.tbclamp:c_ubyte = c_ubyte()
    
    def tryconnect(self, port:int=6772) -> bool:
        try:
            self.sockplug : socket.socket = socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_STREAM)
            self.sockplug.connect((socket.gethostbyname('localhost'), port))
            self.recvsignal()
            self.isconnected = True
        except:
            print("pluginexternal tryconnect failed")
            return False
        return True

    def getclampedbyte(self, val:int) -> int:
        self.tbclamp.value = val
        return self.tbclamp.value

    def sendsignal(self, stype:int, saddr:int, sdata:int) -> bool:
        try:
            self.sockplug.send(bytes([self.getclampedbyte(stype), self.getclampedbyte(saddr), self.getclampedbyte(sdata)]))
        except:
            print("pluginexternal sendsignal failed")
            self.isconnected = False
            return False
        return True
    

    def terminate(self):
        self.sockplug.close()

    def recvsignal(self) -> list[bool, int, int, int]:
        try:
            rsdat = self.sockplug.recv(3)
            stype:int = rsdat[0]
            saddr:int = rsdat[1]
            sbyte:int = rsdat[2]
            return True, stype, saddr, sbyte
        except:
            print ("pluginexternal error on tick")
            self.isconnected = False
            return False, 0, 0, 0

    def inport(self, _saddr:int) -> list [bool, int]:
        self.sendsignal(1, _saddr, 0)
        stat, stype, saddr, sdata = self.recvsignal()
        if (not stat):
            print("pluginexternal inport malfunctioned")
        return stat, sdata
    
    def outport(self, saddr:int, sdata:int) -> bool:
        self.sendsignal(0, saddr, sdata)