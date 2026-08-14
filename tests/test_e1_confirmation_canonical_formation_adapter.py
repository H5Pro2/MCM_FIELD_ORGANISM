from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_formation_adapter import (
    E1ConfirmationCanonicalFormationAdapterError,
    _canonical_inputs,
    produce_e1_confirmation_canonical_formation,
)
from mcm_field_organism.e1_confirmation_canonical_producer_binding import (
    prepare_e1_confirmation_canonical_producer_binding,
)
from mcm_field_organism.e1_confirmation_chain_contract import (
    prepare_e1_confirmation_chain_contract,
)
from tests.test_e1_confirmation_formation_runner import _inputs


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


def _bindings():
    return (
        prepare_e1_confirmation_canonical_producer_binding(REPORTS, UPSTREAM),
        prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM),
    )


class E1ConfirmationCanonicalFormationAdapterTests(unittest.TestCase):
    def test_canonical_resolver_matches_s1eb9_binding_without_running_field(self):
        binding, chain = _bindings()

        corridor, source, ab, ba, field, state = _canonical_inputs(
            binding, chain
        )

        self.assertEqual(chain.confirmation_contract_digest, corridor.digest())
        self.assertEqual(binding.permutation_digest, source.permutation_digest)
        self.assertEqual(binding.ab_plan_digest, ab.digest())
        self.assertEqual(binding.ba_plan_digest, ba.digest())
        self.assertEqual(binding.geometry_digest, field.layer.digest())
        self.assertTrue(all(item.binding == 0.0 for item in state.edge_bindings))
        self.assertEqual(0, field.layer.tick)
        self.assertIsNone(field.last_distribution)

    def test_invalid_binding_fails_before_canonical_inputs(self) -> None:
        binding, chain = _bindings()
        invalid = replace(binding, initial_state_digest="0" * 64)

        with patch(
            "mcm_field_organism.e1_confirmation_canonical_formation_adapter."
            "_canonical_inputs",
            side_effect=AssertionError("canonical inputs built"),
        ):
            with self.assertRaises(E1ConfirmationCanonicalFormationAdapterError):
                produce_e1_confirmation_canonical_formation(invalid, chain)

    def test_five_arm_core_runs_only_with_substituted_synthetic_inputs(self):
        binding, chain = _bindings()
        synthetic = _inputs()

        with patch(
            "mcm_field_organism.e1_confirmation_canonical_formation_adapter."
            "_canonical_inputs",
            return_value=synthetic,
        ):
            result = produce_e1_confirmation_canonical_formation(binding, chain)

        self.assertEqual("canonical-s1eb9", result.source_provenance)
        self.assertEqual(
            (("r2", 2), ("r4", 4), ("r8", 8)),
            tuple(
                (item.refinement_id, item.factor)
                for item in result.refinements
            ),
        )
        for refinement in result.refinements:
            self.assertEqual(refinement.b_ab, refinement.b_ab_identity)
            self.assertIsNot(refinement.b_ab, refinement.b_ab_identity)
            for state in (
                refinement.b_ab_formation_ablated,
                refinement.b_ba_formation_ablated,
            ):
                self.assertTrue(
                    all(item.binding == 0.0 for item in state.edge_bindings)
                )

    def test_substituted_core_is_repeatable_and_preserves_inputs(self) -> None:
        binding, chain = _bindings()
        synthetic = _inputs()
        field = synthetic[4]
        state = synthetic[5]
        layer_digest = field.layer.digest()

        with patch(
            "mcm_field_organism.e1_confirmation_canonical_formation_adapter."
            "_canonical_inputs",
            return_value=synthetic,
        ):
            first = produce_e1_confirmation_canonical_formation(binding, chain)
            second = produce_e1_confirmation_canonical_formation(binding, chain)

        self.assertEqual(first.production_digest, second.production_digest)
        self.assertEqual(layer_digest, field.layer.digest())
        self.assertIsNone(field.last_distribution)
        self.assertTrue(all(item.binding == 0.0 for item in state.edge_bindings))

    def test_adapter_has_no_probe_persistence_or_release_path(self) -> None:
        source = inspect.getsource(produce_e1_confirmation_canonical_formation)
        for forbidden in (
            "_fixed_probe_sequences",
            "run_synthetic_e1_confirmation_seven_arm_probe",
            "compose_synthetic_e1_confirmation_chain",
            "write_text",
            "open(",
            "execution_permitted = True",
        ):
            self.assertNotIn(forbidden, source)

    def test_adapter_keeps_one_shot_paths_free_and_roles_private(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        inspect.getsource(produce_e1_confirmation_canonical_formation)

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))
        for role in (
            "E1ConfirmationCanonicalFormationProduction",
            "produce_e1_confirmation_canonical_formation",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
