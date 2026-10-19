"""Independent object-state reference; no imports from production H."""
import struct
from fractions import Fraction as F

class Reference:
    def __init__(self):
        self.slots=[None,None];self.i=0;self.t=0;self.pair=[];self.pending=None;self.closed=False
    def accept(self,i,v):
        error=None
        if self.pending is not None and i==self.pending['target']:
            total=0.0
            for a,b in zip(self.pending['output'],v,strict=True):
                total=float(F(total)+F(abs(float(F(a)-F(b)))))
            error=float(F(total)/48)
        if i%4==1:self.pending=None;self.pair=[tuple(v)]
        elif i%4==2:
            self.pair.append(tuple(v));key=b''.join(struct.pack('<d',x) for frame in self.pair for x in frame)
            matches=[j for j,s in enumerate(self.slots) if s is not None and s['key']==key]
            slot=matches[0] if matches else None
            self.pending=dict(target=i+1,slot=slot,kind=1 if matches else 2,
                output=tuple(self.slots[slot]['mean']) if matches else tuple(v))
        elif i%4==3:
            j=self.pending['slot'];self.t+=1
            if j is None:
                free=[j for j,s in enumerate(self.slots) if s is None]
                j=free[0] if free else sorted(range(2),key=lambda j:(self.slots[j]['stamp'],j))[0]
                self.slots[j]=dict(key=b''.join(struct.pack('<d',x) for f in self.pair for x in f),mean=list(v),n=1,stamp=self.t)
            else:
                s=self.slots[j];n=s['n']+1
                for k in range(48):
                    a=float(F(v[k])-F(s['mean'][k]));b=float(F(a)/n);s['mean'][k]=float(F(s['mean'][k])+F(b))
                s['n']=n;s['stamp']=self.t
            self.pending=None;self.pair=[]
        else:self.pending=dict(target=i+1,slot=None,kind=3,output=tuple(v))
        self.i=i;return error
    def state(self):
        b=bytearray(3520)
        for j,s in enumerate(self.slots):
            if s:
                o=1168*j;b[o:o+768]=s['key'];struct.pack_into('<48dQQ',b,o+768,*s['mean'],s['n'],s['stamp'])
        struct.pack_into('<QQQ',b,2336,self.i,self.t,0 if self.pending is None else self.pending['target'])
        b[2360]=0 if self.pending is None else self.pending['kind']
        b[2361]=255 if self.i or self.pending else 0
        if self.pending and self.pending['slot'] is not None:b[2361]=self.pending['slot']
        b[2362]=int(self.closed);b[2363]=len(self.pair)
        for j,v in enumerate(self.pair):struct.pack_into('<48d',b,2368+384*j,*v)
        if self.pending:struct.pack_into('<48d',b,3136,*self.pending['output'])
        return bytes(b)
    def close(self):
        self.__init__();self.closed=True
