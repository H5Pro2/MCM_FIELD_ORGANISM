from __future__ import annotations

from dataclasses import asdict
from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_real_output_converters import (
    E1CommonProbeFormationOutputDiagnostic,
    audit_e1_common_probe_n2_r2_real_output_converters,
    convert_e1_common_probe_real_formation_output,
    convert_e1_common_probe_real_probe_output,
    diagnose_e1_common_probe_real_formation_output,
    run_e1_common_probe_n2_r2_typed_conversion_fixture,
)
from mcm_field_organism.e1_common_probe_real_wrappers import E1CommonProbeRealProbeOutput
from mcm_field_organism.e1_confirmation_formation_runner import E1ConfirmationFormationArmAudit
from mcm_field_organism.e1_confirmation_prepared_real_formation_kernel import E1PreparedRealFormationArmResult
from mcm_field_organism.e1_frozen_state_transfer_contract import _probe_digest
from mcm_field_organism.e1_refined_chain_canonical_producer import _initial_field_digest, _initial_state_digest
from mcm_field_organism.e1_refined_formation_runner import _digest, _state_payload
from mcm_field_organism.e1_handoff_digest_schemas import e1_handoff_digest_pair
from tests.test_e1_common_probe_n2_r2_object_handoff import E1CommonProbeN2R2ObjectHandoffTests


class E1CommonProbeN2R2RealOutputConverterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = E1CommonProbeN2R2ObjectHandoffTests
        source.setUpClass()
        cls.handoff = source(methodName="test_carries_all_real_objects_without_field_steps")._prepare()

    def _formation_output(self, resolved):
        arm = resolved.binding.formation_arm_id
        enabled = not arm.endswith("formation_ablated")
        state = self.handoff.initial_state
        audit = E1ConfirmationFormationArmAudit(
            refinement_id="r2",
            arm_id=arm,
            handoff_digest=e1_handoff_digest_pair(
                resolved.formation_plan.handoff
            ).assignment_digest,
            field_digest=_digest(("synthetic-typed-output", arm, "field")),
            source_support_count=resolved.formation_plan.handoff.source_event_count,
            assigned_event_count=resolved.formation_plan.handoff.source_event_count,
            resource_budget_error=0.0,
            formation_enabled=enabled,
            history_backreaction_enabled=False,
            state_remained_neutral=not enabled,
        )
        values = {
            "arm_id": arm,
            "refinement_id": "r2",
            "formation_enabled": enabled,
            "initial_field_digest": _initial_field_digest(self.handoff.initial_field),
            "initial_state_digest": _initial_state_digest(self.handoff.initial_state),
            "output_state": state,
            "output_state_digest": _digest(_state_payload(state)),
            "audit": audit,
            "input_objects_preserved": True,
            "copied_inputs_used": True,
            "canonical_execution_permitted": False,
            "claims_permitted": False,
        }
        payload = {name: value for name, value in values.items() if name not in {"output_state", "audit"}}
        payload["output_state"] = _state_payload(state)
        payload["audit"] = asdict(audit)
        return E1PreparedRealFormationArmResult(**values, result_digest=_digest(payload))

    def _probe_output(self, resolved, state_digest):
        values = {
            "binding_digest": resolved.binding.binding_digest,
            "terminal_field_digest": _digest(("synthetic-typed-output", resolved.binding.role_id, "field")),
            "activation": (0.1, 0.2, 0.3),
            "afterimage": (0.01, 0.02, 0.03),
            "field_step_count": 200,
            "source_support_count": resolved.probe_plan.handoff.source_event_count,
            "frozen_state_digest_before": state_digest,
            "frozen_state_digest_after": state_digest,
            "frozen_state_preserved": True,
            "persistence_performed": False,
            "research_decision_permitted": False,
            "memory_claim_permitted": False,
        }
        return E1CommonProbeRealProbeOutput(**values, result_digest=_digest(values))

    def _replace_formation_output(self, output, **changes):
        values = {
            name: getattr(output, name)
            for name in output.__dataclass_fields__
            if name != "result_digest"
        }
        values.update(changes)
        payload = {
            name: value
            for name, value in values.items()
            if name not in {"output_state", "audit"}
        }
        payload["output_state"] = _state_payload(values["output_state"])
        payload["audit"] = asdict(values["audit"])
        return E1PreparedRealFormationArmResult(
            **values, result_digest=_digest(payload)
        )

    def test_typed_formation_and_probe_outputs_convert_losslessly(self) -> None:
        formation_slot = self.handoff.formation_slots[0]
        formation = convert_e1_common_probe_real_formation_output(
            formation_slot, self._formation_output(formation_slot)
        )
        probe_slot = next(item for item in self.handoff.resolved_slots if item.binding.role_id == "e1-active-ab")
        output = self._probe_output(probe_slot, formation.output_state_digest)
        probe = convert_e1_common_probe_real_probe_output(probe_slot, output, formation)
        self.assertEqual((402, 200), (formation.accounted_field_steps, probe.accounted_field_steps))
        self.assertEqual(output.activation, probe.activation)
        self.assertEqual(output.afterimage, probe.afterimage)
        self.assertEqual("real-wrapper", probe.execution_mode)

    def test_p0_output_converts_without_formation(self) -> None:
        slot = self.handoff.resolved_slots[0]
        output = self._probe_output(slot, None)
        receipt = convert_e1_common_probe_real_probe_output(slot, output, None)
        self.assertIsNone(receipt.selected_state_role)
        self.assertIsNone(receipt.selected_state_digest)

    def test_each_formation_gate_is_named_and_individually_diagnostic(self) -> None:
        slot = self.handoff.formation_slots[0]
        output = self._formation_output(slot)
        baseline = diagnose_e1_common_probe_real_formation_output(slot, output)
        self.assertTrue(baseline.all_passed)
        self.assertEqual((), baseline.failed_gates)

        arm_audit = replace(output.audit, arm_id="ba")
        arm_output = self._replace_formation_output(
            output, arm_id="ba", audit=arm_audit
        )
        self.assertEqual(
            ("formation-arm-identity-exact",),
            diagnose_e1_common_probe_real_formation_output(slot, arm_output).failed_gates,
        )

        refinement_audit = replace(output.audit, refinement_id="r4")
        refinement_output = self._replace_formation_output(
            output, refinement_id="r4", audit=refinement_audit
        )
        self.assertEqual(
            ("formation-refinement-identity-exact",),
            diagnose_e1_common_probe_real_formation_output(slot, refinement_output).failed_gates,
        )

        wrong_handoff_audit = replace(
            output.audit,
            handoff_digest=_digest("wrong-handoff"),
        )
        wrong_handoff = self._replace_formation_output(
            output, audit=wrong_handoff_audit
        )
        self.assertEqual(
            ("formation-runtime-assignment-digest-exact",),
            diagnose_e1_common_probe_real_formation_output(slot, wrong_handoff).failed_gates,
        )

        wrong_plan = replace(
            slot.formation_plan,
            handoff_digest=_digest("wrong-plan-envelope"),
        )
        context_payload = {
            "binding_digest": slot.binding.binding_digest,
            "formation_sequence_digest": _probe_digest(slot.formation_sequences),
            "formation_plan_digest": wrong_plan.digest(),
            "probe_sequence_digest": _probe_digest(slot.probe_sequences),
            "probe_plan_digest": slot.probe_plan.digest(),
        }
        wrong_plan_slot = replace(
            slot,
            formation_plan=wrong_plan,
            context_digest=_digest(context_payload),
        )
        self.assertEqual(
            ("formation-plan-envelope-digest-exact",),
            diagnose_e1_common_probe_real_formation_output(
                wrong_plan_slot, output
            ).failed_gates,
        )

        wrong_support_audit = replace(
            output.audit,
            source_support_count=output.audit.source_support_count - 1,
            assigned_event_count=output.audit.assigned_event_count - 1,
        )
        wrong_support = self._replace_formation_output(
            output, audit=wrong_support_audit
        )
        self.assertEqual(
            ("formation-source-support-count-exact",),
            diagnose_e1_common_probe_real_formation_output(slot, wrong_support).failed_gates,
        )

    def test_converter_error_names_failed_gate(self) -> None:
        slot = self.handoff.formation_slots[0]
        output = self._formation_output(slot)
        wrong_audit = replace(output.audit, handoff_digest=_digest("wrong-handoff"))
        with self.assertRaisesRegex(
            Exception, "formation-runtime-assignment-digest-exact"
        ):
            convert_e1_common_probe_real_formation_output(
                slot, self._replace_formation_output(output, audit=wrong_audit)
            )

    def test_plan_step_gate_is_named_and_fails_closed(self) -> None:
        gates = (
            ("formation-arm-identity-exact", True),
            ("formation-refinement-identity-exact", True),
            ("formation-runtime-assignment-digest-exact", True),
            ("formation-plan-envelope-digest-exact", True),
            ("formation-source-support-count-exact", True),
            ("formation-plan-step-count-exactly-402", False),
        )
        values = {
            "gates": gates,
            "all_passed": False,
            "failed_gates": ("formation-plan-step-count-exactly-402",),
        }
        diagnostic = E1CommonProbeFormationOutputDiagnostic(
            **values, diagnostic_digest=_digest(values)
        )
        self.assertFalse(diagnostic.all_passed)
        self.assertEqual(
            ("formation-plan-step-count-exactly-402",),
            diagnostic.failed_gates,
        )

    def test_static_audit_does_not_execute_converters_or_wrappers(self) -> None:
        result = audit_e1_common_probe_n2_r2_real_output_converters()
        self.assertTrue(result.lossless_formation_mapping_implemented)
        self.assertTrue(result.lossless_probe_mapping_implemented)
        self.assertFalse(result.wrapper_execution_permitted)
        source = inspect.getsource(audit_e1_common_probe_n2_r2_real_output_converters)
        self.assertNotIn("convert_e1_common_probe_real_formation_output(", source)
        self.assertNotIn("convert_e1_common_probe_real_probe_output(", source)

    def test_full_typed_conversion_fixture_is_bounded_and_nonexecuting(self) -> None:
        result = run_e1_common_probe_n2_r2_typed_conversion_fixture(self.handoff)
        self.assertEqual((4, 8), (result.formation_count, result.probe_count))
        self.assertEqual((1608, 1600, 3208), (
            result.accounted_formation_steps,
            result.accounted_probe_steps,
            result.accounted_total_steps,
        ))
        self.assertEqual(0, result.actual_field_steps_executed)
        self.assertTrue(result.all_formation_fields_lossless)
        self.assertTrue(result.all_probe_fields_lossless)
        self.assertFalse(result.wrapper_execution_permitted)


if __name__ == "__main__":
    unittest.main()
