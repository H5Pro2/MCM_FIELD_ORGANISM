from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from tests import test_e1_formation_s1gz_dry_run_real_mode_runner as gz_fixture

from mcm_field_organism.e1_formation_s1gz_dry_run_real_mode_runner import (
    prepare_e1_formation_s1gz_dry_run_real_mode_call_site,
)
from mcm_field_organism.e1_formation_s1ha_final_real_mode_preflight import (
    E1FormationS1HAFinalRealModePreflightError,
    S1_HA_DECISION,
    S1_HA_CHECK_NAMES,
    preflight_e1_formation_s1ha_final_real_mode_without_authorization,
)


class E1FormationS1HAFinalRealModePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = gz_fixture.E1FormationS1GZDryRunRealModeCallSiteTests
        source.setUpClass()
        cls.contract = source.contract
        cls.call_site = prepare_e1_formation_s1gz_dry_run_real_mode_call_site(
            cls.contract
        )

    def _preflight(self):
        return preflight_e1_formation_s1ha_final_real_mode_without_authorization(
            self.contract,
            self.call_site,
        )

    def test_final_preflight_binds_contract_and_call_site(self) -> None:
        preflight = self._preflight()
        self.assertEqual(
            self.contract.contract_digest,
            preflight.source_s1gy_contract_digest,
        )
        self.assertEqual(
            self.call_site.call_site_digest,
            preflight.source_s1gz_call_site_digest,
        )
        self.assertTrue(preflight.source_chain_bound)
        self.assertTrue(preflight.call_site_bound)
        self.assertTrue(preflight.dry_run_blocker_verified)
        self.assertTrue(preflight.atomic_contract_verified)
        self.assertEqual(S1_HA_CHECK_NAMES, tuple(name for name, _ in preflight.checks))

    def test_final_preflight_preserves_exact_budget_and_atomic_boundary(self) -> None:
        preflight = self._preflight()
        self.assertEqual(6, preflight.expected_arm_count)
        self.assertEqual(2800, preflight.expected_transition_count)
        self.assertEqual(2800, preflight.expected_field_step_count)
        self.assertEqual(660, preflight.expected_source_support_count)
        self.assertEqual(6, preflight.expected_output_count)
        self.assertEqual(6, preflight.expected_receipt_count)

    def test_final_preflight_keeps_execution_closed_pending_owner(self) -> None:
        preflight = self._preflight()
        self.assertTrue(preflight.owner_authorization_required_next)
        self.assertFalse(preflight.owner_authorization_present)
        self.assertFalse(preflight.execution_permitted)
        self.assertFalse(preflight.s1gu_runner_called)
        self.assertFalse(preflight.s1gs_callable_called)
        self.assertFalse(preflight.real_kernel_called)
        self.assertFalse(preflight.field_execution_performed)
        self.assertFalse(preflight.persistence_performed)
        self.assertFalse(preflight.retry_permitted)
        self.assertFalse(preflight.claims_permitted)
        self.assertFalse(preflight.memory_decision_permitted)
        self.assertFalse(preflight.partial_return_permitted)
        self.assertEqual(S1_HA_DECISION, preflight.decision)

    def test_final_preflight_is_deterministic_and_tamper_evident(self) -> None:
        first = self._preflight()
        second = self._preflight()
        self.assertEqual(first.preflight_digest, second.preflight_digest)
        with self.assertRaises(E1FormationS1HAFinalRealModePreflightError):
            replace(first, owner_authorization_present=True)
        with self.assertRaises(E1FormationS1HAFinalRealModePreflightError):
            replace(first, expected_transition_count=2799)

    def test_final_preflight_calls_no_runner_transition_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            preflight_e1_formation_s1ha_final_real_mode_without_authorization
        )
        for forbidden in (
            "run_e1_formation_s1gu_six_arm_counting_adapter(",
            "advance_e1_formation_s1gs_real_single_batch_transition(",
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
