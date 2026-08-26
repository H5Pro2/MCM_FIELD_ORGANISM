from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from tests import (
    test_e1_formation_s1gk_fixed_adapter_real_wrapper_contract as contract_fixture,
)

from mcm_field_organism.e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract,
)
from mcm_field_organism.e1_formation_s1gt_six_arm_release_scope_contract import (
    bind_e1_formation_s1gt_six_arm_release_scope_contract,
)
from mcm_field_organism.e1_formation_s1gv_real_mode_binding_contract import (
    bind_e1_formation_s1gv_real_mode_binding_contract,
)
from mcm_field_organism.e1_formation_s1gw_real_mode_gate import (
    build_e1_formation_s1gw_real_mode_gate,
)
from mcm_field_organism.e1_formation_s1gx_real_mode_preflight import (
    preflight_e1_formation_s1gx_real_mode,
)
from mcm_field_organism.e1_formation_s1gy_atomic_real_mode_execution_contract import (
    bind_e1_formation_s1gy_atomic_real_mode_execution_contract,
)
from mcm_field_organism.e1_formation_s1gz_dry_run_real_mode_runner import (
    E1FormationS1GZDryRunRealModeCallSiteError,
    S1_GZ_DECISION,
    S1_GZ_DRY_RUN_GUARDS,
    prepare_e1_formation_s1gz_dry_run_real_mode_call_site,
)


class E1FormationS1GZDryRunRealModeCallSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = contract_fixture.E1FormationS1GKFixedAdapterRealWrapperContractTests
        source.setUpClass()
        cls.bridge = source.bridge
        cls.source_contract = (
            prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
                source.bridge,
                source.integration,
            )
        )
        scope = bind_e1_formation_s1gt_six_arm_release_scope_contract(
            cls.source_contract
        )
        real_mode = bind_e1_formation_s1gv_real_mode_binding_contract(scope)
        gate = build_e1_formation_s1gw_real_mode_gate(real_mode)
        preflight = preflight_e1_formation_s1gx_real_mode(
            scope,
            real_mode,
            gate,
            cls.source_contract,
            cls.bridge,
        )
        cls.contract = bind_e1_formation_s1gy_atomic_real_mode_execution_contract(
            preflight
        )

    def _call_site(self):
        return prepare_e1_formation_s1gz_dry_run_real_mode_call_site(self.contract)

    def test_call_site_binds_runner_and_transition_without_execution(self) -> None:
        call_site = self._call_site()
        self.assertEqual(
            "run_e1_formation_s1gu_six_arm_counting_adapter",
            call_site.runner_name,
        )
        self.assertEqual(
            "advance_e1_formation_s1gs_real_single_batch_transition",
            call_site.selected_transition_name,
        )
        self.assertEqual(("scope", "source_contract", "bridge"), call_site.runner_required_parameters)
        self.assertEqual("carrier_transition", call_site.runner_keyword_injection_parameter)
        self.assertEqual(("fresh", "batch", "carrier"), call_site.transition_required_parameters)
        self.assertTrue(call_site.dry_run_gate_present)
        self.assertTrue(call_site.blocked_before_callable_invocation)

    def test_call_site_preserves_exact_six_arm_budget(self) -> None:
        call_site = self._call_site()
        self.assertEqual(6, call_site.expected_arm_count)
        self.assertEqual(2800, call_site.expected_transition_count)
        self.assertEqual(2800, call_site.expected_field_step_count)
        self.assertEqual(660, call_site.expected_source_support_count)
        self.assertEqual(6, call_site.expected_output_count)
        self.assertEqual(6, call_site.expected_receipt_count)
        self.assertEqual(S1_GZ_DRY_RUN_GUARDS, call_site.dry_run_guards)

    def test_call_site_keeps_real_runner_kernel_and_claims_closed(self) -> None:
        call_site = self._call_site()
        self.assertFalse(call_site.s1gu_runner_called)
        self.assertFalse(call_site.s1gs_callable_called)
        self.assertFalse(call_site.real_kernel_called)
        self.assertFalse(call_site.execution_permitted)
        self.assertFalse(call_site.owner_authorization_present)
        self.assertFalse(call_site.persistence_performed)
        self.assertFalse(call_site.retry_permitted)
        self.assertFalse(call_site.claims_permitted)
        self.assertFalse(call_site.memory_decision_permitted)
        self.assertFalse(call_site.partial_return_permitted)
        self.assertEqual(S1_GZ_DECISION, call_site.decision)

    def test_call_site_is_deterministic_and_tamper_evident(self) -> None:
        first = self._call_site()
        second = self._call_site()
        self.assertEqual(first.call_site_digest, second.call_site_digest)
        with self.assertRaises(E1FormationS1GZDryRunRealModeCallSiteError):
            replace(first, s1gs_callable_called=True)
        with self.assertRaises(E1FormationS1GZDryRunRealModeCallSiteError):
            replace(first, expected_transition_count=2799)

    def test_call_site_source_calls_no_runner_transition_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            prepare_e1_formation_s1gz_dry_run_real_mode_call_site
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
