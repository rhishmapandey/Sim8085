from tkinter import *

class Editor(Text):
    def __init__(self, master=None, **kw) -> None:
        Text.__init__(self, master, kw)
        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        
        self.configure(font=('consolas', 15))
        self.insert(INSERT, 'HLT')
        self.tags = []
        self.bind('<<TextModified>>', self.textmodifiedcallback)
        self.tlines = self.get('1.0', 'end').split('\n')
        self.tag_configure("breakpoint", background='red')

    def calculatetags(self, loffstart:int=0, loffend:int=None) -> None:
        up_str = f'{loffstart+1}.0'
        up_end = 'end'
        if (loffend != None):
            up_end = f'{loffend}.0 lineend'
        
        for id, siders in self.tags:
            self.tag_remove(id, up_str, up_end)

        lines = (self.get('1.0', 'end').split('\n'))
        lines = lines[loffstart:loffend]
        lc = loffstart
        for line in lines:
            lc += 1
            line = line.upper()
            for t_id, t_idnstrs in self.tags:
                for idnstr in t_idnstrs:
                    tl = line
                    l = tl.find(idnstr)
                    to = 0
                    while  (l != -1):
                        tl = tl[(l+len(idnstr)):]
                        if (to+l == 0):
                            if (len(idnstr) == len(line)):
                                self.tag_add(t_id, f'{lc}.{to+l}', f'{lc}.{to+l+len(idnstr)}')
                            elif (line[len(idnstr)] == ' ' or line[len(idnstr)] == ','):
                                self.tag_add(t_id, f'{lc}.{to+l}', f'{lc}.{to+l+len(idnstr)}')
                        elif (to+l == len(line)-len(idnstr) and (line[to+l-1] == " " or line[to+l-1] == ",")):
                            self.tag_add(t_id, f'{lc}.{to+l}', f'{lc}.{to+l+len(idnstr)}')
                        elif ((line[to+l-1] == ' ' or line[to+l-1] == ',')and (line[to+l+len(idnstr)] == ' ' or line[to+l+len(idnstr)] == ',')):
                            self.tag_add(t_id, f'{lc}.{to+l}', f'{lc}.{to+l+len(idnstr)}')
                        to += l + len(idnstr)
                        l = tl.find(idnstr)

    def createtag(self, tag_idnstrs, tag_id, **kw) -> None:
        self.tag_configure(tag_id, kw)
        self.tags.append((tag_id, tag_idnstrs))
        self.calculatetags()

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)
        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")
        return result

    def textmodifiedcallback(self, event=None) -> None:
        _tmp_lines = self.tlines
        self.tlines = self.get('1.0', 'end').split('\n')
        clines = len(_tmp_lines)
        if (clines > len(self.tlines)):
            clines = len(self.tlines)
        ul_start = 0
        ubool = False
        for i in range(clines):
            if (_tmp_lines[i] == self.tlines[i]):
                    if(ubool):
                        #print(f'updated tags from line {ul_start} to {i}.\n')
                        self.calculatetags(ul_start, i)
                    ul_start = i+1
                    ubool = False
            else:
                ubool = True
    
    def updatebreakpoint(self, line:int) -> None:
        self.removebreakpoint()
        self.tag_add('breakpoint', f'{line}.0', f'{line}.0 lineend')

    def removebreakpoint(self) -> None:
        self.tag_remove('breakpoint', '1.0', 'end')