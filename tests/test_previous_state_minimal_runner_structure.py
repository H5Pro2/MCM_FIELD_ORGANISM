from __future__ import annotations

from dataclasses import replace
import json
import unittest

import mcm_field_organism
from mcm_field_organism._previous_state_minimal_runner import (
    PreviousStateMinimalRunnerError,
    build_locked_previous_state_minimal_manifest,
    execute_previous_state_minimal_runner,
)


class PreviousStateMinimalRunnerStructureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = build_locked_previous_state_minimal_manifest()

    def test_fixed_digests_and_dissipation_gate(self) -> None:
        self.assertEqual(
            dict(self.manifest.input_digests),
            {
                "A": "2d435c4331f083939796920ec2ae3e5864992d2cf11f447f9cab8f75e17e9998",
                "B": "66ffdb19bdb743d5fb86a7e65dbb7c8c7f8e2045087aee74999bb5fa5d62da31",
                "C": "81a6cf62a13cbdf246f8309c99eea564c64e035ca8ca094bb391c129036d3be3",
                "config": "fa13c44abcfaf7e80aa396b217eeea7ed28c50a3021bbccd62c59a15ecfd0e6a",
                "bundle": "2b3286d2ca5a5a815e2002674736c828e9ae30ba12de5f60ac7fbca0bf1bdbd0",
            },
        )
        self.assertIsNone(json.loads(self.manifest.config_json)["dissipation_config"])

    def test_exact_arm_replica_and_history_wiring(self) -> None:
        expected_run_ids = tuple(
            f"{arm_id}.r{replicate}"
            for arm_id in (
                "history_a.none",
                "history_b.none",
                "history_a.identity",
                "history_b.identity",
                "history_a.zero",
                "history_b.zero",
                "equalized_a.none",
                "equalized_b.none",
                "permuted_a.none",
                "permuted_b.none",
                "permuted_a.zero",
                "permuted_b.zero",
            )
            for replicate in (1, 2)
        )
        self.assertEqual(
            tuple(arm.run_id for arm in self.manifest.arms),
            expected_run_ids,
        )
        self.assertEqual(len({arm.run_id for arm in self.manifest.arms}), 24)
        by_arm = {}
        for arm in self.manifest.arms:
            by_arm.setdefault(arm.arm_id, []).append(arm)
            self.assertEqual(arm.run_id, f"{arm.arm_id}.r{arm.replicate}")
            self.assertEqual(arm.current_contact_id, "C")
        self.assertEqual(len(by_arm), 12)
        self.assertTrue(
            all(sorted(item.replicate for item in arms) == [1, 2] for arms in by_arm.values())
        )
        self.assertEqual(by_arm["equalized_a.none"][0].history_id, "A")
        self.assertEqual(by_arm["equalized_b.none"][0].history_id, "A")
        self.assertEqual(by_arm["permuted_a.none"][0].history_id, "B")
        self.assertEqual(by_arm["permuted_b.none"][0].history_id, "A")
        self.assertEqual(by_arm["permuted_a.zero"][0].history_id, "B")
        self.assertEqual(by_arm["permuted_b.zero"][0].history_id, "A")

    def test_measurement_abort_and_execution_locks(self) -> None:
        self.assertEqual(self.manifest.measurement_points, ("M0", "M1", "M2", "M3"))
        self.assertEqual(len(self.manifest.abort_conditions), 12)
        self.assertTrue(self.manifest.execution_locked)
        self.assertFalse(self.manifest.field_construction_allowed)
        self.assertFalse(self.manifest.receptor_distribution_allowed)
        self.assertFalse(self.manifest.integrator_execution_allowed)
        self.assertFalse(self.manifest.effect_measurement_allowed)
        with self.assertRaisesRegex(PreviousStateMinimalRunnerError, "not released"):
            execute_previous_state_minimal_runner(self.manifest)

    def test_mutated_or_unlocked_manifest_is_rejected(self) -> None:
        changed = json.loads(self.manifest.config_json)
        changed["dissipation_config"] = {"leak_rate_per_second": 0.0}
        with self.assertRaisesRegex(PreviousStateMinimalRunnerError, "explicit None"):
            replace(
                self.manifest,
                config_json=json.dumps(changed, sort_keys=True, separators=(",", ":")),
            )
        with self.assertRaisesRegex(PreviousStateMinimalRunnerError, "remain locked"):
            replace(self.manifest, execution_locked=False)

    def test_arm_and_abort_contract_mutations_are_rejected(self) -> None:
        first_arm = self.manifest.arms[0]
        arm_mutations = (
            tuple(reversed(self.manifest.arms)),
            (replace(first_arm, history_id="B"), *self.manifest.arms[1:]),
            (replace(first_arm, current_contact_id="A"), *self.manifest.arms[1:]),
            (replace(first_arm, previous_state_operator="zero"), *self.manifest.arms[1:]),
            (replace(first_arm, run_id="changed.r1"), *self.manifest.arms[1:]),
        )
        for arms in arm_mutations:
            with self.subTest(arms=arms[0]):
                with self.assertRaisesRegex(
                    PreviousStateMinimalRunnerError, "fixed arm wiring"
                ):
                    replace(self.manifest, arms=arms)
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "fixed abort conditions"
        ):
            replace(
                self.manifest,
                abort_conditions=self.manifest.abort_conditions[:-1],
            )

    def test_canonical_config_and_digest_tuple_mutations_are_rejected(self) -> None:
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "canonical config bytes"
        ):
            replace(self.manifest, config_json=" " + self.manifest.config_json)
        digest_mutations = (
            tuple(reversed(self.manifest.input_digests)),
            self.manifest.input_digests + (self.manifest.input_digests[0],),
        )
        for input_digests in digest_mutations:
            with self.subTest(input_digests=input_digests):
                with self.assertRaisesRegex(
                    PreviousStateMinimalRunnerError, "fixed input digests"
                ):
                    replace(self.manifest, input_digests=input_digests)

    def test_runner_and_hook_are_not_publicly_exported(self) -> None:
        self.assertFalse(
            hasattr(mcm_field_organism, "build_locked_previous_state_minimal_manifest")
        )
        self.assertFalse(
            hasattr(mcm_field_organism, "execute_previous_state_minimal_runner")
        )
        self.assertFalse(hasattr(mcm_field_organism, "advance_with_previous_state_operator"))


if __name__ == "__main__":
    unittest.main()
