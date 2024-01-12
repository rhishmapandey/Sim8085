from ctypes import *
from enum import Enum

_opcodes = ['MOV', 'MVI', 'STA', 'CALL', 'LXI', 'MVI', 'LDA', 'LDAX', 'STA', 'STAX', 'IN', 'OUT', 'LHLD', 'SHLD', 'XCHG',
                                'ADD', 'ADI', 'SUB', 'SUI', 'INR', 'DCR', 'INX', 'DCX', 'ADC', 'ACI', 'SBB', 'SBI', 'DAD', 'DAA',
                                'ANA', 'ANI', 'ORA', 'ORI', 'XRA', 'XRI', 'CMA', 'CMP', 'CPI', 'RLC', 'RAL', 'RRC', 'RAR', 'CMC', 'STC',
                                'JMP', 'JC', 'JNC', 'JZ', 'JNZ', 'JP', 'JM', 'JPE', 'JPO',
                                'CALL', 'CC', 'CNC', 'CZ', 'CNZ', 'CP', 'CM', 'CPE', 'CPO',
                                'RET', 'RC', 'RNC', 'RZ', 'RNZ', 'RP', 'RM', 'RPE', 'RPO',
                                'RST',
                                'PUSH', 'POP', 'XTHL', 'SPHL', 'PCHL', 'DI', 'EI', 'SIM', 'RIM', 'NOP', 'HLT']

_regs = ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'M']
_reg_misc = ['PSW', 'SP', 'PC']


_inc_sbarg  = {'ACI' : 0xCE, 'ADI' : 0xC6, 'ANI' : 0xE6, 'CPI' : 0xFE, 'IN' : 0xDB, 'ORI': 0xF6, 'OUT' : 0xD3, 'SBI' : 0xDE, 'SUI' : 0xD6, 'XRI' : 0xEE}

_inc_sdarg  = {'LDA' : 0x3A, 'LHLD' : 0x2A, 'SHLD' : 0x22, 'STA' : 0x32}


_inc_srt1arg  = {'ADC' : 0x88, 'ADD' : 0x80, 'ANA' : 0xA0, 'CMP' : 0xB8, 'ORA' : 0xB0, 'SBB' : 0x98, 'SUB':0x90, 'XRA' : 0xA8}

_inc_srt2arg  = {'DCR' : 0x05, 'INR' : 0x04}

_inc_slarg  = {'CALL' : 0xCD, 'CC' : 0xDC, 'CM'  : 0xFC, 'CNC' : 0xD4, 'CNZ' : 0xC4, 'CP' : 0xF4, 'CPE' : 0xEC, 'CPO' : 0xE4, 'CZ' : 0xCC,
               'JC' : 0xDA, 'JM' : 0xFA, 'JMP' : 0xC3, 'JNC' : 0xD2, 'JNZ' : 0xC2, 'JP' : 0xF2, 'JPE' : 0xEA, 'JPO' : 0xE2, 'JZ' : 0xCA}
_inc_narg   = {'CMA' : 0x2F, 'CMC' : 0x3F, 'DAA' : 0x27, 'DI' : 0xF3, 'EI' : 0xFB, 'HLT' : 0x76, 'PCHL' : 0xE9, 'RAL' : 0x17, 'RAR' : 0x1F,
                'RC' : 0xD8, 'RET' : 0xC9, 'RIM' : 0x20, 'RLC' : 0x07, 'RM' : 0xF8, 'RNC' : 0xD0, 'RNZ' : 0xC0, 'RP' : 0xF0, 'RPE' : 0xE8,
                'RPO' : 0xE0, 'RRC' : 0x0F, 'RZ' : 0xC8, 'SIM' : 0x30, 'SPHL' : 0xF9, 'STC' : 0x37, 'XCHG' : 0xEB, 'XTHL' : 0xE3, 'NOP' : 0x00}

_inc_srpt3arg = {'DAD' : 0x09, 'DCX' : 0x0B, 'INX' : 0x03}
_inc_srpt3regs = ['B', 'D', 'H', 'SP']

_inc_srpt4arg = {'POP' : 0xC1, 'PUSH' : 0xC5}
_inc_srpt4regs = ['B', 'D', 'H', 'PSW']

_inc_srpt5arg = {'LDAX' : 0x0A, 'STAX' : 0x02}
_inc_srpt5regs = ['B', 'D']


class LexTag(Enum):
    REG      = 0
    REG_MISC = 1
    OPCODE   = 2
    DBYTE    = 3
    DSHORT   = 4
    DSTRING  = 5
    SCOMMA   = 6
    SCOLON   = 7
        
#please for the sake of god remove comments and unnessary junk adios
def misc_getele(line:str) -> list:
    nws = line.split()
    ret = []
    if (nws == []):
        return ret
    for l in nws:
        start = 0
        for i in range(len(l)):
            if (l[i] == ','):
                if (start < i):
                    ret.append(l[start:i])
                ret.append(',')
                start = i+1
            elif (l[i] == ':'):
                if (start < i):
                    ret.append(l[start:i])
                ret.append(':')
                start = i+1
        if (start < len(l)):
            ret.append(l[start:i+1])
    return ret      

class emu8085:
    def __init__(self) -> None:
        self.memory = []
        self.ploadaddress = c_ushort()
        self.ploadaddress.value = 0x0800

        self.A = c_ubyte()
        self.F = c_ubyte()
        self.B = c_ubyte()
        self.C = c_ubyte()
        self.D = c_ubyte()
        self.E = c_ubyte()
        self.H = c_ubyte()
        self.L = c_ubyte()

        self.SP = c_ushort()
        self.PC = c_ushort()

        self.dbglinecache = []

        self.haulted = False
        for i in range(0xffff+1):
            self.memory.append(c_ubyte())
        self.reset()
    
    def reset(self) -> None:
        for cell in self.memory:
            cell.value = 0x76
        
        self.A.value =0x00
        self.F.value =0x00
        self.B.value =0x00
        self.C.value =0x00
        self.D.value =0x00
        self.E.value =0x00
        self.H.value =0x00
        self.L.value =0x00

        self.SP.value = 0xffff
        self.PC.value = self.ploadaddress.value

        self.haulted = False

        self.dbglinecache = []

    def setdebuglinescache(self, cache) -> None:
        self.dbglinecache = cache
    
    def getcurrentline(self) -> int:
        if self.haulted == False:
            try:
                return self.dbglinecache[self.PC.value - self.ploadaddress.value]
            except:
                print("exeception encountered while getting current binary line program ran out of scope!")
                self.haulted = True
        else:
            return 1

    def loadbinary(self, binary) -> None:
        boff = 0
        for bbyte in binary:
            self.memory[self.ploadaddress.value+boff].value = bbyte
            boff += 1
    
    def pop(self) -> int:
        self.SP.value = self.SP.value+1
        bval = self.memory[self.SP.value].value
        return bval
    
    def push(self, bval:int) -> None:
        self.memory[self.SP.value].value = bval
        self.SP.value = self.SP.value-1

    def runcrntins(self):
        if (self.haulted == True):
            Exception('cpu cannot process instruction haulted!')
            return
        ins = self.memory[self.PC.value].value
        self.incpc() #program counter inc for opcode read
        # #hlt
        # if(ins == 0x76):
        #     self.haulted = True
        #     return
        
        #nop
        if(ins == 0x00):
            return
        #mov b, r/m
        elif(ins & 0xF8 == 0x40):
            sreg = ins - 0x40
            match sreg:
                case 0x0:
                    tval = self.B.value
                    self.B.value = tval
                case 0x1:
                    tval = self.C.value
                    self.B.value = tval
                case 0x2:
                    tval = self.D.value
                    self.B.value = tval
                case 0x3:
                    tval = self.E.value
                    self.B.value = tval
                case 0x4:
                    tval = self.H.value
                    self.B.value = tval
                case 0x5:
                    tval = self.L.value
                    self.B.value = tval
                case 0x6:
                    tval = self.getM()
                    self.B.value = tval
                case 0x7:
                    tval = self.A.value
                    self.B.value = tval
            return
        #mov c, r/m
        elif(ins & 0xF8 == 0x48):
            sreg = ins - 0x48
            match sreg:
                case 0x0:
                    tval = self.B.value
                    self.C.value = tval
                case 0x1:
                    tval = self.C.value
                    self.C.value = tval
                case 0x2:
                    tval = self.D.value
                    self.C.value = tval
                case 0x3:
                    tval = self.E.value
                    self.C.value = tval
                case 0x4:
                    tval = self.H.value
                    self.C.value = tval
                case 0x5:
                    tval = self.L.value
                    self.C.value = tval
                case 0x6:
                    tval = self.getM()
                    self.C.value = tval
                case 0x7:
                    tval = self.A.value
                    self.C.value = tval
            return
        #mov d, r/m
        elif(ins & 0xF8 == 0x50):
            sreg = ins - 0x50
            match sreg:
                case 0x0:
                    tval = self.B.value
                    self.D.value = tval
                case 0x1:
                    tval = self.C.value
                    self.D.value = tval
                case 0x2:
                    tval = self.D.value
                    self.D.value = tval
                case 0x3:
                    tval = self.E.value
                    self.D.value = tval
                case 0x4:
                    tval = self.H.value
                    self.D.value = tval
                case 0x5:
                    tval = self.L.value
                    self.D.value = tval
                case 0x6:
                    tval = self.getM()
                    self.D.value = tval
                case 0x7:
                    tval = self.A.value
                    self.D.value = tval 
            return
        #mov e, r/m
        elif(ins & 0xF8 == 0x58):
            sreg = ins - 0x58
            match sreg:
                case 0x0:
                    tval = self.B.value
                    self.E.value = tval
                case 0x1:
                    tval = self.C.value
                    self.E.value = tval
                case 0x2:
                    tval = self.D.value
                    self.E.value = tval
                case 0x3:
                    tval = self.E.value
                    self.E.value = tval
                case 0x4:
                    tval = self.H.value
                    self.E.value = tval
                case 0x5:
                    tval = self.L.value
                    self.E.value = tval
                case 0x6:
                    tval = self.getM()
                    self.E.value = tval
                case 0x7:
                    tval = self.A.value
                    self.E.value = tval
            return
        #mov h, r/m
        elif(ins & 0xF8 == 0x60):
            sreg = ins - 0x60
            match sreg:
                case 0x0:
                    tval = self.B.value
                    self.H.value = tval
                case 0x1:
                    tval = self.C.value
                    self.H.value = tval
                case 0x2:
                    tval = self.D.value
                    self.H.value = tval
                case 0x3:
                    tval = self.E.value
                    self.H.value = tval
                case 0x4:
                    tval = self.H.value
                    self.H.value = tval
                case 0x5:
                    tval = self.L.value
                    self.H.value = tval
                case 0x6:
                    tval = self.getM()
                    self.H.value = tval
                case 0x7:
                    tval = self.A.value
                    self.H.value = tval
            return
        #mov l, r/m
        elif(ins & 0xF8 == 0x68):
            sreg = ins - 0x68
            match sreg:
                case 0x0:
                    tval = self.B.value
                    self.L.value = tval
                case 0x1:
                    tval = self.C.value
                    self.L.value = tval
                case 0x2:
                    tval = self.D.value
                    self.L.value = tval
                case 0x3:
                    tval = self.E.value
                    self.L.value = tval
                case 0x4:
                    tval = self.H.value
                    self.L.value = tval
                case 0x5:
                    tval = self.L.value
                    self.L.value = tval
                case 0x6:
                    tval = self.getM()
                    self.L.value = tval
                case 0x7:
                    tval = self.A.value
                    self.L.value = tval
            return
        #mov m, r/m
        elif(ins & 0xF8 == 0x70):
            sreg = ins - 0x70
            match sreg:
                case 0x0:
                    tval = self.B.value
                    self.setM(tval)
                case 0x1:
                    tval = self.C.value
                    self.setM(tval)
                case 0x2:
                    tval = self.D.value
                    self.setM(tval)
                case 0x3:
                    tval = self.E.value
                    self.setM(tval)
                case 0x4:
                    tval = self.H.value
                    self.setM(tval)
                case 0x5:
                    tval = self.L.value
                    self.setM(tval)
                case 0x6:
                    self.haulted = True
                case 0x7:
                    tval = self.A.value
                    self.setM(tval)
            return
        #mov a, r/m
        elif(ins & 0xF8 == 0x78):
            sreg = ins - 0x78
            match sreg:
                case 0x0:
                    tval = self.B.value
                    self.A.value = tval
                case 0x1:
                    tval = self.C.value
                    self.A.value = tval
                case 0x2:
                    tval = self.D.value
                    self.A.value = tval
                case 0x3:
                    tval = self.E.value
                    self.A.value = tval
                case 0x4:
                    tval = self.H.value
                    self.A.value = tval
                case 0x5:
                    tval = self.L.value
                    self.A.value = tval
                case 0x6:
                    tval = self.getM()
                    self.A.value = tval
                case 0x7:
                    tval = self.A.value
                    self.A.value = tval
            return
        #mvi r/m, db
        elif((ins & 0xCF == 0x06) or (ins & 0xCF == 0x0E)):
            # print('pass')
            sreg = ((ins & 0x30)>>3) + ((ins & 0x08)>>3)
            # print(hex(sreg))
            tval = self.memory[self.PC.value].value
            self.incpc()
            match sreg:
                case 0x0:
                    self.B.value = tval
                case 0x1:
                    self.C.value = tval
                case 0x2:
                    self.D.value = tval
                case 0x3:
                    self.E.value = tval
                case 0x4:
                    self.H.value = tval
                case 0x5:
                    self.L.value = tval
                case 0x6:
                    self.setM(tval)
                case 0x7:
                    self.A.value = tval
            return
        #lxi rp, ds
        elif((ins & 0xCF) == 0x01):
            print('pass')
            sreg = ins>>4
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            match sreg:
                case 0x0:
                    self.B.value = hval
                    self.C.value = lval
                case 0x1:
                    self.D.value = hval
                    self.E.value = lval
                case 0x2:
                    self.H.value = hval
                    self.L.value = lval
                case 0x7:
                    self.SP.value = ((hval<<8)+lval)
            return
        #lda ds
        elif (ins == 0x3A):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            self.A.value = self.memory[(hval<<8) + lval].value
            return
        #ldax b
        elif (ins == 0x0A):
            self.A.value = self.memory[(self.B.value<<8) + self.C.value].value
            return
        #ldax d
        elif (ins == 0x1A):
            self.A.value = self.memory[(self.D.value<<8) + self.E.value].value
            return
        #sta ds
        elif (ins == 0x32):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            self.memory[(hval<<8) + lval].value = self.A.value
            return
        #stax b
        elif (ins == 0x02):
            self.memory[(self.B.value<<8) + self.C.value].value = self.A.value
            return
        #stax d
        elif (ins == 0x12):
            self.memory[(self.D.value<<8) + self.E.value].value = self.A.value
            return
        #in db
        elif (ins == 0xDB):
            self.incpc()
            return
        #out db
        elif (ins == 0xD3):
            self.incpc()
            return
        #lhld ds
        elif (ins == 0x2A):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            self.L.value = self.memory[(hval<<8) + lval].value 
            self.H.value = self.memory[(hval<<8) + lval+1].value 
            return
        #shld ds
        elif (ins == 0x22):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            self.memory[(hval<<8) + lval].value = self.L.value
            self.memory[(hval<<8) + lval+1].value = self.H.value
        #xchg
        elif (ins == 0xEB):
            tmp = self.H.value
            self.H.value = self.D.value
            self.D.value = tmp
            tmp = self.L.value
            self.L.value = self.E.value
            self.E.value = tmp
        #add r
        elif (ins & 0xF8 == 0x80):
            sreg = ins - 0x80
            opval = 0
            match sreg:
                case 0x0:
                    opval = self.B.value
                case 0x1:
                    opval = self.C.value
                case 0x2:
                    opval = self.D.value
                case 0x3:
                    opval = self.E.value
                case 0x4:
                    opval = self.H.value
                case 0x5:
                    opval = self.L.value
                case 0x6:
                    opval = self.getM()
                case 0x7:
                    opval = self.A.value
            fval = self.A.value + opval
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(self.iscaseauxcarry(opval, self.A.value))
            self.setparityflag(fval)
            if (fval>0xff): self.setcarryflag(1)
            self.A.value = fval
            return
        #adi db
        elif (ins == 0xC6):
            opval = self.memory[self.PC.value].value
            self.incpc()
            fval = self.A.value + opval
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(self.iscaseauxcarry(opval, self.A.value))
            self.setparityflag(fval)
            print(fval)
            if (fval>0xff): self.setcarryflag(1)
            self.A.value = fval
            return
        #sub r
        elif (ins & 0xF8 == 0x90):
            sreg = ins - 0x90
            opval = 0
            match sreg:
                case 0x0:
                    opval = self.B.value
                case 0x1:
                    opval = self.C.value
                case 0x2:
                    opval = self.D.value
                case 0x3:
                    opval = self.E.value
                case 0x4:
                    opval = self.H.value
                case 0x5:
                    opval = self.L.value
                case 0x6:
                    opval = self.getM()
                case 0x7:
                    opval = self.A.value
            fval = self.A.value - opval
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(opval), self.A.value))
            self.setparityflag(fval)
            if (self.A.value<opval): self.setcarryflag(1)
            self.A.value = fval
            return
        #sui db
        elif (ins == 0xD6):
            opval = self.memory[self.PC.value].value
            self.incpc()
            fval = self.A.value - opval
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(opval), self.A.value))
            self.setparityflag(fval)
            if (self.A.value<opval): self.setcarryflag(1)
            self.A.value = fval
            return
        #inr r
        elif((ins & 0xCF == 0x0C) or (ins & 0xCF == 0x04)):
            sreg = ((ins & 0x30)>>3) + ((ins & 0x08)>>3)
            match sreg:
                case 0x0:
                    fval = self.B.value + 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(0x01, self.B.value))
                    self.B.value = fval
                case 0x1:
                    fval = self.C.value + 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(0x01, self.C.value))
                    self.C.value = fval
                case 0x2:
                    fval = self.D.value + 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(0x01, self.D.value))
                    self.D.value = fval
                case 0x3:
                    fval = self.E.value + 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(0x01, self.E.value))
                    self.E.value = fval
                case 0x4:
                    fval = self.H.value + 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(0x01, self.H.value))
                    self.H.value = fval
                case 0x5:
                    fval = self.L.value + 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(0x01, self.L.value))
                    self.L.value = fval
                case 0x6:
                    fval = self.getM() + 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(0x01, self.getM()))
                    self.setM(fval)
                case 0x7:
                    fval = self.A.value + 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(0x01, self.A.value))
                    self.A.value = fval
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setparityflag(fval)
            return
        #dcr r
        elif((ins & 0xCF == 0x0D) or (ins & 0xCF == 0x05)):
            sreg = ((ins & 0x30)>>3) + ((ins & 0x08)>>3)
            fval = 0
            match sreg:
                case 0x0:
                    fval = self.B.value - 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(0x01), self.B.value))
                    self.B.value = fval
                case 0x1:
                    fval = self.C.value - 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(0x01), self.C.value))
                    self.C.value = fval
                case 0x2:
                    fval = self.D.value - 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(0x01), self.D.value))
                    self.D.value = fval
                case 0x3:
                    fval = self.E.value - 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(0x01), self.E.value))
                    self.E.value = fval
                case 0x4:
                    fval = self.H.value - 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(0x01), self.H.value))
                    self.H.value = fval
                case 0x5:
                    fval = self.L.value - 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(0x01), self.L.value))
                    self.L.value = fval
                case 0x6:
                    fval = self.getM() - 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(0x01), self.getM()))
                    self.setM(fval)
                case 0x7:
                    fval = self.A.value - 0x01
                    self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(0x01), self.A.value))
                    self.A.value = fval
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setparityflag(fval)
            return
        #inx rp
        elif(ins & 0xCF == 0x03):
            sreg = (ins & 0xf0)>>4
            match sreg:
                case 0x0:
                    fval = ((self.B.value << 8) + self.C.value) + 1
                    self.B.value = fval >> 8
                    self.C.value = fval & 0xff

                case 0x1:
                    fval = ((self.D.value << 8) + self.E.value) + 1
                    self.D.value = fval >> 8
                    self.E.value = fval & 0xff

                case 0x2:
                    fval = ((self.H.value << 8) + self.L.value) + 1
                    self.H.value = fval >> 8
                    self.L.value = fval & 0xff
                
                case 0x3:
                    fval = self.SP.value + 1
                    self.SP.value = fval
            return
        #dcx rp
        elif(ins & 0xCF == 0x0B):
            sreg = (ins & 0xf0)>>4
            match sreg:
                case 0x0:
                    fval = ((self.B.value << 8) + self.C.value) - 1
                    self.B.value = fval >> 8
                    self.C.value = fval & 0xff

                case 0x1:
                    fval = ((self.D.value << 8) + self.E.value) - 1
                    self.D.value = fval >> 8
                    self.E.value = fval & 0xff

                case 0x2:
                    fval = ((self.H.value << 8) + self.L.value) - 1
                    self.H.value = fval >> 8
                    self.L.value = fval & 0xff
                
                case 0x3:
                    fval = self.SP.value - 1
                    self.SP.value = fval
            return
        #adc r
        elif (ins & 0xFE == 0x88):
            sreg = ins - 0x88
            opval = 0
            match sreg:
                case 0x0:
                    opval = self.B.value + self.getcarryflag()
                case 0x1:
                    opval = self.C.value + self.getcarryflag()
                case 0x2:
                    opval = self.D.value + self.getcarryflag()
                case 0x3:
                    opval = self.E.value + self.getcarryflag()
                case 0x4:
                    opval = self.H.value + self.getcarryflag()
                case 0x5:
                    opval = self.L.value + self.getcarryflag()
                case 0x6:
                    opval = self.getM() + self.getcarryflag()
                case 0x7:
                    opval = self.A.value + self.getcarryflag()
            fval = self.A.value + opval
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(self.iscaseauxcarry(opval, self.A.value))
            self.setparityflag(fval)
            if (fval>0xff): self.setcarryflag(1)
            self.A.value = fval
            return
        #aci db
        elif (ins == 0xCE):
            opval = self.memory[self.PC.value].value + self.getcarryflag()
            self.incpc()
            fval = self.A.value + opval
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(self.iscaseauxcarry(opval, self.A.value))
            self.setparityflag(fval)
            if (fval>0xff): self.setcarryflag(1)
            self.A.value = fval
            return
        #sbb r
        elif (ins & 0xFE == 0x98):
            sreg = ins - 0x98
            opval = 0
            match sreg:
                case 0x0:
                    opval = self.B.value
                case 0x1:
                    opval = self.C.value
                case 0x2:
                    opval = self.D.value
                case 0x3:
                    opval = self.E.value
                case 0x4:
                    opval = self.H.value
                case 0x5:
                    opval = self.L.value
                case 0x6:
                    opval = self.getM()
                case 0x7:
                    opval = self.A.value
            opval += self.getcarryflag()
            fval = self.A.value - opval
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(opval), self.A.value))
            self.setparityflag(fval)
            if (self.A.value<opval): self.setcarryflag(1)
            self.A.value = fval
            return
        #sbb db
        elif (ins == 0xCE):
            opval = self.memory[self.PC.value].value + self.getcarryflag()
            self.incpc()
            fval = self.A.value - opval
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(opval), self.A.value))
            self.setparityflag(fval)
            if (self.A.value<opval): self.setcarryflag(1)
            self.A.value = fval
            return
        #dad rp
        elif (ins & 0xCF == 0x09):
            sreg = (ins & 0xf0)>>4
            fval = (self.H.value << 8) + self.L.value
            match sreg:
                case 0x0:
                    fval += ((self.B.value << 8) + self.C.value)

                case 0x1:
                    fval += ((self.D.value << 8) + self.E.value)

                case 0x2:
                    fval += ((self.H.value << 8) + self.L.value)
                
                case 0x3:
                    fval += self.SP.value
            if (fval > 0xff): self.setcarryflag(1)
            self.H.value = fval >> 8
            self.L.value = fval & 0xff
            return
        #dda
        elif (ins == 0x27):
            return
        #jc ds
        elif (ins == 0xDA):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            if (self.getcarryflag() == 1):
                self.PC.value = (hval << 8) + lval
            return
        #jm ds
        elif (ins == 0xFA):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            if (self.getsignflag() == 1):
                self.PC.value = (hval << 8) + lval
            return
        #jmp ds
        elif (ins == 0xC3):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            self.PC.value = (hval << 8) + lval
            return
        #jnc ds
        elif (ins == 0xD2):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc() 
            if (self.getcarryflag() == 0):
                self.PC.value = (hval << 8) + lval
            return
        #jnz ds
        elif (ins == 0xC2):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            if (self.getzeroflag() == 0):
                self.PC.value = (hval << 8) + lval
            return
        #jp ds
        elif (ins == 0xF2):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            if (self.getsignflag() == 0):
                self.PC.value = (hval << 8) + lval
            return
        #jpe ds
        elif (ins == 0xEA):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()  
            if (self.getparityflag() == 1):
                self.PC.value = (hval << 8) + lval
            return
        #jpo ds
        elif (ins == 0xE2):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc() 
            if (self.getparityflag() == 0):
                self.PC.value = (hval << 8) + lval
            return
        #jz ds
        elif (ins == 0xCA):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            if (self.getzeroflag() == 1):
                self.PC.value = (hval << 8) + lval
            return
        #cc ds
        elif (ins == 0xDC):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            if (self.getcarryflag() == 1):
                self.pushPC()
                self.PC.value = (hval << 8) + lval
            return
        #cm ds
        elif (ins == 0xFC):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            if (self.getsignflag() == 1):
                self.pushPC()
                self.PC.value = (hval << 8) + lval
            return
        #call ds
        elif (ins == 0xCD):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            self.pushPC()
            self.PC.value = (hval << 8) + lval
            return
        #cnc ds
        elif (ins == 0xD4):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc() 
            if (self.getcarryflag() == 0):
                self.pushPC()
                self.PC.value = (hval << 8) + lval
            return
        #cnz ds
        elif (ins == 0xC4):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            if (self.getzeroflag() == 0):
                self.pushPC()
                self.PC.value = (hval << 8) + lval
            return
        #cp ds
        elif (ins == 0xF4):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            if (self.getsignflag() == 0):
                self.pushPC()
                self.PC.value = (hval << 8) + lval
            return
        #cpe ds
        elif (ins == 0xEC):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()  
            if (self.getparityflag() == 1):
                self.pushPC()
                self.PC.value = (hval << 8) + lval
            return
        #cpo ds
        elif (ins == 0xE4):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc() 
            if (self.getparityflag() == 0):
                self.pushPC()
                self.PC.value = (hval << 8) + lval
            return
        #cz ds
        elif (ins == 0xCC):
            lval = self.memory[self.PC.value].value
            self.incpc()
            hval = self.memory[self.PC.value].value
            self.incpc()
            if (self.getzeroflag() == 1):
                self.pushPC()
                self.PC.value = (hval << 8) + lval
            return
        #rc
        elif (ins == 0xD8):
            if (self.getcarryflag() == 1):
                self.popPC()
            return
        #rm
        elif (ins == 0xF8):
            if (self.getsignflag() == 1):
                self.popPC()
            return
        #ret
        elif (ins == 0xC9):
            self.popPC()
            return
        #rnc ds
        elif (ins == 0xD0):
            if (self.getcarryflag() == 0):
                self.popPC()
            return
        #rnz ds
        elif (ins == 0xC0):
            if (self.getzeroflag() == 0):
                self.popPC()
            return
        #rp ds
        elif (ins == 0xF0):
            if (self.getsignflag() == 0):
                self.popPC()
            return
        #rpe ds
        elif (ins == 0xE8):
            if (self.getparityflag() == 1):
                self.popPC()
            return
        #rpo ds
        elif (ins == 0xE0):
            if (self.getparityflag() == 0):
                self.popPC()
            return
        #rz ds
        elif (ins == 0xC8):
            if (self.getzeroflag() == 1):
                self.popPC()
            return
        #ana r
        elif (ins & 0xF8 == 0xA0):
            sreg = ins - 0XA0
            opval = 0
            match sreg:
                case 0x0:
                    opval = self.B.value
                case 0x1:
                    opval = self.C.value
                case 0x2:
                    opval = self.D.value
                case 0x3:
                    opval = self.E.value
                case 0x4:
                    opval = self.H.value
                case 0x5:
                    opval = self.L.value
                case 0x6:
                    opval = self.getM()
                case 0x7:
                    opval = self.A.value
            fval = (self.A.value & opval)
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(opval), self.A.value))
            self.setparityflag(fval)
            self.A.value = fval
            return
        #ani db
        elif (ins == 0xE6):
            opval = self.memory[self.PC.value].value
            self.incpc()
            fval = (self.A.value & opval)
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(1)
            self.setparityflag(fval)
            self.A.value = fval
            return
        #ora r
        elif (ins & 0xF8 == 0xB0):
            sreg = ins - 0XB0
            opval = 0
            match sreg:
                case 0x0:
                    opval = self.B.value
                case 0x1:
                    opval = self.C.value
                case 0x2:
                    opval = self.D.value
                case 0x3:
                    opval = self.E.value
                case 0x4:
                    opval = self.H.value
                case 0x5:
                    opval = self.L.value
                case 0x6:
                    opval = self.getM()
                case 0x7:
                    opval = self.A.value
            fval = (self.A.value | opval)
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setparityflag(fval)
            self.A.value = fval
            return
        #ori db
        elif (ins == 0xF6):
            opval = self.memory[self.PC.value].value
            self.incpc()
            fval = (self.A.value | opval)
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setparityflag(fval)
            self.A.value = fval
            return
        #xra r
        elif (ins & 0xF8 == 0xA8):
            sreg = ins - 0xA8
            opval = 0
            match sreg:
                case 0x0:
                    opval = self.B.value
                case 0x1:
                    opval = self.C.value
                case 0x2:
                    opval = self.D.value
                case 0x3:
                    opval = self.E.value
                case 0x4:
                    opval = self.H.value
                case 0x5:
                    opval = self.L.value
                case 0x6:
                    opval = self.getM()
                case 0x7:
                    opval = self.A.value
            fval = (self.A.value ^ opval)
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setparityflag(fval)
            self.A.value = fval
            return
        #xri db
        elif (ins == 0xF6):
            opval = self.memory[self.PC.value].value
            self.incpc()
            fval = (self.A.value ^ opval)
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setparityflag(fval)
            self.A.value = fval
            return
        #cma
        elif (ins == 0x2F):
            fval = 0
            for i in range(8):
                bval = self.A.value & (0x1<<i)
                if (bval == 0):
                    fval += (0x1<<i)
            self.A.value = fval
            return
        #cmp r
        elif (ins & 0xF8 == 0xB8):
            sreg = ins - 0xB8
            opval = 0
            match sreg:
                case 0x0:
                    opval = self.B.value
                case 0x1:
                    opval = self.C.value
                case 0x2:
                    opval = self.D.value
                case 0x3:
                    opval = self.E.value
                case 0x4:
                    opval = self.H.value
                case 0x5:
                    opval = self.L.value
                case 0x6:
                    opval = self.getM()
                case 0x7:
                    opval = self.A.value
            fval = self.A.value - opval
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(opval), self.A.value))
            if (self.A.value < opval):
                self.setcarryflag(1)
            self.setparityflag(fval)
            return
        #cpi db
        elif (ins == 0xFE):
            opval = self.memory[self.PC.value].value
            self.incpc()
            fval = self.A.value - opval
            self.resetflags()
            self.setsignflag(fval)
            self.setzeroflag(fval)
            self.setauxicarryflag(self.iscaseauxcarry(self.ln2comp(opval), self.A.value))
            if (self.A.value < opval):
                self.setcarryflag(1)
            self.setparityflag(fval)
            return
        #rlc
        elif (ins == 0x07):
            # d7 = (self.A.value & 0x80)>>7
            d7 = (self.A.value & 0x80)
            self.setcarryflag(d7)
            self.A.value = self.A.value<<1
            if (d7 != 0):
                self.A.value = self.A.value | 0x01
            return
        #ral
        elif (ins == 0x17):
            # d7 = (self.A.value & 0x80)>>7
            d7 = (self.A.value & 0x80)
            cf = self.getcarryflag()
            self.setcarryflag(d7)
            self.A.value = self.A.value<<1
            if (cf != 0):
                self.A.value = self.A.value | 0x01
            return
        #rrc
        elif (ins == 0x0F):
            d0 = (self.A.value & 0x01)
            self.setcarryflag(d0)
            self.A.value = self.A.value>>1
            if (d0 != 0):
                self.A.value = self.A.value | 0x80
            return
        #rar
        elif (ins == 0x1F):
            d0 = (self.A.value & 0x01)
            cf = self.getcarryflag()
            self.setcarryflag(d0)
            self.A.value = self.A.value>>1
            if (cf != 0):
                self.A.value = self.A.value | 0x80
            return
        #cmc
        elif (ins == 0x3F):
            if (self.getcarryflag() == 0):
                self.setcarryflag(1)
            else:
                self.setcarryflag(0)
            return
        #stc
        elif (ins == 0x37):
            self.setcarryflag(1)
            return
        #push rp
        elif (ins & 0xCF == 0xC5):
            sreg = (ins - 0xC5)>>4
            match sreg:
                case 0x0:
                    self.push(self.C.value)
                    self.push(self.B.value)
                case 0x1:
                    self.push(self.E.value)
                    self.push(self.D.value)
                case 0x2:
                    self.push(self.L.value)
                    self.push(self.H.value)
                case 0x3:
                    self.push(self.F.value)
                    self.push(self.A.value)
            return
        #pop rp
        elif (ins & 0xCF == 0xC1):
            sreg = (ins - 0xC1)>>4
            match sreg:
                case 0x0:
                    self.B.value = self.pop()
                    self.C.value = self.pop()
                case 0x1:
                    self.D.value = self.pop()
                    self.E.value = self.pop()
                case 0x2:
                    self.H.value = self.pop()
                    self.L.value = self.pop()
                case 0x3:
                    self.A.value = self.pop()
                    self.F.value = self.pop()
            return
    def iscaseauxcarry(self, val1, val2):
        n1 = val1 & 0x0f
        n2 = val2 & 0x0f
        if (abs(n1+n2) > 0x0f):
            return 1
        return 0

    def pushPC(self):
        self.push(self.PC.value & 0xff)
        self.push((self.PC.value & 0xff00)>>8)

    def popPC(self):
        hval = self.pop()
        lval = self.pop()
        self.PC.value = (hval<<8) + lval

    def getM(self):
        # print((self.H.value << 8) + self.L.value)
        return self.memory[(self.H.value << 8) + self.L.value].value
    
    def setM(self, val):
        # print((self.H.value << 8) + self.L.value)
        self.memory[(self.H.value << 8) + self.L.value].value = val

    def incpc(self):
        self.PC.value = self.PC.value+1

    def setsignflag(self, val):
        if (val & 0x80 != 0):
            self.F.value = self.F.value | 0x80
        else:
            self.F.value = self.F.value & 0x7f
    
    #for simply checking the bits are set or not we donot need to bitshift to right ;(
    def getsignflag(self, val):
        return (self.F.value & 0x80)>>7

    def setzeroflag(self, val):
        if ((val&0xff) == 0):
            self.F.value = self.F.value | 0x40
        else:
            self.F.value = self.F.value & 0xBF
    
    def getzeroflag(self):
        return (self.F.value & 0x40)>>6
    
    def setparityflag(self, val):
        parity = 1
        for i in range(8):
            parity = ((val>>i) & 0x01) ^ parity
        if (parity == 1):
            self.F.value = self.F.value | 0x04
        else:
            self.F.value = self.F.value & 0xFB
    
    def getparityflag(self):
        return (self.F.value & 0x04)>>2
    
    def setcarryflag(self, val):
        if (val != 0):
            self.F.value = self.F.value | 0x01
        else:
            self.F.value = self.F.value & 0xFE
    
    def getcarryflag(self):
        return self.F.value & 0x01
    
    def setauxicarryflag(self, val):
        if (val != 0):
            self.F.value = self.F.value | 0x10
        else:
            self.F.value = self.F.value & 0xEF
    
    def getauxicarryflag(self):
        return (self.F.value & 0x10)>>4

    def resetflags(self):
        self.F.value = 0x00

    def ln2comp(self, val):
        t = (val)&0x0f
        r = 0x0
        for i in range(4):
            if ((t&(0x1<<i)) == 0):
                r = r | 0x1<<i
        r = r+1
        return r&val

def checkhex(v:str):
    if (v[-1] != 'H' or not (len(v) == 3 or len(v) == 5)):
        return False
    try:
        int(v[:-1], 16)
        return True
    except:
        return False
    
def lexline(line:str):
    l = line.upper()
    if l.find(';') != -1:
        l = l[0:l.find(';')]
    ele = misc_getele(l)
    lexana = []
    if (ele == []):
        return [], []
    for l in ele:
        if (l == ','):
            lexana.append(LexTag.SCOMMA)
        elif (l == ':'):
            lexana.append(LexTag.SCOLON)
        elif (l in _opcodes):
            lexana.append(LexTag.OPCODE)
        elif (l in _regs):
            lexana.append(LexTag.REG)
        elif (l in _reg_misc):
            lexana.append(LexTag.REG_MISC)
        elif checkhex(l):
            if (len(l) == 3):
                lexana.append(LexTag.DBYTE)
            if (len(l) == 5):
                lexana.append(LexTag.DSHORT)
        else: 
            lexana.append(LexTag.DSTRING)
    return ele, lexana

class assembler():
    def __init__(self) -> None:
        self.toresolvelabels = {}
        self.ploadoff = 0x0800
        self.cprogmemoff = 0x0000
        self.dbgtoresolvelines = {}
        self.labeloff = {}
        self.pmemory = []

        self.plsize = []

        self.dbugasm = ""
        self.dclines = []
        self.dbglinecache = []

    def reset(self) -> None:
        self.toresolvelabels = {}
        self.ploadoff = 0x0800
        self.cprogmemoff = 0x0000
        self.dbgtoresolvelines = {}
        self.labeloff = {}
        self.pmemory = []

        self.plsize = []

        self.dbugasm = ""
        self.dclines = []
        
        self.dbglinecache = []
    
    def addtooresolvelabel(self, label:str, offset:int, cline:int=None) -> None:
        if not label in self.toresolvelabels:
            #print(label)
            self.toresolvelabels[label] = []
            self.toresolvelabels[label].append(offset)
            if (cline != None):
                self.dbgtoresolvelines[label] = []
                self.dbgtoresolvelines[label].append(cline)            
        else:
            self.toresolvelabels[label].append(offset)
            if (cline != None):
                self.dbgtoresolvelines[label].append(cline)
    
    def addlabeloff(self, label:str, offset:int) -> bool:
        if not label in self.labeloff:
            self.labeloff[label] = offset
            return True
        else: return False
    
    def miscissinglebarg(self, lexa, off) -> (bool, str):
        if (len(lexa) == (off+1)+1):
            if lexa[off+1] == LexTag.DBYTE:
                return True, ''
            else : 
                return False, 'invaid arg, was expecting a byte'
        else:
            if (len(lexa) > (off+1)+1):
                return False, "was expecting fewer args!"
            if (len(lexa) > (off+1)+1):
                return False, "was expecting a byte arg!"

    def miscissingledarg(self, lexa, off) -> (bool, str):
        if (len(lexa) == (off+1)+1):
            if lexa[off+1] == LexTag.DSHORT:
                return True, ''
            else : 
                return False, 'invaid arg, was expecting a double'
        else:
            if (len(lexa) > (off+1)+1):
                return False, "was expecting fewer args!"
            if (len(lexa) > (off+1)+1):
                return False, "was expecting two bytes arg!"
    
    def miscissinglerarg(self, lexa, off) -> (bool, str):
        if (len(lexa) == (off+1)+1):
            if lexa[off+1] == LexTag.REG:
                return True, ''
            else : 
                return False, 'invaid arg, was expecting a register!'
        else:
            if (len(lexa) > (off+1)+1):
                return False, "was expecting fewer args!"
            if (len(lexa) < (off+1)+1):
                return False, "was expecting a reg arg"
            
    def miscissinglelab(self, lexa, off) -> (bool, str):
        if (len(lexa) == (off+1)+1):
            if lexa[off+1] == LexTag.DSTRING or LexTag.DSHORT:
                return True, ''
            else : 
                return False, 'invaid arg, was expecting a string or label!'
        else:
            if (len(lexa) > (off+1)+1):
                return False, "was expecting fewer args!"
            if (len(lexa) < (off+1)+1):
                return False, "was expecting a string arg"
            
    def miscissinglerparg(self, lexa, s, off, regs=['B', 'D', 'H', 'SP']) -> (bool,str):
        if (len(lexa) == (off+1)+1):
            if s in regs:
                return True, ''
            else : 
                return False, f'invaid arg, was expecting a registers {regs}!'
        else:
            if (len(lexa) > (off+1)+1):
                return False, "was expecting fewer args!"
            if (len(lexa) < (off+1)+1):
                return False, "was expecting a rpargs"
            
    def miscisnoarg(self, lexa, off) -> (bool, str):
        if (len(lexa) == (off+1)):
                return True, ''
        else : 
            return False, 'invaid arg, was expecting no arg!'
    
        
    def miscopcodertoff(self, bopcode, sval, inc=1):
        match sval:
            case 'B':
                return bopcode
            case 'C':
                return bopcode + inc*1
            case 'D':
                return bopcode + inc*2
            case 'E':
                return bopcode + inc*3
            case 'H':
                return bopcode + inc*4
            case 'L':
                return bopcode + inc*5
            case 'M':
                return bopcode + inc*6
            case 'A':
                return bopcode + inc*7
            case _:
                Exception("error:: was expecting a string arg")
                return 0x00
    #demon
    def miscopcoderpt3off(self, bopcode, sval, aregstr=['B', 'D', 'H', 'SP'], inc=16):
                off = 0
                for reg in aregstr:
                    if reg == sval: break
                    off +=1
                return bopcode + off*inc
    def resolvelabels(self) -> (bool, str):
        # print(list(self.labeloff))
        for label in list(self.labeloff):
            if label in list(self.toresolvelabels):
                #print(f'resolving label \'{label}\'')
                memoff  = self.labeloff[label] + self.ploadoff 
                adl = memoff >> 8
                adu = memoff & 0x00ff
                for toupoff in self.toresolvelabels[label]:
                    self.pmemory[toupoff] = adu
                    self.pmemory[toupoff+1] = adl
                self.toresolvelabels.pop(label)
        if (self.toresolvelabels != {}):
            return False, f'error unresolved labels {list(self.toresolvelabels)}'
        return True, ''
    def assemble(self, lines) -> (bool, str):
        self.dclines = lines
        for line in lines:
            sa, lexa = lexline(line)
            oplen = 0
            opcodes = []
            #instruction offset incase of label defined before instruction 
            inso = 0
            if sa != []:
                if LexTag.SCOLON in lexa:
                    scount = 0
                    for lex in lexa:
                        if (lex == LexTag.SCOLON):
                            scount += 1
                    if (scount > 1):
                        return False, "was expecting single colon"
                    if lexa[0] == LexTag.DSTRING and lexa[1] == LexTag.SCOLON:
                        if(self.addlabeloff(sa[0], self.cprogmemoff) == False):
                            return False, f'label {sa[0]} was already defined'
                        if (len(lexa) == 2):
                            inso = -1
                        else:
                            inso = 2
                    else:
                        return False, "was expecting string before colon"
                if (inso != -1):
                    if lexa[inso] != LexTag.OPCODE:
                        return False, 'was expecting a opcode!'
                    else:
                        #type no arg
                        ins = sa[inso]
                        if ins in list(_inc_narg):
                                b, m = self.miscisnoarg(lexa, inso)
                                if (b == False):
                                    return False, m
                                opcodes.append(_inc_narg[ins])
                                oplen = 1
                        #type single byte arg
                        elif ins in list(_inc_sbarg):
                                b, m = self.miscissinglebarg(lexa, inso)
                                if (b == False):
                                    return False, m
                                opcodes.append(_inc_sbarg[ins])
                                opcodes.append(int(sa[inso+1][:-1], 16))
                                oplen = 2
                        #type single reg with offset relation t1 arg
                        elif ins in list(_inc_srt1arg):
                                b, m = self.miscissinglerarg(lexa, inso)
                                if (b == False):
                                    return False, m
                                opcodes.append(self.miscopcodertoff(_inc_srt1arg[ins], sa[inso+1]))
                                oplen = 1
                        #type single reg with offset relation t2 arg
                        elif ins in list(_inc_srt2arg):
                                b, m = self.miscissinglerarg(lexa, inso)
                                if (b == False):
                                    return False, m
                                opcodes.append(self.miscopcodertoff(_inc_srt2arg[ins], sa[inso+1], 8))
                                oplen = 1
                        #type single reg pair with offset relation t3 arg
                        elif ins in list(_inc_srpt3arg):
                                b, m = self.miscissinglerparg(lexa, sa[inso+1], inso, _inc_srpt3regs)
                                if (b == False):
                                    return False, m
                                opcodes.append(self.miscopcoderpt3off(_inc_srpt3arg[ins], sa[inso+1], _inc_srpt3regs, 16))
                                oplen = 1
                        #type single reg pair with offset relation t4 arg
                        elif ins in list(_inc_srpt4arg):
                                b, m = self.miscissinglerparg(lexa, sa[inso+1], inso, _inc_srpt4regs)
                                if (b == False):
                                    return False, m
                                opcodes.append(self.miscopcoderpt3off(_inc_srpt4arg[ins], sa[inso+1], _inc_srpt4regs, 16))
                                oplen = 1
                        #type single reg pair with offset relation t5 arg
                        elif ins in list(_inc_srpt5arg):
                                b, m = self.miscissinglerparg(lexa, sa[inso+1], inso, _inc_srpt5regs)
                                if (b == False):
                                    return False, m
                                opcodes.append(self.miscopcoderpt3off(_inc_srpt5arg[ins], sa[inso+1], _inc_srpt5regs, 16))
                                oplen = 1
                        #type single lab arg
                        elif ins in list(_inc_slarg):
                                b, m = self.miscissinglelab(lexa, inso)
                                if (b == False):
                                    return False, m
                                opcodes.append(_inc_slarg[ins])
                                if lexa[inso+1] == LexTag.DSHORT:
                                    tm = int(sa[inso+1][:-1], 16)
                                    adu = tm >> 8
                                    adl = tm & 0x00ff
                                    opcodes.append(adl)
                                    opcodes.append(adu)
                                else:
                                    opcodes.append(0xCA)
                                    opcodes.append(0xCA)
                                    self.addtooresolvelabel(sa[inso+1], self.cprogmemoff+1)
                                oplen = 3
                        #type single double arg
                        elif ins in list(_inc_sdarg):
                                b, m = self.miscissingledarg(lexa, inso)
                                if (b == False):
                                    return False, m
                                tm = int(sa[inso+1][:-1], 16)
                                adu = tm >> 8
                                adl = tm & 0x00ff
                                opcodes.append(_inc_sdarg[ins])
                                opcodes.append(adl)
                                opcodes.append(adu)
                                oplen = 3
                        #some distinct hardcoded
                        elif ins == 'LXI':
                            if (len(sa) != (inso+1)+3):
                                return False, 'not enough args'
                            if (sa[inso+1] in _inc_srpt3regs and lexa[inso+2] == LexTag.SCOMMA and lexa[inso+3] == LexTag.DSHORT):
                                tm = int(sa[inso+3][:-1], 16)
                                adl = tm >> 8
                                adu = tm & 0x00ff
                                opcodes.append(self.miscopcoderpt3off(0x01, sa[inso+1], _inc_srpt3regs, 16))
                                opcodes.append(adu)
                                opcodes.append(adl)
                                oplen = 3
                            else:
                                return False, 'invalid args'
                        elif ins == 'MVI':
                            if (len(sa) != (inso+1)+3):
                                return False, 'not enough args'
                            if (lexa[inso+1] == LexTag.REG and lexa[inso+2] == LexTag.SCOMMA and lexa[inso+3] == LexTag.DBYTE):
                                d = int(sa[inso+3][:-1], 16)
                                opcodes.append(self.miscopcodertoff(0x06, sa[inso+1], 8))
                                opcodes.append(d)
                                oplen = 2
                            else:
                                return False, 'invalid args'
                        elif ins == 'MOV':
                            if (len(sa) != (inso+1)+3):
                                return False, 'not enough args'
                            if (lexa[inso+1] == LexTag.REG and lexa[inso+2] == LexTag.SCOMMA and lexa[inso+3] == LexTag.REG and not (sa[inso+1]=='M' and sa[inso+3]=='M')):
                                topcode =  self.miscopcodertoff(self.miscopcodertoff(0x40, sa[inso+3]), sa[inso+1], 8)
                                opcodes.append(topcode)
                                oplen = 1
                            else:
                                return False, 'invalid args'
                        else:
                            return False, 'opcode locate error'
            self.plsize.append(oplen)
            for opcode in opcodes:
                self.pmemory.append(opcode)
            self.cprogmemoff += oplen
        bl, ml = self.resolvelabels()
        if (bl == False):
            return False, ml
        return True, "success!"
    
    def generateasmdump(self):
        memoff = self.ploadoff
        poff = 0
        loff = 0
        for lc in self.plsize:
            self.dbugasm += f'{"%04x"%(memoff+poff)}      '.upper()
            lsize = lc
            toline = ''
            for i in range(lsize):
                toline += (f'{"%02x"%self.pmemory[poff+i]} '.upper())
                self.dbglinecache.append(loff+1)
            self.dbugasm += "{:<10}".format(toline)
            self.dbugasm += f'   <=> <{lsize} bytes> \'{self.dclines[loff]}\'\n'
            loff += 1
            poff += lsize

# a = assembler()
# c, d = a.assemble([';simple program in one shot!', 'Ree:MOV A, A', 'INR M', 'ACI 00H', 'ADI 01H', 'CALL L2', 'CC L2', 'ADC H', 'L2:', 'LDA 4000H','HLT'])
# print(c, d)
# if (c== True):
#     print(a.toresolvelabels)
#     print(a.labeloff)
#     a.generateasmdump()
#     print(a.dbugasm)


#check opcodes
# opcodes_resloved = [_inc_sbarg, _inc_sdarg, _inc_srt1arg, _inc_srt2arg, _inc_slarg, _inc_narg, _inc_srpt3arg, _inc_srpt4arg, _inc_srpt5arg]
# resoved  =  []
# for oca in opcodes_resloved:
#     for oc in list(oca):
#         resoved.append(oc)
# for r in resoved:
#     if r not in _opcodes:
#         print(r)
