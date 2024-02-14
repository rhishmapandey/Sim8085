from plugininternal import PluginInternal
from tkinter import *
from sevseg import SevSeg

## the higher nibble controls the states the selection
## byte 0 (if 0 the date represents the lowernibble, if 1 higher) for the selected digit
## remaining bits 000-100 (select the display)
## remaining bits if 111 (its update)
## the lower nibble contains the data

class Plugin(PluginInternal):
    def __init__(self) -> None:
        self.address = 0x67
        self.states = [0x00, 0x00, 0x00, 0x00, 0x00] # all off
        self.shouldupdate = False
        super().__init__()
    
    def handlein(self, saddr: int, sbyte: int):
        self.sendsignal(0, 0, 0)
    
    def handleout(self, saddr: int, sbyte: int):
        if (saddr != self.address):
            print("warning:: invaild address for access!")
            return
        print("info:: write signal recieved at valid address!")
        ln = (sbyte&0x0f)
        ns = (sbyte&0x80)>>4
        leds = (sbyte&0x70)>>4
        if (leds == 0x7):
            self.shouldupdate = 1
            return
        if (leds < 5):
            if (ns == 0):
                self.states[leds] = (self.states[leds] & 0xf0) | ln
            else:
                self.states[leds] = (self.states[leds] & 0x0f) | (ln<<4)
        else:
            print("warning:: invaild led select")


def isopen(instance:Tk) -> bool:
    try:
        return instance.winfo_exists()
    except:
        return False

root = Tk()
# root window title and dimension
root.title("five7seg")
# set geometry(widthxheight)
root.geometry("520x120")
# add widgets
segframe = Frame(root)
segframe.place(relx=0, rely=0, relwidth=1, relheight=1, anchor='nw')

sevseg_1 = SevSeg(segframe, width=100, height=100)
sevseg_1.pack(side="left")

sevseg_2 = SevSeg(segframe, width=100, height=100)
sevseg_2.pack(side="left")

sevseg_3 = SevSeg(segframe, width=100, height=100)
sevseg_3.pack(side="left")

sevseg_4 = SevSeg(segframe, width=100, height=100)
sevseg_4.pack(side="left")

sevseg_5 = SevSeg(segframe, width=100, height=100)
sevseg_5.pack(side="left")

d7leds = [sevseg_1, sevseg_2, sevseg_3, sevseg_4, sevseg_5]

#run plugin
plugin = Plugin()

#reset
def reset():
    for i in range(5):
        d7leds[i].reset()

#update
def update():
    for i in range(5):
        d7leds[i].updatedisplay(plugin.states[i])

if (not plugin.establishconnection()):
    exit()
plugin.run()
#mainloop
while (isopen(root)):
    if (plugin.shouldupdate):
        update()
        plugin.shouldupdate = False
    root.update()
 
plugin.terminate()