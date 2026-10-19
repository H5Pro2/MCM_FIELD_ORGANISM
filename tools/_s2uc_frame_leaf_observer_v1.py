"""Versioned resource visitor: only validated immutable Frame payloads are leaves.
Original observer and every policy remain unchanged. No cache or trace filtering.
"""
import dataclasses
import sys
from pathlib import Path
from tools.s2uc_context_prediction_check import BudgetObserver
from tools._s2tu_retained_trace import Frame
from tools._s2uc_continuation_adapter import ContinuationAdapter
from tools._s2uc_factor_recency import FactorRecencyArm


def scalar_frame_leaf(x):
    return (type(x) is Frame and type(x.values) is tuple
        and len(x.values)==48 and all(type(v) is float for v in x.values)
        and type(x.profile) is str and type(x.owner) is str
        and type(x.segment) is str and type(x.ordinal) is int)


class FrameLeafBudgetObserver(BudgetObserver):
    def trace(self,frame,event,arg):
        names={'_s2uc_continuation_adapter.py','_s2uc_pair_context_adapter.py','_s2uc_factor_hint.py','_s2uc_perception_recency.py','_s2uc_four_arm.py','_s2uc_provisional_hint.py','_s2ub_candidate_confirmation.py'}
        if Path(frame.f_code.co_filename).name not in names:return None
        seen=set();frames=set();outputs=[]
        def visit(x):
            if id(x) in seen:return
            seen.add(id(x))
            if isinstance(x,Frame):frames.add(id(x))
            if scalar_frame_leaf(x):return
            if isinstance(x,ContinuationAdapter):
                if x.pending_prediction is not None:outputs.append(x.pending_prediction)
                visit(vars(x))
            elif isinstance(x,FactorRecencyArm):visit(vars(x))
            elif isinstance(x,dict):
                for v in x.values():visit(v)
            elif isinstance(x,(list,tuple)):
                for v in x:visit(v)
            elif dataclasses.is_dataclass(x) and not isinstance(x,type):
                for f in dataclasses.fields(x):visit(getattr(x,f.name))
        cursor=frame
        while cursor:
            if Path(cursor.f_code.co_filename).name in names:
                for x in cursor.f_locals.values():visit(x)
            cursor=cursor.f_back
        slots=max((1+(p.context_values is not None) for p in outputs),default=0)
        bytecost=max((sys.getsizeof(p)+sys.getsizeof(p.provenance_json)+sum(sys.getsizeof(v)+sum(sys.getsizeof(x) for x in v) for v in (p.context_values,p.persistence_values) if v is not None) for p in outputs),default=0)
        self.frame_peak=max(self.frame_peak,len(frames));self.output_slots_peak=max(self.output_slots_peak,slots);self.combined_peak=max(self.combined_peak,len(frames)+slots);self.output_python_bytes_peak=max(self.output_python_bytes_peak,bytecost);self.samples+=1
        assert len(frames)<=18 and slots<=2 and len(frames)+slots<=20
        return self.trace
