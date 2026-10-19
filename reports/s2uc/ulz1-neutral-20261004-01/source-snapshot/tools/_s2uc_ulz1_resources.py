"""Observer accounting only: identical traversal and meter for both arms."""
import sys
from tools._s2uc_multi_observer import Meter as BaseMeter
from tools._s2tu_retained_trace import Frame

def deep(value, seen=None):
    if seen is None: seen=set()
    if id(value) in seen or value is None:return 0
    seen.add(id(value));n=sys.getsizeof(value)
    if isinstance(value,dict):
        return n+sum(deep(k,seen)+deep(v,seen) for k,v in value.items())
    if isinstance(value,(tuple,list,set)):
        return n+sum(deep(v,seen) for v in value)
    if hasattr(value,'__dict__'):n+=deep(vars(value),seen)
    for slot in getattr(type(value),'__slots__',()):
        if slot not in ('__dict__','__weakref__') and hasattr(value,slot):n+=deep(getattr(value,slot),seen)
    return n

class Meter(BaseMeter):
    def __init__(self,a):
        super().__init__(a)
        self.boundary=[]
        self.phase={}

    def capture(self,name):
        a=self.a
        frames=list(a.pair)+list(a.arm._forming)+list(a.arm._hints)
        for _,_,fs in a._sources():frames.extend(fs)
        frames.extend(x for x in a._frozen if x is not None)
        if a._pframe is not None:frames.append(a._pframe)
        union={id(f):f for f in frames}
        outputs=[] if a.pending_prediction is None else [a.pending_prediction.persistence_values]
        if a.pending_prediction is not None and a.pending_prediction.context_values is not None:
            outputs.append(a.pending_prediction.context_values)
        # Deep whole-arm includes original frames and metadata, unlike the additional-heap cap.
        row=dict(phase=name,originals=len(union),ordinals=sorted(f.ordinal for f in union.values()),
                 valid_cells=sum(bool(a.bank[i*32+27]) for i in range(6)),
                 system_reachable_bytes=deep(a),base_arm_bytes=deep(a.arm),
                 original_payload_bytes=384*len(union),original_objects_bytes=deep(list(union.values())),
                 output_slots=len(outputs),output_payload_equivalent=384*len(outputs),
                 output_new_payloads=sum(all(v is not f.values for f in union.values()) for v in outputs))
        self.boundary.append(row)

    def measure(self,name,operation):
        self.capture(name+':before')
        try:return super().measure(name,operation)
        finally:
            self.capture(name+':after')
            if self.calls:
                c=self.calls[-1]
                self.phase[name]={k:max(self.phase.get(name,{}).get(k,0),c[k]) for k in ('retained','transient','total')}

    def snapshot(self):
        return super().snapshot()|dict(phase_peaks=self.phase,boundary_peaks={
            k:max((r[k] for r in self.boundary),default=0) for k in
            ('originals','valid_cells','system_reachable_bytes','base_arm_bytes','original_payload_bytes',
             'original_objects_bytes','output_slots','output_payload_equivalent','output_new_payloads')},
            allocation_boundaries=self.boundary,
            limits_note='Boundary census is not an intra-operation whole-process peak; additional heap includes operation transients.')
