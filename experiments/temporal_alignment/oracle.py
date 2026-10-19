"""Scalar independent alignment decision; imports no production alignment code."""
import math
EPS=float.fromhex('0x1.1a414d9cf9967p-15')
def decide(hint,sources,base_status):
    if base_status!='ABSTAIN_NO_APPROX_CONTEXT':return {'status':'NOT_ELIGIBLE','matches':[],'value':None}
    if any(math.fsum(abs(x) for x in v)/48<=EPS for v in hint):return {'status':'ABSTAIN_ALIGNMENT_LOW_SIGNAL','matches':[],'value':None}
    found=[]
    for index,source in enumerate(sources):
        values=source['values']
        for pos in range(21):
            if any(math.fsum(abs(x) for x in values[pos+10*j])/48<=EPS for j in (0,1)):continue
            scales=[]
            for factor in (.5,1.,2.):
                same=True
                for j in (0,1):
                    for component in range(48):
                        if values[pos+10*j][component]*factor!=hint[j][component]:same=False;break
                    if not same:break
                if same:scales.append(factor)
            if scales:found.append([index,pos,scales])
    value=None
    if not found:status='ABSTAIN_ALIGNMENT_NO_MATCH'
    elif len(set(x[0] for x in found))>1:status='ABSTAIN_TRACE_AMBIGUOUS'
    elif len(found)>1:status='ABSTAIN_ALIGNMENT_AMBIGUOUS'
    else:
        i,k,f=found[0]
        if f!=[1.]:status='FACTOR_CONTINUATION_NOT_SPECIFIED'
        elif k+20>=31:status='ABSTAIN_ALIGNMENT_NO_SUCCESSOR'
        else:status='PREDICTED_ALIGNMENT';value=tuple(sources[i]['values'][k+20])
    return dict(status=status,matches=found,value=value)
