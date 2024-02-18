from tkinter import *

class BreakPoint(Button):
    def __init__(self, master=None, cnf={}, **kw):
        Button.__init__(self, master, kw)
        self.config(highlightthickness=0, bd=0)
        self.nline = 0
        self.enabled = False
        self.configure(command=self.clicked)
        self.defaultimg = self['image']
        self.img_breakpoint = self.defaultimg
        self.ba = []
    
    def setlinenoandimg(self, count, img, ba):
        self.ba = ba
        self.nline = count
        self.img_breakpoint = img

    def isset(self):
        return self.enabled
    
    def clicked(self, opt=None):
        if (self.enabled):
            self.configure(image=self.defaultimg)
            if self.nline in self.ba:
                self.ba.remove(self.nline)
        else:
            self.configure(image=self.img_breakpoint)
            self.ba.append(self.nline)
        self.enabled = not self.enabled
    
    def reset(self):
        self.enabled = False
        self.configure(image=self.defaultimg)
        if self.nline in self.ba:
            self.ba.remove(self.nline)