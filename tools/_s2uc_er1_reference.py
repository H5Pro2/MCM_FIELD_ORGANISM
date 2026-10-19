"""Independent ER1 observer: own stock, keys, cell history and U selection."""
import math
from tools._s2uc_er1_stock_reference import Reference as Stock

def mae(a,b):
    total=0.0
    for j in range(48):total=total+abs(a[j]-b[j])
    return total/48.0

class Reference:
    def __init__(self,mode):
        if mode not in ('E','F'):raise ValueError('MODE')
        self.mode=mode;self.stock=Stock(self.mode == 'E');self.cells={};self.pair=[]
        self.pending=None;self.index=0;self.closed=False

    @staticmethod
    def select(hypotheses, mode):
        if mode not in ('E', 'F'): raise ValueError('MODE')
        if not hypotheses: return None, 'NO_ELIGIBLE_CONTEXT'
        scores = [(h['before'][0]-h['before'][1], h['key']) for h in hypotheses if h['before'] is not None]
        if not scores: return None, 'COLD_ONLY'
        minimum = min(v for v, _ in scores)
        if minimum >= 0: return None, 'NO_ESTIMATED_IMPROVEMENT'
        winners = [k for v,k in scores if v == minimum]
        return (winners[0], 'SELECTED_BY_ERROR') if len(winners)==1 else (None, 'TIED_IMPROVEMENT')

    def live(self):
        return {(0,t['generation']) for t in self.stock.retained}|(
            set() if self.stock.candidate is None else {(1,self.stock.candidate['generation'])})

    def feedback(self,index,values):
        if not self.pending or self.pending['target']!=index:raise ValueError('REF_TICKET')
        pending=self.pending;updates=[]
        for h in pending['hypotheses']:
            key=h['key'];ec=mae(h['values'],values);ep=mae(pending['persistence'],values)
            live=key[:2] in self.live()
            if live:
                old=self.cells.get(key)
                self.cells[key]=(ec,ep) if old is None else (.5*old[0]+.5*ec,.5*old[1]+.5*ep)
            updates.append(dict(key=key,original=h['original'],live=live,ec=ec,ep=ep))
        error=mae(pending['output'],values);self.pending=None
        return dict(error=error,updates=updates)

    def perceive(self,index,values):
        if self.closed or index!=self.index+1:raise ValueError('REF_INDEX')
        self.index=index;self.pair.append((index,tuple(values)))
        if len(self.pair)<2:return None
        pair=tuple(v for _,v in self.pair);matches=[];hypotheses=[]
        traces=[(0,t) for t in self.stock.retained]+([] if self.stock.candidate is None else [(1,self.stock.candidate)])
        for role,t in traces:
            frames=t['frames']
            for off in range(3):
                factors=[]
                for exponent in (-1,0,1):
                    try:equal=all(math.ldexp(frames[off+k][1][j],exponent)==pair[k][j] for k in range(2) for j in range(48))
                    except OverflowError:equal=False
                    if equal:factors.append(math.ldexp(1.0,exponent))
                if not factors:continue
                key=(role,t['generation'],off)
                matches.append(dict(key=key,ordinals=[o for o,_ in frames],factors=factors))
                if factors==[1.0] and off<2:
                    hypotheses.append(dict(key=key,original=frames[off+2][0],values=frames[off+2][1],before=self.cells.get(key)))
        chosen, decision = self.select(hypotheses, self.mode)
        output=pair[-1] if chosen is None else next(h['values'] for h in hypotheses if h['key']==chosen)
        self.pending=dict(target=index+1,hypotheses=hypotheses,chosen=chosen,output=output,persistence=pair[-1])
        result=dict(matches=matches,decision=decision,**self.pending)
        before=self.stock.snapshot();old=self.stock.candidate
        for ordinal,vector in self.pair:self.stock.feed(ordinal,vector)
        after=self.stock.snapshot()
        promoted=next((t for t in after['retained'] if old and t['ordinals']==[o for o,_ in old['frames']] and
                       not any(t['generation']==b['generation'] for b in before['retained'])),None)
        if promoted:
            for key in list(self.cells):
                if key[:2]==(1,old['generation']):self.cells[(0,promoted['generation'],key[2])]=self.cells.pop(key)
        self.cells={k:v for k,v in self.cells.items() if k[:2] in self.live()}
        self.pair=[]
        return result

    def finish(self):
        if self.closed or self.pair or not self.pending or self.pending['target']!=self.index+1:raise ValueError('REF_FINISH')
        self.stock=Stock(self.mode == 'E');self.cells.clear();self.pending=None;self.closed=True
