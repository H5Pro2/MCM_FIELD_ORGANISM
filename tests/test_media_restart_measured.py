"""One focused measured-publication qualification; no historical suite replay."""
import json
from unittest.mock import patch

from tests import test_media_restart_reserved as prepared
from tests.media_restart_neutral import NeutralWorker
from tools import _media_restart_checkpoint as c
from tools import _media_restart_evidence as e
from tools import _media_restart_serialization as s
from tools import _media_restart_work as w


class Measured(prepared.Reserved):
    # The six inherited groups were prepared at -03 but never invoked there.
    def test_07_bounded_canonical_and_reference_expansion(self):
        value = {"a": [-0.0, float.fromhex("0x0.0000000000001p-1022"), 1.0],
                 "z": {"text": "\u00e4\n\U0001f642", "count": 20}}
        expected = c.b.canonical(value)
        self.assertEqual(s.measure(value), len(expected))
        self.assertEqual(s.canonical(value, len(expected)), expected)
        self.error("MEDIA_SERIALIZATION_LIMIT", lambda: s.canonical(value, len(expected)-1))
        # Oversized text is rejected while measuring bounded escaped chunks,
        # before construction of the complete encoded string.
        with patch.object(s.ENCODER, "iterencode", side_effect=AssertionError("encoder reached")):
            self.error("MEDIA_SERIALIZATION_LIMIT", lambda: s.canonical("x"*(s.MAX_BYTES+1)))
        store = e.Store(prepared.ROOT/"serialization-controls")
        ref = store.intern({"s": "x"*1024}, "native")
        self.error("MEDIA_SERIALIZATION_LIMIT", lambda: store.resolve([ref]*5000))
        packed = store.pack({"core": {"inputs": [value], "states": {}, "rows": [], "scans": []}})
        self.assertEqual(e.canonical(store.resolve(packed)), c.b.canonical(
            {"core": {"inputs": [value], "states": {}, "rows": [], "scans": []}}))

    def test_08_native_budget_failure_preserves_progress(self):
        manifest, store = prepared.bound()
        with patch.object(c, "MAIN_GATE", True), patch.object(c, "QUALIFIED", True), \
                patch.object(w, "WorkerDecoder", NeutralWorker):
            session = c.Session(manifest, prepared.ROOT/"native-primary-failure", store)
        try:
            session.next()
            self.assertFalse(session.runtime.failed)
            self.assertEqual(len(session.runtime.rows), 1)
            memory = session.runtime.subject.snapshot().memory_state_digest
            field = session.runtime.fb.state.field_component_digest
            field_state = session.runtime.fb.state.state_digest
            current = store.budget()
            filler = e.LIMITS["metadata"]-current["charged"]["metadata"]-1
            self.assertGreaterEqual(filler, 0)
            original = store.ledger
            def ledger(extra=()):
                return original([dict(path="synthetic-occupation", bytes=filler, category="metadata"), *extra])
            with patch.object(store, "ledger", side_effect=ledger):
                exc = self.error("MEDIA_STORE_BUDGET", lambda: session.publish(
                    session.directory/"rejected.json", {"done": True}))
                session.fail(exc)
            proof = store.read(session.directory/"failure.json")
            self.assertEqual(proof["status"], "NOT_EVALUABLE")
            failure = proof["failure"]
            self.assertEqual(failure["code"], "MEDIA_STORE_BUDGET")
            self.assertEqual(failure["completed"], 1)
            self.assertEqual(failure["details"]["phase"], "EVIDENCE")
            self.assertEqual(failure["details"]["event"], 1)
            self.assertEqual(failure["progress"]["memory"], memory)
            self.assertEqual(failure["progress"]["field"], field)
            self.assertEqual(failure["progress"]["field_state"], field_state)
            self.assertEqual(session.runtime.subject.snapshot().memory_state_digest, memory)
            self.assertEqual(session.runtime.fb.state.field_component_digest, field)
            self.assertTrue(failure["resources"]["worker_closed"])
            self.assertTrue(session.closed)
            before = (session.directory/"failure.json").read_bytes()
            session.fail(w.RestartError("MEDIA_INCOMPLETE"))
            session.close()
            self.assertEqual((session.directory/"failure.json").read_bytes(), before)
        finally:
            if not session.closed:
                session.fail(w.RestartError("NEUTRAL_CLEANUP"))


if __name__ == "__main__":
    import unittest
    unittest.main()
