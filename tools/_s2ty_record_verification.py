"""Independent functional verifier for canonical S2TY success records."""
from __future__ import annotations
import math
from tools import _s2ty_record as record
class Error(ValueError): pass
def need(ok,code):
 if not ok: raise Error(code)
def decision(retained,h):
 m=[[g,i] for g,t in retained for i in range(3) if t[i]==h[0] and t[i+1]==h[1]]
 return {"decision":"TRACE_MATCH" if len(m)==1 else "ABSTAIN_AMBIGUOUS_RETAINED_TRACE" if m else "ABSTAIN_NO_RETAINED_TRACE","matches":m}
def verify(data):
 r=record.loads(data);inputs=record.decode_events(r["inputs"]);res=r["result"];need(r["status"]=="COMPLETE" and res["status"]=="COMPLETE" and res["failure"] is None and res["completed"]==len(inputs) and res["attempted"]==inputs[-1]["ordinal"],"STATUS_INVALID")
 retained=[];forming={};hints={};gen=0;expected=[];last=0
 for e in inputs:
  need(e["ordinal"]>last,"ORDER_INVALID");last=e["ordinal"];kind=e["kind"]
  if kind=="CLOSE":
   f=forming.pop(e["segment"],None);need(f is not None and len(f)==4,"FORMATION_INVALID");same=[x for x in retained if x[1]==tuple(f)]
   if len(same)==1:x={"action":"TRACE_CONFIRMED","generation":same[0][0],"evicted":None}
   else:
    need(not same,"AMBIGUOUS_INVALID");gen+=1;ev=retained[0][0] if len(retained)==2 else None;retained=(retained+[(gen,tuple(f))])[-2:];x={"action":"TRACE_RETAINED","generation":gen,"evicted":ev}
  else:
   v=e["values"];need(kind in {"FORMATION","HINT"} and len(v)==48 and all(math.isfinite(z) for z in v),"VALUE_INVALID")
   if kind=="FORMATION":forming.setdefault(e["segment"],[]).append(v);x="TRACE_COMPLETE" if len(forming[e["segment"]])==4 else "TRACE_FORMING"
   else:
    hints.setdefault(e["segment"],[]).append(v);h=hints[e["segment"]];x=decision(retained,tuple(h)) if len(h)==2 else None
    if len(h)==2:hints[e["segment"]]=[]
  expected.append((e["ordinal"],x,x))
 need([(x["ordinal"],x["adapter"],x["direct"]) for x in res["events"]]==expected,"ARM_RECEIPT_INVALID")
 need(len(res["owner_closes"])==2 and {x.get("arm") for x in res["owner_closes"]}=={"adapter","direct"} and all(x.get("closed") for x in res["owner_closes"]),"OWNER_CLOSE_INVALID")
 need([x.get("before") for x in res["owner_closes"]]==[[g for g,_ in retained],[g for g,_ in retained]],"INVENTORY_INVALID")
 return {"status":"VERIFIED","events":len(expected),"inventory":[g for g,_ in retained]}
