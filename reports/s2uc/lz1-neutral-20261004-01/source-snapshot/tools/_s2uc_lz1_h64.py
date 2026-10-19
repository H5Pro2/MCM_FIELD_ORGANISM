"""Past-only comparison baseline; not part of the MCM policy."""
from array import array
import struct

VECTOR=struct.Struct('<48d')
PAIR=struct.Struct('<96d')
STRIDE=1152

class H64:
    def __init__(self):
        self.ring=bytearray(64*STRIDE)
        self.count=0
        self.pending=None
        self.output=None
        self.winner=None

    def predict(self,first,second):
        if self.pending is not None:raise ValueError('H64_PENDING')
        pair=PAIR.pack(*first,*second)
        counts=array('Q',[0])*64
        view=memoryview(self.ring)
        valid=min(self.count,64)
        for i in range(valid):
            base=i*STRIDE
            if view[base:base+768]!=pair:continue
            target=view[base+768:base+STRIDE]
            previous=next((j for j in range(i) if counts[j] and view[j*STRIDE+768:(j+1)*STRIDE]==target),None)
            counts[i if previous is None else previous]+=1
        best=max(counts)
        winners=[i for i,n in enumerate(counts) if n==best] if best else []
        self.pending=pair
        self.winner=winners[0] if len(winners)==1 else None
        self.output=tuple(second) if self.winner is None else VECTOR.unpack_from(self.ring,self.winner*STRIDE+768)
        return self.output

    def feedback(self,target):
        if self.pending is None:raise ValueError('H64_NO_PENDING')
        base=(self.count%64)*STRIDE
        self.ring[base:base+STRIDE]=self.pending+VECTOR.pack(*target)
        self.count+=1
        self.pending=self.output=self.winner=None

    def close(self):
        empty=bytes(STRIDE)
        for i in range(64):self.ring[i*STRIDE:(i+1)*STRIDE]=empty
        self.pending=self.output=self.winner=None

