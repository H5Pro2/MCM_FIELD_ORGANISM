import json
import unittest
from unittest.mock import patch

from tools import _s2ty_event_control as control
from tools import _s2ty_failure_verification as verify
from tools import _s2ty_record as record
from tools import _s2ty_resource_ledger as ledger


P = "a" * 64


def event(ordinal, kind, segment, value=None):
    return dict(ordinal=ordinal, kind=kind, segment=segment, values=None if value is None else (float(value),) * 48)


def formation(segment="a"):
    return [event(1, "FORMATION", segment, 1), event(2, "FORMATION", segment, 2), event(3, "FORMATION", segment, 3), event(4, "FORMATION", segment, 4), event(5, "CLOSE", segment)]


def failed(events):
    return record.dumps(record.build(events, P, "owner"))


def direct_arm_failure():
    original = control.tw.ExactConfirmationStore

    class DirectFailureStore(original):
        instances = []

        def __init__(self, *args):
            super().__init__(*args)
            DirectFailureStore.instances.append(self)

        def form(self, frame):
            result = super().form(frame)
            if self is DirectFailureStore.instances[1]:
                raise RuntimeError("direct-after-change")
            return result

    with patch.object(control.tw, "ExactConfirmationStore", DirectFailureStore):
        return failed([event(1, "FORMATION", "a", 1)])


def owner_close_failure(events):
    original = control.adapter.PerceptionTraceAdapter

    class BrokenAdapter(original):
        def __init__(self, *args):
            super().__init__(*args)
            self.store.close_owner = lambda: (_ for _ in ()).throw(RuntimeError("close"))

    with patch.object(control.adapter, "PerceptionTraceAdapter", BrokenAdapter):
        return failed(events)


class Tests(unittest.TestCase):
    def test_error_before_first_formation_is_verified(self):
        proof = verify.verify(failed([event(1, "CLOSE", "missing")]))
        self.assertEqual((proof["status"], proof["completed"]), ("VERIFIED_FAILURE_PROGRESS", 0))

    def test_error_after_completed_progress_is_verified(self):
        proof = verify.verify(failed([*formation(), event(6, "CLOSE", "missing")]))
        self.assertEqual(proof["completed"], 5)

    def test_error_between_arms_records_changed_direct_state(self):
        payload = direct_arm_failure()
        document = record.loads(payload)
        self.assertEqual(document["result"]["failure"]["progress"]["arms"]["direct"]["state"]["forming"], [["a", 1]])
        self.assertTrue(document["result"]["failure"]["progress"]["arms"]["direct"]["changed_without_return"])
        self.assertEqual(verify.verify(payload)["completed"], 0)

    def test_owner_close_error_preserves_primary_error(self):
        payload = owner_close_failure([event(1, "CLOSE", "missing")])
        document = record.loads(payload)
        self.assertEqual(document["result"]["failure"]["phase"], "CLOSE")
        self.assertEqual(verify.verify(payload)["status"], "VERIFIED_FAILURE_PROGRESS")

    def test_owner_close_error_after_complete_input_is_verified(self):
        payload = owner_close_failure(formation())
        document = record.loads(payload)
        self.assertEqual(document["result"]["failure"]["phase"], "OWNER_CLOSE")
        self.assertEqual(verify.verify(payload)["completed"], 5)

    def test_manipulated_progress_arm_and_close_are_rejected(self):
        payload = failed([*formation(), event(6, "CLOSE", "missing")])
        mutations = (
            ("progress", lambda value: value["result"]["failure"]["progress"].__setitem__("last_completed_ordinal", 4)),
            ("arm", lambda value: value["result"]["failure"]["progress"]["arms"]["adapter"].__setitem__("returned_steps", 99)),
            ("changed-state", lambda value: value["result"]["failure"]["progress"]["arms"]["adapter"].__setitem__("returned_steps", 6)),
            ("close", lambda value: value["result"]["owner_closes"][1].__setitem__("arm", "unknown")),
        )
        for name, mutate in mutations:
            document = json.loads(payload)
            mutate(document)
            with self.subTest(name=name):
                with self.assertRaises(verify.Error):
                    verify.verify(record.dumps(document))

    def test_mismatched_attempted_and_completed_counters_are_rejected(self):
        payload = failed([*formation(), event(6, "CLOSE", "missing")])
        mutations = (
            ("result-attempted", lambda value: value["result"].__setitem__("attempted", 99)),
            ("failure-attempted", lambda value: value["result"]["failure"].__setitem__("attempted", 99)),
            ("failure-completed", lambda value: value["result"]["failure"].__setitem__("completed", 4)),
        )
        for name, mutate in mutations:
            document = json.loads(payload)
            mutate(document)
            with self.subTest(name=name):
                with self.assertRaises(verify.Error):
                    verify.verify(record.dumps(document))

    def test_owner_close_failure_requires_a_failed_close_receipt(self):
        document = record.loads(owner_close_failure(formation()))
        failed_close = next(item for item in document["result"]["owner_closes"] if not item["closed"])
        failed_close["closed"] = True
        failed_close.pop("error")
        with self.assertRaises(verify.Error):
            verify.verify(record.dumps(document))

    def test_complete_neutral_failure_envelopes_fit_the_failure_ledger_branch(self):
        payloads = [
            failed([event(1, "CLOSE", "missing")]),
            failed([*formation(), event(6, "CLOSE", "missing")]),
            direct_arm_failure(),
            owner_close_failure([event(1, "CLOSE", "missing")]),
        ]
        for payload in payloads:
            result = ledger.ledger(
                ledger.planned_shape(),
                source_bytes=0,
                metadata_bytes=0,
                shared_bytes=0,
                success_record_bytes=0,
                failure_record_bytes=len(payload),
                verification_bytes=0,
            )
            with self.subTest(bytes=len(payload)):
                self.assertEqual(result["branches"]["failure"]["contributions"]["record"], len(payload))
                self.assertLessEqual(len(payload), ledger.LIMITS["record"])
