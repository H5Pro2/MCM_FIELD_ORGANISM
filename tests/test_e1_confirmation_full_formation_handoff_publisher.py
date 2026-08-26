from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from mcm_field_organism.e1_confirmation_full_formation_handoff import (
    build_full_formation_handoff_envelope,
)
from mcm_field_organism.e1_confirmation_full_formation_handoff_publisher import (
    E1ConfirmationFullFormationHandoffPublisherError,
    S1_EC15_POLICY_DIGEST,
    publish_full_formation_handoff_fixture_once,
    prepare_full_formation_handoff_fixture_publication,
)
from mcm_field_organism.e1_refined_formation_runner import _digest
from tests.test_e1_confirmation_full_formation_handoff import (
    S1_EC13_REPORT,
    S1_EC13_REPORT_SHA256,
    _full_geometry_fixture_result,
)
from tests.test_e1_confirmation_typed_prepared_inputs import CANONICAL_TARGETS


class E1ConfirmationFullFormationHandoffPublisherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.envelope = build_full_formation_handoff_envelope(
            _full_geometry_fixture_result()
        )

    def test_fixture_payload_is_published_reread_and_typed_reloaded(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_full_formation_handoff_fixture_publication(
                Path(directory)
            )
            receipt = publish_full_formation_handoff_fixture_once(
                contract, self.envelope
            )
            report = json.loads(Path(receipt.report_path).read_text("ascii"))

            self.assertEqual(
                self.envelope.payload_digest,
                _digest(report["payload"]),
            )
            self.assertEqual(self.envelope.payload_digest, receipt.payload_digest)
            self.assertEqual(
                S1_EC15_POLICY_DIGEST,
                report["publisher_policy_digest"],
            )
            self.assertTrue(receipt.final_reread_verified)
            self.assertTrue(receipt.typed_reload_verified)
            self.assertFalse(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())

    def test_same_publication_identity_cannot_be_used_twice(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_full_formation_handoff_fixture_publication(
                Path(directory)
            )
            publish_full_formation_handoff_fixture_once(contract, self.envelope)

            with self.assertRaises(E1ConfirmationFullFormationHandoffPublisherError):
                publish_full_formation_handoff_fixture_once(contract, self.envelope)

    def test_failure_after_attempt_retains_attempt_and_rejects_retry(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_full_formation_handoff_fixture_publication(
                Path(directory)
            )
            with patch(
                "mcm_field_organism.e1_confirmation_full_formation_handoff_publisher."
                "load_full_formation_handoff_payload",
                side_effect=ValueError("fixture reload failure"),
            ):
                with self.assertRaisesRegex(ValueError, "fixture reload failure"):
                    publish_full_formation_handoff_fixture_once(
                        contract, self.envelope
                    )

            self.assertTrue(Path(contract.attempt_path).is_file())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaises(E1ConfirmationFullFormationHandoffPublisherError):
                publish_full_formation_handoff_fixture_once(contract, self.envelope)

    def test_mutated_prepared_payload_is_rejected_before_markers(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_full_formation_handoff_fixture_publication(
                Path(directory)
            )
            changed = copy.deepcopy(self.envelope)
            changed.payload["result"]["r4_r8_state_residual"] += 1e-9

            with self.assertRaises(ValueError):
                publish_full_formation_handoff_fixture_once(contract, changed)

            self.assertFalse(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            self.assertFalse(Path(contract.report_path).exists())

    def test_publisher_has_no_formation_probe_or_canonical_consumer(self) -> None:
        source = inspect.getsource(publish_full_formation_handoff_fixture_once)

        for forbidden in (
            "_run_arm",
            "run_small_five_arm_formation_in_memory",
            "execute_prepared_full_formation_lifecycle",
            "run_e1_confirmation_probe",
            "run_seven_arm_probe",
            "reports/",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1ec13_and_terminal_artifacts_remain_unchanged(self) -> None:
        before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )
        with TemporaryDirectory() as directory:
            contract = prepare_full_formation_handoff_fixture_publication(
                Path(directory)
            )
            publish_full_formation_handoff_fixture_once(contract, self.envelope)
        after = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )

        self.assertEqual(before, after)
        self.assertEqual(
            S1_EC13_REPORT_SHA256,
            hashlib.sha256(S1_EC13_REPORT.read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
