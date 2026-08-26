from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_probe_adapter import (
    _run_bound_probe_core,
)
from mcm_field_organism.e1_confirmation_canonical_probe_handoff import (
    prepare_e1_confirmation_canonical_probe_handoff,
)
from mcm_field_organism.e1_confirmation_canonical_result_handoff import (
    E1ConfirmationCanonicalResultHandoffError,
    prepare_e1_confirmation_canonical_result_handoff,
)
from mcm_field_organism.e1_frozen_state_transfer_contract import _probe_digest
from mcm_field_organism.e1_refined_formation_runner import _digest
from tests.test_e1_a0_av_history_producer import field
from tests.test_e1_confirmation_canonical_probe_handoff import (
    _inputs_with_substituted_formation,
)
from tests.test_e1_confirmation_seven_arm_probe import _inputs


REPORTS = Path("reports")
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


def _canonicalized_probe_results(binding, probe_handoff):
    corridor, formation, source, plans = _inputs()
    source_digest = _probe_digest(source)
    synthetic = tuple(
        _run_bound_probe_core(
            corridor, formed, field, source, plan, source_digest
        )
        for formed, plan in zip(
            formation.refinements, plans.plans, strict=True
        )
    )
    canonical_plans = dict(probe_handoff.probe_plan_digests)
    results = []
    for item in synthetic:
        values = {
            name: getattr(item, name)
            for name in item.__dataclass_fields__
            if name != "result_digest"
        }
        values["probe_source_digest"] = binding.probe_digest
        values["probe_plan_digest"] = canonical_plans[item.refinement_id]
        results.append(
            replace(item, **values, result_digest=_digest(values))
        )
    return tuple(results)


class E1ConfirmationCanonicalResultHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.binding, cls.chain, cls.formation = (
            _inputs_with_substituted_formation()
        )
        cls.probe_handoff = prepare_e1_confirmation_canonical_probe_handoff(
            cls.binding, cls.chain, cls.formation
        )
        cls.probes = _canonicalized_probe_results(
            cls.binding, cls.probe_handoff
        )

    def test_handoff_binds_three_probes_to_result_inventory(self) -> None:
        result = prepare_e1_confirmation_canonical_result_handoff(
            self.binding,
            self.chain,
            self.formation,
            self.probe_handoff,
            self.probes,
        )

        self.assertEqual(("r2", "r4", "r8"), tuple(
            role for role, _ in result.probe_result_digests
        ))
        self.assertEqual(self.chain.metrics, result.metrics)
        self.assertEqual(
            self.chain.required_controls, result.required_controls
        )
        self.assertEqual(
            self.chain.technical_decisions, result.technical_decisions
        )
        self.assertTrue(result.result_handoff_bound)

    def test_frozen_state_bindings_match_formation(self) -> None:
        result = prepare_e1_confirmation_canonical_result_handoff(
            self.binding,
            self.chain,
            self.formation,
            self.probe_handoff,
            self.probes,
        )

        self.assertEqual(
            self.probe_handoff.formation_state_digests,
            result.frozen_state_digests,
        )

    def test_changed_probe_source_fails_closed(self) -> None:
        values = {
            name: getattr(self.probes[0], name)
            for name in self.probes[0].__dataclass_fields__
            if name != "result_digest"
        }
        values["probe_source_digest"] = "0" * 64
        changed = replace(
            self.probes[0], **values, result_digest=_digest(values)
        )

        with self.assertRaises(E1ConfirmationCanonicalResultHandoffError):
            prepare_e1_confirmation_canonical_result_handoff(
                self.binding,
                self.chain,
                self.formation,
                self.probe_handoff,
                (changed, self.probes[1], self.probes[2]),
            )

    def test_changed_probe_order_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationCanonicalResultHandoffError,
            "ordered",
        ):
            prepare_e1_confirmation_canonical_result_handoff(
                self.binding,
                self.chain,
                self.formation,
                self.probe_handoff,
                tuple(reversed(self.probes)),
            )

    def test_handoff_is_repeatable_and_all_release_roles_are_closed(self):
        args = (
            self.binding,
            self.chain,
            self.formation,
            self.probe_handoff,
            self.probes,
        )
        first = prepare_e1_confirmation_canonical_result_handoff(*args)
        second = prepare_e1_confirmation_canonical_result_handoff(*args)

        self.assertEqual(first, second)
        for role in (
            "result_composition_permitted",
            "decision_permitted",
            "persistence_permitted",
            "claims_permitted",
        ):
            self.assertFalse(getattr(first, role))

    def test_handoff_has_no_composition_decision_or_persistence_call(self):
        source = inspect.getsource(
            prepare_e1_confirmation_canonical_result_handoff
        )
        for forbidden in (
            "build_e1_confirmation_chain_result(",
            "compose_synthetic_e1_confirmation_chain",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)

    def test_handoff_keeps_paths_free_and_roles_private(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        inspect.getsource(prepare_e1_confirmation_canonical_result_handoff)

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))
        for role in (
            "E1ConfirmationCanonicalResultHandoff",
            "prepare_e1_confirmation_canonical_result_handoff",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
