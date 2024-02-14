from tkinter import *

class SevSeg(Frame):
    def __init__(self, master=None, **kw) -> None:
        Frame.__init__(self, master, kw)
        # add widgets
        self.a = Label(self,  background="black")
        self.a.place(relx=0.3, rely=0.05, relwidth=0.4, relheight=0.05, anchor="nw")

        self.g = Label(self,  background="black")
        self.g.place(relx=0.3, rely=0.525, relwidth=0.4, relheight=0.05, anchor="sw")

        self.d = Label(self,  background="black")
        self.d.place(relx=0.3, rely=0.95, relwidth=0.4, relheight=0.05, anchor="sw")

        self.f = Label(self,  background="black")
        self.f.place(relx=0.3, rely=0.1075, relwidth=0.05, relheight=0.35, anchor="nw")

        self.b = Label(self,  background="black")
        self.b.place(relx=0.7, rely=0.1075, relwidth=0.05, relheight=0.35, anchor="ne")

        self.e = Label(self,  background="black")
        self.e.place(relx=0.3, rely=0.89025, relwidth=0.05, relheight=0.35, anchor="sw")

        self.c = Label(self,  background="black")
        self.c.place(relx=0.7, rely=0.89025, relwidth=0.05, relheight=0.35, anchor="se")

        self.dp = Label(self,  background="black")
        self.dp.place(relx=0.9, rely=0.9, relwidth=0.05, relheight=0.05)

        self.aleds = [self.a, self.b, self.c, self.d, self.e, self.f, self.g, self.dp]
    
    def updatedisplay(self, state:int):
        tbits = bin(((state | 0xff00) & 0xffff))[10:]
        print(tbits)
        for i in range(8):
            if (tbits[7-i] == '1'):
                self.aleds[i].configure(background='red')
            else:
                self.aleds[i].configure(background='black')
    
    def reset(self):
        for i in range(8):
            self.aleds[i].configure(background='black')