from tkinter import *
from tooltip import CreateToolTip

class MemoryView(Frame):
    def __init__(self, master=None, **kw) -> None:
        Frame.__init__(self, master, kw)

        self.fmemcells = Frame(self)
        self.fmemcells.place(relx=0.1, rely=1.0/17, relwidth=0.9, relheight=1-1.0/17, anchor='nw')
        self.memorycells = []
        #memory page
        for i in range(16):
            for j in range(16):
                cell = Label(self.fmemcells, text='00', highlightthickness=1, highlightbackground='grey', font=('consolas', 12))
                cell.place(relx=(i)*(1.0/16), rely=(j)*(1.0/16), relwidth=1.0/16, relheight=1.0/16 ,anchor='nw')
                self.memorycells.append(cell)

        #horizontal offset is same
        self.fhoff = Frame(self)
        self.fhoff.place(relx=0.1, rely=0, relwidth=0.9, relheight=1.0/17, anchor='nw')
        self.pagehorizontal = []
        for i in range(16):
            off = Label(self.fhoff, text=f'{"%01x"%i}', highlightthickness=1, highlightbackground='grey', foreground='purple', font=('consolas', 12))
            off.place(relx=(i)*(1.0/16), rely=0, relwidth=1.0/16, relheight=1 ,anchor='nw')
            self.pagehorizontal.append(off)

        #vertical offset
        self.fvoff = Frame(self)
        self.fvoff.place(relx=0, rely=1.0/17, relwidth=0.1, relheight=1-1.0/17, anchor='nw')
        self.pagevertical = []
        self.currentpage = 0
        for i in range(16):
            off = Label(self.fvoff, text=f'{"0x"+"%03x"%i}', highlightthickness=1, highlightbackground='grey', foreground='purple', font=('consolas', 12))
            off.place(relx=0, rely=(i)*(1.0/16), relwidth=1, relheight=1.0/16 ,anchor='nw')
            self.pagevertical.append(off)
        self.fbtn = Frame(self)
        self.fbtn.place(relx=0, rely=0, relwidth=0.1, relheight=1.0/17, anchor='nw')
        self.bpagelower = Button(self.fbtn, text='<<', command=self.loadlower, font=('consolas', 12))
        self.bpageupper = Button(self.fbtn, text='>>', command=self.loadupper, font=('consolas', 12))
        self.bpagelower.place(relx=0, rely=0, relwidth=1.0/2.5, relheight=1, anchor='nw')
        self.bpageupper.place(relx=1, rely=0, relwidth=1.0/2.5, relheight=1, anchor='ne')
        CreateToolTip(self.bpagelower, "get memory lower", 35, 35)
        CreateToolTip(self.bpageupper, "get memory upper", 35, 35)
        
        self.updatememorypage(self.currentpage)
        
    def updatememorypage(self, no:int) -> None:
        if (no <= 0 or no <= 255):
            memstart = no*16*16
            for i in range(16):
                self.pagevertical[i].configure(text=f'{"0x"+("%04x"%(memstart+i*16))[0:3]}')
            self.currentpage = no
        else:
            raise Exception("error:invaid memory page!")
        if (self.currentpage == 255):
            self.bpageupper.configure(state='disabled')
            self.bpagelower.configure(state='active')
        elif (self.currentpage == 0):
            self.bpagelower.configure(state='disabled')
            self.bpageupper.configure(state='active')
        else:
            self.bpagelower.configure(state='active')
            self.bpageupper.configure(state='active')

    def loadupper(self) -> None:
        self.updatememorypage(self.currentpage + 1)
    
    def loadlower(self) -> None:
        self.updatememorypage(self.currentpage - 1)