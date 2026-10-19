import json
import unittest

from tools import _s2ty_record as r
from tools import _s2ty_record_verification as v


P = "a" * 64


def e(n, kind, segment, value=None):
    return dict(
        ordinal=n,
        kind=kind,
        segment=segment,
        values=None if value is None else (float(value),) * 48,
    )


def append_formation(rows, ordinal, segment, values):
    for value in values:
        rows.append(e(ordinal, "FORMATION", segment, value))
        ordinal += 1
    rows.append(e(ordinal, "CLOSE", segment))
    return ordinal + 1


def fixture():
    rows = []
    ordinal = append_formation(rows, 1, "a", (1, 2, 3, 4))
    ordinal = append_formation(rows, ordinal, "b", (5, 6, 7, 8))
    rows.extend([e(ordinal, "HINT", "h", 2), e(ordinal + 1, "HINT", "h", 3)])
    append_formation(rows, ordinal + 2, "c", (9, 10, 11, 12))
    return r.dumps(r.build(rows, P, "o"))


def exact_confirmation_fixture():
    rows = []
    ordinal = append_formation(rows, 1, "a", (1, 2, 3, 4))
    ordinal = append_formation(rows, ordinal, "b", (5, 6, 7, 8))
    append_formation(rows, ordinal, "a-repeat", (1, 2, 3, 4))
    return r.dumps(r.build(rows, P, "o"))


class Tests(unittest.TestCase):
    def test_full_flow(self):
        self.assertEqual(v.verify(fixture())["status"], "VERIFIED")

    def test_manipulated_receipts_and_inventory_fail(self):
        for path in (("events", 0, "adapter"), ("owner_closes", 0, "before")):
            document = json.loads(fixture())
            key, index, field = path
            document["result"][key][index][field] = [] if key == "owner_closes" else "bad"
            with self.subTest(path=path):
                with self.assertRaises(v.Error):
                    v.verify(r.dumps(document))

    def test_order_and_status_fail(self):
        document = json.loads(fixture())
        document["inputs"][1]["ordinal"] = 1
        with self.assertRaises(v.Error):
            v.verify(r.dumps(document))

    def test_inner_success_status_mismatch_is_rejected(self):
        document = json.loads(fixture())
        document["result"]["status"] = "NOT_EVALUABLE"
        with self.assertRaises(v.Error):
            v.verify(r.dumps(document))

    def test_exact_confirmation_keeps_generation_and_fifo_position(self):
        document = json.loads(exact_confirmation_fixture())
        confirmation = document["result"]["events"][14]
        self.assertEqual(confirmation["ordinal"], 15)
        self.assertEqual(
            confirmation["direct"],
            {"action": "TRACE_CONFIRMED", "generation": 1, "evicted": None},
        )
        self.assertEqual(document["result"]["owner_closes"][0]["before"], [1, 2])
        self.assertEqual(v.verify(r.dumps(document))["inventory"], [1, 2])

        confirmation["direct"]["action"] = "TRACE_RETAINED"
        with self.assertRaises(v.Error):
            v.verify(r.dumps(document))

    def test_direct_hint_decision_before_eviction_is_verified(self):
        document = json.loads(fixture())
        hint_receipt = document["result"]["events"][11]
        self.assertEqual(hint_receipt["ordinal"], 12)
        self.assertEqual(hint_receipt["direct"]["decision"], "TRACE_MATCH")
        self.assertEqual(hint_receipt["direct"]["matches"], [[1, 1]])

        hint_receipt["direct"]["decision"] = "ABSTAIN_NO_RETAINED_TRACE"
        with self.assertRaises(v.Error):
            v.verify(r.dumps(document))

    def test_eviction_manipulation_fails(self):
        document = json.loads(fixture())
        document["result"]["events"][16]["direct"]["evicted"] = 99
        with self.assertRaises(v.Error):
            v.verify(r.dumps(document))

    def test_duplicate_owner_arm_is_rejected(self):
        document = json.loads(fixture())
        document["result"]["owner_closes"][1]["arm"] = "adapter"
        with self.assertRaises(v.Error):
            v.verify(r.dumps(document))

    def test_missing_owner_arm_is_rejected(self):
        document = json.loads(fixture())
        document["result"]["owner_closes"].pop()
        with self.assertRaises(v.Error):
            v.verify(r.dumps(document))

    def test_unknown_owner_arm_is_rejected(self):
        document = json.loads(fixture())
        document["result"]["owner_closes"][1]["arm"] = "unknown"
        with self.assertRaises(v.Error):
            v.verify(r.dumps(document))
