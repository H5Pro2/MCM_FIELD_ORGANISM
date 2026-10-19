"""Independent read-only S2TX verifier."""
import json,math
from tools import _s2ts_temporal_trace_run as source
from tools import _s2tx_run as run
from tools import _s2tx_source_schedule as schedule
class S2TXVerificationError(ValueError): pass
def need(x,c):
 if not x: raise S2TXVerificationError(c)
def verify(record):
 need(record.get("status")=="RECORDING_COMPLETE","RECORDING_STATUS_INVALID"); bound=json.loads(run.canonical(schedule.binding())); need(record.get("binding")==bound and record.get("binding_digest")==run.digest(bound),"BINDING_INVALID"); need(record.get("counts")==dict(audio=22,nj=22,endpoints=22,formations=20,hints=2,segment_closes=5,owner_closes=2),"COUNTERS_INVALID")
 rows={r["ordinal"]:r for r in record["endpoints"]}; need(len(rows)==22,"ENDPOINT_COUNT_INVALID"); src,_=source.source_rows(); retained=[[],[]]; gen=[0,0]; forming=[{},{}]; hints=[{},{}]; trans=[]; decisions=[]
 def close(arm,frames):
  matches=[t for _,t in retained[arm] if t==tuple(frames)]
  if len(matches)==1:
   g=next(g for g,t in retained[arm] if t==tuple(frames))
   if arm: retained[arm]=[(x,y) for x,y in retained[arm] if x!=g]+[(g,tuple(frames))]; return dict(action="TRACE_CONFIRMED_RECENT",generation=g,evicted=None)
   return dict(action="TRACE_CONFIRMED",generation=g,evicted=None)
  need(not matches,"AMBIGUOUS_EQUALITY_INVALID"); gen[arm]+=1; ev=retained[arm][0][0] if len(retained[arm])==2 else None; retained[arm]=(retained[arm]+[(gen[arm],tuple(frames))])[-2:];return dict(action="TRACE_RETAINED",generation=gen[arm],evicted=ev)
 def read(arm,h):
  m=[[g,o] for g,t in retained[arm] for o in range(3) if t[o]==h[0] and t[o+1]==h[1]];return dict(decision="TRACE_MATCH" if len(m)==1 else "ABSTAIN_AMBIGUOUS_RETAINED_TRACE" if m else "ABSTAIN_NO_RETAINED_TRACE",matches=m)
 for e in bound["events"]:
  if e["kind"]=="SEGMENT_CLOSE":
   out=[]
   for arm in range(2): f=forming[arm].pop(e["segment"],None);need(f is not None and len(f)==4,"FORMATION_CHAIN_INVALID");out.append(close(arm,f))
   trans.append(dict(ordinal=e["ordinal"],unchanged=out[0],recent=out[1],unchanged_inventory=[g for g,_ in retained[0]],recent_inventory=[g for g,_ in retained[1]]));continue
  r=rows.get(e["ordinal"]);need(r and r["source_id"]==e["source_id"] and r["pcm_sha256"]==src[e["source_id"]]["pcm_sha256"] and r["payload_hash_checked"] is True,"SOURCE_BINDING_INVALID");v=tuple(float.fromhex(x) for x in r["values"]);need(len(v)==48 and all(math.isfinite(x) and 0<=x<=1 for x in v) and run.digest(r["values"])==r["value_digest"],"VALUE_INVALID")
  if e["kind"]=="FORMATION":
   for arm in range(2): forming[arm].setdefault(e["segment"],[]).append(v)
  else:
   out=[]
   for arm in range(2): hints[arm].setdefault(e["segment"],[]).append(v);h=hints[arm][e["segment"]];out.append(read(arm,tuple(h))) if len(h)==2 else None
   if out: decisions.append(dict(ordinal=e["ordinal"],unchanged=out[0],recent=out[1]))
 need(record["transitions"]==trans,"TRANSITIONS_INVALID");need(record["decisions"]==decisions,"DECISIONS_INVALID");need(record["inventories_before_owner_close"]==dict(unchanged=[2,3],recent=[3,4]) and record["owner_closed"] is True,"OWNER_CLOSE_INVALID");return dict(status="VERIFIED",read_only=True,transitions=5,decisions=1)
