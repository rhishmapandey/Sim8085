from plugininternal import PluginInternal
from tkinter import *
from sevseg import SevSeg
from dipswitch import DipSwitch

class Plugin(PluginInternal):
    def __init__(self) -> None:
        self.address = 0x67
        self.dipaddress = 0x72
        self.state = 0x00 # all off
        self.dipvalue = 0x00
        super().__init__()
    
    def handlein(self, saddr: int, sbyte: int):
        if (saddr != self.dipaddress):
            print("warning:: invaid address for access!")
            self.sendsignal(0, 0, 0)
            return
        print("info:: read signal recieved at valid address!")
        self.sendsignal(0, 0, self.dipvalue)
    
    def handleout(self, saddr: int, sbyte: int):
        if (saddr != self.address):
            print("warning:: invaid address for access!")
            return
        print("info:: write signal recieved at valid address!")
        self.state = sbyte

def isopen(instance:Tk) -> bool:
    try:
        return instance.winfo_exists()
    except:
        return False

root = Tk()
# root window title and dimension
root.title("dip7seg")

#root.overrideredirect(True)
root.wm_attributes("-topmost", 1)
root.wm_attributes("-alpha", 0.6)

# set geometry(widthxheight)
root.geometry("250x300")
# add widgets
sevseg_1 = SevSeg(root)
sevseg_1.place(relx=0, rely=0, relwidth=1, relheight=0.6)


dips = []

for i in range(8):
    dip = DipSwitch(root)
    dip.place(relx=(1.0/8.0)*i, rely=0.6, relwidth=(1.0/8.0), relheight=0.4)
    dip.setindex(7-i)
    dips.append(dip)

def getdipval():
    val = 0x00
    for i in range(8):
        if (dips[i].isactive):
            val = val | (0x80 >> i)
    return val

#run plugin
plugin = Plugin()
if (not plugin.establishconnection()):
    exit()
plugin.run()


tmpstate = plugin.state
#mainloop
while (isopen(root)):
    if ((not plugin.isconnected) and plugin.wasconnected):
        break
    if (tmpstate != plugin.state):
        tmpstate = plugin.state
        sevseg_1.updatedisplay(tmpstate)
        pass
    plugin.dipvalue = getdipval()
    root.update()
 
plugin.terminate()
