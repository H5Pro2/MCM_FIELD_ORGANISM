"""Two-slot H. Only current input/index enter; all retained state is one bank."""
import math
import struct

SLOT=1168
CONTROL=2336
BUFFER=2368
OUTPUT=3136
SIZE=3520
NONE,KNOWN,UNKNOWN,SKELETON=0,1,2,3

class HintMean:
    __slots__=('bank',)
    def __init__(self):self.bank=bytearray(SIZE)
    def word(self,offset):return struct.unpack_from('<Q',self.bank,offset)[0]
    def put(self,offset,value):struct.pack_into('<Q',self.bank,offset,value)
    @property
    def index(self):return self.word(CONTROL)
    @property
    def kind(self):return self.bank[CONTROL+24]
    @property
    def slot(self):return self.bank[CONTROL+25]
    @property
    def closed(self):return bool(self.bank[CONTROL+26])
    def clear(self,start,end):
        for k in range(start,end):self.bank[k]=0
    def same(self,slot):
        start=slot*SLOT
        for k in range(768):
            if self.bank[start+k]!=self.bank[BUFFER+k]:return False
        return True
    def copy(self,dest,src,size):
        for k in range(size):self.bank[dest+k]=self.bank[src+k]
    def vector(self,dest,values):
        for j in range(48):struct.pack_into('<d',self.bank,dest+8*j,values[j])
    def ticket(self,kind,target,slot=255):
        self.put(CONTROL+16,target);self.bank[CONTROL+24]=kind;self.bank[CONTROL+25]=slot
    def abort(self):
        self.clear(0,SIZE);self.bank[CONTROL+26]=1
    def accept(self,index,values):
        try:return self._accept(index,values)
        except BaseException:
            self.abort();raise
    def _accept(self,index,values):
        if self.closed or type(index) is not int or index!=self.index+1 or not 1<=index<=1024:
            raise ValueError('H_INDEX_CLOSED')
        if len(values)!=48:raise ValueError('H_DIMENSION')
        for v in values:
            if type(v) is not float or not math.isfinite(v):raise ValueError('H_NONFINITE_INPUT')
        phase=index%4;error=None
        if phase in (1,3) and index>1:
            if self.word(CONTROL+16)!=index:raise ValueError('H_TARGET')
            if phase==1 and self.kind!=SKELETON or phase==3 and self.kind not in (KNOWN,UNKNOWN):raise ValueError('H_TICKET')
            if phase==3:
                if self.word(CONTROL+8)>=256:raise ValueError('H_COUNTER')
                if self.kind==KNOWN and (self.slot>1 or not self.same(self.slot) or not 1<=self.word(self.slot*SLOT+1152)<256):raise ValueError('H_SLOT')
                if self.kind==UNKNOWN:
                    if self.slot!=255:raise ValueError('H_UNKNOWN_SLOT')
                    for slot in (0,1):
                        if self.word(slot*SLOT+1152) and self.same(slot):raise ValueError('H_UNKNOWN_EXISTS')
            total=0.0
            for j in range(48):
                difference=abs(struct.unpack_from('<d',self.bank,OUTPUT+8*j)[0]-values[j]);total=total+difference
            error=total/48.0
            if not math.isfinite(error):raise ValueError('H_NONFINITE_ERROR')
        elif self.kind!=NONE:raise ValueError('H_UNEXPECTED_PENDING')
        if phase==1:
            self.clear(BUFFER,SIZE);self.vector(BUFFER,values);self.ticket(NONE,0)
            self.bank[CONTROL+27]=1
        elif phase==2:
            if self.bank[CONTROL+27]!=1:raise ValueError('H_BUFFER')
            self.vector(BUFFER+384,values);self.bank[CONTROL+27]=2
            found=255
            for slot in (0,1):
                if self.word(slot*SLOT+1152) and self.same(slot):
                    if found!=255:raise ValueError('H_DUPLICATE_KEYS')
                    found=slot
            if found==255:self.copy(OUTPUT,BUFFER+384,384);self.ticket(UNKNOWN,index+1)
            else:self.copy(OUTPUT,found*SLOT+768,384);self.ticket(KNOWN,index+1,found)
        elif phase==3:
            if self.bank[CONTROL+27]!=2:raise ValueError('H_BUFFER')
            slot=self.slot
            if self.kind==UNKNOWN:
                slot=0 if not self.word(1152) else 1 if not self.word(SLOT+1152) else (0 if self.word(1160)<=self.word(SLOT+1160) else 1)
                self.clear(slot*SLOT,(slot+1)*SLOT);self.copy(slot*SLOT,BUFFER,768)
                self.vector(slot*SLOT+768,values);self.put(slot*SLOT+1152,1)
            else:
                k=self.word(slot*SLOT+1152)+1
                for j in range(48):
                    old=struct.unpack_from('<d',self.bank,slot*SLOT+768+8*j)[0]
                    difference=values[j]-old;increment=difference/float(k);value=old+increment
                    if not math.isfinite(value):raise ValueError('H_NONFINITE_UPDATE')
                    struct.pack_into('<d',self.bank,slot*SLOT+768+8*j,value)
                self.put(slot*SLOT+1152,k)
            self.put(CONTROL+8,self.word(CONTROL+8)+1)
            self.put(slot*SLOT+1160,self.word(CONTROL+8))
            self.clear(BUFFER,SIZE);self.ticket(NONE,0);self.bank[CONTROL+27]=0
        else:self.vector(OUTPUT,values);self.ticket(SKELETON,index+1)
        self.put(CONTROL,index)
        return error
    def finish(self):
        try:
            if self.closed or self.index!=1024 or self.kind!=SKELETON or self.word(CONTROL+16)!=1025:
                raise ValueError('H_INCOMPLETE_FINISH')
        finally:self.abort()
