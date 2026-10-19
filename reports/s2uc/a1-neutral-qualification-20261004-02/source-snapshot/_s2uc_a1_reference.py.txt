"""Observer A1 state machine: no production adapter or admission calls."""
import math
from tools._s2uc_k1_reference import Reference as UReference


class Reference(UReference):
    def __init__(self):super().__init__(False)

    def preforecast(self,pair):
        options=[]
        traces=[(0,t) for t in self.retained]+([] if self.candidate is None else [(1,self.candidate)])
        for role,t in traces:
            for offset in (0,1):
                scales=[e for e in (-1,0,1) if all(math.ldexp(x,e)==y
                    for j in (0,1) for x,y in zip(t['frames'][offset+j][1],pair[j][1]))]
                if scales==[0]:options.append((role,t,offset))
        if len(options)!=1 or options[0][0]!=1:return None
        role,c,off=options[0]
        if min(o for o,_ in pair)<=c['frames'][-1][0]:return None
        observed=self.pending+pair
        if len(observed)==4 and any(self.payload(t)==tuple(v for _,v in observed) for _,t in traces):return None
        victim=self.retained.pop(0) if len(self.retained)==2 else None
        if victim is not None:del self.observation_end[victim['generation']]
        self.retained_serial+=1
        self.retained.append(dict(generation=self.retained_serial,frames=c['frames']))
        self.observation_end[self.retained_serial]=c['frames'][-1][0]
        self.candidate=None
        return dict(reason='PARTIAL_RETRIEVAL_ADMISSION',full_repeat=False,ordinals=[o for o,_ in c['frames']],offset=off,
            hints=[o for o,_ in pair],old_key=[1,c['generation']],new_key=[0,self.retained_serial],
            victim=None if victim is None else dict(generation=victim['generation'],ordinals=[o for o,_ in victim['frames']]))
