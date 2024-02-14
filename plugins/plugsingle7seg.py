from plugininternal import PluginInternal
from tkinter import *
from sevseg import SevSeg
class Plugin(PluginInternal):
    def __init__(self) -> None:
        self.address = 0x67
        self.state = 0x00 # all off
        super().__init__()
    
    def handlein(self, saddr: int, sbyte: int):
        self.sendsignal(0, 0, 0)
    
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
root.title("7seg")

#root.overrideredirect(True)
root.wm_attributes("-topmost", 1)
root.wm_attributes("-alpha", 0.6)

# set geometry(widthxheight)
root.geometry("200x200")
# add widgets
sevseg_1 = SevSeg(root)
sevseg_1.place(relx=0, rely=0, relwidth=1, relheight=1)

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
    root.update()
 
plugin.terminate()
