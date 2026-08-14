from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_formation_adapter import (
    produce_e1_confirmation_canonical_formation,
)
from mcm_field_organism.e1_confirmation_canonical_probe_handoff import (
    E1ConfirmationCanonicalProbeHandoffError,
    _canonical_probe_binding,
    prepare_e1_confirmation_canonical_probe_handoff,
)
from mcm_field_organism.e1_confirmation_canonical_producer_binding import (
    prepare_e1_confirmation_canonical_producer_binding,
)
from mcm_field_organism.e1_confirmation_chain_contract import (
    prepare_e1_confirmation_chain_contract,
)
from mcm_field_organism.e1_refined_formation_runner import _digest
from tests.test_e1_confirmation_formation_runner import _inputs


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


def _inputs_with_substituted_formation():
    binding = prepare_e1_confirmation_canonical_producer_binding(
        REPORTS, UPSTREAM
    )
    chain = prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM)
    with patch(
        "mcm_field_organism.e1_confirmation_canonical_formation_adapter."
        "_canonical_inputs",
        return_value=_inputs(),
    ):
        formation = produce_e1_confirmation_canonical_formation(binding, chain)
    production_payload = {
        "source_provenance": "canonical-s1eb9",
        "binding_digest": binding.digest(),
        "chain_contract_digest": chain.digest(),
        "ab_plan_digest": binding.ab_plan_digest,
        "ba_plan_digest": binding.ba_plan_digest,
        "initial_field_digest": binding.initial_field_digest,
        "initial_state_digest": binding.initial_state_digest,
        "result_digests": tuple(
            item.result_digest for item in formation.refinements
        ),
    }
    formation = replace(
        formation,
        ab_plan_digest=binding.ab_plan_digest,
        ba_plan_digest=binding.ba_plan_digest,
        initial_field_digest=binding.initial_field_digest,
        initial_state_digest=binding.initial_state_digest,
        production_digest=_digest(production_payload),
    )
    return binding, chain, formation


class E1ConfirmationCanonicalProbeHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.binding, cls.chain, cls.formation = (
            _inputs_with_substituted_formation()
        )

    def test_handoff_aligns_formation_and_canonical_probe_refinements(self):
        result = prepare_e1_confirmation_canonical_probe_handoff(
            self.binding, self.chain, self.formation
        )

        self.assertEqual(("r2", "r4", "r8"), tuple(
            role for role, _ in result.formation_result_digests
        ))
        self.assertEqual(("r2", "r4", "r8"), tuple(
            role for role, _ in result.probe_plan_digests
        ))
        self.assertEqual(self.binding.probe_digest, result.probe_source_digest)
        self.assertEqual(
            self.binding.probe_plan_digest, result.probe_plan_set_digest
        )
        self.assertTrue(result.handoff_bound)

    def test_probe_binding_resolves_without_field_or_probe_execution(self):
        corridor, source, plans = _canonical_probe_binding(self.chain)

        self.assertEqual(
            self.chain.confirmation_contract_digest, corridor.digest()
        )
        self.assertEqual(self.binding.probe_plan_digest, plans.digest())
        self.assertEqual(110, plans.source_event_count)
        self.assertEqual(2, len(source))

    def test_changed_formation_fails_before_probe_binding(self) -> None:
        changed = replace(self.formation, ab_plan_digest="0" * 64)

        with patch(
            "mcm_field_organism.e1_confirmation_canonical_probe_handoff."
            "_canonical_probe_binding",
            side_effect=AssertionError("probe binding built"),
        ):
            with self.assertRaises(E1ConfirmationCanonicalProbeHandoffError):
                prepare_e1_confirmation_canonical_probe_handoff(
                    self.binding, self.chain, changed
                )

    def test_handoff_is_repeatable_and_execution_stays_closed(self) -> None:
        first = prepare_e1_confirmation_canonical_probe_handoff(
            self.binding, self.chain, self.formation
        )
        second = prepare_e1_confirmation_canonical_probe_handoff(
            self.binding, self.chain, self.formation
        )

        self.assertEqual(first, second)
        for role in (
            "probe_execution_permitted",
            "decision_permitted",
            "persistence_permitted",
            "claims_permitted",
        ):
            self.assertFalse(getattr(first, role))

    def test_handoff_contains_no_runtime_decision_or_persistence_call(self):
        source = inspect.getsource(
            prepare_e1_confirmation_canonical_probe_handoff
        )
        for forbidden in (
            "run_synthetic_e1_confirmation_seven_arm_probe",
            "advance_frozen_e1_fast_shared_field_transient",
            "build_e1_confirmation_chain_result",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)

    def test_handoff_keeps_paths_free_and_roles_private(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        prepare_e1_confirmation_canonical_probe_handoff(
            self.binding, self.chain, self.formation
        )

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))
        for role in (
            "E1ConfirmationCanonicalProbeHandoff",
            "prepare_e1_confirmation_canonical_probe_handoff",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
