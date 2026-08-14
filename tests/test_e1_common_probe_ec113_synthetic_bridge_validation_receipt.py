from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec112_owner_message_classifier import (
    classify_e1_common_probe_ec112_owner_message,
)
from mcm_field_organism.e1_common_probe_ec113_synthetic_bridge_validation_receipt import (
    E1CommonProbeEC113SyntheticBridgeValidationError,
    validate_e1_common_probe_ec113_synthetic_bridge_candidate,
)
from mcm_field_organism.e1_common_probe_n2_r2_real_mode_coordinator import (
    S1_EC67_EC59_HANDOFF_DIGEST,
)


def _complete_candidate(*, gate: str = "1" * 64, session: str = "2" * 64):
    return classify_e1_common_probe_ec112_owner_message(
        "EC67-r2 genau einen Lauf maximal 3.208 Feldschritte nicht persistent "
        "kein Retry reale Ausfuehrung "
        f"gate:{gate} handoff:{S1_EC67_EC59_HANDOFF_DIGEST} session:{session}"
    )


class E1CommonProbeEC113SyntheticBridgeValidationReceiptTests(unittest.TestCase):
    def test_complete_candidate_produces_closed_synthetic_receipt(self) -> None:
        candidate = _complete_candidate()
        receipt = validate_e1_common_probe_ec113_synthetic_bridge_candidate(candidate)
        self.assertTrue(receipt.candidate_structure_validated)
        self.assertEqual(candidate.classification_digest, receipt.source_classification_digest)
        self.assertFalse(receipt.external_owner_origin_attested)
        self.assertFalse(receipt.release_attestation_issued)
        self.assertFalse(receipt.owner_scope_token_creation_permitted)
        self.assertFalse(receipt.execution_permitted)

    def test_continuation_and_incomplete_candidate_fail_closed(self) -> None:
        for message in ("ok weiter", "Ich gebe einen Lauf frei"):
            with self.subTest(message=message):
                classification = classify_e1_common_probe_ec112_owner_message(message)
                with self.assertRaises(E1CommonProbeEC113SyntheticBridgeValidationError):
                    validate_e1_common_probe_ec113_synthetic_bridge_candidate(
                        classification
                    )

    def test_receipt_is_deterministic(self) -> None:
        candidate = _complete_candidate()
        first = validate_e1_common_probe_ec113_synthetic_bridge_candidate(candidate)
        second = validate_e1_common_probe_ec113_synthetic_bridge_candidate(candidate)
        self.assertEqual(first.receipt_digest, second.receipt_digest)

    def test_gate_or_session_change_changes_receipt(self) -> None:
        first = validate_e1_common_probe_ec113_synthetic_bridge_candidate(
            _complete_candidate()
        )
        changed_gate = validate_e1_common_probe_ec113_synthetic_bridge_candidate(
            _complete_candidate(gate="3" * 64)
        )
        changed_session = validate_e1_common_probe_ec113_synthetic_bridge_candidate(
            _complete_candidate(session="4" * 64)
        )
        self.assertNotEqual(first.receipt_digest, changed_gate.receipt_digest)
        self.assertNotEqual(first.receipt_digest, changed_session.receipt_digest)

    def test_tampering_with_receipt_fails_closed(self) -> None:
        receipt = validate_e1_common_probe_ec113_synthetic_bridge_candidate(
            _complete_candidate()
        )
        for change in (
            {"external_owner_origin_attested": True},
            {"release_attestation_issued": True},
            {"owner_scope_token_creation_permitted": True},
            {"maximum_field_steps": 3209},
        ):
            with self.subTest(change=change):
                with self.assertRaises(E1CommonProbeEC113SyntheticBridgeValidationError):
                    replace(receipt, **change)

    def test_wrong_input_type_fails_closed(self) -> None:
        with self.assertRaises(E1CommonProbeEC113SyntheticBridgeValidationError):
            validate_e1_common_probe_ec113_synthetic_bridge_candidate(object())  # type: ignore[arg-type]

    def test_validator_does_not_call_factory_coordinator_adapter_or_writer(self) -> None:
        source = inspect.getsource(
            validate_e1_common_probe_ec113_synthetic_bridge_candidate
        )
        for forbidden in (
            "create_e1_common_probe_ec110_owner_scope_token(",
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_real_formation_receipt_adapter(",
            "run_e1_common_probe_real_probe_receipt_adapter(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
