import unittest
from tools import _s2tu_retained_trace as tu

P, O = "a" * 64, "owner"


def frame(value, segment, ordinal):
    return tu.Frame((float(value),) * 48, P, O, segment, ordinal)


class RetainedTraceTests(unittest.TestCase):
    def form(self, store, segment, values, ordinal):
        for value in values:
            store.form(frame(value, segment, ordinal[0])); ordinal[0] += 1
        return store.close_segment(segment)

    def test_fifo_retention_order_and_readonly_hints(self):
        store = tu.RetainedTraceStore(P, O); ordinal = [1]
        self.assertEqual(self.form(store, "t1", (1,2,3,4), ordinal)["generation"], 1)
        self.assertEqual(self.form(store, "t2", (3,2,4,1), ordinal)["generation"], 2)
        store.hint(frame(2, "h1", ordinal[0])); ordinal[0] += 1
        self.assertEqual(store.hint(frame(3, "h1", ordinal[0]))["decision"], "TRACE_MATCH"); ordinal[0] += 1
        store.hint(frame(3, "h1", ordinal[0])); ordinal[0] += 1
        self.assertEqual(store.hint(frame(2, "h1", ordinal[0]))["decision"], "TRACE_MATCH"); ordinal[0] += 1
        receipt = self.form(store, "t3", (1,3,2,4), ordinal)
        self.assertEqual((receipt["evicted"], store.generations), (1, (2,3)))
        store.hint(frame(2, "h2", ordinal[0])); ordinal[0] += 1
        self.assertEqual(store.hint(frame(3, "h2", ordinal[0]))["decision"], "ABSTAIN_NO_RETAINED_TRACE"); ordinal[0] += 1
        store.hint(frame(3, "h2", ordinal[0])); ordinal[0] += 1
        self.assertEqual(store.hint(frame(2, "h2", ordinal[0]))["decision"], "ABSTAIN_AMBIGUOUS_RETAINED_TRACE")

    def test_owner_scope_and_close_reject_stale_access(self):
        store = tu.RetainedTraceStore(P, O)
        with self.assertRaisesRegex(tu.S2TUError, "FRAME_SCOPE_INVALID"):
            store.form(tu.Frame((1.0,) * 48, P, "other", "x", 1))
        store.close_owner()
        with self.assertRaisesRegex(tu.S2TUError, "FRAME_SCOPE_INVALID"):
            store.hint(frame(1, "x", 1))
