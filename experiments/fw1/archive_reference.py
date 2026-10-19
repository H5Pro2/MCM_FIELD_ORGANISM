"""Archive reference: independently detects refresh from its own stock transition."""
from tools._s2uc_er1_reference import Reference as Base

class Reference(Base):
    def __init__(self,mode):
        if mode not in ('KEEP','RESET'):raise ValueError('MODE')
        super().__init__('E');self.reset_enabled=mode=='RESET';self.resets=[]

    def perceive(self,index,values):
        old=dict(self.stock.observation_end)
        result=super().perceive(index,values)
        if self.reset_enabled:
            refreshed=[g for g,end in self.stock.observation_end.items() if g in old and old[g]!=end]
            if len(refreshed)>1:raise ValueError('ARCHIVE_REFRESH_AMBIGUOUS')
            for g in refreshed:
                if index%4 or self.stock.observation_end[g]!=index:raise ValueError('ARCHIVE_REFRESH_TIME')
                offsets=[];survivors={}
                for key,value in self.cells.items():
                    if key[0]==0 and key[1]==g:offsets.append(key[2])
                    else:survivors[key]=value
                self.cells=survivors
                self.resets.append(dict(end=index,generation=g,offsets=sorted(offsets),deleted=len(offsets)))
        return result
