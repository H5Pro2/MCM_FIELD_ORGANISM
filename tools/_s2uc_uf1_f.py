"""UF1 bounded feedback-only frequency baseline. Retained state is one bank."""
import math
import struct

SLOT=1560
CONTROL=3120
BUFFER=3152
OUTPUT=3920
SIZE=4304
NONE,UNKNOWN,TIE,MAJORITY,SKELETON=0,1,2,3,4

class HintFrequency:
    __slots__=('bank',)
    def __init__(self):
        self.bank=bytearray(SIZE);self.bank[CONTROL+25]=255;self.bank[CONTROL+26]=255
    def word(self,o):return struct.unpack_from('<Q',self.bank,o)[0]
    def put(self,o,v):struct.pack_into('<Q',self.bank,o,v)
    @property
    def index(self):return self.word(CONTROL)
    @property
    def kind(self):return self.bank[CONTROL+24]
    @property
    def slot(self):return self.bank[CONTROL+25]
    @property
    def value(self):return self.bank[CONTROL+26]
    @property
    def closed(self):return bool(self.bank[CONTROL+27]&1)
    def clear(self,start,end):
        for k in range(start,end):self.bank[k]=0
    def equal(self,a,b,size):
        for k in range(size):
            if self.bank[a+k]!=self.bank[b+k]:return False
        return True
    def zero(self,a,b):
        for k in range(a,b):
            if self.bank[k]:return False
        return True
    def same(self,slot):return self.equal(slot*SLOT,BUFFER,768)
    def copy(self,dest,src,size):
        for k in range(size):self.bank[dest+k]=self.bank[src+k]
    def vector(self,dest,values):
        for j in range(48):struct.pack_into('<d',self.bank,dest+8*j,values[j])
    def matches_vector(self,start,values):
        for j in range(48):
            bits=struct.pack('<d',values[j])
            for k in range(8):
                if self.bank[start+j*8+k]!=bits[k]:return False
        return True
    def ticket(self,kind,target,slot=255,value=255):
        self.put(CONTROL+16,target);self.bank[CONTROL+24]=kind
        self.bank[CONTROL+25]=slot;self.bank[CONTROL+26]=value
    def abort(self):
        self.clear(0,SIZE);self.bank[CONTROL+25]=255;self.bank[CONTROL+26]=255;self.bank[CONTROL+27]=1
    def invariants(self):
        t=self.word(CONTROL+8);total=0
        if t>256 or self.bank[CONTROL+27]&~7 or not self.zero(CONTROL+28,CONTROL+32):raise ValueError('F_CONTROL')
        for s in (0,1):
            o=s*SLOT;a=self.word(o+1536);b=self.word(o+1544);stamp=self.word(o+1552)
            if a>256 or b>256 or a+b>256 or not a and b:raise ValueError('F_COUNTS')
            if a:
                if not 1<=stamp<=t:raise ValueError('F_STAMP')
                if b and self.equal(o+768,o+1152,384):raise ValueError('F_DUPLICATE_VALUES')
                if not b and not self.zero(o+1152,o+1536):raise ValueError('F_EMPTY_VALUE')
            elif not self.zero(o,o+SLOT):raise ValueError('F_EMPTY_SLOT')
            total+=a+b
        if total>t:raise ValueError('F_TOTAL_COUNT')
        if self.word(1536) and self.word(SLOT+1536) and self.equal(0,SLOT,768):raise ValueError('F_DUPLICATE_KEYS')
    def accept(self,index,values):
        try:return self._accept(index,values)
        except BaseException:
            self.abort();raise
    def _accept(self,index,values):
        if self.closed or type(index) is not int or index!=self.index+1 or not 1<=index<=1024:raise ValueError('F_INDEX_CLOSED')
        if len(values)!=48:raise ValueError('F_DIMENSION')
        for v in values:
            if type(v) is not float or not math.isfinite(v):raise ValueError('F_INPUT')
        self.invariants();phase=index%4;error=None
        if phase in (1,3) and index>1:
            if self.word(CONTROL+16)!=index:raise ValueError('F_TARGET')
            if phase==1:
                if self.kind!=SKELETON or self.slot!=255 or self.value!=255 or self.bank[CONTROL+27]:raise ValueError('F_SKELETON')
            else:
                if self.kind not in (UNKNOWN,TIE,MAJORITY) or self.bank[CONTROL+27]!=6:raise ValueError('F_TICKET')
                if self.kind==UNKNOWN:
                    if self.slot!=255 or self.value!=255:raise ValueError('F_UNKNOWN_SLOT')
                    for s in (0,1):
                        if self.word(s*SLOT+1536) and self.same(s):raise ValueError('F_UNKNOWN_EXISTS')
                    if not self.equal(OUTPUT,BUFFER+384,384):raise ValueError('F_OUTPUT')
                else:
                    if self.slot>1 or not self.same(self.slot):raise ValueError('F_SLOT')
                    o=self.slot*SLOT;a=self.word(o+1536);b=self.word(o+1544)
                    if not a:raise ValueError('F_EMPTY_TICKET')
                    if self.kind==TIE:
                        if a!=b or self.value!=255 or not self.equal(OUTPUT,BUFFER+384,384):raise ValueError('F_TIE')
                    else:
                        winner=0 if a>b else 1
                        if a==b or self.value!=winner or not self.equal(OUTPUT,o+768+384*winner,384):raise ValueError('F_MAJORITY')
            total=0.0
            for j in range(48):total=total+abs(struct.unpack_from('<d',self.bank,OUTPUT+8*j)[0]-values[j])
            error=total/48.0
            if not math.isfinite(error):raise ValueError('F_ERROR_NONFINITE')
        elif self.kind!=NONE or self.word(CONTROL+16) or self.slot!=255 or self.value!=255:raise ValueError('F_UNEXPECTED_PENDING')
        if phase==1:
            if self.bank[CONTROL+27]:raise ValueError('F_BUFFER')
            self.clear(BUFFER,SIZE);self.vector(BUFFER,values);self.ticket(NONE,0);self.bank[CONTROL+27]=2
        elif phase==2:
            if self.bank[CONTROL+27]!=2:raise ValueError('F_BUFFER')
            self.vector(BUFFER+384,values);self.bank[CONTROL+27]=6;found=255
            for s in (0,1):
                if self.word(s*SLOT+1536) and self.same(s):found=s
            if found==255:self.copy(OUTPUT,BUFFER+384,384);self.ticket(UNKNOWN,index+1)
            else:
                o=found*SLOT;a=self.word(o+1536);b=self.word(o+1544)
                if a==b:self.copy(OUTPUT,BUFFER+384,384);self.ticket(TIE,index+1,found)
                else:
                    winner=0 if a>b else 1;self.copy(OUTPUT,o+768+384*winner,384);self.ticket(MAJORITY,index+1,found,winner)
        elif phase==3:
            if self.word(CONTROL+8)>=256:raise ValueError('F_COUNTER')
            s=self.slot
            if self.kind==UNKNOWN:
                s=0 if not self.word(1536) else 1 if not self.word(SLOT+1536) else (0 if self.word(1552)<=self.word(SLOT+1552) else 1)
                self.clear(s*SLOT,(s+1)*SLOT);self.copy(s*SLOT,BUFFER,768);self.vector(s*SLOT+768,values);self.put(s*SLOT+1536,1)
            else:
                o=s*SLOT
                if self.matches_vector(o+768,values):entry=0
                elif self.word(o+1544) and self.matches_vector(o+1152,values):entry=1
                elif not self.word(o+1544):entry=1
                else:raise ValueError('F_VALUE_CAPACITY')
                if self.word(o+1536)+self.word(o+1544)>=256:raise ValueError('F_COUNTER')
                if not self.word(o+1536+8*entry):self.vector(o+768+384*entry,values)
                self.put(o+1536+8*entry,self.word(o+1536+8*entry)+1)
            self.put(CONTROL+8,self.word(CONTROL+8)+1);self.put(s*SLOT+1552,self.word(CONTROL+8))
            self.clear(BUFFER,SIZE);self.ticket(NONE,0);self.bank[CONTROL+27]=0
        else:
            if self.bank[CONTROL+27]:raise ValueError('F_BUFFER')
            self.vector(OUTPUT,values);self.ticket(SKELETON,index+1)
        self.put(CONTROL,index);return error
    def finish(self):
        try:
            self.invariants()
            if self.closed or self.index!=1024 or self.word(CONTROL+8)!=256 or self.kind!=SKELETON or self.word(CONTROL+16)!=1025 or self.slot!=255 or self.value!=255 or self.bank[CONTROL+27]:raise ValueError('F_INCOMPLETE_FINISH')
        finally:self.abort()
