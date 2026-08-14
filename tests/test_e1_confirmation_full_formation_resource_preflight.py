from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_full_formation_resource_preflight import (
    S1_EC12_EXPECTED_REFINEMENTS,
    preflight_prepared_full_formation_resources,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


class E1ConfirmationFullFormationResourcePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.descriptor = build_e1_confirmation_research_corridor(UPSTREAM)

    def _preflight(self, directory: Path):
        run = prepare_e1_confirmation_synthetic_run_contract(
            self.descriptor, directory
        )
        bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )
        return run, preflight_prepared_full_formation_resources(bundle)

    def test_preflight_binds_exact_full_inventory_and_upper_bounds(self) -> None:
        with TemporaryDirectory() as directory:
            run, result = self._preflight(Path(directory))

            self.assertEqual(S1_EC12_EXPECTED_REFINEMENTS, result.refinement_step_counts)
            self.assertEqual(15, result.formation_arm_runs)
            self.assertEqual(14_000, result.total_arm_steps)
            self.assertEqual(1_176_000, result.node_step_units_upper_bound)
            self.assertEqual(2_030_000, result.edge_step_units_upper_bound)
            self.assertTrue(result.resource_gate_passed)
            self.assertFalse(Path(run.attempt_path).exists())
            self.assertFalse(Path(run.lock_path).exists())
            self.assertFalse(Path(run.report_path).exists())

    def test_preflight_digest_is_independent_of_temporary_run_paths(self) -> None:
        digests = []
        for _ in range(2):
            with TemporaryDirectory() as directory:
                _, result = self._preflight(Path(directory))
                digests.append(result.result_digest)

        self.assertEqual(digests[0], digests[1])

    def test_preflight_contains_no_execution_or_persistence_call(self) -> None:
        source = inspect.getsource(preflight_prepared_full_formation_resources)

        for forbidden in (
            "_run_arm",
            "run_small_five_arm_formation_in_memory",
            "execute_prepared_bundle_synthetically",
            "_exclusive_marker",
            "_atomic_publish",
            "write_text",
            "write_bytes",
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
            self._preflight(Path(directory))
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
