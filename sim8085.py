from tkinter import *
import json
from tooltip import CreateToolTip
from editor import Editor
from memory import MemoryView
from emu import assembler, emu8085
from regview import RegView

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
        self.feditor.place(relx=1-0.5, y=self.btnc_size+20, relwidth=0.5, relheight=1, anchor='nw')
        self.feditor.createtag(['MOV', 'MVI', 'STA', 'CALL', 'LXI', 'MVI', 'LDA', 'LDAX', 'STA', 'STAX', 'IN', 'OUT', 'LHLD', 'SHLD', 'XCHG',
                                'ADD', 'ADI', 'SUB', 'SUI', 'INR', 'DCR', 'INX', 'DCX', 'ADC', 'ACI', 'SBB', 'SBI', 'DAD', 'DAA',
                                'ANA', 'ANI', 'ORA', 'ORI', 'XRA', 'XRI', 'CMA', 'CMP', 'CPI', 'RLC', 'RAL', 'RRC', 'RAR', 'CMC', 'STC',
                                'JMP', 'JC', 'JNC', 'JZ', 'JNZ', 'JP', 'JM', 'JPE', 'JPO',
                                'CALL', 'CC', 'CNC', 'CZ', 'CNZ', 'CP', 'CM', 'CPE', 'CPO',
                                'RET', 'RC', 'RNC', 'RZ', 'RNZ', 'RP', 'RM', 'RPE', 'RPO',
                                'RST',
                                'PUSH', 'POP', 'XTHL', 'SPHL', 'PCHL', 'DI', 'EI', 'SIM', 'RIM', 'NOP', 'HLT'], 'ins', foreground='purple')
        self.feditor.createtag(['A', 'PSW', 'B', 'C', 'D', 'E', 'H', 'L', 'SP', 'PC', 'M'], 'reg', foreground='blue')
        self.feditor.twidget.insert(INSERT, 'hlt')

        self.fmemview = MemoryView(self.rootframe)
        self.fmemview.place(relx=0, y=self.btnc_size+20, relwidth=0.325, relheight=0.4, anchor='nw')
        
        self.regview = RegView(self.rootframe, background='white')
        self.regview.place(relx=0.33, y=self.btnc_size+20, relwidth=0.15, relheight=0.4, anchor='nw')

        self.celine = 1

        self.fasmview = Text(self.rootframe, font=('consolas', 14), wrap='none')
        self.fasmview.configure(state=DISABLED)
        self.fasmview.place(relx=0, rely=1, relwidth=0.325, relheight=0.5, anchor='sw')
        
        # Create scrollbars
        self.xscrollbar = Scrollbar(self.rootframe, orient=HORIZONTAL, command=self.fasmview.xview)
        self.xscrollbar.place(rely=1, relwidth=0.325, anchor='sw')
        self.yscrollbar = Scrollbar(self.rootframe, orient=VERTICAL, command=self.fasmview.yview)
        self.yscrollbar.place(relx= 0.325, rely=1, relheight=0.5, anchor='sw')

        # Attach canvas to scrollbars
        self.fasmview.configure(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set, foreground='brown')

        self.asmer = assembler()
        self.emu = emu8085()

        self.fmemview.setemulator(self.emu)
        self.regview.setemulator(self.emu)

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
        print('simstop called!')
        self.feditor.removebreakpoint()
        for simbtn in self.a_simbtn:
            simbtn.config(state='disabled')
        self.btn_start.config(state='active')
        self.feditor.enable()
        pass
    
    def simstart(self) -> None:
        print('simstart called!')
        # print('breakpoints at', self.feditor.getbreakpoints())
        self.assemblecode()
        self.emu.reset()
        self.emu.loadbinary(self.asmer.pmemory)
        self.emu.setdebuglinescache(self.asmer.dbglinecache)

        self.fmemview.refreshpage()
        self.regview.refreshpage()
        # print(self.asmer.dbglinecache)
        for simbtn in self.a_simbtn:
            simbtn.config(state='active')

        self.feditor.disable()
        self.btn_start.config(state='disabled')
        self.celine = self.emu.getcurrentline()
        self.feditor.updatebreakpoint(self.celine)
        pass

    def simpause(self) -> None:
        print('simpause called!')
        pass

    def simcontinue(self) -> None:
        print('simcontinue called!')
        pass

    def simstepover(self) -> None:
        print('simstepover called!')
        self.emu.runcrntins()
        if (self.emu.haulted):
            self.simstop()
            return
        self.celine = self.emu.getcurrentline()
        self.fmemview.refreshpage()
        self.regview.refreshpage()
        self.feditor.updatebreakpoint(self.celine)
    

    def simstepback(self) -> None:
        self.celine -= 1
        self.feditor.updatebreakpoint(self.celine)
        print('simstepback called!')
        pass

    def updateasmout(self, str="") -> None:
        self.fasmview.configure(state=NORMAL)
        self.fasmview.delete('1.0', END)
        self.fasmview.insert(INSERT, str)
        self.fasmview.configure(state=DISABLED)

    def assemblecode(self) -> (bool, str):
        self.asmer.reset()
        state , err = self.asmer.assemble(self.feditor.getlines())
        print(state, err)
        self.asmer.generateasmdump()
        self.updateasmout(self.asmer.dbugasm)
        return state, err