from __future__ import annotations

import inspect
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_probe_adapter import (
    E1ConfirmationCanonicalProbeAdapterError,
    _canonical_probe_inputs,
    _run_bound_probe_core,
    run_e1_confirmation_canonical_seven_arm_probe,
)
from mcm_field_organism.e1_confirmation_canonical_probe_handoff import (
    prepare_e1_confirmation_canonical_probe_handoff,
)
from mcm_field_organism.e1_frozen_state_transfer_contract import _probe_digest
from tests.test_e1_confirmation_canonical_probe_handoff import (
    _inputs_with_substituted_formation,
)
from tests.test_e1_confirmation_seven_arm_probe import _inputs
from tests.test_e1_a0_av_history_producer import field


REPORTS = Path("reports")
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


class E1ConfirmationCanonicalProbeAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.binding, cls.chain, cls.formation = (
            _inputs_with_substituted_formation()
        )
        cls.handoff = prepare_e1_confirmation_canonical_probe_handoff(
            cls.binding, cls.chain, cls.formation
        )
        cls.corridor, cls.synthetic_formation, cls.probe, cls.plans = _inputs()

    def test_canonical_resolver_binds_probe_without_running_it(self) -> None:
        corridor, probe, plans, factory = _canonical_probe_inputs(
            self.binding, self.chain
        )

        self.assertEqual(self.chain.confirmation_contract_digest, corridor.digest())
        self.assertEqual(self.binding.probe_digest, _probe_digest(probe))
        self.assertEqual(self.binding.probe_plan_digest, plans.digest())
        first = factory()
        second = factory()
        self.assertIsNot(first, second)
        self.assertEqual(first.layer.digest(), second.layer.digest())

    def test_synthetic_core_preserves_all_seven_arm_controls(self) -> None:
        expected_source = _probe_digest(self.probe)
        results = tuple(
            _run_bound_probe_core(
                self.corridor,
                formed,
                field,
                self.probe,
                plan,
                expected_source,
            )
            for formed, plan in zip(
                self.synthetic_formation.refinements,
                self.plans.plans,
                strict=True,
            )
        )

        self.assertEqual(("r2", "r4", "r8"), tuple(
            item.refinement_id for item in results
        ))
        for result in results:
            self.assertEqual(0.0, result.probe_ablation_residual)
            self.assertEqual(0.0, result.fixed_adapter_residual)
            self.assertEqual(
                result.pre_probe_ab_state_digest,
                result.post_probe_ab_state_digest,
            )
            self.assertEqual(
                result.pre_probe_ba_state_digest,
                result.post_probe_ba_state_digest,
            )

    def test_synthetic_core_is_repeatable(self) -> None:
        expected_source = _probe_digest(self.probe)
        args = (
            self.corridor,
            self.synthetic_formation.refinements[0],
            field,
            self.probe,
            self.plans.plans[0],
            expected_source,
        )

        self.assertEqual(
            _run_bound_probe_core(*args),
            _run_bound_probe_core(*args),
        )

    def test_source_mismatch_fails_before_field_construction(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationCanonicalProbeAdapterError,
            "does not match",
        ):
            _run_bound_probe_core(
                self.corridor,
                self.synthetic_formation.refinements[0],
                lambda: (_ for _ in ()).throw(AssertionError("field built")),
                self.probe,
                self.plans.plans[0],
                "0" * 64,
            )

    def test_canonical_entrypoint_stops_before_input_resolution(self) -> None:
        with patch(
            "mcm_field_organism.e1_confirmation_canonical_probe_adapter."
            "_canonical_probe_inputs",
            side_effect=AssertionError("canonical inputs resolved"),
        ):
            with self.assertRaisesRegex(
                E1ConfirmationCanonicalProbeAdapterError,
                "remains locked",
            ):
                run_e1_confirmation_canonical_seven_arm_probe(
                    self.binding,
                    self.chain,
                    self.formation,
                    self.handoff,
                )

    def test_invalid_handoff_fails_closed_without_attribute_error(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationCanonicalProbeAdapterError,
            "S1-EB11 handoff",
        ):
            run_e1_confirmation_canonical_seven_arm_probe(
                self.binding,
                self.chain,
                self.formation,
                None,
            )

    def test_adapter_has_no_decision_or_persistence_path(self) -> None:
        source = inspect.getsource(run_e1_confirmation_canonical_seven_arm_probe)
        for forbidden in (
            "build_e1_confirmation_chain_result",
            "technical_decision",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)

    def test_adapter_keeps_paths_free_and_roles_private(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        inspect.getsource(_run_bound_probe_core)

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))
        for role in (
            "E1ConfirmationCanonicalProbeAdapterError",
            "run_e1_confirmation_canonical_seven_arm_probe",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
