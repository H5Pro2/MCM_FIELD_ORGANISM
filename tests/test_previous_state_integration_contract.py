from __future__ import annotations

from dataclasses import replace
import ast
from pathlib import Path
import unittest

import mcm_field_organism
import mcm_field_organism._previous_state_integration_contract as contract_module
from mcm_field_organism._previous_state_integration_contract import (
    _StaticContactObservation,
    _build_private_integration_contract,
    _verify_static_contact_observations,
)
from mcm_field_organism._previous_state_minimal_runner import (
    PreviousStateMinimalRunnerError,
    build_locked_previous_state_minimal_manifest,
)
from mcm_field_organism._runtime_fixation_structure import (
    _FixedDigestBundle,
    _FixedDigestEntry,
    _SOURCE_DIGESTS,
    _STATIC_CONTRACT,
)


class PreviousStateIntegrationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = build_locked_previous_state_minimal_manifest()
        contact_ids = tuple(
            contact.snapshot_id
            for contact in (
                *self.manifest.input_a,
                *self.manifest.input_b,
                *self.manifest.input_c,
            )
        )
        self.bundle = _FixedDigestBundle(
            entries=tuple(
                _FixedDigestEntry(contact_id, str(index) * 64, "a" * 64, "b" * 64)
                for index, contact_id in enumerate(contact_ids, start=1)
            ),
            schema_version=1,
            source_digests=_SOURCE_DIGESTS,
            static_contract=_STATIC_CONTRACT,
        )
        self.contract = _build_private_integration_contract(
            self.bundle,
            self.manifest,
        )

    def _observations(self) -> tuple[_StaticContactObservation, ...]:
        return tuple(
            _StaticContactObservation(
                run_id=arm.run_id,
                freshness_token=arm.freshness_token,
                contact_id=stage.stage_id,
                receptor_distribution_digest=stage.digest_gate.receptor_distribution_digest,
                generator_digest=stage.digest_gate.generator_digest,
                boundary_digest=stage.digest_gate.boundary_digest,
            )
            for arm in self.contract.arms
            for stage in arm.stages
            if stage.digest_gate is not None
        )

    def test_contract_is_private_locked_and_has_24_fresh_slots(self) -> None:
        self.assertEqual(len(self.contract.arms), 24)
        self.assertEqual(
            tuple(arm.freshness_token for arm in self.contract.arms),
            tuple(arm.run_id for arm in self.contract.arms),
        )
        self.assertTrue(self.contract.execution_locked)
        self.assertFalse(self.contract.field_execution_allowed)
        self.assertFalse(self.contract.hook_execution_allowed)
        self.assertFalse(self.contract.effect_measurement_allowed)

    def test_stage_order_places_operator_only_between_m1_and_m2(self) -> None:
        for arm in self.contract.arms:
            self.assertEqual(
                tuple(stage.kind for stage in arm.stages),
                (
                    "measurement",
                    "contact",
                    "contact",
                    "contact",
                    "measurement",
                    "operator_boundary",
                    "measurement",
                    "contact",
                    "measurement",
                ),
            )
            self.assertEqual(arm.stages[4].stage_id, "M1")
            self.assertEqual(arm.stages[6].stage_id, "M2")
            self.assertEqual(arm.stages[7].stage_id, "contact.c.e1")

    def test_fake_observations_pass_all_digest_and_order_gates(self) -> None:
        self.assertIsNone(
            _verify_static_contact_observations(self.contract, self._observations())
        )

    def test_spied_mutations_abort_without_partial_result(self) -> None:
        observations = self._observations()
        mutations = (
            tuple(reversed(observations)),
            (replace(observations[0], freshness_token="foreign"), *observations[1:]),
            (replace(observations[0], generator_digest="f" * 64), *observations[1:]),
            observations[:-1],
        )
        for mutated in mutations:
            with self.subTest(first=mutated[0]):
                with self.assertRaisesRegex(
                    PreviousStateMinimalRunnerError,
                    "^static integration verification failed$",
                ):
                    _verify_static_contact_observations(self.contract, mutated)

    def test_rejects_foreign_bundle_and_manifest(self) -> None:
        for bundle, manifest in (
            (object(), self.manifest),
            (self.bundle, object()),
        ):
            with self.subTest(bundle=bundle, manifest=manifest):
                with self.assertRaisesRegex(
                    PreviousStateMinimalRunnerError,
                    "private integration contract invalid",
                ):
                    _build_private_integration_contract(bundle, manifest)  # type: ignore[arg-type]

    def test_module_has_no_field_hook_or_measurement_dependency_and_is_private(self) -> None:
        tree = ast.parse(Path(contract_module.__file__).read_text(encoding="utf-8"))
        imports = {
            node.module
            for node in tree.body
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        self.assertEqual(
            imports,
            {
                "__future__",
                "dataclasses",
                "_previous_state_minimal_runner",
                "_runtime_fixation_structure",
            },
        )
        package_source = Path(mcm_field_organism.__file__).read_text(encoding="utf-8")
        self.assertNotIn("previous_state_integration_contract", package_source)
        self.assertFalse(hasattr(mcm_field_organism, "_build_private_integration_contract"))


if __name__ == "__main__":
    unittest.main()
