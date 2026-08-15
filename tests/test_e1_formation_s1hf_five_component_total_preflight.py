from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gz_real_path_implementation_plan as plan_fixture

from mcm_field_organism.e1_formation_s1hf_five_component_total_preflight import (
    E1FormationS1HFFiveComponentTotalPreflightError,
    S1_HF_COMPONENT_STATUS,
    S1_HF_PRODUCTION_BLOCKERS,
    audit_e1_formation_s1hf_five_component_total_preflight,
)


class E1FormationS1HFFiveComponentTotalPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = plan_fixture.E1FormationS1GZRealPathImplementationPlanTests
        source.setUpClass()
        cls.plan = source()._build()

    def _audit(self):
        return audit_e1_formation_s1hf_five_component_total_preflight(
            self.plan
        )

    def test_all_twelve_static_checks_pass(self) -> None:
        preflight = self._audit()
        self.assertEqual(12, len(preflight.checks))
        self.assertTrue(all(value for _, value in preflight.checks))
        self.assertTrue(preflight.all_five_local_components_present)
        self.assertTrue(preflight.local_contracts_complete)

    def test_five_component_statuses_follow_original_plan(self) -> None:
        preflight = self._audit()
        self.assertEqual(S1_HF_COMPONENT_STATUS, preflight.component_status)
        self.assertEqual(
            self.plan.implementation_sequence,
            tuple(name for name, _ in preflight.component_status),
        )
        self.assertTrue(preflight.synthetic_integration_complete)

    def test_two_productive_trust_boundaries_remain_explicit(self) -> None:
        preflight = self._audit()
        self.assertEqual(S1_HF_PRODUCTION_BLOCKERS, preflight.production_blockers)
        self.assertEqual(2, len(preflight.production_blockers))
        self.assertFalse(preflight.productive_host_verifier_connected)
        self.assertFalse(preflight.productive_kernel_adapter_connected)
        self.assertFalse(preflight.production_implementation_complete)

    def test_preflight_does_not_request_authorize_or_execute(self) -> None:
        preflight = self._audit()
        self.assertFalse(preflight.authorization_request_ready)
        self.assertFalse(preflight.execution_permitted)
        self.assertFalse(preflight.authorization_present)
        self.assertFalse(preflight.token_created)
        self.assertFalse(preflight.receipt_created)
        self.assertFalse(preflight.transition_created)
        self.assertEqual((0, 0), (
            preflight.adapter_calls,
            preflight.field_steps_executed,
        ))
        self.assertFalse(preflight.persistence_performed)
        self.assertFalse(preflight.claims_permitted)

    def test_readiness_tampering_fails_closed(self) -> None:
        preflight = self._audit()
        for change in (
            {"productive_host_verifier_connected": True},
            {"productive_kernel_adapter_connected": True},
            {"production_implementation_complete": True},
            {"authorization_request_ready": True},
            {"execution_permitted": True},
            {"adapter_calls": 1},
        ):
            with self.assertRaises(
                E1FormationS1HFFiveComponentTotalPreflightError
            ):
                replace(preflight, **change)

    def test_preflight_calls_no_effectful_component_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1hf_five_component_total_preflight
        )
        for forbidden in (
            "build_e1_formation_s1ha_pure_real_transition(",
            "bind_e1_formation_s1hb_external_owner_authorization(",
            "issue_e1_formation_s1hc_real_single_use_token(",
            "_seal_e1_formation_s1hd_real_adapter_call_receipt(",
            "run_e1_formation_s1he_gated_single_batch_adapter_synthetically(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            ".consume(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
