from __future__ import annotations

import copy
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_worker_binding import (
    E1ConfirmationCanonicalWorkerBindingError,
    S1_EB27_FUNCTION_INVENTORY,
    S1_EB27_REFINEMENTS,
    bind_e1_confirmation_canonical_worker_functions,
    current_s1_eb27_function_inventory,
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


def _audit():
    return audit_e1_confirmation_released_worker_contract(
        *_prepare_worker_inputs()
    )


class E1ConfirmationCanonicalWorkerBindingTests(unittest.TestCase):
    def test_binding_resolves_all_six_functions_without_invocation(self) -> None:
        result = bind_e1_confirmation_canonical_worker_functions(_audit())

        self.assertEqual(S1_EB27_FUNCTION_INVENTORY, result.function_inventory)
        self.assertEqual(6, len(result.function_inventory))
        self.assertTrue(result.all_functions_resolved)
        self.assertTrue(result.signatures_bound)
        self.assertTrue(result.source_digests_bound)
        self.assertFalse(result.canonical_calls_performed)

    def test_binding_preserves_r2_r4_r8_and_dataflow_order(self) -> None:
        result = bind_e1_confirmation_canonical_worker_functions(_audit())

        self.assertEqual(S1_EB27_REFINEMENTS, result.refinements)
        self.assertEqual(
            (
                "formation",
                "probe_handoff",
                "probe_r2_r4_r8",
                "result_handoff",
                "result_composition",
                "report_handoff",
            ),
            result.dataflow_roles,
        )

    def test_all_execution_marker_persistence_and_claim_gates_stay_closed(self) -> None:
        result = bind_e1_confirmation_canonical_worker_functions(_audit())

        for role in (
            "canonical_calls_performed",
            "marker_creation_permitted",
            "canonical_execution_permitted",
            "canonical_persistence_permitted",
            "claims_permitted",
        ):
            self.assertFalse(getattr(result, role))
        self.assertEqual(
            "CANONICAL_FUNCTIONS_BOUND_WITHOUT_INVOCATION",
            result.binding_status,
        )

    def test_changed_audit_fails_closed(self) -> None:
        changed = copy.deepcopy(_audit())
        object.__setattr__(changed, "audit_digest", "0" * 64)

        with self.assertRaises(E1ConfirmationCanonicalWorkerBindingError):
            bind_e1_confirmation_canonical_worker_functions(changed)

    def test_binding_is_repeatable_and_targets_stay_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = bind_e1_confirmation_canonical_worker_functions(_audit())
        second = bind_e1_confirmation_canonical_worker_functions(_audit())

        self.assertEqual(first, second)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_inventory_matches_current_functions_and_sources(self) -> None:
        self.assertEqual(
            S1_EB27_FUNCTION_INVENTORY,
            current_s1_eb27_function_inventory(),
        )

    def test_binding_source_contains_no_canonical_invocation_or_writer(self) -> None:
        source = inspect.getsource(
            bind_e1_confirmation_canonical_worker_functions
        )
        for forbidden in (
            "produce_e1_confirmation_canonical_formation(",
            "prepare_e1_confirmation_canonical_probe_handoff(",
            "run_e1_confirmation_canonical_seven_arm_probe(",
            "prepare_e1_confirmation_canonical_result_handoff(",
            "compose_e1_confirmation_canonical_result(",
            "prepare_e1_confirmation_canonical_report_handoff(",
            "_exclusive_marker(",
            "_atomic_publish(",
        ):
            self.assertNotIn(forbidden, source)

    def test_binding_roles_remain_private(self) -> None:
        for role in (
            "E1ConfirmationCanonicalWorkerBinding",
            "bind_e1_confirmation_canonical_worker_functions",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
