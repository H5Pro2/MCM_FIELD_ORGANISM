from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_prepared_execution_bundle import (
    E1ConfirmationPreparedBundleError,
    execute_prepared_bundle_synthetically,
)
from mcm_field_organism.e1_confirmation_prepared_formation_consumer import (
    E1ConfirmationPreparedFormationConsumerError,
    S1_EC7_FORMATION_ARMS,
    run_prepared_formation_consumer_synthetically,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


class E1ConfirmationPreparedFormationConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.descriptor = build_e1_confirmation_research_corridor(UPSTREAM)

    def _bundle(self, directory: Path):
        run = prepare_e1_confirmation_synthetic_run_contract(
            self.descriptor, directory
        )
        return run, prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )

    def test_consumer_runs_15_ordered_kernels_after_attempt(self) -> None:
        calls = []
        with TemporaryDirectory() as directory:
            root = Path(directory)
            run, bundle = self._bundle(root)
            formed = []

            def kernel(arm, refinement, sequences, steps, field, state, enabled):
                self.assertTrue(Path(run.attempt_path).is_file())
                self.assertIs(field, bundle.value("initial_field"))
                self.assertIs(state, bundle.value("initial_state"))
                calls.append((refinement, arm, enabled, sequences, steps))
                return hashlib.sha256(
                    f"{refinement}:{arm}:{enabled}".encode("ascii")
                ).hexdigest()

            def consumer(received):
                result = run_prepared_formation_consumer_synthetically(
                    received, kernel
                )
                formed.append(result)
                return result.result_digest

            execute_prepared_bundle_synthetically(bundle, consumer)

        self.assertEqual(15, len(calls))
        self.assertEqual(
            ("r2", "r4", "r8"),
            tuple(calls[index][0] for index in (0, 5, 10)),
        )
        for offset in (0, 5, 10):
            self.assertEqual(
                S1_EC7_FORMATION_ARMS,
                tuple(item[1] for item in calls[offset : offset + 5]),
            )
        self.assertEqual(1, len(formed))
        self.assertTrue(formed[0].prepared_inputs_only)
        self.assertFalse(formed[0].field_execution_permitted)

    def test_arm_sources_and_steps_are_the_prepared_objects(self) -> None:
        with TemporaryDirectory() as directory:
            _, bundle = self._bundle(Path(directory))
            source = bundle.value("av_permutation")
            ab_plans = bundle.value("history_ab_plans")
            ba_plans = bundle.value("history_ba_plans")
            observed = []

            def kernel(arm, refinement, sequences, steps, _field, _state, _enabled):
                observed.append((arm, refinement, sequences, steps))
                return "0" * 64

            run_prepared_formation_consumer_synthetically(bundle, kernel)

            self.assertIs(source.history_ab, observed[0][2])
            self.assertIs(source.history_ba, observed[1][2])
            self.assertIs(ab_plans.plans[0].proposal_steps, observed[0][3])
            self.assertIs(ba_plans.plans[0].proposal_steps, observed[1][3])

    def test_invalid_kernel_result_after_attempt_retains_attempt(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            run, bundle = self._bundle(root)

            def consumer(received):
                return run_prepared_formation_consumer_synthetically(
                    received,
                    lambda *_args: "not-a-digest",
                ).result_digest

            with self.assertRaisesRegex(
                E1ConfirmationPreparedFormationConsumerError,
                "returned no SHA-256",
            ):
                execute_prepared_bundle_synthetically(bundle, consumer)

            self.assertTrue(Path(run.attempt_path).is_file())
            self.assertFalse(Path(run.report_path).exists())
            self.assertFalse(Path(run.lock_path).exists())
            with self.assertRaisesRegex(
                E1ConfirmationPreparedBundleError, "already used"
            ):
                execute_prepared_bundle_synthetically(bundle, consumer)

    def test_consumer_source_contains_no_input_or_field_builder(self) -> None:
        source = inspect.getsource(run_prepared_formation_consumer_synthetically)

        for forbidden in (
            "build_e1_confirmation_research_corridor",
            "build_e1_av_history_permutation",
            "build_e1_confirmation_descriptor_refinement_plans",
            "_fresh_canonical_field",
            "build_neutral_e1_state",
            "_run_arm",
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
            _, bundle = self._bundle(Path(directory))
            run_prepared_formation_consumer_synthetically(
                bundle,
                lambda *_args: "0" * 64,
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
