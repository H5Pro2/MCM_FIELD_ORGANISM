"""Independent UF1 object-state oracle; no production baseline import."""
import math
import struct
from fractions import Fraction

def bits(v):return b''.join(struct.pack('<d',x) for x in v)

class Reference:
    def __init__(self):
        self.slots=[None,None];self.i=0;self.t=0;self.pair=[];self.pending=None;self.closed=False
    def accept(self,i,v):
        try:return self.step(i,v)
        except BaseException:
            self.close();raise
    def step(self,i,v):
        if self.closed or type(i) is not int or i!=self.i+1 or not 1<=i<=1024:raise ValueError('REFERENCE_INDEX')
        if len(v)!=48 or any(type(x) is not float or not math.isfinite(x) for x in v):raise ValueError('REFERENCE_INPUT')
        error=None
        if i>1 and i%2:
            if self.pending is None or self.pending['target']!=i:raise ValueError('REFERENCE_TICKET')
            total=0.0
            for a,b in zip(self.pending['output'],v,strict=True):total=float(Fraction(total)+Fraction(abs(float(Fraction(a)-Fraction(b)))))
            error=float(Fraction(total)/48)
        if i%4==1:self.pending=None;self.pair=[tuple(v)]
        elif i%4==2:
            self.pair.append(tuple(v));key=bits(self.pair[0]+self.pair[1])
            found=[n for n,s in enumerate(self.slots) if s is not None and s['key']==key]
            if len(found)>1:raise ValueError('REFERENCE_DUPLICATE')
            slot=None if not found else found[0];value=None;kind=1;output=tuple(v)
            if slot is not None:
                s=self.slots[slot];counts=[e['n'] for e in s['entries']]
                if len(counts)==2 and counts[0]==counts[1]:kind=2
                else:
                    value=max(range(len(counts)),key=lambda j:counts[j]);kind=3;output=tuple(s['entries'][value]['vector'])
            self.pending=dict(target=i+1,slot=slot,value=value,kind=kind,output=output)
        elif i%4==3:
            if self.t>=256:raise ValueError('REFERENCE_COUNTER')
            slot=self.pending['slot'];vb=bits(v)
            if slot is None:
                free=[j for j,s in enumerate(self.slots) if s is None]
                slot=free[0] if free else min(range(2),key=lambda j:(self.slots[j]['stamp'],j))
                self.slots[slot]=dict(key=bits(self.pair[0]+self.pair[1]),entries=[dict(vector=tuple(v),n=1)],stamp=self.t+1)
            else:
                s=self.slots[slot];found=[e for e in s['entries'] if bits(e['vector'])==vb]
                if len(found)>1:raise ValueError('REFERENCE_DUPLICATE_VALUE')
                if not found and len(s['entries'])==2:raise ValueError('F_VALUE_CAPACITY')
                if sum(e['n'] for e in s['entries'])>=256:raise ValueError('REFERENCE_COUNTER')
                if found:found[0]['n']+=1
                else:s['entries'].append(dict(vector=tuple(v),n=1))
                s['stamp']=self.t+1
            self.t+=1;self.pending=None;self.pair=[]
        else:self.pending=dict(target=i+1,slot=None,value=None,kind=4,output=tuple(v))
        self.i=i;return error
    def state(self):
        b=bytearray(4304)
        for j,s in enumerate(self.slots):
            if s is not None:
                o=1560*j;b[o:o+768]=s['key']
                for k,e in enumerate(s['entries']):
                    struct.pack_into('<48d',b,o+768+k*384,*e['vector']);struct.pack_into('<Q',b,o+1536+k*8,e['n'])
                struct.pack_into('<Q',b,o+1552,s['stamp'])
        struct.pack_into('<QQQ',b,3120,self.i,self.t,0 if self.pending is None else self.pending['target'])
        b[3144]=0 if self.pending is None else self.pending['kind'];b[3145]=b[3146]=255
        if self.pending:
            if self.pending['slot'] is not None:b[3145]=self.pending['slot']
            if self.pending['value'] is not None:b[3146]=self.pending['value']
            struct.pack_into('<48d',b,3920,*self.pending['output'])
        b[3147]=int(self.closed)+(2 if len(self.pair)>0 else 0)+(4 if len(self.pair)>1 else 0)
        for j,v in enumerate(self.pair):struct.pack_into('<48d',b,3152+j*384,*v)
        return bytes(b)
    def finish(self):
        try:
            if self.closed or self.i!=1024 or self.t!=256 or not self.pending or self.pending['kind']!=4 or self.pending['target']!=1025:raise ValueError('REFERENCE_FINISH')
        finally:self.close()
    def close(self):self.__init__();self.closed=True
