from __future__ import annotations

from dataclasses import replace
import inspect
import math
from pathlib import Path
import unittest

from mcm_field_organism.dynamic_substrate_dts1_common_interval_materializer import (
    DTS1CommonIntervalMaterializationError,
    DTS1CommonIntervalPrivateState,
    S1_JO_DECISION,
    build_dts1_s1jo_implementation_receipt,
    canonical_dts1_common_interval_envelope_fixtures,
    materialize_dts1_common_interval,
)
from mcm_field_organism.dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    S1_JK_SEQUENCE_FIXTURES,
)
from mcm_field_organism.dynamic_substrate_s1jn_finite_materialization_schema_contract import (
    build_dts1_s1jn_finite_materialization_schema_contract,
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


class DTS1CommonIntervalMaterializerTests(unittest.TestCase):
    def _sequence_digest(self, key: str) -> str:
        return next(row[4] for row in S1_JK_SEQUENCE_FIXTURES if row[0] == key)

    def _fixture(self, key: str, ordinal: int):
        digest = self._sequence_digest(key)
        return next(
            row
            for row in canonical_dts1_common_interval_envelope_fixtures()
            if row.sequence_digest == digest and row.ordinal == ordinal
        )

    def _field(
        self,
        width: int,
        *,
        tick: int = 0,
        activation: tuple[float, ...] | None = None,
        afterimage: tuple[float, ...] | None = None,
        last_distribution=None,
        with_substrate: bool = False,
    ) -> SharedMCMField:
        suffix = f"{width}n"
        node_ids = tuple(f"node-{chr(ord('a') + index)}" for index in range(width))
        activation = activation or (0.0,) * width
        afterimage = afterimage or (0.0,) * width
        neurons = tuple(
            MCMNeuron(
                neuron_id=node_id,
                field_id=f"mcm.s1jn.field.{suffix}",
                modality_id="auditory",
                geometry_id=f"mcm.s1jn.geometry.{suffix}",
                position=(index,),
                activation=activation[index],
                afterimage=afterimage[index],
                perception=MCMFieldPerception(
                    tick=tick,
                    receptor_contact=0.0,
                    local_samples=(),
                ),
            )
            for index, node_id in enumerate(node_ids)
        )
        layer = MCMNeuronLayer(
            layer_id=f"mcm.s1jn.layer.{suffix}",
            neurons=neurons,
            sample_offsets=((-1,), (1,)),
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
        field = SharedMCMField(layer, (dock,), last_distribution)
        if not with_substrate:
            return field
        substrate = MCMSubstrateState(
            MCMSubstrateArmContract("s1jo.test.arm", 0.1, 0.0, 0.0),
            tuple(MCMSubstrateMass(node_id, 1.0 / width) for node_id in node_ids),
            mcm_substrate_edge_inventory_digest(layer),
        )
        return replace(field, substrate=substrate)

    def _dts_state(self, sidecar=None, anatomy_value: float = 1.0):
        return DTS1CommonIntervalPrivateState(
            "DTS1",
            (
                ("complete_resource_anatomy_payload", {"resource": anatomy_value}),
                ("candidate_sidecar_digest_or_null", sidecar),
            ),
        )

    def _carried_field(self, key: str, width: int, activation, afterimage):
        first = materialize_dts1_common_interval(
            self._fixture(key, 1),
            "DTS1",
            self._field(width),
            self._dts_state(),
            None,
            None,
        )
        field = first.model_invocation.materialized_field
        neurons = tuple(
            replace(
                neuron,
                activation=activation[index],
                afterimage=afterimage[index],
                perception=MCMFieldPerception(1, 0.0, ()),
            )
            for index, neuron in enumerate(field.layer.neurons)
        )
        return replace(
            field,
            layer=replace(field.layer, neurons=neurons),
            last_distribution=first.model_invocation.receptor_distribution,
        )

    def test_binds_exact_s1jn_source_and_twenty_three_fixtures(self) -> None:
        receipt = build_dts1_s1jo_implementation_receipt()
        self.assertEqual(
            build_dts1_s1jn_finite_materialization_schema_contract().contract_digest,
            receipt.source_s1jn_digest,
        )
        self.assertEqual(23, len(canonical_dts1_common_interval_envelope_fixtures()))
        self.assertEqual(tuple(f"T{index:02d}" for index in range(1, 21)), receipt.matrix_case_ids)

    def test_materializes_pie_initial_sh_distribution_and_time(self) -> None:
        fixture = self._fixture("P_IE_F_HIGH", 1)
        result = materialize_dts1_common_interval(
            fixture, "DTS1", self._field(2), self._dts_state(), None, None
        )
        field = result.model_invocation.materialized_field
        self.assertEqual((-1.0, 1.0), tuple(row.activation for row in field.layer.neurons))
        self.assertEqual((-0.2, 0.2), tuple(row.afterimage for row in field.layer.neurons))
        self.assertEqual((0.0, 0.0), result.model_invocation.receptor_distribution.contacts[0].frame.values)
        self.assertEqual((0, 1, 2.0), (result.model_invocation.step_time.start_tick, result.model_invocation.step_time.end_tick, result.model_invocation.step_time.ticks_per_second))
        self.assertIsNone(field.last_distribution)

    def test_pie_carry_preserves_complete_field_by_identity(self) -> None:
        fixture = self._fixture("P_IE_F_HIGH", 2)
        field = self._carried_field("P_IE_F_HIGH", 2, (-0.3, 0.4), (0.1, -0.1))
        result = materialize_dts1_common_interval(
            fixture,
            "DTS1",
            field,
            self._dts_state(),
            self._fixture("P_IE_F_HIGH", 1).interval_digest,
            "a" * 64,
        )
        self.assertIs(field, result.model_invocation.materialized_field)
        self.assertEqual((1, 2), (result.model_invocation.step_time.start_tick, result.model_invocation.step_time.end_tick))

    def test_two_node_boundary_replaces_only_sh(self) -> None:
        field = self._field(2)
        result = materialize_dts1_common_interval(
            self._fixture("P_IH_A_A_A", 1),
            "DTS1",
            field,
            self._dts_state(),
            None,
            None,
        )
        output = result.model_invocation.materialized_field
        self.assertEqual((-0.5, 0.5), tuple(row.activation for row in output.layer.neurons))
        self.assertEqual((0.0, 0.0), tuple(row.afterimage for row in output.layer.neurons))
        self.assertEqual(field.docks, output.docks)

    def test_three_node_boundary_replaces_only_sh(self) -> None:
        result = materialize_dts1_common_interval(
            self._fixture("P_IK_A_B_A", 1),
            "DTS1",
            self._field(3),
            self._dts_state(),
            None,
            None,
        )
        self.assertEqual((-0.5, 0.5, 0.5), tuple(row.activation for row in result.model_invocation.materialized_field.layer.neurons))

    def test_common_exposure_is_arm_equal_while_private_digest_differs(self) -> None:
        left = materialize_dts1_common_interval(
            self._fixture("P_IE_F_HIGH", 1), "DTS1", self._field(2), self._dts_state("1" * 64, 0.2), None, None
        )
        right = materialize_dts1_common_interval(
            self._fixture("P_IE_R_HIGH", 1), "DTS1", self._field(2), self._dts_state("2" * 64, 0.8), None, None
        )
        self.assertEqual(left.integrity_record.common_exposure_digest, right.integrity_record.common_exposure_digest)
        self.assertNotEqual(left.integrity_record.private_prestate_digest, right.integrity_record.private_prestate_digest)
        self.assertNotEqual(left.integrity_record.orchestration_control_digest, right.integrity_record.orchestration_control_digest)

    def test_pik_registered_b_and_gap_exposures_differ(self) -> None:
        rows = []
        for key in ("P_IK_A_B_A", "P_IK_A_GAP_A"):
            field = self._carried_field(key, 3, (-0.1, 0.2, 0.3), (0.0, 0.0, 0.0))
            rows.append(
                materialize_dts1_common_interval(
                    self._fixture(key, 2), "DTS1", field, self._dts_state(), self._fixture(key, 1).interval_digest, "b" * 64
                )
            )
        self.assertNotEqual(rows[0].integrity_record.common_exposure_digest, rows[1].integrity_record.common_exposure_digest)

    def test_accepts_role_owned_embedded_m_and_rejects_m_for_dts1(self) -> None:
        field = self._field(2, with_substrate=True)
        state = DTS1CommonIntervalPrivateState(
            "B3",
            (("embedded_M_state_digest", field.substrate.digest()), ("B3_configuration_digest", "c" * 64)),
        )
        result = materialize_dts1_common_interval(
            self._fixture("P_IH_A_A_A", 1), "B3", field, state, None, None
        )
        self.assertIs(result.model_invocation.materialized_field.substrate, field.substrate)
        with self.assertRaises(DTS1CommonIntervalMaterializationError):
            materialize_dts1_common_interval(
                self._fixture("P_IH_A_A_A", 1), "DTS1", field, self._dts_state(), None, None
            )

    def test_rejects_wrong_identity_private_schema_and_provenance(self) -> None:
        fixture = self._fixture("P_IE_F_HIGH", 1)
        wrong = replace(self._field(2).layer, layer_id="wrong.layer")
        with self.assertRaises(DTS1CommonIntervalMaterializationError):
            materialize_dts1_common_interval(fixture, "DTS1", replace(self._field(2), layer=wrong), self._dts_state(), None, None)
        with self.assertRaises(DTS1CommonIntervalMaterializationError):
            DTS1CommonIntervalPrivateState("DTS1", (("wrong", 1),))
        with self.assertRaises(DTS1CommonIntervalMaterializationError):
            materialize_dts1_common_interval(fixture, "DTS1", self._field(2), self._dts_state(), "d" * 64, None)

    def test_rejects_nonfinite_private_payload(self) -> None:
        with self.assertRaises(DTS1CommonIntervalMaterializationError):
            self._dts_state(anatomy_value=math.inf)

    def test_negative_zero_is_canonicalized(self) -> None:
        fixture = self._fixture("P_IE_F_HIGH", 1)
        negative = materialize_dts1_common_interval(fixture, "DTS1", self._field(2), self._dts_state(anatomy_value=-0.0), None, None)
        positive = materialize_dts1_common_interval(fixture, "DTS1", self._field(2), self._dts_state(anatomy_value=0.0), None, None)
        self.assertEqual(negative.integrity_record.private_prestate_digest, positive.integrity_record.private_prestate_digest)

    def test_is_deterministic_and_does_not_change_input(self) -> None:
        fixture = self._fixture("P_IE_F_HIGH", 1)
        field = self._field(2)
        first = materialize_dts1_common_interval(fixture, "DTS1", field, self._dts_state(), None, None)
        second = materialize_dts1_common_interval(fixture, "DTS1", field, self._dts_state(), None, None)
        self.assertEqual(first.integrity_record, second.integrity_record)
        self.assertEqual((0.0, 0.0), tuple(row.activation for row in field.layer.neurons))

    def test_model_invocation_contains_only_four_fields(self) -> None:
        result = materialize_dts1_common_interval(
            self._fixture("P_IH_A_A_A", 1), "DTS1", self._field(2), self._dts_state(), None, None
        )
        self.assertEqual(("materialized_field", "receptor_distribution", "step_time", "geometry_digest"), tuple(item.name for item in result.model_invocation.__dataclass_fields__.values()))

    def test_receipt_and_module_are_model_runtime_and_export_free(self) -> None:
        receipt = build_dts1_s1jo_implementation_receipt()
        self.assertTrue(receipt.pure_materializer_implemented)
        self.assertEqual((False, False, False, False), (receipt.model_kernel_import_present, receipt.adapter_import_present, receipt.runtime_integration_present, receipt.baseline_models_executed))
        self.assertEqual((0, 0), (receipt.technical_field_steps_executed, receipt.research_field_steps_executed))
        self.assertEqual(S1_JO_DECISION, receipt.decision)
        source = inspect.getsource(materialize_dts1_common_interval)
        for forbidden in ("advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)
        api_source = (Path(__file__).parents[1] / "mcm_field_organism" / "current_api.py").read_text(encoding="utf-8")
        self.assertNotIn("materialize_dts1_common_interval", api_source)


if __name__ == "__main__":
    unittest.main()
