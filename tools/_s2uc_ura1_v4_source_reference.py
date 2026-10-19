"""Independent URA1 source reconstruction; no production permutation/generator."""
import hashlib
import json
from collections import Counter
from tools._s2uc_ura1_v4_sources import gate


def verify(record,r,*,neutral=True,permit=None):
    gate(neutral,permit)
    if type(r) is not int or not 1<=r<=32:raise ValueError('REFERENCE_REPLICATE')
    counters={}
    def shuffle(sequence,name):
        result=list(sequence);cursor=0
        for length in range(len(result),1,-1):
            limit=((1<<64)//length)*length
            while True:
                if cursor==4096:raise ValueError('REFERENCE_DRAW_LIMIT')
                label='MCM-URA1/'+('neutral/v1' if neutral else 'source/v4')+'/r='+str(r)+'/stream='+name+'/draw='+str(cursor)
                value=int(hashlib.sha256(label.encode('ascii')).hexdigest()[:16],16);cursor+=1
                if value<limit:break
            index=value%length;last=result[length-1];result[length-1]=result[index];result[index]=last
        counters[name]=cursor;return result
    target=shuffle([3 for _ in range(128)]+[4 for _ in range(128)],'continuation');cue=[1 for _ in target]
    for val,name,n in [(3,'dependent-A',96 if r%2 else 32),(4,'dependent-B',32 if r%2 else 96)]:
        for pos in shuffle([i for i in range(256) if target[i]==val],name)[:n]:cue[pos]=0
    ids=[]
    for i in range(256):ids.extend([cue[i],2,target[i],5])
    expected=dict(replicate=r,orientation=(r-1)%2,neutral_only=neutral,
        catalog=[[float(base+j/4096) for j in range(48)] for base in (1/8,7/8,1/2,1/4,3/4,1/16)],ids=ids,draws=counters)
    encode=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
    if encode(record)!=encode(expected):raise ValueError('SOURCE_REFERENCE')
    actual=Counter(zip(ids[::4],ids[2::4]));want=(96,32,32,96) if r%2 else (32,96,96,32)
    if tuple(actual[k] for k in ((0,3),(0,4),(1,3),(1,4)))!=want:raise ValueError('CONTINGENCY')
    return dict(reference_equal=True,frames=1024,draws=counters,orientation=(r-1)%2)
