from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gd_fixed_adapter_invocation_binding as binding_fixture

from mcm_field_organism.e1_formation_s1gd_fixed_adapter_invocation_binding import bind_e1_formation_s1gd_fixed_adapter_invocations
from mcm_field_organism.e1_formation_s1gh_fresh_field_bridge import bind_e1_formation_s1gh_fresh_fields
from mcm_field_organism.e1_formation_s1gi_fixed_adapter_output_converter import (
    E1FormationS1GIFixedAdapterOutputConverterError,
    build_e1_formation_s1gi_synthetic_typed_output,
    convert_e1_formation_s1gi_fixed_adapter_output,
)


class E1FormationS1GIFixedAdapterOutputConverterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = binding_fixture.E1FormationS1GDFixedAdapterInvocationBindingTests
        source.setUpClass()
        bindings = bind_e1_formation_s1gd_fixed_adapter_invocations(
            source.wrapper_contract,
            source.contexts,
            source.handoffs,
        )
        cls.fresh = bind_e1_formation_s1gh_fresh_fields(bindings, source.inputs)

    @staticmethod
    def _vectors(item, scale=1.0):
        size = len(item.ordered_neuron_ids)
        activation = tuple(scale * (index + 1) / (size + 1) for index in range(size))
        afterimage = tuple(-value / 2.0 for value in activation)
        return activation, afterimage

    def test_converts_all_six_outputs_to_exact_common_schema(self) -> None:
        receipts = []
        for item in self.fresh.fresh_bindings:
            vectors = self._vectors(item)
            output = build_e1_formation_s1gi_synthetic_typed_output(item, *vectors)
            receipts.append(convert_e1_formation_s1gi_fixed_adapter_output(item, output))
        self.assertEqual(6, len(receipts))
        self.assertEqual(
            ("r2", "fixed-adapter-ab"),
            (receipts[0].refinement_id, receipts[0].role_id),
        )
        self.assertEqual(
            ("r8", "fixed-adapter-ba"),
            (receipts[-1].refinement_id, receipts[-1].role_id),
        )
        self.assertTrue(all(len(item.__dataclass_fields__) == 22 for item in receipts))

    def test_fixed_adapter_causal_evidence_stays_separate(self) -> None:
        fresh = self.fresh.fresh_bindings[0]
        output = build_e1_formation_s1gi_synthetic_typed_output(
            fresh,
            *self._vectors(fresh),
        )
        receipt = convert_e1_formation_s1gi_fixed_adapter_output(fresh, output)
        self.assertIsNotNone(receipt.source_state_digest)
        self.assertIsNotNone(receipt.fixed_adapter_digest)
        self.assertIsNone(receipt.state_digest_before)
        self.assertIsNone(receipt.state_digest_after)
        self.assertEqual("fixed-adapter", receipt.probe_mode)

    def test_raw_vectors_and_neuron_order_are_lossless(self) -> None:
        fresh = self.fresh.fresh_bindings[2]
        vectors = self._vectors(fresh, scale=0.25)
        output = build_e1_formation_s1gi_synthetic_typed_output(fresh, *vectors)
        receipt = convert_e1_formation_s1gi_fixed_adapter_output(fresh, output)
        self.assertEqual(vectors, (receipt.activation_vector, receipt.afterimage_vector))
        self.assertEqual(fresh.ordered_neuron_ids, receipt.ordered_neuron_ids)
        self.assertEqual(0, output.actual_field_steps_executed)

    def test_tampered_output_and_cross_binding_fail_closed(self) -> None:
        first, second = self.fresh.fresh_bindings[:2]
        output = build_e1_formation_s1gi_synthetic_typed_output(
            first,
            *self._vectors(first),
        )
        with self.assertRaises(E1FormationS1GIFixedAdapterOutputConverterError):
            replace(output, fixed_adapter_preserved=False)
        with self.assertRaises(E1FormationS1GIFixedAdapterOutputConverterError):
            convert_e1_formation_s1gi_fixed_adapter_output(second, output)

    def test_builder_and_converter_call_no_field_kernel_or_writer(self) -> None:
        sources = (
            inspect.getsource(build_e1_formation_s1gi_synthetic_typed_output),
            inspect.getsource(convert_e1_formation_s1gi_fixed_adapter_output),
        )
        for source in sources:
            for forbidden in (
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
