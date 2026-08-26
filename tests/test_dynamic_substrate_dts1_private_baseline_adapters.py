from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.dynamic_substrate_dts1_common_interval_materializer import (
    DTS1CommonIntervalPrivateState,
    canonical_dts1_common_interval_envelope_fixtures,
    materialize_dts1_common_interval,
)
from mcm_field_organism.dynamic_substrate_dts1_private_baseline_adapters import (
    DTS1PrivateBaselineAdapterContext,
    DTS1PrivateBaselineAdapterError,
    S1_JW_CONFIGURATION_DIGESTS,
    S1_JW_DECISION,
    advance_dts1_private_baseline,
    build_dts1_s1jw_implementation_receipt,
)
from mcm_field_organism.dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    S1_JK_SEQUENCE_FIXTURES,
)
from mcm_field_organism.dynamic_substrate_s1jt_finite_adapter_payload_contract import (
    S1_JT_B6_SPEC_DIGEST,
    build_dts1_s1jt_finite_adapter_payload_contract,
)
from mcm_field_organism.dynamic_substrate_s1jv_finite_geometry_digest_mapping_contract import (
    S1_JV_GEOMETRY_DIGEST_MAPPINGS,
    build_dts1_s1jv_finite_geometry_digest_mapping_contract,
)
from mcm_field_organism.mcm_neuron import MCMFieldPerception, MCMNeuron
from mcm_field_organism.mcm_neuron_layer import MCMNeuronLayer
from mcm_field_organism.mcm_substrate_state import (
    MCMSubstrateArmContract,
    MCMSubstrateMass,
    MCMSubstrateState,
    mcm_substrate_edge_inventory_digest,
)
from mcm_field_organism.receptor_contract import ReceptorNeuronDockMap
from mcm_field_organism.shared_mcm_field import SharedFieldDock, SharedMCMField


class DTS1PrivateBaselineAdapterTests(unittest.TestCase):
    def _fixture(self, width: int):
        key = "P_IH_A_A_A" if width == 2 else "P_IK_A_B_A"
        sequence = next(row[4] for row in S1_JK_SEQUENCE_FIXTURES if row[0] == key)
        return next(
            item
            for item in canonical_dts1_common_interval_envelope_fixtures()
            if item.sequence_digest == sequence and item.ordinal == 1
        )

    def _field(self, width: int, role: str) -> SharedMCMField:
        suffix = f"{width}n"
        node_ids = tuple(f"node-{chr(ord('a') + index)}" for index in range(width))
        neurons = tuple(
            MCMNeuron(
                node_id,
                f"mcm.s1jn.field.{suffix}",
                "auditory",
                f"mcm.s1jn.geometry.{suffix}",
                (index,),
                0.0,
                0.0,
                MCMFieldPerception(0, 0.0, ()),
            )
            for index, node_id in enumerate(node_ids)
        )
        layer = MCMNeuronLayer(
            f"mcm.s1jn.layer.{suffix}",
            neurons,
            ((-1,), (1,)),
            receptor_dock_ids=node_ids,
        )
        dock = SharedFieldDock(
            f"dock.s1jn.auditory.{suffix}",
            ReceptorNeuronDockMap(
                "auditory",
                f"mcm.s1jn.receptor.{suffix}",
                tuple(
                    (f"carrier-{chr(ord('a') + index)}", node_id)
                    for index, node_id in enumerate(node_ids)
                ),
            ),
        )
        field = SharedMCMField(layer, (dock,))
        if role not in ("B3", "B4", "B5", "B6"):
            return field
        records = {
            "B3": ("mcm.s1jt.b3.local-leaky", 1.0),
            "B4": ("mcm.s1jt.b4.linear-coupled", 1.0),
            "B5": ("mcm.s1jt.b5.full", 1.0),
            "B6": ("mcm.s1jt.b6.const-v", 0.5),
        }
        arm_id, rate = records[role]
        substrate = MCMSubstrateState(
            MCMSubstrateArmContract(arm_id, rate, 0.5, 1.0, 1.0),
            tuple(MCMSubstrateMass(node_id, 1.0 / width) for node_id in node_ids),
            mcm_substrate_edge_inventory_digest(layer),
        )
        return replace(field, substrate=substrate)

    def _private_state(self, width: int, role: str, field: SharedMCMField):
        digest = S1_JW_CONFIGURATION_DIGESTS[role]
        internal = next(row[7] for row in S1_JV_GEOMETRY_DIGEST_MAPPINGS if len(row[5]) == width)
        if role == "B1":
            rates = (
                ({"first_node_id": "node-a", "second_node_id": "node-b", "rate_per_second": 1.2},)
                if width == 2
                else (
                    {"first_node_id": "node-a", "second_node_id": "node-b", "rate_per_second": 1.1},
                    {"first_node_id": "node-b", "second_node_id": "node-c", "rate_per_second": 1.1},
                )
            )
            payload = {
                "schema_id": "mcm.s1jt.b1-fixed-adapter.v1",
                "backreaction_enabled": True,
                "base_rate_per_second": 1.0,
                "edge_inventory_digest": internal,
                "edge_rates": rates,
            }
            rows = (("fixed_adapter_payload", payload), ("fixed_adapter_configuration_digest", digest))
        elif role == "B2":
            payload = {
                "schema_id": "mcm.s1jt.b2-private-L.v1",
                "entries": tuple(
                    {"node_id": f"node-{chr(ord('a') + index)}", "value": 0.0}
                    for index in range(width)
                ),
            }
            rows = (("complete_L_state_payload", payload), ("B2_configuration_digest", digest))
        else:
            rows = [("embedded_M_state_digest", field.substrate.digest())]
            if role == "B6":
                rows.append(("frozen_CONST_V_spec_digest", S1_JT_B6_SPEC_DIGEST))
            rows.append((f"{role}_configuration_digest", digest))
        return DTS1CommonIntervalPrivateState(role, tuple(rows))

    def _case(self, role: str, width: int = 2, refinement: int = 4):
        field = self._field(width, role)
        state = self._private_state(width, role, field)
        materialized = materialize_dts1_common_interval(
            self._fixture(width), role, field, state, None, None
        )
        context = DTS1PrivateBaselineAdapterContext(
            role, state, S1_JW_CONFIGURATION_DIGESTS[role], refinement
        )
        return materialized.model_invocation, context

    def test_receipt_binds_exact_sources_and_six_roles(self) -> None:
        receipt = build_dts1_s1jw_implementation_receipt()
        self.assertEqual(build_dts1_s1jt_finite_adapter_payload_contract().contract_digest, receipt.source_s1jt_digest)
        self.assertEqual(build_dts1_s1jv_finite_geometry_digest_mapping_contract().contract_digest, receipt.source_s1jv_digest)
        self.assertEqual(("B1", "B2", "B3", "B4", "B5", "B6"), receipt.adapter_roles)

    def test_b1_two_and_three_node_payloads_reach_exact_kernel(self) -> None:
        for width in (2, 3):
            output = advance_dts1_private_baseline(*self._case("B1", width))
            self.assertEqual(width, len(output.complete_field.layer.neurons))
            self.assertEqual("exact-spectral", dict(output.diagnostics)["method_id"])
            self.assertEqual("B1", output.next_private_state.model_role)

    def test_b1_control_labels_are_bit_identical_repeats(self) -> None:
        outputs = tuple(
            advance_dts1_private_baseline(*self._case("B1", refinement=level))
            for level in (2, 4, 8)
        )
        self.assertEqual(1, len({item.output_digest for item in outputs}))

    def test_b2_returns_complete_L_and_exact_diagnostics(self) -> None:
        output = advance_dts1_private_baseline(*self._case("B2"))
        state = dict(output.next_private_state.payload)["complete_L_state_payload"]
        self.assertEqual(("node-a", "node-b"), tuple(item["node_id"] for item in state["entries"]))
        self.assertEqual("exact-matrix-exponential", dict(output.diagnostics)["method_id"])
        self.assertEqual(0.0, dict(output.diagnostics)["partition_error"])

    def test_b2_control_labels_are_bit_identical_repeats(self) -> None:
        outputs = tuple(
            advance_dts1_private_baseline(*self._case("B2", refinement=level))
            for level in (2, 4, 8)
        )
        self.assertEqual(1, len({item.output_digest for item in outputs}))

    def test_b3_through_b6_use_native_refinement_and_return_M(self) -> None:
        for role in ("B3", "B4", "B5", "B6"):
            output = advance_dts1_private_baseline(*self._case(role, refinement=2))
            diagnostics = dict(output.diagnostics)
            self.assertEqual("ssprk33", diagnostics["method_id"])
            self.assertEqual(2, diagnostics["refinement"])
            self.assertEqual(output.complete_field.substrate.digest(), dict(output.next_private_state.payload)["embedded_M_state_digest"])

    def test_native_levels_are_independent_and_reported(self) -> None:
        results = tuple(
            advance_dts1_private_baseline(*self._case("B5", refinement=level))
            for level in (2, 4, 8)
        )
        self.assertEqual((2, 4, 8), tuple(dict(item.diagnostics)["refinement"] for item in results))
        self.assertEqual(3, len({item.output_digest for item in results}))

    def test_b6_preserves_frozen_spec_digest(self) -> None:
        output = advance_dts1_private_baseline(*self._case("B6"))
        self.assertEqual(S1_JT_B6_SPEC_DIGEST, dict(output.next_private_state.payload)["frozen_CONST_V_spec_digest"])

    def test_rejects_outer_internal_role_swap_before_kernel(self) -> None:
        invocation, context = self._case("B1")
        with self.assertRaises(DTS1PrivateBaselineAdapterError):
            advance_dts1_private_baseline(
                replace(invocation, geometry_digest=S1_JV_GEOMETRY_DIGEST_MAPPINGS[0][7]),
                context,
            )

    def test_rejects_wrong_configuration_and_refinement(self) -> None:
        _invocation, context = self._case("B1")
        with self.assertRaises(DTS1PrivateBaselineAdapterError):
            replace(context, configuration_digest="0" * 64)
        with self.assertRaises(DTS1PrivateBaselineAdapterError):
            replace(context, refinement=3)

    def test_rejects_B1_payload_rate_or_internal_digest_drift(self) -> None:
        invocation, context = self._case("B1")
        payload = dict(dict(context.private_state.payload)["fixed_adapter_payload"])
        payload["edge_inventory_digest"] = invocation.geometry_digest
        state = replace(context.private_state, payload=(("fixed_adapter_payload", payload), context.private_state.payload[1]))
        with self.assertRaises(DTS1PrivateBaselineAdapterError):
            advance_dts1_private_baseline(invocation, replace(context, private_state=state))

    def test_rejects_B2_incomplete_or_reordered_L(self) -> None:
        invocation, context = self._case("B2")
        payload = dict(dict(context.private_state.payload)["complete_L_state_payload"])
        payload["entries"] = tuple(reversed(payload["entries"]))
        state = replace(context.private_state, payload=(("complete_L_state_payload", payload), context.private_state.payload[1]))
        with self.assertRaises(DTS1PrivateBaselineAdapterError):
            advance_dts1_private_baseline(invocation, replace(context, private_state=state))

    def test_rejects_embedded_M_or_B6_spec_drift(self) -> None:
        invocation, context = self._case("B6")
        rows = list(context.private_state.payload)
        rows[1] = (rows[1][0], "0" * 64)
        state = replace(context.private_state, payload=tuple(rows))
        with self.assertRaises(DTS1PrivateBaselineAdapterError):
            advance_dts1_private_baseline(invocation, replace(context, private_state=state))

    def test_output_is_canonical_and_excludes_control_data(self) -> None:
        output = advance_dts1_private_baseline(*self._case("B3"))
        payload = output.canonical_payload()
        self.assertEqual({"schema_id", "model_role", "complete_field", "next_private_state", "diagnostics"}, set(payload))
        encoded = repr(payload)
        for forbidden in ("control_label", "sequence_digest", "checkpoint", "candidate_sidecar"):
            self.assertNotIn(forbidden, encoded)

    def test_result_is_deterministic_and_input_is_unchanged(self) -> None:
        invocation, context = self._case("B4")
        first = advance_dts1_private_baseline(invocation, context)
        second = advance_dts1_private_baseline(invocation, context)
        self.assertEqual(first, second)
        self.assertIsNone(invocation.materialized_field.last_distribution)

    def test_receipt_closes_profile_runtime_and_research_execution(self) -> None:
        receipt = build_dts1_s1jw_implementation_receipt()
        self.assertTrue(receipt.six_adapter_bridges_implemented)
        self.assertTrue(receipt.dual_geometry_digest_validation_implemented)
        self.assertEqual(0, receipt.profile_cases_executed)
        self.assertFalse(receipt.runtime_integration_present)
        self.assertFalse(receipt.research_execution_permitted)
        self.assertEqual(S1_JW_DECISION, receipt.decision)

    def test_module_is_private_and_receipt_is_kernel_call_free(self) -> None:
        api = (Path(__file__).parents[1] / "mcm_field_organism" / "current_api.py").read_text(encoding="utf-8")
        self.assertNotIn("advance_dts1_private_baseline", api)
        source = inspect.getsource(build_dts1_s1jw_implementation_receipt)
        for forbidden in ("advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
