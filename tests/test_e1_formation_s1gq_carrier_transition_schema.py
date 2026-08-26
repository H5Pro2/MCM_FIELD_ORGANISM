from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gn_live_field_carrier as carrier_fixture

from mcm_field_organism.e1_formation_s1gn_live_field_carrier import (
    advance_e1_formation_s1gn_live_field_carrier_synthetically,
    build_e1_formation_s1gn_initial_live_field_carrier,
)
from mcm_field_organism.e1_formation_s1gq_carrier_transition_schema import (
    E1FormationS1GQCarrierTransitionSchemaError,
    E1FormationS1GQRealFieldCarrierTransition,
    S1_GQ_COMMON_FIELDS,
    audit_e1_formation_s1gq_carrier_transition_schema,
    bind_e1_formation_s1gq_carrier_transition_envelope,
)


class E1FormationS1GQCarrierTransitionSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = carrier_fixture.E1FormationS1GNLiveFieldCarrierTests
        source.setUpClass()
        cls.fresh = source.bridge.fresh_bindings[0]

    def _synthetic_transition(self):
        carrier = build_e1_formation_s1gn_initial_live_field_carrier(self.fresh)
        batch = self.fresh.invocation.context.probe_plan.handoff.batches[0]
        return advance_e1_formation_s1gn_live_field_carrier_synthetically(
            self.fresh,
            batch,
            carrier,
        )

    def test_real_schema_and_synthetic_type_share_only_narrow_fields(self) -> None:
        audit = audit_e1_formation_s1gq_carrier_transition_schema()
        self.assertEqual(S1_GQ_COMMON_FIELDS, audit.common_fields)
        self.assertTrue(audit.synthetic_fields_complete)
        self.assertTrue(audit.real_fields_complete)
        self.assertTrue(audit.separate_semantics_enforced)

    def test_shared_envelope_accepts_exact_synthetic_transition(self) -> None:
        transition = self._synthetic_transition()
        envelope = bind_e1_formation_s1gq_carrier_transition_envelope(
            transition
        )
        self.assertEqual("synthetic-no-field-advance", envelope.transition_kind)
        self.assertIs(envelope.previous_carrier, transition.previous_carrier)
        self.assertIs(envelope.next_carrier, transition.next_carrier)
        self.assertFalse(envelope.field_object_replaced)
        self.assertEqual(0, envelope.actual_field_steps_executed)

    def test_envelope_tampering_and_unknown_type_fail_closed(self) -> None:
        envelope = bind_e1_formation_s1gq_carrier_transition_envelope(
            self._synthetic_transition()
        )
        with self.assertRaises(E1FormationS1GQCarrierTransitionSchemaError):
            replace(envelope, transition_kind="real-field-advance")
        with self.assertRaises(E1FormationS1GQCarrierTransitionSchemaError):
            bind_e1_formation_s1gq_carrier_transition_envelope(object())

    def test_no_real_builder_adapter_or_execution_is_open(self) -> None:
        audit = audit_e1_formation_s1gq_carrier_transition_schema()
        self.assertFalse(audit.real_transition_builder_present)
        self.assertFalse(audit.adapter_import_present)
        self.assertFalse(audit.execution_permitted)
        self.assertFalse(audit.persistence_performed)
        self.assertFalse(audit.claims_permitted)
        self.assertEqual(
            "SEPARATE_REAL_TRANSITION_SCHEMA_AND_SHARED_ENVELOPE_READY",
            audit.decision,
        )

    def test_real_schema_requires_new_field_and_one_real_step(self) -> None:
        source = inspect.getsource(
            E1FormationS1GQRealFieldCarrierTransition.__post_init__
        )
        for required in (
            "self.previous_field_digest == self.next_field_digest",
            "self.synthetic_no_field_advance is not False",
            "self.actual_field_steps_executed != 1",
            "self.previous_carrier.actual_field_steps_executed + 1",
        ):
            self.assertIn(required, source)

    def test_module_has_no_real_adapter_kernel_or_writer(self) -> None:
        module_source = inspect.getsource(
            audit_e1_formation_s1gq_carrier_transition_schema
        )
        for forbidden in (
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, module_source)


if __name__ == "__main__":
    unittest.main()
