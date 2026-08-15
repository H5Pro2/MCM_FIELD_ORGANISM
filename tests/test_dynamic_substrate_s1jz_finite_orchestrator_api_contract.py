from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jx_sequence_carry_orchestration_contract import build_dts1_s1jx_sequence_carry_orchestration_contract
from mcm_field_organism.dynamic_substrate_s1jy_orchestrator_api_readiness_precheck import build_dts1_s1jy_orchestrator_api_readiness_precheck
from mcm_field_organism.dynamic_substrate_s1jz_finite_orchestrator_api_contract import (
    DTS1S1JZFiniteOrchestratorAPIContractError,
    S1_JZ_DECISION,
    build_dts1_s1jz_finite_orchestrator_api_contract,
)


class DTS1S1JZFiniteOrchestratorAPIContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jz_finite_orchestrator_api_contract()

    def test_binds_exact_s1jy_and_s1jx_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1jy_orchestrator_api_readiness_precheck().audit_digest, contract.source_s1jy_digest)
        self.assertEqual(build_dts1_s1jx_sequence_carry_orchestration_contract().contract_digest, contract.source_s1jx_digest)

    def test_runner_input_is_replica_id_only(self) -> None:
        schema = dict(self._contract().runner_input_schema)
        self.assertEqual(("schema_id", "replica_id"), schema["fields"])
        for role in ("field", "private_state", "candidate_data", "threshold", "retry"):
            self.assertIn(role, schema["excluded"])

    def test_binds_twelve_complete_fresh_state_records(self) -> None:
        contract = self._contract()
        self.assertEqual(12, contract.fresh_state_record_count)
        self.assertEqual(12, len({(row[0], row[1]) for row in contract.fresh_state_records}))
        self.assertTrue(all(len(row[6]) == 64 and len(row[8]) == 64 for row in contract.fresh_state_records))

    def test_all_fresh_fields_are_zero_and_unadvanced(self) -> None:
        for row in self._contract().fresh_state_records:
            field = dict(row[5])
            self.assertIsNone(field["last_distribution"])
            self.assertIsNone(field["development"])
            for neuron in field["neurons"]:
                values = dict(neuron)
                self.assertEqual((0.0, 0.0, 0, 0.0, ()), (values["activation"], values["afterimage"], values["perception_tick"], values["receptor_contact"], values["local_samples"]))

    def test_b1_uses_internal_digest_and_geometry_bound_rates(self) -> None:
        rows = [row for row in self._contract().fresh_state_records if row[0] == "B1"]
        for row in rows:
            payload = dict(dict(row[7])["fixed_adapter_payload"])
            self.assertEqual(row[4], payload["edge_inventory_digest"])
            expected = 1.2 if len(row[2]) == 2 else 1.1
            self.assertTrue(all(dict(rate)["rate_per_second"] == expected for rate in payload["edge_rates"]))

    def test_b2_is_complete_uniform_zero_L(self) -> None:
        rows = [row for row in self._contract().fresh_state_records if row[0] == "B2"]
        for row in rows:
            entries = dict(dict(row[7])["complete_L_state_payload"])["entries"]
            self.assertEqual(row[2], tuple(node for node, _value in entries))
            self.assertTrue(all(value == 0.0 for _node, value in entries))

    def test_b3_through_b6_have_uniform_M_and_private_digest(self) -> None:
        for row in self._contract().fresh_state_records:
            if row[0] not in ("B3", "B4", "B5", "B6"):
                continue
            substrate = dict(dict(row[5])["substrate"])
            masses = substrate["masses"]
            self.assertTrue(all(value == 1.0 / len(row[2]) for _node, value in masses))
            self.assertEqual(substrate["edge_inventory_digest"], row[4])
            self.assertEqual(64, len(dict(row[7])["embedded_M_state_digest"]))

    def test_checkpoint_schema_is_complete_and_read_only(self) -> None:
        schema = dict(self._contract().checkpoint_schema)
        for field in ("sequence_key", "ordinal", "activation", "afterimage", "complete_field_digest", "private_state_digest", "adapter_output_digest"):
            self.assertIn(field, schema["fields"])
        self.assertIn("registered-true-checkpoint", schema["capture"])

    def test_component_indices_are_exact_eight_eight_six_six(self) -> None:
        records = self._contract().component_index_records
        counts = {}
        for row in records:
            counts[row[0]] = counts.get(row[0], 0) + 1
            self.assertEqual("left-minus-right", row[8])
        self.assertEqual((8, 8, 6, 6), tuple(counts.values()))
        self.assertEqual(28, self._contract().component_index_count)

    def test_component_order_is_checkpoint_channel_node(self) -> None:
        rows = self._contract().component_index_records[:8]
        self.assertEqual((0, 1, 2, 3, 4, 5, 6, 7), tuple(row[1] for row in rows))
        self.assertEqual(("activation", "activation", "afterimage", "afterimage") * 2, tuple(row[6] for row in rows))
        self.assertEqual(("node-a", "node-b") * 4, tuple(row[7] for row in rows))

    def test_output_digest_and_error_boundary_are_atomic(self) -> None:
        output = dict(self._contract().replica_output_schema)
        error = dict(self._contract().error_boundary)
        self.assertIn("output_digest", output["fields"])
        self.assertEqual("DTS1OneReplicaOrchestratorError", error["public_error"])
        self.assertFalse(error["partial_output"])
        self.assertFalse(error["retry"])

    def test_selects_one_exact_eight_call_exemplar(self) -> None:
        exemplar = dict(self._contract().technical_exemplar)
        self.assertEqual("B1:P_IE_CAUSAL_TWO_SUBSTEP:r2", exemplar["replica_id"])
        self.assertEqual((4, 2, 8), (exemplar["interval_calls_per_repeat"], exemplar["deterministic_repeat_count"], exemplar["maximum_total_interval_calls"]))

    def test_executes_nothing_and_authorizes_only_one_replica_implementation(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.finite_orchestrator_api_bound)
        self.assertFalse(contract.initializer_implemented)
        self.assertFalse(contract.orchestrator_implemented)
        self.assertEqual((0, 0, 0), (contract.technical_replicas_executed, contract.profile_cases_executed, contract.baseline_interval_calls_executed))
        self.assertTrue(contract.one_replica_implementation_authorized_next_stage)
        self.assertEqual(S1_JZ_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JZFiniteOrchestratorAPIContractError):
            replace(contract, orchestrator_implemented=True)
        source = inspect.getsource(build_dts1_s1jz_finite_orchestrator_api_contract)
        for forbidden in ("materialize_", "advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
