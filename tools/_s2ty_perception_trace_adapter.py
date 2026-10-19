"""Bound handoff from existing NJ half-profile states to S2TW traces."""
from tools import _s2tu_retained_trace as tu
from tools import _s2tw_exact_confirmation as tw

class S2TYError(ValueError): pass
class PerceptionTraceAdapter:
 def __init__(self,profile,owner,segments):
  self.store=tw.ExactConfirmationStore(profile,owner);self.segments=set(segments);self.closed=set()
 def accept(self,values,profile,owner,segment,ordinal):
  if segment not in self.segments or segment in self.closed: raise S2TYError("SEGMENT_INVALID")
  return self.store.form(tu.Frame(tuple(values),profile,owner,segment,ordinal))
 def close(self,segment):
  if segment not in self.segments or segment in self.closed: raise S2TYError("CLOSE_INVALID")
  self.closed.add(segment);return self.store.close_segment(segment)
 def hint(self,values,profile,owner,segment,ordinal): return self.store.hint(tu.Frame(tuple(values),profile,owner,segment,ordinal))
