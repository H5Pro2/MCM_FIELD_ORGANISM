from __future__ import annotations

import copy
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_dataflow_contract import (
    prepare_e1_confirmation_canonical_dataflow_contract,
)
from mcm_field_organism.e1_confirmation_canonical_gate_transition_contract import (
    prepare_e1_confirmation_canonical_gate_transition_contract,
)
from mcm_field_organism.e1_confirmation_canonical_worker_binding import (
    bind_e1_confirmation_canonical_worker_functions,
)
from mcm_field_organism.e1_confirmation_final_go_no_go_audit import (
    E1ConfirmationFinalGoNoGoAuditError,
    S1_EB30_GO_REQUIREMENTS,
    S1_EB30_IMPLEMENTATION_DIGESTS,
    S1_EB30_ONLY_REMAINING_UNIT,
    audit_e1_confirmation_final_go_no_go,
    current_s1_eb30_implementation_digests,
)
from mcm_field_organism.e1_confirmation_one_shot_worker import (
    _prepare_worker_inputs,
)
from mcm_field_organism.e1_confirmation_released_worker_audit import (
    audit_e1_confirmation_released_worker_contract,
)


TARGETS = (
    Path("reports/e1_refined_confirmation_s1eb_once_v1.json"),
    Path("reports/e1_refined_confirmation_s1eb_once_v1.attempt.json"),
    Path("reports/e1_refined_confirmation_s1eb_once_v1.lock"),
)


def _inputs():
    released = audit_e1_confirmation_released_worker_contract(
        *_prepare_worker_inputs()
    )
    binding = bind_e1_confirmation_canonical_worker_functions(released)
    dataflow = prepare_e1_confirmation_canonical_dataflow_contract(binding)
    transitions = prepare_e1_confirmation_canonical_gate_transition_contract(
        dataflow
    )
    return released, transitions


class E1ConfirmationFinalGoNoGoAuditTests(unittest.TestCase):
    def test_audit_returns_go_with_all_requirements_satisfied(self) -> None:
        result = audit_e1_confirmation_final_go_no_go(*_inputs())

        self.assertEqual(
            "GO_FOR_FINAL_CANONICAL_WORKER_IMPLEMENTATION", result.decision
        )
        self.assertEqual(S1_EB30_GO_REQUIREMENTS, result.satisfied_requirements)
        self.assertEqual(
            "ONE_IMPLEMENTATION_AND_EXECUTION_UNIT_ONLY",
            result.decision_scope,
        )

    def test_audit_forbids_more_adapter_steps(self) -> None:
        result = audit_e1_confirmation_final_go_no_go(*_inputs())

        self.assertFalse(result.further_adapter_steps_permitted)
        self.assertEqual(S1_EB30_ONLY_REMAINING_UNIT, result.only_remaining_unit)

    def test_audit_keeps_run_persistence_retry_tuning_and_claims_unstarted(self) -> None:
        result = audit_e1_confirmation_final_go_no_go(*_inputs())

        for role in (
            "canonical_worker_implemented",
            "canonical_execution_started",
            "canonical_persistence_started",
            "retry_permitted",
            "posthoc_tuning_permitted",
            "claims_permitted",
        ):
            self.assertFalse(getattr(result, role))

    def test_audit_binds_complete_implementation_inventory_and_resources(self) -> None:
        result = audit_e1_confirmation_final_go_no_go(*_inputs())

        self.assertEqual(S1_EB30_IMPLEMENTATION_DIGESTS, result.implementation_digests)
        self.assertEqual(23_800, result.total_field_steps)
        self.assertEqual(1_800, result.max_wall_seconds)
        self.assertEqual(4 * 1024**3, result.max_peak_rss_bytes)

    def test_changed_transition_contract_fails_closed(self) -> None:
        released, transitions = _inputs()
        changed = copy.deepcopy(transitions)
        object.__setattr__(changed, "contract_digest", "0" * 64)

        with self.assertRaises(E1ConfirmationFinalGoNoGoAuditError):
            audit_e1_confirmation_final_go_no_go(released, changed)

    def test_audit_is_repeatable_and_targets_stay_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = audit_e1_confirmation_final_go_no_go(*_inputs())
        second = audit_e1_confirmation_final_go_no_go(*_inputs())

        self.assertEqual(first, second)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_inventory_matches_current_sources(self) -> None:
        self.assertEqual(
            S1_EB30_IMPLEMENTATION_DIGESTS,
            current_s1_eb30_implementation_digests(),
        )

    def test_audit_has_no_implementation_runtime_marker_or_writer_call(self) -> None:
        source = inspect.getsource(audit_e1_confirmation_final_go_no_go)
        for forbidden in (
            "produce_e1_confirmation_canonical_formation(",
            "run_e1_confirmation_canonical_seven_arm_probe(",
            "execute_e1_confirmation_canonical_worker_once(",
            "_exclusive_marker(",
            "_atomic_publish(",
            "subprocess",
        ):
            self.assertNotIn(forbidden, source)

    def test_audit_roles_remain_private(self) -> None:
        for role in (
            "E1ConfirmationFinalGoNoGoAudit",
            "audit_e1_confirmation_final_go_no_go",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
