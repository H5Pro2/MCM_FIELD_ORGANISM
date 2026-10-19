"""Neutral S2TY event control over pre-materialized half-profile values."""
from tools import _s2tu_retained_trace as tu
from tools import _s2tw_exact_confirmation as tw
from tools import _s2ty_perception_trace_adapter as adapter

VALID={"FORMATION","HINT","CLOSE"}
def _owners(owner):
 if type(owner) is str:return owner,owner
 if type(owner) is dict and set(owner)=={"adapter","direct"} and all(type(value) is str and value for value in owner.values()):return owner["adapter"],owner["direct"]
 raise ValueError("OWNER_INVALID")
def _snapshot(store):
 if store is None:return None
 return dict(generations=list(store.generations),forming=sorted((segment,len(frames)) for segment,frames in store._forming.items()),hints=sorted((segment,len(frames)) for segment,frames in store._hints.items()))
def _progress(a,d,adapter_returns,direct_returns,completed,last_completed,attempted_event,attempt_before):
 adapter_state,direct_state=_snapshot(a.store if a else None),_snapshot(d)
 return dict(last_completed_ordinal=last_completed,attempted_event=attempted_event,arms=dict(adapter=dict(returned_steps=adapter_returns,state=adapter_state,changed_without_return=adapter_returns==completed and attempt_before is not None and adapter_state!=attempt_before["adapter"]),direct=dict(returned_steps=direct_returns,state=direct_state,changed_without_return=direct_returns==completed and attempt_before is not None and direct_state!=attempt_before["direct"])))
def run(events,profile,owner):
 attempted=completed=adapter_returns=direct_returns=0;last_completed=None;out=[];failure=None;a=d=None;phase="INITIALIZATION";attempted_event=None;attempt_before=None
 try:
  adapter_owner,direct_owner=_owners(owner)
  segments={e["segment"] for e in events if e.get("kind") in {"FORMATION","CLOSE"}}
  a=adapter.PerceptionTraceAdapter(profile,adapter_owner,segments);d=tw.ExactConfirmationStore(profile,direct_owner)
  for e in events:
   attempted=e["ordinal"];phase=e.get("kind");attempted_event=dict(ordinal=e["ordinal"],kind=e.get("kind"),segment=e.get("segment"))
   attempt_before=dict(adapter=_snapshot(a.store),direct=_snapshot(d))
   if e.get("kind") not in VALID: raise ValueError("EVENT_KIND_INVALID")
   if e["kind"]=="CLOSE": x=a.close(e["segment"])
   else:
    f=tu.Frame(tuple(e["values"]),profile,direct_owner,e["segment"],e["ordinal"])
    x=a.accept(f.values,profile,adapter_owner,e["segment"],e["ordinal"]) if e["kind"]=="FORMATION" else a.hint(f.values,profile,adapter_owner,e["segment"],e["ordinal"])
   adapter_returns+=1
   y=d.close_segment(e["segment"]) if e["kind"]=="CLOSE" else d.form(f) if e["kind"]=="FORMATION" else d.hint(f)
   direct_returns+=1;out.append(dict(ordinal=attempted,adapter=x,direct=y));completed+=1;last_completed=attempted
 except Exception as exc: failure=dict(code=type(exc).__name__+":"+str(exc),phase=phase,attempted=attempted,completed=completed,progress=_progress(a,d,adapter_returns,direct_returns,completed,last_completed,attempted_event,attempt_before))
 finally:
  closes=[]
  for arm,store in (("adapter",a.store if a else None),("direct",d)):
   if store:
    receipt=dict(arm=arm,before=list(store.generations),closed=False)
    try: store.close_owner();receipt["closed"]=True
    except Exception as exc:
     receipt["error"]=type(exc).__name__+":"+str(exc)
     if failure is None: failure=dict(code="OWNER_CLOSE_FAILED:"+type(exc).__name__+":"+str(exc),phase="OWNER_CLOSE",attempted=attempted,completed=completed,progress=_progress(a,d,adapter_returns,direct_returns,completed,last_completed,None,dict(adapter=_snapshot(a.store if a else None),direct=_snapshot(d))))
    closes.append(receipt)
 return dict(status="NOT_EVALUABLE" if failure else "COMPLETE",attempted=attempted,completed=completed,events=out,failure=failure,owner_closes=closes)
