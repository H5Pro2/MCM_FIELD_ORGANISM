import unittest
from tools import _s2tu_retained_trace as tu
from tools import _s2tx_recency_confirmation as tx
P="a"*64
def frame(v,s,n): return tu.Frame((float(v),)*48,P,"owner",s,n)
class RecencyTests(unittest.TestCase):
 def close(self,s,seg,vs,n):
  for v in vs: s.form(frame(v,seg,n[0]));n[0]+=1
  return s.close_segment(seg)
 def test_exact_confirm_recent(self):
  s=tx.RecencyConfirmationStore(P,"owner");n=[1];self.close(s,"a",(1,2,3,4),n);self.close(s,"b",(5,6,7,8),n);r=self.close(s,"c",(1,2,3,4),n);self.assertEqual((r["action"],r["generation"],s.inventory),("TRACE_CONFIRMED_RECENT",1,(2,1)))
 def test_reverse(self):
  s=tx.RecencyConfirmationStore(P,"owner");n=[1];self.close(s,"a",(1,2,3,4),n);self.assertEqual(self.close(s,"r",(4,3,2,1),n)["action"],"TRACE_RETAINED")
 def test_partial_single_value(self):
  s=tx.RecencyConfirmationStore(P,"owner");n=[1];self.close(s,"a",(1,2,3,4),n);self.assertEqual(self.close(s,"p",(1,2,3,5),n)["action"],"TRACE_RETAINED")
 def test_incomplete(self):
  s=tx.RecencyConfirmationStore(P,"owner");n=[1]
  for v in (1,2,3): s.form(frame(v,"i",n[0]));n[0]+=1
  self.assertEqual(s.close_segment("i")["action"],"TRACE_DISCARDED_INCOMPLETE")
 def test_ambiguous(self):
  s=tx.RecencyConfirmationStore(P,"owner");n=[1];self.close(s,"a",(1,2,3,4),n);self.close(s,"b",(5,6,7,8),n);s._retained.append(s._retained[0]);self.assertEqual(self.close(s,"c",(1,2,3,4),n)["action"],"CONFIRMATION_AMBIGUOUS_EXISTING_TRACE")
 def test_hint_readonly(self):
  s=tx.RecencyConfirmationStore(P,"owner");n=[1];self.close(s,"a",(1,2,3,4),n);before=s.inventory;s.hint(frame(2,"h",n[0]));n[0]+=1;s.hint(frame(3,"h",n[0]));self.assertEqual(s.inventory,before)
