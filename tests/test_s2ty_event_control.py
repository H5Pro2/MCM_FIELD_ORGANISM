import unittest
from unittest.mock import patch

from tools import _s2ty_event_control as c


P = "a" * 64


def e(n, kind, segment, value=None):
    return dict(
        ordinal=n,
        kind=kind,
        segment=segment,
        values=None if value is None else (float(value),) * 48,
    )


def complete_segment():
    return [
        e(1, "FORMATION", "a", 1),
        e(2, "FORMATION", "a", 2),
        e(3, "FORMATION", "a", 3),
        e(4, "FORMATION", "a", 4),
        e(5, "CLOSE", "a"),
    ]


class Tests(unittest.TestCase):
    def test_complete(self):
        result = c.run(complete_segment(), P, "o")
        self.assertEqual(result["status"], "COMPLETE")

    def test_primary_error(self):
        result = c.run([e(1, "CLOSE", "bad")], P, "o")
        self.assertEqual(
            (result["failure"]["phase"], result["failure"]["attempted"]),
            ("CLOSE", 1),
        )

    def test_owner_close_failure_without_primary_error_closes_direct_owner(self):
        result, direct_close_calls = self.run_with_broken_adapter_close(complete_segment())

        self.assertEqual(
            (
                result["status"],
                result["failure"]["phase"],
                result["failure"]["attempted"],
                result["failure"]["completed"],
            ),
            ("NOT_EVALUABLE", "OWNER_CLOSE", 5, 5),
        )
        self.assertTrue({item["arm"]: item["closed"] for item in result["owner_closes"]}["direct"])
        self.assertEqual(direct_close_calls, 1)

    def test_owner_close_failure_preserves_primary_error_and_closes_direct_owner(self):
        result, direct_close_calls = self.run_with_broken_adapter_close([e(1, "CLOSE", "bad")])

        self.assertEqual(
            (
                result["status"],
                result["failure"]["phase"],
                result["failure"]["attempted"],
                result["failure"]["completed"],
            ),
            ("NOT_EVALUABLE", "CLOSE", 1, 0),
        )
        self.assertNotIn("OWNER_CLOSE_FAILED", result["failure"]["code"])
        self.assertTrue({item["arm"]: item["closed"] for item in result["owner_closes"]}["direct"])
        self.assertEqual(direct_close_calls, 1)

    def run_with_broken_adapter_close(self, events):
        original_adapter = c.adapter.PerceptionTraceAdapter
        original_store = c.tw.ExactConfirmationStore

        class SpyStore(original_store):
            instances = []

            def __init__(self, *args):
                super().__init__(*args)
                self.close_calls = 0
                SpyStore.instances.append(self)

            def close_owner(self):
                self.close_calls += 1
                return super().close_owner()

        class BrokenAdapter(original_adapter):
            def __init__(self, *args):
                super().__init__(*args)
                self.store.close_owner = lambda: (_ for _ in ()).throw(RuntimeError("close"))

        with patch.object(c.tw, "ExactConfirmationStore", SpyStore), patch.object(
            c.adapter, "PerceptionTraceAdapter", BrokenAdapter
        ):
            result = c.run(events, P, "o")

        self.assertEqual(len(SpyStore.instances), 2)
        return result, SpyStore.instances[1].close_calls
