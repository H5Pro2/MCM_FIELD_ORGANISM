from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1is_baseline_surface_compatibility import (
    build_dts1_s1is_baseline_surface_compatibility,
)
from mcm_field_organism.dynamic_substrate_s1it_private_adapter_contract import (
    DTS1S1ITPrivateAdapterContractError,
    S1_IT_DECISION,
    build_dts1_s1it_private_adapter_contract,
)


class DTS1S1ITPrivateAdapterContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1it_private_adapter_contract()

    def test_binds_exact_s1is_audit(self) -> None:
        self.assertEqual(
            build_dts1_s1is_baseline_surface_compatibility().audit_digest,
            self._contract().source_s1is_digest,
        )

    def test_binds_six_distinct_private_adapters(self) -> None:
        contract = self._contract()
        self.assertEqual(6, contract.adapter_role_count)
        self.assertEqual(6, len({row[0] for row in contract.adapter_contracts}))

    def test_common_schema_preserves_complete_sh_and_atomic_output(self) -> None:
        inputs = " ".join(self._contract().common_input_schema)
        outputs = " ".join(self._contract().common_output_schema)
        self.assertIn("complete-finite-S-H-prestate", inputs)
        self.assertIn("complete-finite-S-H-checkpoint-vectors", outputs)
        self.assertIn("no-partial-profile", outputs)

    def test_b1_contract_enforces_predivergence_information_barrier(self) -> None:
        b1 = self._contract().adapter_contracts[0]
        self.assertIn("sanitized-common-predivergence-conductive", b1[1])
        self.assertIn("reject-original-DTS1-anatomy", b1[5])

    def test_owned_state_initialization_is_not_candidate_derived(self) -> None:
        rows = self._contract().adapter_contracts
        self.assertIn("neutral-zero-L", rows[1][2])
        self.assertTrue(all("uniform-M" in row[2] for row in rows[2:]))
        forbidden = " ".join(self._contract().forbidden_inputs)
        self.assertIn("DTS1-free-refractory-transfer", forbidden)

    def test_schedule_preserves_events_and_explicit_zero_intervals(self) -> None:
        rules = " ".join(self._contract().schedule_rules)
        self.assertIn("preserve-every-contact-value-order", rules)
        self.assertIn("without-merge-split-delay-replay-or-lookahead", rules)
        self.assertIn("zero-contact-intervals-remain-explicit", rules)

    def test_names_sources_but_selects_no_values_or_digests(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.parameter_source_identities_named)
        self.assertFalse(contract.parameter_values_selected)
        self.assertFalse(contract.configuration_digests_bound)
        rules = " ".join(contract.configuration_rules)
        self.assertIn("remain-unselected-in-S1-IT", rules)

    def test_fail_closed_before_kernel_and_on_any_adapter_failure(self) -> None:
        rules = " ".join(self._contract().fail_closed_rules)
        self.assertIn("before-kernel-entry", rules)
        self.assertIn("invalidates-the-complete-later-joint-audit", rules)

    def test_implements_or_executes_nothing(self) -> None:
        contract = self._contract()
        for value in (
            contract.adapters_implemented,
            contract.profile_container_implemented,
            contract.baseline_models_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_IT_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1ITPrivateAdapterContractError):
            replace(contract, adapter_role_count=5)
        with self.assertRaises(DTS1S1ITPrivateAdapterContractError):
            replace(contract, parameter_values_selected=True)
        source = inspect.getsource(build_dts1_s1it_private_adapter_contract)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
