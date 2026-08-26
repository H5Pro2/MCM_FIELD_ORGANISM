from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_prepared_execution_bundle import (
    E1PreparedRuntimeInput,
    execute_prepared_bundle_synthetically,
    prepare_e1_confirmation_execution_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from mcm_field_organism.e1_confirmation_typed_prepared_inputs import (
    S1_EC2_INPUT_ROLES,
)
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )
    return hashlib.sha256(encoded).hexdigest()


class E1ConfirmationRunContractBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.descriptor = build_e1_confirmation_research_corridor(UPSTREAM)

    def test_bundle_copies_identity_and_paths_from_run_contract(self) -> None:
        value = {"prepared": True}
        with TemporaryDirectory() as directory:
            run = prepare_e1_confirmation_synthetic_run_contract(
                self.descriptor, Path(directory)
            )
            bundle = prepare_e1_confirmation_execution_bundle_from_run_contract(
                run,
                lambda: (
                    E1PreparedRuntimeInput(
                        "synthetic",
                        value,
                        _digest(value),
                        _digest,
                    ),
                ),
            )

            self.assertEqual(run.execution_id, bundle.execution_id)
            self.assertEqual(run.report_path, bundle.report_path)
            self.assertEqual(run.attempt_path, bundle.attempt_path)
            self.assertEqual(run.lock_path, bundle.lock_path)
            self.assertEqual(run.digest(), bundle.run_contract_digest)

    def test_contract_bound_bundle_executes_only_on_contract_paths(self) -> None:
        with TemporaryDirectory() as directory:
            run = prepare_e1_confirmation_synthetic_run_contract(
                self.descriptor, Path(directory)
            )
            bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
                run, UPSTREAM
            )
            receipt = execute_prepared_bundle_synthetically(
                bundle,
                lambda received: hashlib.sha256(
                    received.bundle_digest.encode("ascii")
                ).hexdigest(),
            )

            self.assertEqual(run.digest(), receipt.run_contract_digest)
            self.assertEqual(run.report_path, receipt.report_path)
            self.assertTrue(Path(run.report_path).is_file())
            self.assertFalse(Path(run.attempt_path).exists())
            self.assertFalse(Path(run.lock_path).exists())
            self.assertEqual(
                S1_EC2_INPUT_ROLES,
                tuple(role for role, _ in bundle.input_manifest),
            )

    def test_new_bundle_constructor_does_not_derive_target_names(self) -> None:
        source = inspect.getsource(
            prepare_e1_confirmation_execution_bundle_from_run_contract
        )

        for forbidden in (
            "S1_EC1_REPORT",
            "S1_EC1_ATTEMPT",
            "S1_EC1_LOCK",
            "S1_EC3_REPORT",
            "S1_EC3_ATTEMPT",
            "S1_EC3_LOCK",
            "synthetic_directory /",
        ):
            self.assertNotIn(forbidden, source)

    def test_terminal_s1eb31_artifacts_remain_unchanged(self) -> None:
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
            run = prepare_e1_confirmation_synthetic_run_contract(
                self.descriptor, Path(directory)
            )
            prepare_e1_confirmation_descriptor_bundle_from_run_contract(
                run, UPSTREAM
            )
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


if __name__ == "__main__":
    unittest.main()
