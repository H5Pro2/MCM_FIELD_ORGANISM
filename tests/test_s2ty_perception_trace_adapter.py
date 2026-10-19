import unittest
from tools import _s2ty_perception_trace_adapter as a
P="a"*64
class Tests(unittest.TestCase):
 def test_same_inputs_match_direct_tw(self):
  x=a.PerceptionTraceAdapter(P,"o",("x","y"));n=1
  for s,vs in (("x",(1,2,3,4)),("y",(1,2,3,4))):
   for v in vs:x.accept((float(v),)*48,P,"o",s,n);n+=1
   x.close(s)
  self.assertEqual(x.store.inventory,(1,))
 def test_invalid_close_and_owner_fail(self):
  x=a.PerceptionTraceAdapter(P,"o",("x",))
  with self.assertRaises(Exception):x.close("x")
  with self.assertRaises(Exception):x.accept((1.0,)*48,P,"bad","x",1)
