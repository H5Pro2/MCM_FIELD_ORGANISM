import unittest
from tools import _s2tu_source_schedule as s
from tools import _s2tu_retained_trace as tu

class ScheduleTests(unittest.TestCase):
    def test_schedule_and_lifecycle_budget(self):
        bound=s.binding(); events=bound["events"]
        self.assertEqual((len(events),sum(x["source_id"] is not None for x in events)),(23,20))
        self.assertEqual(bound["lifecycle_calls"],dict(segment_closes=3,owner_close=1))
        self.assertEqual(bound["resources"]["active_peak_bytes"],5376)

    def test_neutral_full_chain_owner_close_and_readonly_results(self):
        store=tu.RetainedTraceStore("a"*64,"s2tu-owner-01"); values=dict(a=0.1,b=0.2,c=0.3,d=0.4); hints=[]
        for event in s.schedule():
            if event["kind"]=="FORMATION": store.form(tu.Frame((values[event["label"]],)*48,"a"*64,event["owner"],event["segment"],event["ordinal"]))
            elif event["kind"]=="SEGMENT_CLOSE": store.close_segment(event["segment"])
            else:
                result=store.hint(tu.Frame((values[event["label"]],)*48,"a"*64,event["owner"],event["segment"],event["ordinal"]))
                if result is not None: hints.append(result["decision"])
        self.assertEqual(hints,["TRACE_MATCH","TRACE_MATCH","ABSTAIN_NO_RETAINED_TRACE","ABSTAIN_AMBIGUOUS_RETAINED_TRACE"])
        self.assertEqual(store.generations,(2,3)); store.close_owner()
        with self.assertRaisesRegex(tu.S2TUError,"FRAME_SCOPE_INVALID"):
            store.hint(tu.Frame((0.1,)*48,"a"*64,"s2tu-owner-01","late",24))
