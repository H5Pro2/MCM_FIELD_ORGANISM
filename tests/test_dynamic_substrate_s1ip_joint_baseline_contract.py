from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1io_evidence_falsification_audit import (
    build_dts1_s1io_evidence_falsification_audit,
)
from mcm_field_organism.dynamic_substrate_s1ip_joint_baseline_contract import (
    DTS1S1IPJointBaselineContractError,
    S1_IP_DECISION,
    build_dts1_s1ip_joint_baseline_contract,
)


class DTS1S1IPJointBaselineContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1ip_joint_baseline_contract()

    def test_binds_s1io_and_all_five_reference_receipts(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1io_evidence_falsification_audit().audit_digest, contract.source_s1io_audit_digest)
        self.assertEqual(("S1-IB", "S1-IE", "S1-IH", "S1-IK", "S1-IN"), tuple(name for name, _ in contract.reference_receipts))

    def test_binds_six_existing_executable_and_two_structural_roles(self) -> None:
        contract = self._contract()
        self.assertEqual(6, len(contract.executable_baseline_roles))
        self.assertEqual(2, len(contract.structural_baseline_roles))
        roles = {name for name, _ in contract.executable_baseline_roles}
        self.assertIn("B1_FIXED_PRERELEASE_ADAPTER", roles)
        self.assertIn("B2_S2_LINEAR_INTEGRATOR", roles)
        self.assertIn("B3_F3_LOCAL_LEAKY", roles)
        self.assertIn("B5_F3_FULL", roles)
        self.assertIn("B6_CONST_V", roles)

    def test_profile_has_four_blocks_and_exactly_36_signed_components(self) -> None:
        contract = self._contract()
        self.assertEqual(4, len(contract.profile_blocks))
        self.assertEqual(36, sum(count for _, _, count in contract.profile_blocks))
        self.assertEqual(36, contract.profile_component_count)
        rules = " ".join(contract.profile_rules)
        self.assertIn("all-components-remain-signed", rules)
        self.assertIn("two-node-and-three-node-blocks-remain-separate", rules)

    def test_direct_resource_and_control_evidence_remain_hard_gates(self) -> None:
        gates = " ".join(self._contract().structural_gates)
        for source in ("S1-IB", "S1-IE", "S1-IH", "S1-IK", "S1-IN"):
            self.assertIn(source, gates)
        self.assertIn("no-observable-profile-fit-may-substitute", gates)

    def test_baselines_receive_no_dts1_partition_or_result_information(self) -> None:
        contract = self._contract()
        forbidden = " ".join(contract.forbidden_baseline_inputs)
        self.assertIn("DTS1-free-refractory-or-transfer-ledger", forbidden)
        self.assertIn("arm-id-case-id-checkpoint-id-target-direction", forbidden)
        self.assertIn("result-dependent-parameter-values", forbidden)
        self.assertIn("postdivergence", forbidden)

    def test_one_configuration_per_baseline_and_no_oracle(self) -> None:
        rules = " ".join(self._contract().parameter_rules)
        self.assertIn("one-configuration-digest-across-all-compatible-profile-blocks", rules)
        self.assertIn("not-equations-parameters-or-state-dimension", rules)
        self.assertIn("no-oracle-gain-per-checkpoint", rules)

    def test_metrics_and_atomic_decision_order_are_bound_without_threshold(self) -> None:
        contract = self._contract()
        metrics = " ".join(contract.comparison_metrics)
        self.assertIn("profile_linf_residual-over-all-36", metrics)
        self.assertIn("per-block-linf-residual", metrics)
        self.assertEqual("INVALID_JOINT_BASELINE_AUDIT", contract.decision_order[0])
        self.assertTrue(contract.atomic_decision_required)
        self.assertFalse(contract.comparison_threshold_selected)

    def test_stops_on_incompatibility_omission_or_failed_direct_gate(self) -> None:
        stopp = " ".join(self._contract().stopp_conditions)
        self.assertIn("incompatible-baseline-is-silently-omitted", stopp)
        self.assertIn("profile-fit-is-used-to-overrule", stopp)
        self.assertIn("result-dependent-fit", stopp)

    def test_selects_no_values_implementation_runtime_or_execution(self) -> None:
        contract = self._contract()
        for value in (
            contract.parameter_values_selected,
            contract.geometry_adapters_implemented,
            contract.profile_container_implemented,
            contract.baseline_models_executed,
            contract.joint_comparison_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
            contract.baseline_closure_proven,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_IP_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1IPJointBaselineContractError):
            replace(contract, profile_component_count=35)
        with self.assertRaises(DTS1S1IPJointBaselineContractError):
            replace(contract, baseline_models_executed=True)
        source = inspect.getsource(build_dts1_s1ip_joint_baseline_contract)
        for forbidden in ("compute_", "advance_", "execute_", "run_", "open(", "write_text("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
