from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1it_private_adapter_contract import (
    build_dts1_s1it_private_adapter_contract,
)
from mcm_field_organism.dynamic_substrate_s1iu_finite_binding_precheck import (
    DTS1S1IUFiniteBindingPrecheckError,
    S1_IU_DECISION,
    build_dts1_s1iu_finite_binding_precheck,
)


class DTS1S1IUFiniteBindingPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1iu_finite_binding_precheck()

    def test_binds_exact_s1it_contract(self) -> None:
        self.assertEqual(
            build_dts1_s1it_private_adapter_contract().contract_digest,
            self._audit().source_s1it_digest,
        )

    def test_ie_and_ih_have_common_field_exposures(self) -> None:
        records = {row[0]: row[1:] for row in self._audit().exposure_records}
        self.assertEqual("COMMON_CAUSAL_FIELD_SCHEDULE_BOUND", records["P_IE_CAUSAL_TWO_SUBSTEP"][1])
        self.assertEqual("COMMON_CAUSAL_FIELD_SCHEDULE_BOUND", records["P_IH_ATTENUATION"][1])

    def test_ik_and_in_are_blocked_before_finite_binding(self) -> None:
        records = {row[0]: row[1:] for row in self._audit().exposure_records}
        self.assertEqual("BLOCKED_COMMON_BASELINE_CAUSAL_EXPOSURE_UNBOUND", records["P_IK_INTERFERENCE"][1])
        self.assertEqual("BLOCKED_COMMON_BASELINE_CAUSAL_EXPOSURE_UNBOUND", records["P_IN_RELEASE_REUSE"][1])

    def test_records_resource_only_history_and_fresh_final_readout(self) -> None:
        facts = " ".join(self._audit().blocking_facts)
        self.assertIn("supplied-as-DTS1-edge-participation", facts)
        self.assertIn("fresh-common-S-H-prestates", facts)
        self.assertIn("not-the-complete-causal-exposure", facts)

    def test_splits_planned_matrix_into_ready_and_blocked_cases(self) -> None:
        audit = self._audit()
        self.assertEqual(24, audit.planned_adapter_case_count)
        self.assertEqual(12, audit.ready_adapter_case_count)
        self.assertEqual(12, audit.blocked_adapter_case_count)
        self.assertFalse(audit.finite_case_matrix_bound)

    def test_forbids_invented_mapping_and_candidate_information(self) -> None:
        rules = " ".join(self._audit().stopp_rules)
        self.assertIn("do-not-invent-map-or-fit-receptor-histories", rules)
        self.assertIn("do-not-pass-DTS1-participation-resource-state", rules)

    def test_binds_no_values_digests_implementation_or_execution(self) -> None:
        audit = self._audit()
        for value in (
            audit.common_exposure_contract_valid,
            audit.parameter_values_selected,
            audit.configuration_digests_bound,
            audit.refinements_selected,
            audit.adapters_implemented,
            audit.baseline_models_executed,
            audit.runtime_integration_present,
            audit.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (audit.technical_field_steps_executed, audit.research_field_steps_executed))
        self.assertEqual(S1_IU_DECISION, audit.decision)

    def test_authorizes_only_common_exposure_contract_next(self) -> None:
        self.assertTrue(self._audit().common_exposure_contract_authorized_next_stage)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1IUFiniteBindingPrecheckError):
            replace(audit, finite_case_matrix_bound=True)
        with self.assertRaises(DTS1S1IUFiniteBindingPrecheckError):
            replace(audit, blocked_adapter_case_count=0)
        source = inspect.getsource(build_dts1_s1iu_finite_binding_precheck)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
