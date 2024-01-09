from tkinter import *

class RegView(Frame):
    def __init__(self, master=None, **kw) -> None:
        Frame.__init__(self, master, kw)
        hoff = 1.0/6
        self.emulator = None
        self.btna = Button(self, text= 'A:00', font=('consolas', 15), state='disabled')
        self.btnf = Button(self, text= 'F:00000000', font=('consolas', 13), state='disabled')
        self.btnb = Button(self, text= 'B:00', font=('consolas', 15), state='disabled')
        self.btnc = Button(self, text= 'C:00', font=('consolas', 15), state='disabled')
        self.btnd = Button(self, text= 'D:00', font=('consolas', 15), state='disabled')
        self.btne = Button(self, text= 'E:00', font=('consolas', 15), state='disabled')
        self.btnh = Button(self, text= 'H:00', font=('consolas', 15), state='disabled')
        self.btnl = Button(self, text= 'L:00', font=('consolas', 15), state='disabled')
        self.btnsp = Button(self, text='SP:0000', font=('consolas', 15), state='disabled')
        self.btnpc = Button(self, text='PC:0000', font=('consolas', 15), state='disabled')
        
        self.btna.place(rely=hoff*0, anchor='nw', relwidth=0.5, relheight=hoff)
        self.btnf.place(rely=hoff*0, relx=0.5, anchor='nw', relwidth=0.5, relheight=hoff)
        self.btnb.place(rely=hoff*1, anchor='nw', relwidth=0.5, relheight=hoff)
        self.btnc.place(rely=hoff*1, relx=0.5, anchor='nw',  relwidth=0.5, relheight=hoff)
        self.btnd.place(rely=hoff*2, anchor='nw', relwidth=0.5, relheight=hoff)
        self.btne.place(rely=hoff*2, relx=0.5, anchor='nw',  relwidth=0.5, relheight=hoff)
        self.btnh.place(rely=hoff*3, anchor='nw', relwidth=0.5, relheight=hoff)
        self.btnl.place(rely=hoff*3, relx=0.5, anchor='nw',  relwidth=0.5, relheight=hoff)
        self.btnsp.place(rely=hoff*4, anchor='nw', relwidth=1, relheight=hoff)
        self.btnpc.place(rely=hoff*5, anchor='nw', relwidth=1, relheight=hoff)

    def setemulator(self, emu):
        self.emulator = emu
        self.refreshpage()
    
    def refreshpage(self):
        if (self.emulator != None):
            self.btna.config(text=f'A:{"%02x"%self.emulator.A.value}')
            self.btnf.config(text=f'F:{self.tobytes(self.emulator.F.value)}')
            self.btnb.config(text=f'B:{"%02x"%self.emulator.B.value}')
            self.btnc.config(text=f'C:{"%02x"%self.emulator.C.value}')
            self.btnd.config(text=f'D:{"%02x"%self.emulator.D.value}')
            self.btne.config(text=f'E:{"%02x"%self.emulator.E.value}')
            self.btnh.config(text=f'H:{"%02x"%self.emulator.H.value}')
            self.btnl.config(text=f'L:{"%02x"%self.emulator.L.value}')
            self.btnsp.config(text=f'SP:{"%04x"%self.emulator.SP.value}')
            self.btnpc.config(text=f'PC:{"%04x"%self.emulator.PC.value}')
    
    def tobytes(self, val):
        byte = val & 0xff
        ret = ""
        for i in range(8):
            ret += f'{((byte&(0x80>>i))>>(7-i))}'
        return ret