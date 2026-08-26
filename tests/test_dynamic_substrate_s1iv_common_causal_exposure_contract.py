from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1iu_finite_binding_precheck import (
    build_dts1_s1iu_finite_binding_precheck,
)
from mcm_field_organism.dynamic_substrate_s1iv_common_causal_exposure_contract import (
    DTS1S1IVCommonCausalExposureContractError,
    S1_IV_DECISION,
    build_dts1_s1iv_common_causal_exposure_contract,
)


class DTS1S1IVCommonCausalExposureContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1iv_common_causal_exposure_contract()

    def test_binds_exact_s1iu_precheck(self) -> None:
        self.assertEqual(
            build_dts1_s1iu_finite_binding_precheck().audit_digest,
            self._contract().source_s1iu_digest,
        )

    def test_common_events_are_model_neutral_and_delivered_to_all_models(self) -> None:
        schema = " ".join(self._contract().common_event_schema)
        self.assertIn("no-model-state-coordinate", schema)
        self.assertIn("delivered-to-DTS1-B1-B2-B3-B4-B5-and-B6", schema)
        self.assertIn("its-carried-prestate", schema)

    def test_pik_binds_aba_and_a_gap_a_before_common_readout(self) -> None:
        schedule = self._contract().p_ik_schedule
        self.assertEqual(("A_EXPOSURE", "B_EXPOSURE", "A_EXPOSURE"), tuple(row[2] for row in schedule[:3]))
        self.assertEqual(("A_EXPOSURE", "GAP_EXPOSURE", "A_EXPOSURE"), tuple(row[2] for row in schedule[3:6]))
        self.assertEqual(("COMMON_SH_RESET", "COMMON_ZERO_CONTACT_READOUT"), tuple(row[2] for row in schedule[-2:]))

    def test_pin_separates_common_exposure_from_dts1_recovery_switch(self) -> None:
        schedule = self._contract().p_in_schedule
        self.assertEqual("DTS1_RECOVERY_CHANNEL_ON_ONLY", schedule[2][3])
        self.assertEqual("DTS1_RECOVERY_CHANNEL_OFF_ONLY", schedule[3][3])
        rules = " ".join(self._contract().intervention_rules)
        self.assertIn("remain-configuration-identical-between-P_IN-arms", rules)

    def test_reset_changes_only_sh_and_preserves_every_owned_state(self) -> None:
        rules = " ".join(self._contract().state_rules)
        self.assertIn("overwrites-only-exposed-S-H", rules)
        self.assertIn("preserves-DTS1-anatomy-B1-fixed-adapter-B2-L", rules)
        self.assertIn("B3-through-B6-M-bit-for-bit", rules)

    def test_quarantines_old_field_vectors_but_retains_direct_ledgers(self) -> None:
        dispositions = dict(self._contract().profile_disposition)
        self.assertEqual("RETAIN_EXISTING_PROFILE_AND_RECEIPT", dispositions["P_IE_CAUSAL_TWO_SUBSTEP"])
        self.assertIn("QUARANTINE_OLD_FIELD_VECTOR", dispositions["P_IK_INTERFERENCE"])
        self.assertIn("RETAIN_DIRECT_LEDGERS", dispositions["P_IN_RELEASE_REUSE"])
        self.assertEqual((2, 2, 2), (self._contract().old_profile_blocks_retained, self._contract().old_field_blocks_quarantined, self._contract().direct_ledger_blocks_retained))

    def test_requires_controlled_reregistration_without_old_numeric_reuse(self) -> None:
        rules = " ".join(self._contract().reregistration_rules)
        self.assertIn("without-reusing-old-numeric-vectors", rules)
        self.assertIn("final-two-six-component-blocks-require-new-receipts", rules)
        self.assertEqual(28, self._contract().future_profile_component_count)

    def test_selects_no_values_implementation_or_execution(self) -> None:
        contract = self._contract()
        for value in (
            contract.exposure_values_selected,
            contract.durations_selected,
            contract.reset_prestate_selected,
            contract.configuration_values_selected,
            contract.configuration_digests_bound,
            contract.fixture_implemented,
            contract.adapters_implemented,
            contract.baseline_models_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_IV_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1IVCommonCausalExposureContractError):
            replace(contract, old_field_blocks_quarantined=0)
        with self.assertRaises(DTS1S1IVCommonCausalExposureContractError):
            replace(contract, exposure_values_selected=True)
        source = inspect.getsource(build_dts1_s1iv_common_causal_exposure_contract)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
