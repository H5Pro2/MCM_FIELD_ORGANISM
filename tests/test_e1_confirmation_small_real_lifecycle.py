from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_completion_aligned_refinement import _refined_steps
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from mcm_field_organism.e1_confirmation_small_real_lifecycle import (
    E1SmallRealLifecyclePreparedInputs,
    S1_EC11_STEP_COUNTS,
    consume_prepared_small_real_formation,
    execute_prepared_small_real_formation_lifecycle,
    prepare_small_real_formation_bundle_from_run_contract,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from tests.test_e1_a0_av_history_producer import contract, field, source
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


class E1ConfirmationSmallRealLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = source()
        cls.field = field()
        cls.state = build_neutral_e1_state(cls.field.layer, contract())
        clock_id = cls.source.history_ab[0].clock_id
        cls.values = E1SmallRealLifecyclePreparedInputs(
            history_ab=cls.source.history_ab,
            history_ba=cls.source.history_ba,
            refinement_steps=tuple(
                (
                    name,
                    _refined_steps(
                        clock_id,
                        1_000_000.0,
                        (0, 1_000_000, 2_000_000),
                        factor,
                    ),
                )
                for name, factor in (("r2", 2), ("r4", 4), ("r8", 8))
            ),
            initial_field=cls.field,
            initial_state=cls.state,
        )
        cls.descriptor = build_e1_confirmation_research_corridor(UPSTREAM)

    def _bundle(self, directory: Path):
        run = prepare_e1_confirmation_synthetic_run_contract(
            self.descriptor, directory
        )
        bundle = prepare_small_real_formation_bundle_from_run_contract(
            run, self.values
        )
        return run, bundle

    def test_real_matrix_crosses_attempt_and_publishes_verified_report(self) -> None:
        with TemporaryDirectory() as directory:
            run, bundle = self._bundle(Path(directory))
            result = execute_prepared_small_real_formation_lifecycle(bundle)
            report = json.loads(Path(run.report_path).read_text(encoding="ascii"))

            self.assertTrue(result.formation.real_field_kernels_executed)
            self.assertTrue(result.formation.attempt_present_during_execution)
            self.assertEqual(S1_EC11_STEP_COUNTS, result.formation.step_counts)
            self.assertEqual(
                result.formation.result_digest, report["consumer_digest"]
            )
            self.assertTrue(Path(run.report_path).is_file())
            self.assertFalse(Path(run.attempt_path).exists())
            self.assertFalse(Path(run.lock_path).exists())

    def test_lifecycle_is_repeatable_under_fresh_temporary_identity_paths(self) -> None:
        digests = []
        for _ in range(2):
            with TemporaryDirectory() as directory:
                _, bundle = self._bundle(Path(directory))
                result = execute_prepared_small_real_formation_lifecycle(bundle)
                digests.append(
                    tuple(
                        item.result_digest
                        for item in result.formation.refinements
                    )
                )

        self.assertEqual(digests[0], digests[1])

    def test_consumer_uses_no_resolver_builder_or_canonical_path(self) -> None:
        source_text = inspect.getsource(consume_prepared_small_real_formation)

        self.assertIn("run_small_five_arm_formation_in_memory(", source_text)
        for forbidden in (
            "build_e1_confirmation_research_corridor",
            "build_e1_av_history_permutation",
            "build_e1_confirmation_descriptor_refinement_plans",
            "_fresh_canonical_field",
            "build_neutral_e1_state",
            "reports/",
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
            execute_prepared_small_real_formation_lifecycle(bundle)
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
