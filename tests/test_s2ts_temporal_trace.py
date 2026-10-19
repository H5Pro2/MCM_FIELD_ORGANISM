"""Focused neutral qualification of the private exact temporal trace."""
import unittest
from tools import _s2ts_temporal_trace as ts

P, S = "a" * 64, "neutral-session"

def frame(value, ordinal):
    return ts.Frame((float(value),) * 48, P, S, ordinal, ordinal * 4800, ordinal * 100)

class TemporalTraceTests(unittest.TestCase):
    def _trace(self, values=(1, 2, 3, 4)):
        state = ts.TemporalTrace(P, S)
        for ordinal, value in enumerate(values, 1):
            state.form(frame(value, ordinal))
        return state

    def test_order_and_fair_baselines(self):
        state = self._trace(); active = state._active
        self.assertEqual(state.hint(frame(2, 5)), None)
        self.assertEqual(state.hint(frame(3, 6))["decision"], "TRACE_MATCH")
        before = state._active
        self.assertEqual(state.hint(frame(3, 7)), None)
        self.assertIs(state._active, before)
        self.assertEqual(state.hint(frame(2, 8))["decision"], "ABSTAIN_ORDER_MISMATCH")
        self.assertFalse(state._hint)
        reverse = (frame(3, 7), frame(2, 8)); forward = (frame(2, 5), frame(3, 6))
        self.assertEqual(ts.unordered_membership(active, forward), ts.unordered_membership(active, reverse))

    def test_non_neighbor_duplicate_close_and_capacity(self):
        state = self._trace(); state.hint(frame(1, 5))
        self.assertEqual(state.hint(frame(3, 6))["decision"], "ABSTAIN_ORDER_MISMATCH")
        self.assertEqual(state.form(frame(5, 7)), "TRACE_CAPACITY_EXPIRED")
        self.assertEqual(state.hint(frame(2, 8)), None)
        self.assertEqual(state.hint(frame(3, 9))["decision"], "ABSTAIN_NO_TRACE")
        duplicate = self._trace((1, 2, 1, 2)); duplicate.hint(frame(1, 5))
        self.assertEqual(duplicate.hint(frame(2, 6))["decision"], "ABSTAIN_AMBIGUOUS_OFFSET")
        duplicate.close()
        with self.assertRaisesRegex(ts.S2TSError, "SESSION_CLOSED"):
            duplicate.hint(frame(1, 7))

    def test_hints_do_not_mutate_and_invalid_scope_rejected(self):
        state = self._trace(); before = state._active
        state.hint(frame(2, 5)); state.hint(frame(3, 6))
        self.assertIs(state._active, before)
        with self.assertRaisesRegex(ts.S2TSError, "FRAME_SCOPE_INVALID"):
            state.hint(ts.Frame((1.0,) * 48, P, "other", 7, 33600, 700))

if __name__ == "__main__":
    unittest.main()
