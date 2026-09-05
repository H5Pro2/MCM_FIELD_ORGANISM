"""Neutral qualification of the compact S2-MU failure observation."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import hashlib
import json
import unittest

from tools import _s2mt_private_transfer_runtime_runner as runner
from tools import _s2mt_private_transfer_runtime_verifier as verifier


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _source_hashes() -> dict[str, str]:
    return {path: _sha(path) for path in runner.SOURCE_PATHS}


def _record(value: runner.S2MTFailureReceiptV1) -> dict[str, object]:
    return {
        **value.payload_without_digest(),
        "failure_receipt_digest": value.failure_receipt_digest,
    }


def _redigest(value: dict[str, object]) -> dict[str, object]:
    payload = dict(value)
    payload.pop("failure_receipt_digest", None)
    return {**payload, "failure_receipt_digest": verifier._digest(payload)}


class S2MUFailureObservabilityQualification(unittest.TestCase):
    def setUp(self) -> None:
        self.source_hashes = _source_hashes()
        self.bindings = runner._attempt_bindings(self.source_hashes)

    def receipt(
        self,
        phase: str,
        *,
        ordinal: int | None = None,
        completed: int = 0,
        last_snapshot: str | None = None,
    ) -> runner.S2MTFailureReceiptV1:
        return runner._failure_receipt(
            phase=phase,
            event_ordinal=ordinal,
            completed_event_count=completed,
            last_runtime_snapshot_digest=last_snapshot,
            bindings=self.bindings,
        )

    def test_01_attempt_bindings_are_independently_reconstructed(self) -> None:
        expected = verifier._expected_attempt_bindings(self.source_hashes)
        self.assertEqual(
            expected,
            {
                "source_binding_digest": self.bindings.source_binding_digest,
                "plan_binding_digest": self.bindings.plan_binding_digest,
                "config_binding_digest": self.bindings.config_binding_digest,
                "runtime_binding_digest": self.bindings.runtime_binding_digest,
            },
        )

    def test_02_all_six_phases_have_valid_neutral_receipts(self) -> None:
        cases = (
            ("SOURCE_PLAN", None, 0, None),
            ("MATERIALIZATION", None, 0, None),
            ("RUNTIME_INIT", None, 0, None),
            ("EVENT_PROCESSING", 7, 6, _sha("snapshot-6")),
            ("RUNTIME_CLOSE", None, 28, _sha("snapshot-open")),
            ("EVALUATION", None, 28, _sha("snapshot-closed")),
        )
        for phase, ordinal, completed, snapshot in cases:
            with self.subTest(phase=phase):
                value = self.receipt(phase, ordinal=ordinal, completed=completed, last_snapshot=snapshot)
                self.assertEqual(value.error_code, runner.FAILURE_CODES[phase])
                verifier._verify_failure_receipt(_record(value), self.source_hashes)

    def test_03_failure_receipt_is_immutable_and_compact(self) -> None:
        value = self.receipt("EVENT_PROCESSING", ordinal=1, last_snapshot=_sha("initial"))
        with self.assertRaises(FrozenInstanceError):
            value.phase = "EVALUATION"  # type: ignore[misc]
        self.assertLess(len(runner._canonical_bytes(_record(value))), 2_048)

    def test_04_event_progress_must_bind_the_current_ordinal(self) -> None:
        value = _record(self.receipt("EVENT_PROCESSING", ordinal=7, completed=6, last_snapshot=_sha("snapshot-6")))
        for key, replacement in (("event_ordinal", 8), ("completed_event_count", 7), ("last_runtime_snapshot_digest", None)):
            with self.subTest(key=key), self.assertRaises(verifier.S2MTVerificationError):
                verifier._verify_failure_receipt(_redigest({**value, key: replacement}), self.source_hashes)

    def test_05_pre_runtime_and_terminal_progress_cannot_be_mixed(self) -> None:
        source = _record(self.receipt("SOURCE_PLAN"))
        terminal = _record(self.receipt("RUNTIME_CLOSE", completed=28, last_snapshot=_sha("open")))
        with self.assertRaises(verifier.S2MTVerificationError):
            verifier._verify_failure_receipt(_redigest({**source, "completed_event_count": 1}), self.source_hashes)
        with self.assertRaises(verifier.S2MTVerificationError):
            verifier._verify_failure_receipt(_redigest({**terminal, "event_ordinal": 28}), self.source_hashes)

    def test_06_phase_code_and_attempt_bindings_fail_closed(self) -> None:
        value = _record(self.receipt("MATERIALIZATION"))
        mutations = (
            ("error_code", runner.FAILURE_CODES["EVALUATION"]),
            ("source_binding_digest", _sha("foreign-source")),
            ("plan_binding_digest", _sha("foreign-plan")),
            ("config_binding_digest", _sha("foreign-config")),
            ("runtime_binding_digest", _sha("foreign-runtime")),
        )
        for key, replacement in mutations:
            with self.subTest(key=key), self.assertRaises(verifier.S2MTVerificationError):
                verifier._verify_failure_receipt(_redigest({**value, key: replacement}), self.source_hashes)

    def test_07_digest_and_extra_diagnostics_fail_closed(self) -> None:
        value = _record(self.receipt("EVALUATION", completed=28, last_snapshot=_sha("closed")))
        with self.assertRaises(verifier.S2MTVerificationError):
            verifier._verify_failure_receipt({**value, "failure_receipt_digest": _sha("changed")}, self.source_hashes)
        with self.assertRaises(verifier.S2MTVerificationError):
            verifier._verify_failure_receipt(_redigest({**value, "exception_text": "forbidden"}), self.source_hashes)

    def test_08_not_evaluable_record_has_no_partial_outputs_or_roles(self) -> None:
        receipt = self.receipt("EVENT_PROCESSING", ordinal=4, completed=3, last_snapshot=_sha("snapshot-3"))
        record = runner._not_evaluable_record("s2mt-neutral-observation", self.source_hashes, receipt)
        self.assertIsNone(record["execution"])
        self.assertIsNone(record["evaluation"])
        self.assertEqual(record["failure_code"], receipt.error_code)
        encoded = runner._canonical_bytes(record)
        self.assertNotIn(b"traceback", encoded.lower())
        self.assertNotIn(b"exception_text", encoded.lower())
        self.assertNotIn(b"target", encoded.lower())
        self.assertNotIn(b"distractor", encoded.lower())
        payload = dict(record)
        self.assertEqual(payload.pop("record_digest"), runner._digest(payload))
        verifier._verify_failure_receipt(record["failure_receipt"], self.source_hashes)


if __name__ == "__main__":
    unittest.main()
