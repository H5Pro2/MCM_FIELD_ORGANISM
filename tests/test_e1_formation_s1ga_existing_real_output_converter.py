from __future__ import annotations

import copy
from dataclasses import replace
import inspect
import unittest

import tests.test_e1_common_probe_n2_r2_object_handoff as handoff_fixture

from mcm_field_organism.e1_common_probe_real_wrappers import (
    E1CommonProbeFreshField,
    E1CommonProbeRealProbeOutput,
)
from mcm_field_organism.e1_formation_s1fx_common_probe_receipt_contract import S1_FX_RECEIPT_SCHEMA
from mcm_field_organism.e1_formation_s1ga_existing_real_output_converter import (
    E1FormationS1GAExistingRealOutputConverterError,
    convert_e1_formation_s1ga_existing_real_output,
)
from mcm_field_organism.e1_refined_chain_canonical_producer import _initial_field_digest
from mcm_field_organism.e1_refined_formation_runner import _digest


class E1FormationS1GAExistingRealOutputConverterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = handoff_fixture.E1CommonProbeN2R2ObjectHandoffTests
        source.setUpClass()
        cls.handoff = source(methodName="test_carries_all_real_objects_without_field_steps")._prepare()

    def _objects(self, role_id: str, index: int = 0):
        resolved = next(item for item in self.handoff.resolved_slots if item.binding.role_id == role_id)
        field = copy.deepcopy(self.handoff.initial_field)
        fresh = E1CommonProbeFreshField(resolved.binding.binding_digest, _initial_field_digest(field), field)
        state_digest = None if resolved.binding.state_role is None else self.handoff.initial_state_digest
        neuron_count = len(field.layer.neurons)
        scale = float(index + 1)
        values = {
            "binding_digest": resolved.binding.binding_digest,
            "terminal_field_digest": _digest(("s1ga-synthetic-output", role_id, index)),
            "activation": tuple(scale * (offset + 1) / 1000.0 for offset in range(neuron_count)),
            "afterimage": tuple(scale * (offset + 1) / 10000.0 for offset in range(neuron_count)),
            "field_step_count": len(resolved.probe_plan.proposal_steps),
            "source_support_count": resolved.probe_plan.handoff.source_event_count,
            "frozen_state_digest_before": state_digest,
            "frozen_state_digest_after": state_digest,
            "frozen_state_preserved": True,
            "persistence_performed": False,
            "research_decision_permitted": False,
            "memory_claim_permitted": False,
        }
        output = E1CommonProbeRealProbeOutput(
            **values,
            result_digest=_digest(values),
        )
        return resolved, fresh, output

    def test_p0_converts_losslessly_into_common_schema(self) -> None:
        resolved, fresh, output = self._objects("p0-reset-ab")
        receipt = convert_e1_formation_s1ga_existing_real_output(resolved, fresh, output, field_execution_kind="synthetic-typed-real-output")
        self.assertEqual(S1_FX_RECEIPT_SCHEMA, tuple(receipt.__dataclass_fields__))
        self.assertEqual(output.activation, receipt.activation_vector)
        self.assertEqual(output.afterimage, receipt.afterimage_vector)
        self.assertIsNone(receipt.source_state_digest)
        self.assertEqual("neutral-p0", receipt.probe_mode)

    def test_frozen_e1_converts_with_unchanged_state_evidence(self) -> None:
        resolved, fresh, output = self._objects("e1-active-ab", 1)
        receipt = convert_e1_formation_s1ga_existing_real_output(resolved, fresh, output, field_execution_kind="synthetic-typed-real-output")
        self.assertEqual(receipt.source_state_digest, receipt.state_digest_before)
        self.assertEqual(receipt.source_state_digest, receipt.state_digest_after)
        self.assertIsNone(receipt.fixed_adapter_digest)
        self.assertEqual("frozen-e1-feedback-enabled", receipt.probe_mode)

    def test_binding_mismatch_fails_closed(self) -> None:
        resolved, fresh, output = self._objects("p0-reset-ab")
        other = next(item for item in self.handoff.resolved_slots if item.binding.role_id == "p0-reset-ba")
        wrong_fresh = E1CommonProbeFreshField(other.binding.binding_digest, fresh.initial_field_digest, fresh.field)
        with self.assertRaises(E1FormationS1GAExistingRealOutputConverterError):
            convert_e1_formation_s1ga_existing_real_output(resolved, wrong_fresh, output, field_execution_kind="synthetic-typed-real-output")

    def test_execution_origin_must_be_explicit_and_tamper_is_detected(self) -> None:
        resolved, fresh, output = self._objects("e1-probe-feedback-ablated-ba", 2)
        receipt = convert_e1_formation_s1ga_existing_real_output(resolved, fresh, output, field_execution_kind="synthetic-typed-real-output")
        self.assertEqual("frozen-e1-feedback-disabled", receipt.probe_mode)
        with self.assertRaises(E1FormationS1GAExistingRealOutputConverterError):
            replace(receipt, field_execution_kind="real-in-memory-common-probe")
        with self.assertRaises(E1FormationS1GAExistingRealOutputConverterError):
            convert_e1_formation_s1ga_existing_real_output(resolved, fresh, output, field_execution_kind="unknown")

    def test_converter_calls_no_probe_kernel_or_writer(self) -> None:
        source = inspect.getsource(convert_e1_formation_s1ga_existing_real_output)
        for forbidden in ("advance_fixed_e1_adapter_fast_shared_field_transient(", "advance_frozen_e1_fast_shared_field_transient(", "advance_neutral_fast_shared_field_transient(", "run_e1_common_probe_real_probe_wrapper(", "open(", "write_text(", "write_bytes("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
