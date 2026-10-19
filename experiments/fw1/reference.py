"""Independent FW1 live reference: detects recurrence from incoming raw frames."""
from tools._s2uc_er1_reference import Reference as Base, mae

class Reference(Base):
    def __init__(self,mode):
        if mode not in ('KEEP','RESET'):raise ValueError('MODE')
        super().__init__('E');self.reset_enabled=mode=='RESET';self.resets=[]

    def perceive(self,index,values):
        generation=None
        if index%4==0:
            frames=self.stock.pending+self.pair+[(index,tuple(values))]
            if len(frames)!=4:raise ValueError('REFERENCE_BLOCK')
            candidates=[t for t in self.stock.retained if tuple(v for _,v in t['frames'])==tuple(v for _,v in frames)
                        and frames[0][0]>self.stock.observation_end[t['generation']]]
            if len(candidates)>1:raise ValueError('REFERENCE_AMBIGUOUS')
            if candidates:generation=candidates[0]['generation']
        result=super().perceive(index,values)
        if self.reset_enabled and generation is not None:
            removed=sorted(k for k in self.cells if k[:2]==(0,generation))
            self.resets.append(dict(end=index,generation=generation,offsets=[k[2] for k in removed],deleted=len(removed)))
            for k in removed:del self.cells[k]
        return result
