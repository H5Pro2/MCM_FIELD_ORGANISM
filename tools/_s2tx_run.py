"""One bounded S2TX comparison run."""
import hashlib,json
from pathlib import Path
from tools import _s2ts_temporal_trace_run as source
from tools import _s2tw_exact_confirmation as base
from tools import _s2tx_recency_confirmation as recent
from tools import _s2tx_source_schedule as schedule
from tools import _s2tu_retained_trace as tu
from tools import _s2tx_qualification_gate as qualification

RUN_ID="s2tx-recency-confirmation-real-20260919-01"; MAIN_GATE=False; USED=False; LIMIT=262144; QUALIFICATION_RECEIPT=None
def canonical(x): return json.dumps(x,allow_nan=False,sort_keys=True,separators=(",",":")).encode()
def digest(x): return hashlib.sha256(canonical(x)).hexdigest()
def run_once(out:Path):
 global MAIN_GATE,USED
 if not MAIN_GATE or USED or out.exists(): raise ValueError("RUN_NOT_AUTHORIZED")
 qualification.authorize(Path(__file__).resolve().parents[1], QUALIFICATION_RECEIPT)
 USED=True; phase="BINDING"; counts=dict(audio=0,nj=0,endpoints=0,formations=0,hints=0,segment_closes=0,owner_closes=0); progress={"ordinal":0,"source_id":None}
 try:
  bound=schedule.binding(); sources,plan=source.source_rows(); profile=bound["profile"]
  import numpy as np
  from mcm_field_organism.log_spectral_receptor import LogSpectralConfig,LogSpectralReceptor
  from mcm_field_organism.broadband_hearing_path import AuditoryReceptorContact,AuditoryReceptorState
  from tools import _s2nj_private_auditory_output_projection as nj
  receptor=LogSpectralReceptor(LogSpectralConfig(**plan["profiles"]["raw"]["config"])); old=base.ExactConfirmationStore(profile,"s2tx-old"); new=recent.RecencyConfirmationStore(profile,"s2tx-new"); endpoints=[]; transitions=[]; decisions=[]
  for event in bound["events"]:
   progress={"ordinal":event["ordinal"],"source_id":event["source_id"]}
   if event["kind"]=="SEGMENT_CLOSE":
    phase="CLOSE"; a=old.close_segment(event["segment"]); b=new.close_segment(event["segment"]); transitions.append(dict(ordinal=event["ordinal"],unchanged=a,recent=b,unchanged_inventory=list(old.inventory),recent_inventory=list(new.inventory))); counts["segment_closes"]+=1; continue
   item=sources[event["source_id"]]; phase="PCM"; payload=source.nu.pcm_window(source.nu.WindowSpec(int(item["stream_id"][1:]),int(item["window_ordinal"])))
   if hashlib.sha256(payload).hexdigest()!=item["pcm_sha256"]: raise ValueError("PCM_HASH_INVALID")
   phase="RECEPTOR"; raw=receptor.analyze(np.frombuffer(payload,dtype="<f4")); counts["audio"]+=1
   state=AuditoryReceptorState("auditory",nj.RAW_GEOMETRY,int(item["nj_snapshot_index"]),int(item["window_start_sample"]),int(item["window_end_sample"]),receptor.channel_ids,raw,AuditoryReceptorContact.ACTIVE_ENERGY if any(raw) else AuditoryReceptorContact.ACTIVE_ZERO)
   phase="NJ"; half=nj.project_auditory_half_v1(state,config=receptor.config,source_profile_digest=nj.RAW_PROFILE_DIGEST); counts["nj"]+=1; counts["endpoints"]+=1; values=[v.hex() for v in half.values]; endpoints.append(dict(ordinal=event["ordinal"],source_id=event["source_id"],pcm_sha256=item["pcm_sha256"],payload_hash_checked=True,values=values,value_digest=digest(values)))
   f1=tu.Frame(tuple(half.values),profile,"s2tx-old",event["segment"],event["ordinal"]); f2=tu.Frame(tuple(half.values),profile,"s2tx-new",event["segment"],event["ordinal"]); a=old.form(f1) if event["kind"]=="FORMATION" else old.hint(f1); b=new.form(f2) if event["kind"]=="FORMATION" else new.hint(f2)
   if event["kind"]=="FORMATION": counts["formations"]+=1
   else:
    counts["hints"]+=1
    if a is not None: decisions.append(dict(ordinal=event["ordinal"],unchanged=a,recent=b))
  before=dict(unchanged=list(old.inventory),recent=list(new.inventory)); old.close_owner();new.close_owner();counts["owner_closes"]=2; record=dict(status="RECORDING_COMPLETE",run_id=RUN_ID,binding=bound,binding_digest=digest(bound),counts=counts,endpoints=endpoints,transitions=transitions,decisions=decisions,inventories_before_owner_close=before,owner_closed=True)
 except Exception as e: record=dict(status="NOT_EVALUABLE",run_id=RUN_ID,counts=counts,failure=dict(phase=phase,code=type(e).__name__+":"+str(e),progress=progress))
 finally: MAIN_GATE=False
 data=canonical(record)
 if len(data)>LIMIT: raise ValueError("RECORD_SIZE_LIMIT")
 out.mkdir();(out/"record.json").write_bytes(data);return record
