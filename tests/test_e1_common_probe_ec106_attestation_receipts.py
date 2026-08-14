from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec106_attestation_receipts import (
    E1CommonProbeEC106AttestationReceiptError,
    _build_e1_common_probe_ec106_synthetic_combined_ingress_attestation,
    run_e1_common_probe_ec106_synthetic_fixture,
)


class E1CommonProbeEC106AttestationReceiptsTests(unittest.TestCase):
    def test_three_receipts_bind_exact_lineage(self) -> None:
        attestation = run_e1_common_probe_ec106_synthetic_fixture()
        self.assertEqual(8, len(attestation.r2_receipt.source_probe_receipt_digests))
        self.assertEqual(
            16, len(attestation.r4_r8_receipt.source_probe_receipt_digests)
        )
        self.assertEqual(24, len(attestation.source_probe_receipt_digests))
        self.assertEqual(22456, attestation.accounted_field_steps)
        self.assertTrue(attestation.same_objects_forwarded_to_ec102)
        self.assertTrue(attestation.contractual_not_cryptographic)

    def test_fixture_is_deterministic(self) -> None:
        first = run_e1_common_probe_ec106_synthetic_fixture()
        second = run_e1_common_probe_ec106_synthetic_fixture()
        self.assertEqual(first.attestation_digest, second.attestation_digest)

    def test_changed_producer_receipt_fails_closed(self) -> None:
        attestation = run_e1_common_probe_ec106_synthetic_fixture()
        with self.assertRaises(E1CommonProbeEC106AttestationReceiptError):
            replace(attestation.r2_receipt, accounted_field_steps=3207)

    def test_swapped_receipts_fail_closed(self) -> None:
        attestation = run_e1_common_probe_ec106_synthetic_fixture()
        with self.assertRaises(E1CommonProbeEC106AttestationReceiptError):
            _build_e1_common_probe_ec106_synthetic_combined_ingress_attestation(
                attestation.r4_r8_receipt,  # type: ignore[arg-type]
                attestation.r2_receipt,  # type: ignore[arg-type]
                attestation.source_probe_objects,
                attestation.forwarded_probe_objects,
            )

    def test_changed_object_identity_fails_closed(self) -> None:
        attestation = run_e1_common_probe_ec106_synthetic_fixture()
        changed = (
            object(),
            *attestation.forwarded_probe_objects[1:],
        )
        with self.assertRaises(E1CommonProbeEC106AttestationReceiptError):
            _build_e1_common_probe_ec106_synthetic_combined_ingress_attestation(
                attestation.r2_receipt,
                attestation.r4_r8_receipt,
                attestation.source_probe_objects,
                changed,
            )

    def test_fixture_does_not_call_coordinator_ec102_writer_or_decider(self) -> None:
        source = inspect.getsource(run_e1_common_probe_ec106_synthetic_fixture)
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_ec96_authorized_r4_r8_once(",
            "extract_e1_common_probe_ec102_coordinator_results(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
