from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.four_node_fresh_factory import build_four_node_role_fresh_bundle
from mcm_field_organism.four_node_fresh_manifest import load_four_node_fresh_manifest
from mcm_field_organism.four_node_model_input_assembly import assemble_four_node_model_input
from mcm_field_organism.four_node_model_invocation import (
    COMPLETED,
    NOT_COMPUTABLE,
    FourNodeModelCarry,
    invoke_four_node_model,
)
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_distributor import ReceptorDistributor, ReceptorDock
from mcm_field_organism.transient_neuron_input import (
    TransientLocalReceptorContact,
    TransientNeuronDockInput,
    TransientNeuronInputSet,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = load_four_node_fresh_manifest(ROOT / "reports" / "s1rk_four_node_fresh_manifest.json")
MODULE = "mcm_field_organism.four_node_model_invocation"
ROLES = (
    "A0_CURRENT_CONTACT", "A1_FAST_SH", "A2_B1_FIXED_ADAPTER",
    "A2_B2_INTEGRATOR", "A2_B3_LOCAL_LEAKY", "A2_B4_LINEAR_COUPLED",
    "A2_B5_F3_FULL", "A2_B6_CONST_V", "A3_NORM", "M1_PARALLEL_LEAK",
    "M2_DELAY", "M2_REPLAY", "M4_DTS1_T1", "M5_DIRECT",
)
F3 = frozenset(ROLES[4:8])


def _assembly(role: str):
    return assemble_four_node_model_input(build_four_node_role_fresh_bundle(MANIFEST, role))


def _distribution(start: int, end: int, values=(0.8, -0.4, 0.2, 0.1)):
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock(
        "dock.s1rf.technical-control.4n", "technical-control", "mcm.s1rf.receptor.4n"
    ))
    frame = ReceptorContactFrame(
        modality_id="technical-control",
        geometry_id="mcm.s1rf.receptor.4n",
        snapshot_id=f"s1rx.contact.{start}.{end}",
        clock_id="s1rx.source",
        window_start_tick=start,
        window_end_tick=end,
        carrier_ids=("carrier-a", "carrier-b", "carrier-c", "carrier-d"),
        values=values,
    )
    return distributor.distribute((frame,), CommonFieldTime("s1rx.field", start, end))


def _sync(start=0, end=10):
    return _distribution(start, end), MCMFieldStepTime("s1rx.field", start, end, 10.0)


def _transient(assembly, start=0, end=10):
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock(
        "dock.s1rf.technical-control.4n", "technical-control", "mcm.s1rf.receptor.4n"
    ))
    distribution = distributor.distribute((), CommonFieldTime("s1rx.field", start, end))
    step = MCMFieldStepTime("s1rx.field", start, end, 10.0)
    pairs = {neuron: carrier for carrier, neuron in assembly.model_input_field.docks[0].dock_map.pairs}
    inputs = tuple(
        TransientNeuronDockInput(
            neuron.neuron_id,
            "dock.s1rf.technical-control.4n",
            pairs[neuron.neuron_id],
            step,
            (TransientLocalReceptorContact(
                snapshot_id=f"s1rx.transient.{neuron.neuron_id}",
                source_clock_id="s1rx.source",
                source_window_start_tick=start,
                source_window_end_tick=end,
                organism_read_time=CommonFieldTime("s1rx.field", start, end),
                value=0.25,
            ),),
        )
        for neuron in assembly.model_input_field.layer.neurons
    )
    return distribution, TransientNeuronInputSet(step, inputs)


class FourNodeModelInvocationTests(unittest.TestCase):
    def test_all_fourteen_roles_complete_one_synchronous_interval(self) -> None:
        distribution, interval = _sync()
        for role in ROLES:
            with self.subTest(role=role):
                result = invoke_four_node_model(
                    _assembly(role), distribution, interval,
                    refinement=2 if role in F3 else None,
                )
                self.assertEqual(COMPLETED, result.status, result.failure_codes)
                self.assertEqual(1, result.field_time_advance_count)
                self.assertIsInstance(result.next_carry_or_none, FourNodeModelCarry)

    def test_supported_roles_complete_one_transient_interval(self) -> None:
        for role in tuple(item for item in ROLES if item not in {"A2_B1_FIXED_ADAPTER", "A2_B2_INTEGRATOR", "M4_DTS1_T1"}):
            with self.subTest(role=role):
                assembly = _assembly(role)
                distribution, interval = _transient(assembly)
                result = invoke_four_node_model(
                    assembly, distribution, interval,
                    refinement=2 if role in F3 else None,
                )
                self.assertEqual(COMPLETED, result.status, result.failure_codes)

    def test_sync_only_roles_reject_transient_without_kernel_call(self) -> None:
        for role in ("A2_B1_FIXED_ADAPTER", "A2_B2_INTEGRATOR", "M4_DTS1_T1"):
            with self.subTest(role=role):
                assembly = _assembly(role)
                distribution, interval = _transient(assembly)
                result = invoke_four_node_model(assembly, distribution, interval)
                self.assertEqual(NOT_COMPUTABLE, result.status)
                self.assertIn("TRANSIENT_NOT_CONNECTABLE", result.failure_codes[0])
                self.assertIsNone(result.output_field_or_none)
                self.assertIsNone(result.next_carry_or_none)

    def test_successful_carry_is_the_only_source_for_the_next_interval(self) -> None:
        first_distribution, first_interval = _sync(0, 10)
        first = invoke_four_node_model(_assembly("A1_FAST_SH"), first_distribution, first_interval)
        second_distribution, second_interval = _sync(10, 20)
        second = invoke_four_node_model(first.next_carry_or_none, second_distribution, second_interval)
        self.assertEqual(COMPLETED, second.status)
        self.assertEqual(first.output_field_digest_or_none, second.input_field_digest)
        self.assertEqual(2, second.output_field_or_none.layer.tick)

    def test_b3_carry_wrapper_references_exact_output_substrate(self) -> None:
        distribution, interval = _sync()
        result = invoke_four_node_model(
            _assembly("A2_B3_LOCAL_LEAKY"), distribution, interval, refinement=2
        )
        self.assertEqual(COMPLETED, result.status, result.failure_codes)
        self.assertIs(
            result.next_private_state_or_none.substrate,
            result.output_field_or_none.substrate,
        )

    def test_b1_state_is_unchanged_and_b2_l_state_is_complete(self) -> None:
        distribution, interval = _sync()
        for role in ("A2_B1_FIXED_ADAPTER", "A2_B2_INTEGRATOR"):
            with self.subTest(role=role):
                assembly = _assembly(role)
                result = invoke_four_node_model(assembly, distribution, interval)
                self.assertEqual(COMPLETED, result.status, result.failure_codes)
                if role == "A2_B1_FIXED_ADAPTER":
                    self.assertIs(result.next_private_state_or_none, assembly.native_private_state_or_none)
                else:
                    self.assertEqual(4, len(result.next_private_state_or_none.entries))

    def test_m4_returns_complete_anatomy_and_keeps_sidecar_absent(self) -> None:
        distribution, interval = _sync()
        result = invoke_four_node_model(_assembly("M4_DTS1_T1"), distribution, interval)
        self.assertEqual(COMPLETED, result.status, result.failure_codes)
        self.assertIsNone(result.next_private_state_or_none.candidate_sidecar_digest_or_none)
        self.assertEqual(4.0, result.next_private_state_or_none.anatomy.global_capacity)

    def test_refinement_is_required_only_for_f3_roles(self) -> None:
        distribution, interval = _sync()
        missing = invoke_four_node_model(_assembly("A2_B5_F3_FULL"), distribution, interval)
        foreign = invoke_four_node_model(_assembly("A1_FAST_SH"), distribution, interval, refinement=2)
        self.assertEqual(NOT_COMPUTABLE, missing.status)
        self.assertEqual(NOT_COMPUTABLE, foreign.status)

    def test_kernel_exception_publishes_no_partial_result(self) -> None:
        distribution, interval = _sync()
        with patch(f"{MODULE}.advance_neutral_shared_field", side_effect=RuntimeError("closed")):
            result = invoke_four_node_model(_assembly("A0_CURRENT_CONTACT"), distribution, interval)
        self.assertEqual(NOT_COMPUTABLE, result.status)
        self.assertIsNone(result.output_field_or_none)
        self.assertIsNone(result.next_private_state_or_none)
        self.assertEqual(0, result.field_time_advance_count)

    def test_result_and_carry_digests_are_deterministic(self) -> None:
        first_distribution, first_interval = _sync()
        second_distribution, second_interval = _sync()
        first = invoke_four_node_model(_assembly("A3_NORM"), first_distribution, first_interval)
        second = invoke_four_node_model(_assembly("A3_NORM"), second_distribution, second_interval)
        self.assertEqual(first.result_digest, second.result_digest)
        self.assertEqual(first.next_carry_or_none.carry_digest, second.next_carry_or_none.carry_digest)

    def test_production_module_does_not_import_historical_adapter_or_orchestrator(self) -> None:
        source = (ROOT / "mcm_field_organism" / "four_node_model_invocation.py").read_text(encoding="utf-8")
        self.assertNotIn("dynamic_substrate_dts1_private_baseline_adapters", source)
        self.assertNotIn("dynamic_substrate_dts1_one_replica_orchestrator", source)
        self.assertNotIn("dynamic_substrate_dts1_common_interval_materializer", source)


if __name__ == "__main__":
    unittest.main()
