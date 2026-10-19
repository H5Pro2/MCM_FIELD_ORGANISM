import unittest

from tools import _s2tu_retained_trace as tu
from tools import _s2tw_exact_confirmation as tw


P = "a" * 64


def frame(value, segment, ordinal):
    return tu.Frame((float(value),) * 48, P, "owner", segment, ordinal)


class ExactConfirmationTests(unittest.TestCase):
    def close(self, store, segment, values, ordinal):
        for value in values:
            store.form(frame(value, segment, ordinal[0])); ordinal[0] += 1
        return store.close_segment(segment)

    def test_confirm_keeps_generation_and_fifo_age(self):
        store = tw.ExactConfirmationStore(P, "owner"); ordinal = [1]
        self.assertEqual(self.close(store, "p1", (1, 2, 3, 4), ordinal), {"action": "TRACE_RETAINED", "generation": 1, "evicted": None})
        self.assertEqual(self.close(store, "p2", (1, 2, 3, 4), ordinal), {"action": "TRACE_CONFIRMED", "generation": 1, "evicted": None})
        self.assertEqual(store.inventory, (1,))
        self.assertEqual(self.close(store, "p3", (4, 3, 2, 1), ordinal)["generation"], 2)
        receipt = self.close(store, "p4", (1, 2, 3, 5), ordinal)
        self.assertEqual((receipt["evicted"], store.inventory), (1, (2, 3)))

    def test_reverse_and_single_changed_value_do_not_confirm(self):
        store = tw.ExactConfirmationStore(P, "owner"); ordinal = [1]
        self.close(store, "p1", (1, 2, 3, 4), ordinal)
        self.assertEqual(self.close(store, "reverse", (4, 3, 2, 1), ordinal)["action"], "TRACE_RETAINED")
        store = tw.ExactConfirmationStore(P, "owner"); ordinal = [1]
        self.close(store, "p1", (1, 2, 3, 4), ordinal)
        self.assertEqual(self.close(store, "changed", (1, 2, 3, 5), ordinal)["action"], "TRACE_RETAINED")

    def test_hints_do_not_confirm_or_mutate(self):
        store = tw.ExactConfirmationStore(P, "owner"); ordinal = [1]
        self.close(store, "p1", (1, 2, 3, 4), ordinal); before = store.inventory
        store.hint(frame(2, "h", ordinal[0])); ordinal[0] += 1
        self.assertEqual(store.hint(frame(3, "h", ordinal[0]))["decision"], "TRACE_MATCH")
        self.assertEqual(store.inventory, before)
