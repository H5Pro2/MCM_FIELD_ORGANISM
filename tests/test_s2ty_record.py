import unittest
from tools import _s2ty_record as r
P="a"*64
def e(n,k,s,v=None):return dict(ordinal=n,kind=k,segment=s,values=None if v is None else (float(v),)*48)
class RecordTests(unittest.TestCase):
 def test_success_roundtrip_preserves_values_order_and_multiplicity(self):
  events=[e(1,"FORMATION","a",1),e(2,"FORMATION","a",1),e(3,"FORMATION","a",2),e(4,"FORMATION","a",3),e(5,"CLOSE","a")]
  record=r.build(events,P,"o");loaded=r.loads(r.dumps(record));self.assertEqual(loaded["result"]["status"],"COMPLETE");self.assertEqual(r.decode_events(loaded["inputs"]),events)
