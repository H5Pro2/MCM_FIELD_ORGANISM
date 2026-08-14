from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec99_typed_vector_input_adapters import (
    E1CommonProbeEC99TypedVectorInputAdapterError,
    adapt_e1_common_probe_ec99_typed_vector_inputs,
    run_e1_common_probe_ec99_synthetic_fixture,
)
from mcm_field_organism.e1_common_probe_ec91_refinement_receipts_converters import (
    run_e1_common_probe_ec91_synthetic_fixture,
)
from mcm_field_organism.e1_common_probe_n2_r2_positive_step_receipt_contract import (
    build_e1_common_probe_n2_r2_positive_step_receipt_fixture,
)
from tests.test_e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffsTests,
)
from tests.test_e1_common_probe_n2_r2_object_handoff import (
    E1CommonProbeN2R2ObjectHandoffTests,
)


class E1CommonProbeEC99TypedVectorInputAdaptersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1CommonProbeN2R2ObjectHandoffTests.setUpClass()
        cls.r2_handoff = E1CommonProbeN2R2ObjectHandoffTests()._prepare()
        E1CommonProbeEC89R4R8ObjectHandoffsTests.setUpClass()
        cls.r4_r8_handoffs = E1CommonProbeEC89R4R8ObjectHandoffsTests()._prepare()

    def test_all_24_typed_receipts_enter_ec98_exactly_once(self) -> None:
        result = run_e1_common_probe_ec99_synthetic_fixture()
        self.assertEqual((("r2", 8), ("r4", 8), ("r8", 8)), result.refinement_counts)
        self.assertEqual(24, len(result.inputs))
        self.assertEqual(6, result.vector_receipt.active_vector_count)
        self.assertTrue(result.all_roles_exact_once_per_refinement)
        self.assertTrue(result.common_vector_geometry)
        self.assertEqual(0, result.field_steps_executed)

    def test_fixture_is_deterministic(self) -> None:
        first = run_e1_common_probe_ec99_synthetic_fixture()
        second = run_e1_common_probe_ec99_synthetic_fixture()
        self.assertEqual(first.result_digest, second.result_digest)
        self.assertEqual(first.vector_receipt_digest, second.vector_receipt_digest)

    def test_established_ec63_and_ec91_receipts_are_compatible(self) -> None:
        r2 = build_e1_common_probe_n2_r2_positive_step_receipt_fixture(
            self.r2_handoff
        )
        refined = run_e1_common_probe_ec91_synthetic_fixture(
            self.r4_r8_handoffs
        )
        result = adapt_e1_common_probe_ec99_typed_vector_inputs(
            r2.probes, tuple(item for group in refined.probes for item in group)
        )
        self.assertEqual(24, len(result.inputs))
        self.assertEqual(6, result.vector_receipt.active_vector_count)
        self.assertEqual(0, result.field_steps_executed)

    def test_wrong_order_and_mixed_receipt_type_fail_closed(self) -> None:
        result = run_e1_common_probe_ec99_synthetic_fixture()
        r2 = tuple(result.inputs[:8])
        with self.assertRaises(E1CommonProbeEC99TypedVectorInputAdapterError):
            adapt_e1_common_probe_ec99_typed_vector_inputs(r2, tuple())  # type: ignore[arg-type]

    def test_changed_geometry_fails_closed(self) -> None:
        result = run_e1_common_probe_ec99_synthetic_fixture()
        with self.assertRaises(E1CommonProbeEC99TypedVectorInputAdapterError):
            replace(result, common_vector_geometry=False)

    def test_adapter_has_no_field_wrapper_decider_or_writer(self) -> None:
        source = inspect.getsource(adapt_e1_common_probe_ec99_typed_vector_inputs)
        for forbidden in (
            "run_e1_common_probe_real_formation_wrapper(",
            "run_e1_common_probe_real_probe_wrapper(",
            "run_e1_common_probe_ec96_authorized_r4_r8_once(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
