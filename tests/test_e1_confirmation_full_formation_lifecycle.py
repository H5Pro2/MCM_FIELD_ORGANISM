from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from mcm_field_organism.e1_completion_aligned_refinement import _refined_steps
from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_full_formation_lifecycle import (
    consume_prepared_full_formation,
    execute_prepared_full_formation_lifecycle,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from mcm_field_organism.e1_confirmation_small_five_arm_formation import (
    run_small_five_arm_formation_in_memory,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from tests.test_e1_a0_av_history_producer import contract, field, source
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


class E1ConfirmationFullFormationLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        small_source = source()
        small_field = field()
        small_state = build_neutral_e1_state(small_field.layer, contract())
        clock_id = small_source.history_ab[0].clock_id
        cls.small_results = tuple(
            run_small_five_arm_formation_in_memory(
                name,
                small_source.history_ab,
                small_source.history_ba,
                _refined_steps(
                    clock_id,
                    1_000_000.0,
                    (0, 1_000_000, 2_000_000),
                    factor,
                ),
                _refined_steps(
                    clock_id,
                    1_000_000.0,
                    (0, 1_000_000, 2_000_000),
                    factor,
                ),
                small_field,
                small_state,
            )
            for name, factor in (("r2", 2), ("r4", 4), ("r8", 8))
        )

    def _bundle(self, directory: Path):
        run = prepare_e1_confirmation_synthetic_run_contract(
            self.descriptor, directory
        )
        bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )
        return run, bundle

    def test_lifecycle_gates_and_publishes_one_full_consumer_result(self) -> None:
        with TemporaryDirectory() as directory:
            run, bundle = self._bundle(Path(directory))
            with patch(
                "mcm_field_organism.e1_confirmation_full_formation_lifecycle."
                "run_small_five_arm_formation_in_memory",
                side_effect=self.small_results,
            ) as runner:
                result = execute_prepared_full_formation_lifecycle(bundle)
            report = json.loads(Path(run.report_path).read_text(encoding="ascii"))

            self.assertEqual(3, runner.call_count)
            self.assertTrue(result.formation.attempt_present_during_execution)
            self.assertEqual(
                result.preflight.result_digest,
                result.formation.in_attempt_preflight_digest,
            )
            self.assertEqual(
                result.formation.result_digest, report["consumer_digest"]
            )
            self.assertFalse(Path(run.attempt_path).exists())
            self.assertFalse(Path(run.lock_path).exists())

    def test_consumer_uses_prepared_plans_and_contains_no_builder(self) -> None:
        source_text = inspect.getsource(consume_prepared_full_formation)

        self.assertIn("ab.proposal_steps", source_text)
        self.assertIn("ba.proposal_steps", source_text)
        for forbidden in (
            "build_e1_confirmation_research_corridor",
            "build_e1_av_history_permutation",
            "build_e1_confirmation_descriptor_refinement_plans",
            "_fresh_canonical_field",
            "build_neutral_e1_state",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source_text)

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
            _, bundle = self._bundle(Path(directory))
            with patch(
                "mcm_field_organism.e1_confirmation_full_formation_lifecycle."
                "run_small_five_arm_formation_in_memory",
                side_effect=self.small_results,
            ):
                execute_prepared_full_formation_lifecycle(bundle)
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
