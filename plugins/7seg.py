from plugininternal import PluginInternal
from tkinter import *

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
# set geometry(widthxheight)
root.geometry("200x200")
# add widgets
a = Label(background="black")
a.place(relx=0.3, rely=0.05, relwidth=0.4, relheight=0.05, anchor="nw")

g = Label(background="black")
g.place(relx=0.3, rely=0.525, relwidth=0.4, relheight=0.05, anchor="sw")

d = Label(background="black")
d.place(relx=0.3, rely=0.95, relwidth=0.4, relheight=0.05, anchor="sw")

f = Label(background="black")
f.place(relx=0.3, rely=0.1075, relwidth=0.05, relheight=0.35, anchor="nw")

b = Label(background="black")
b.place(relx=0.7, rely=0.1075, relwidth=0.05, relheight=0.35, anchor="ne")

e = Label(background="black")
e.place(relx=0.3, rely=0.89025, relwidth=0.05, relheight=0.35, anchor="sw")

c = Label(background="black")
c.place(relx=0.7, rely=0.89025, relwidth=0.05, relheight=0.35, anchor="se")

dp = Label(background="black")
dp.place(relx=0.9, rely=0.9, relwidth=0.05, relheight=0.05)

aleds = [a, b, c, d, e, f, g, dp]

def updatedisplay(state:int):
    tbits = bin(((state | 0xff00) & 0xffff))[10:]
    print(tbits)
    for i in range(8):
        if (tbits[7-i] == '1'):
            aleds[i].configure(background='red')
        else:
            aleds[i].configure(background='black')

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
        updatedisplay(tmpstate)
        pass
    root.update()
 
plugin.terminate()