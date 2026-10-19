"""Bounded online G/P. No labels, history, source manifest or observer access."""
import math
import struct

class GlobalMean:
    def __init__(self):
        self.bank=bytearray(400);self.index=0;self.output=None
    def accept(self,index,values):
        if index!=self.index+1 or len(values)!=48 or not all(math.isfinite(v) for v in values):
            raise ValueError('G_INPUT')
        if index%2 and index>1:
            if self.output is None: raise ValueError('G_MISSING_FREEZE')
            self.output=None
        if index%4==3:
            n=struct.unpack_from('<Q',self.bank,384)[0]
            for j in range(48):
                v=values[j]
                if n:
                    old=struct.unpack_from('<d',self.bank,8*j)[0]
                    difference=v-old;increment=difference/float(n+1);v=old+increment
                if not math.isfinite(v): raise ValueError('G_NONFINITE')
                struct.pack_into('<d',self.bank,8*j,v)
            struct.pack_into('<Q',self.bank,384,n+1)
        if index%2==0:
            n=struct.unpack_from('<Q',self.bank,384)[0]
            self.output=struct.unpack_from('<48d',self.bank) if index%4==2 and n else values
        self.index=index
    def close(self):
        self.output=None;self.bank[:]=bytes(400)

class Persistence:
    def __init__(self): self.index=0;self.output=None
    def accept(self,index,values):
        if index!=self.index+1: raise ValueError('P_INPUT')
        self.output=values if index%2==0 else None
        self.index=index
    def close(self): self.output=None

class MeanReference:
    """Independent rational operation-by-operation IEEE rounding."""
    def __init__(self): self.n=0;self.mean=None;self.output=None
    def accept(self,i,v):
        from fractions import Fraction as F
        if i%4==3:
            if not self.n: self.mean=list(v)
            else:
                for j,value in enumerate(v):
                    subtract=float(F(value)-F(self.mean[j]))
                    divide=float(F(subtract)/F(self.n+1))
                    self.mean[j]=float(F(self.mean[j])+F(divide))
            self.n+=1
        self.output=tuple(self.mean) if i%4==2 and self.n else tuple(v) if i%2==0 else None
    def state(self):
        return bytes(384) if self.mean is None else struct.pack('<48d',*self.mean)

def bits(values): return None if values is None else struct.pack('<48d',*values).hex()
