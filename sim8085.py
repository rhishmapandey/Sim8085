from tkinter import *
from tooltip import CreateToolTip
from editor import Editor
from memory import MemoryView
from emu import assembler, emu8085
from regview import RegView
from threading import Thread, Lock
from tkinter import messagebox
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

        self.btn_pluginconnect = Button(self.simcbntframe, image=self.img_pluginconnect, width=self.btnc_size, height=self.btnc_size, command=self.simpluginconnect)
        self.btn_pluginconnect.pack(side=LEFT)
        CreateToolTip(self.btn_pluginconnect, 'pluginconnect', self.btn_ospawn, self.btn_ospawn)

        self.a_simbtn = [self.btn_stop, self.btn_continue, self.btn_stepover, self.btn_start, self.btn_pause]
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
        
        self.fregview = RegView(self.rootframe, background='white')
        self.fregview.place(relx=0.33, y=self.btnc_size+20, relwidth=0.15, relheight=0.4, anchor='nw')

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

        self.lockexe = Lock()
        self.lockexestatus = Lock()
        self.threadexe:Thread = None

        self.fmemview.setemulator(self.emu)
        self.fregview.setemulator(self.emu)
        self.isneedtostop = False
        self.isexecthreadactive = True
    
        self.wassimstop = False

        self.wasconnected = False
    
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
            self.img_pluginconnect = PhotoImage(file="res/pluginconnect.png")
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
            self.checkexecthread()

    def simstop(self) -> None:
        print('simstop called!')
        self.wassimstop = True
        
        self.lockexe.acquire()
        self.isneedtostop = True
        self.lockexe.release()
        self.feditor.removebreakpoint()
        for simbtn in self.a_simbtn:
            simbtn.config(state='disabled')
        self.btn_start.config(state='active')
        #send a ignore signal to check if plugin is still active
        if (self.wasconnected):
            self.emu.plugin.sendsignal(0xff, 0xff, 0xff)
        if (not self.emu.plugin.isconnected):
            if (self.wasconnected):
                messagebox.showerror("PluginError", "Plugin was disconnected!")
                self.wasconnected = False
            self.btn_pluginconnect.configure(state='active')
        self.feditor.enable()
        # self.threadexe.join()
    
    def simstart(self) -> None:
        print('simstart called!')
        # print('breakpoints at', self.feditor.getbreakpoints())
        self.isneedtostop = False
        self.wassimstop = False
        assemble_status , msg = self.assemblecode()
        if (assemble_status == True):
            self.emu.reset()
            self.emu.loadbinary(self.asmer.pmemory)
            self.emu.setdebuglinescache(self.asmer.dbglinecache)

            self.btn_start.config(state='disabled')
            self.btn_pluginconnect.config(state='disabled')
            self.btn_stop.configure(state='normal')

            self.fmemview.refreshpage()
            self.fregview.refreshpage()
            # print(self.asmer.dbglinecache)

            self.btn_pause.configure(state='normal')
            self.feditor.disable()
            self.threadexe = Thread(target=self.funcexecution)
            self.threadexe.start()

    def simpause(self) -> None:
        self.lockexe.acquire()
        self.isneedtostop = True
        self.lockexe.release()
        print('simpause called!')
        pass

    def simcontinue(self) -> None:
        print('simcontinue called!')

        self.isneedtostop = False
        self.wassimstop = False
        self.btn_stepover.configure(state='disabled')
        self.feditor.removebreakpoint()

        self.threadexe = Thread(target=self.funcexecution, args=(True,))
        self.btn_pause.configure(state='normal')
        self.btn_continue.configure(state='disabled')
        self.threadexe.start()

    def simstepover(self) -> None:
        print('simstepover called!')
        self.emu.runcrntins()
        if (self.emu.haulted):
            self.execerrcallbackhandle(self.emu.wasexecerr)
            self.simstop()
            return
        self.celine = self.emu.getcurrentline()
        self.fmemview.refreshpage()
        self.fregview.refreshpage()
        self.feditor.updatebreakpoint(self.celine)
    

    def simpluginconnect(self) -> None:
        # self.celine -= 1
        # self.feditor.updatebreakpoint(self.celine)
        print('simpluginconnect called!')
        if (self.emu.connectplugin()):
            messagebox.showinfo("PluginConnected", "Plugin was successfully attached!")
            self.btn_pluginconnect.configure(state='disabled')
            self.wasconnected = True
            print('plugin connected')
        else:
            messagebox.showerror("PluginError", "Plugin wasnot able to connect!")
            print('plugin couldnot be connected')

    def updateasmout(self, str="") -> None:
        self.fasmview.configure(state=NORMAL)
        self.fasmview.delete('1.0', END)
        self.fasmview.insert(INSERT, str)
        self.fasmview.configure(state=DISABLED)

    def assemblecode(self) -> list[bool, str]:
        self.asmer.reset()
        state , err = self.asmer.assemble(self.feditor.getlines())
        print(state, err)
        self.asmer.generateasmdump()
        if state == True:
            self.fasmview.configure(foreground='brown')
            self.updateasmout(self.asmer.dbugasm)
        else:
            self.fasmview.configure(foreground='red')
            cerrline = len(self.asmer.plsize)+1
            self.updateasmout(f'line::{str(cerrline) + " " + err}')
        return state, err

    def funcexecution(self, ignorefbreak=False):
        self.lockexe.acquire()
        self.celine = self.emu.getcurrentline()
        while self.emu.haulted == False and ((self.celine not in self.feditor.activebreakpoints) or (ignorefbreak == True)) and not self.isneedtostop:
            self.lockexe.release()
            self.emu.runcrntins()
            self.lockexe.acquire()
            self.celine = self.emu.getcurrentline()
            ignorefbreak = False
        self.lockexe.release()
        print("thread has done executing")
        self.lockexestatus.acquire()
        self.isexecthreadactive = False
        self.lockexestatus.release()
        return
    
    def postexecution(self):
        self.fmemview.refreshpage()
        self.fregview.refreshpage()
        
        if(self.emu.haulted == True):
            self.simstop()
            self.execerrcallbackhandle(self.emu.wasexecerr)
        elif (self.wassimstop == True):
            return
        else:
            self.feditor.updatebreakpoint(self.celine) 
            for simbtn in self.a_simbtn[:-2]:
                simbtn.configure(state='active')
            self.btn_pause.configure(state='disabled')

    def checkexecthread(self):
        self.lockexestatus.acquire()
        status = self.isexecthreadactive
        self.lockexestatus.release()
        if (status == False):
            self.threadexe.join()
            self.postexecution()
            self.isexecthreadactive = True
            print("thread has now joined the main thread")
    
    def teminate(self):
        self.lockexestatus.acquire()
        status = self.isexecthreadactive
        self.lockexestatus.release()
        if (status == True):
            print("terminating running threads!")
            self.lockexe.acquire()
            self.isneedtostop = True
            self.lockexe.release()
            try:
                self.threadexe.join()
            except:
                pass
            print("treminate completed!")
    
    def execerrcallbackhandle(self, err):
        if (err):
            messagebox.showerror("Execution Error", "Program Ran Out Of Scope!")
        else:
            messagebox.showinfo("Success", "Program Execution Was Completed!")
