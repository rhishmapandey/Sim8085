from tkinter import *

class DipSwitch(Frame):
    def __init__(self, master=None, **kw) -> None:
        Frame.__init__(self, master, kw, background='black')
        # add widgets
        self.a = Label(self,  background='red')
        self.a.place(relx=0, rely=0, relwidth=1, relheight=1, anchor='nw')
        self.labelon = Label(self, text='ON', background='red', foreground='white')
        self.labelon.place(relwidth=1, relheight=0.25, anchor='nw')
        self.labelindex = Label(self, text='0', background='red', foreground='white')
        self.labelindex.place(rely=0.8, relwidth=1, relheight=0.25, anchor='nw')
        self.miscbg = Label(self,  background='grey')
        self.miscbg.place(relx=0.3, rely=0.35, relwidth=0.4, relheight=0.4, anchor='nw')
        self.butn = Button(self, background='white', command=self.onclick)
        self.butn.place(relx=0.3, rely=0.6, relwidth=0.4, relheight=0.2, anchor='nw')
        self.isactive:bool = False
        self.index = 0
    
    def onclick(self, opt=None):
        if (self.isactive):
            self.isactive = False
            self.butn.place(relx=0.3, rely=0.6, relwidth=0.4, relheight=0.2, anchor='nw')
        else:
            self.isactive = True
            self.butn.place(relx=0.3, rely=0.35, relwidth=0.4, relheight=0.2, anchor='nw')
    
    def setindex(self, index:int):
        self.index = index
        self.labelindex.configure(text=str(index))
    
    def reset(self):
        self.isactive = False
        self.butn.place(relx=0.3, rely=0.6, relwidth=0.4, relheight=0.2, anchor='nw')