from tkinter import *
from tooltip import CreateToolTip

class MemoryView(Frame):
    def __init__(self, master=None, **kw) -> None:
        self.memcellsize = 30
        self.padoff = 4
        self.pagevertical_size = 90
        self.width = self.memcellsize*16 + self.padoff + self.pagevertical_size
        self.height = self.memcellsize*17 + self.padoff
        Frame.__init__(self, master, kw)
        self.memorycells = []
        #memory page
        for i in range(16):
            for j in range(16):
                cell = Label(self, text='00', font=('consolas', 15), highlightthickness=1, highlightbackground='grey')
                cell.place(x=(i+1)*self.memcellsize+self.padoff+(self.pagevertical_size-self.memcellsize), y=(j+1)*self.memcellsize+self.padoff, width=self.memcellsize, height=self.memcellsize ,anchor='nw')
                self.memorycells.append(cell)

        #horizontal offset is same
        self.pagehorizontal = []
        for i in range(16):
            off = Label(self, text=f'{"%01x"%i}', font=('consolas', 15), highlightthickness=1, highlightbackground='grey', foreground='purple')
            off.place(x=(i+1)*self.memcellsize+self.padoff+(self.pagevertical_size-self.memcellsize), y=0, width=self.memcellsize, height=self.memcellsize ,anchor='nw')
            self.pagehorizontal.append(off)

        #vertical offset
        self.pagevertical = []
        self.currentpage = 0
        for i in range(16):
            off = Label(self, text=f'{"0x"+"%03x"%i}', font=('consolas', 15), highlightthickness=1, highlightbackground='grey', foreground='purple')
            off.place(x=0, y=(i+1)*self.memcellsize+self.padoff, width=self.pagevertical_size, height=self.memcellsize ,anchor='nw')
            self.pagevertical.append(off)

        self.bpagelower = Button(self, text='<<', command=self.loadlower)
        self.bpageupper = Button(self, text='>>', command=self.loadupper)
        boffset = 10
        bgap = self.pagevertical_size - self.memcellsize - boffset
        self.bpagelower.place(x=boffset, y=0, width=self.memcellsize, height=self.memcellsize, anchor='nw')
        self.bpageupper.place(x=bgap, y=0, width=self.memcellsize, height=self.memcellsize, anchor='nw')
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