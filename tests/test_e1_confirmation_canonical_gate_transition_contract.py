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
    E1ConfirmationCanonicalGateTransitionContractError,
    S1_EB29_FAILURE_POLICY,
    S1_EB29_PERMANENT_CLOSURES,
    S1_EB29_REQUIRED_EVIDENCE,
    S1_EB29_TRANSITIONS,
    prepare_e1_confirmation_canonical_gate_transition_contract,
)
from mcm_field_organism.e1_confirmation_canonical_worker_binding import (
    bind_e1_confirmation_canonical_worker_functions,
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


def _dataflow():
    audit = audit_e1_confirmation_released_worker_contract(
        *_prepare_worker_inputs()
    )
    binding = bind_e1_confirmation_canonical_worker_functions(audit)
    return prepare_e1_confirmation_canonical_dataflow_contract(binding)


class E1ConfirmationCanonicalGateTransitionContractTests(unittest.TestCase):
    def test_contract_binds_only_four_minimal_transitions(self) -> None:
        result = prepare_e1_confirmation_canonical_gate_transition_contract(
            _dataflow()
        )

        self.assertEqual(S1_EB29_TRANSITIONS, result.transitions)
        self.assertEqual(4, result.transition_count)
        self.assertFalse(result.gates_opened_now)

    def test_retry_claims_decision_and_tuning_stay_permanently_closed(self) -> None:
        result = prepare_e1_confirmation_canonical_gate_transition_contract(
            _dataflow()
        )

        self.assertEqual(S1_EB29_PERMANENT_CLOSURES, result.permanent_closures)
        self.assertEqual(10, result.permanent_closure_count)
        self.assertIn("report_handoff.retry_permitted", result.permanent_closures)
        self.assertIn("report_handoff.claims_permitted", result.permanent_closures)
        self.assertIn("release.posthoc_tuning_permitted", result.permanent_closures)

    def test_transition_evidence_binds_preflight_attempt_and_resources(self) -> None:
        result = prepare_e1_confirmation_canonical_gate_transition_contract(
            _dataflow()
        )

        self.assertEqual(S1_EB29_REQUIRED_EVIDENCE, result.required_evidence)
        self.assertIn(
            "same_process_preflight_younger_than_five_seconds",
            result.required_evidence,
        )
        self.assertIn("exclusive_attempt_created", result.required_evidence)
        self.assertIn(
            "resource_guard_active_for_entire_worker_process",
            result.required_evidence,
        )

    def test_failure_policy_retains_attempt_and_forbids_retry(self) -> None:
        result = prepare_e1_confirmation_canonical_gate_transition_contract(
            _dataflow()
        )

        self.assertEqual(S1_EB29_FAILURE_POLICY, result.failure_policy)
        self.assertEqual(
            "retain_attempt_remove_lock_no_retry",
            dict(result.failure_policy)["after_attempt_before_publish"],
        )

    def test_all_current_execution_and_persistence_gates_remain_closed(self) -> None:
        result = prepare_e1_confirmation_canonical_gate_transition_contract(
            _dataflow()
        )

        for role in (
            "gates_opened_now",
            "objects_constructed",
            "canonical_calls_performed",
            "marker_creation_permitted",
            "canonical_execution_permitted",
            "canonical_persistence_permitted",
            "retry_permitted",
            "claims_permitted",
        ):
            self.assertFalse(getattr(result, role))

    def test_changed_dataflow_contract_fails_closed(self) -> None:
        changed = copy.deepcopy(_dataflow())
        object.__setattr__(changed, "contract_digest", "0" * 64)

        with self.assertRaises(E1ConfirmationCanonicalGateTransitionContractError):
            prepare_e1_confirmation_canonical_gate_transition_contract(changed)

    def test_contract_is_repeatable_and_targets_stay_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = prepare_e1_confirmation_canonical_gate_transition_contract(
            _dataflow()
        )
        second = prepare_e1_confirmation_canonical_gate_transition_contract(
            _dataflow()
        )

        self.assertEqual(first, second)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_contract_has_no_replace_runtime_marker_or_writer_call(self) -> None:
        source = inspect.getsource(
            prepare_e1_confirmation_canonical_gate_transition_contract
        )
        for forbidden in (
            "dataclasses.replace(",
            "replace(dataflow",
            "produce_e1_confirmation_canonical_formation(",
            "run_e1_confirmation_canonical_seven_arm_probe(",
            "_exclusive_marker(",
            "_atomic_publish(",
        ):
            self.assertNotIn(forbidden, source)

    def test_contract_roles_remain_private(self) -> None:
        for role in (
            "E1ConfirmationCanonicalGateTransitionContract",
            "prepare_e1_confirmation_canonical_gate_transition_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
