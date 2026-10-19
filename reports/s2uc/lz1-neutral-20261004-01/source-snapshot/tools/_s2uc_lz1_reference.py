"""Observer-only H64 model: deque and tuple counting, no packed-ring imports."""
from collections import Counter,deque

class H64Reference:
    def __init__(self):
        self.records=deque(maxlen=64)
        self.pending=None
        self.count=0

    def predict(self,first,second):
        if self.pending is not None:raise ValueError('REFERENCE_PENDING')
        self.pending=(tuple(first),tuple(second))
        counts=Counter(t for a,b,t in self.records if (a,b)==self.pending)
        high=max(counts.values(),default=0)
        options=[v for v,n in counts.items() if n==high]
        return options[0] if len(options)==1 else tuple(second)

    def feedback(self,target):
        if self.pending is None:raise ValueError('REFERENCE_NO_PENDING')
        self.records.append((*self.pending,tuple(target)))
        self.count+=1
        self.pending=None
