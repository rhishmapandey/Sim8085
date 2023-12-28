from tkinter import *
import json
from tooltip import CreateToolTip
from editor import Editor
from memory import MemoryView
class App():
    def __init__(self, setting:str=None) -> None:
        self.root = Tk()
        self.root.title("Sim8085")
        self.dpiaware()

        self.rootframe = Frame(self.root)
        self.rootframe.place(relx=0, rely=0, relwidth=1, relheight=1, anchor='nw')

        if (not self.loadsettings(setting)):
            print("error loading settings!")
        
        self.simcbntframe = Frame(self.rootframe, width=self.btnc_size*6, height=self.btnc_size)
        self.simcbntframe.pack()

        self.btn_stop = Button(self.simcbntframe, image=self.img_stop, width=self.btnc_size, height=self.btnc_size, command=self.simstop)
        self.btn_stop.pack(side=LEFT)
        CreateToolTip(self.btn_stop, 'stop', self.btn_ospawn, self.btn_ospawn)

        self.btn_start = Button(self.simcbntframe, image=self.img_start, width=self.btnc_size, height=self.btnc_size, command=self.simstart)
        self.btn_start.pack(side=LEFT)
        CreateToolTip(self.btn_start, 'start', self.btn_ospawn, self.btn_ospawn)

        self.btn_pause = Button(self.simcbntframe, image=self.img_pause, width=self.btnc_size, height=self.btnc_size, command=self.simpause)
        self.btn_pause.pack(side=LEFT)
        CreateToolTip(self.btn_pause, 'pause', self.btn_ospawn, self.btn_ospawn)

        self.btn_continue = Button(self.simcbntframe, image=self.img_continue, width=self.btnc_size, height=self.btnc_size, command=self.simcontinue)
        self.btn_continue.pack(side=LEFT)
        CreateToolTip(self.btn_continue, 'continue', self.btn_ospawn, self.btn_ospawn)

        self.btn_stepover = Button(self.simcbntframe, image=self.img_stepover, width=self.btnc_size, height=self.btnc_size, command=self.simstepover)
        self.btn_stepover.pack(side=LEFT)
        CreateToolTip(self.btn_stepover, 'stepover', self.btn_ospawn, self.btn_ospawn)

        self.btn_stepback = Button(self.simcbntframe, image=self.img_stepback, width=self.btnc_size, height=self.btnc_size, command=self.simstepback)
        self.btn_stepback.pack(side=LEFT)
        CreateToolTip(self.btn_stepback, 'stepback', self.btn_ospawn, self.btn_ospawn)

        self.a_simbtn = [self.btn_stop, self.btn_start, self.btn_pause, self.btn_continue, self.btn_stepover, self.btn_stepback]
        for simbtn in self.a_simbtn:
            simbtn.config(state='disabled')
        
        self.btn_start.config(state='active')

        self.feditor = Editor(self.rootframe)
        self.feditor.place(relx=1-0.4, y=self.btnc_size+20, relwidth=0.4, relheight=1, anchor='nw')
        self.feditor.createtag(['MOV', 'MVI', 'STA', 'CALL', 'LXI', 'MVI', 'LDA', 'LDAX', 'STA', 'STAX', 'IN', 'OUT', 'LHLD', 'SHLD', 'XCHG',
                                'ADD', 'ADI', 'SUB', 'SUI', 'INR', 'DCR', 'INX', 'DCX', 'ADC', 'ACI', 'SBB', 'SBI', 'DAD', 'DAA',
                                'ANA', 'ANI', 'ORA', 'ORI', 'XRA', 'XRI', 'CMA', 'CMP', 'CPI', 'RLC', 'RAL', 'RRC', 'RAR', 'CMC', 'STC', 'CMA',
                                'JMP', 'JC', 'JNC', 'JZ', 'JNZ', 'JP', 'JM', 'JPE', 'JPO',
                                'CALL', 'CC', 'CNC', 'CZ', 'CNZ', 'CP', 'CM', 'CPE', 'CPO',
                                'RET', 'RC', 'RNC', 'RZ', 'RNZ', 'RP', 'RM', 'RPE', 'RPO',
                                'RST',
                                'PUSH', 'POP', 'XTHL', 'SPHL', 'PCHL', 'DI', 'EI', 'SIM', 'RIM', 'NOP', 'HLT'], 'ins', foreground='purple')
        self.feditor.createtag(['A', 'PSW', 'B', 'C', 'D', 'E', 'H', 'L', 'SP', 'PC', 'M'], 'reg', foreground='green')
        
        self.fmemview = MemoryView(self.rootframe, background="#f0f5cb")
        self.fmemview.place(x=10, y=self.btnc_size+20, width=self.fmemview.width, height=self.fmemview.height, anchor='nw')
        
        self.celine = 1

    def dpiaware(self) -> None:
        import os
        if (os.name == 'nt'):
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)

    def loadsettings(self, setting:str) -> bool:
        if (setting == None):
            self.root.geometry("1280x720")
            self.root.iconphoto(False, PhotoImage(file="res/icon.png"))
            self.img_stop = PhotoImage(file="res/stop.png")
            self.img_start = PhotoImage(file="res/start.png")
            self.img_continue = PhotoImage(file="res/continue.png")
            self.img_pause = PhotoImage(file="res/pause.png")
            self.img_stepover = PhotoImage(file="res/stepover.png")
            self.img_stepback = PhotoImage(file="res/stepback.png")
            self.img_breakpoint = PhotoImage(file="res/breakpoint.png")
            self.btnc_size = 32
            self.btn_ospawn = 40
            pass
        else:
            pass
        return True
    
    def isopen(self) -> bool:
        try:
            return self.root.winfo_exists()
        except:
            return False

    def mainloop(self) -> None:
        while self.isopen():
            self.root.update()

    def simstop(self) -> None:
        self.feditor.removebreakpoint()
        for simbtn in self.a_simbtn:
            simbtn.config(state='disabled')
        print('simstop called!')
        self.btn_start.config(state='active')
        pass
    
    def simstart(self) -> None:
        print('simstart called!')
        for simbtn in self.a_simbtn:
            simbtn.config(state='active')

        self.btn_start.config(state='disabled')
        self.feditor.updatebreakpoint(self.celine)
        pass

    def simpause(self) -> None:
        print('simpause called!')
        pass

    def simcontinue(self) -> None:
        print('simcontinue called!')
        pass

    def simstepover(self) -> None:
        self.celine += 1
        self.feditor.updatebreakpoint(self.celine)
        print('simstepover called!')
        pass

    def simstepback(self) -> None:
        self.celine -= 1
        self.feditor.updatebreakpoint(self.celine)
        print('simstepback called!')
        pass