from __future__ import annotations

from dataclasses import replace
import inspect
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mcm_field_organism.w7as_terminal_in_memory_handoff as handoff
from mcm_field_organism.w7an_r124_resolution_container import (
    _P0_REFERENCE_DIGEST,
    W7ANR124ResolutionContainer,
)
from mcm_field_organism.w7an_staged_r124_coordinator import (
    _CANONICAL_STAGED_RESOLUTION_DIGESTS,
    _ROLES,
    _TOTAL_PHASES,
    _start_w7an_staged_r124_coordinator,
)
from mcm_field_organism.w7ao_resolution_comparison_contract import (
    build_w7ao_resolution_comparison_contract,
)
from mcm_field_organism.w7ap_raw_resolution_distance_compositor import (
    W7APRawResolutionDistanceComposition,
)
from mcm_field_organism.w7aq_numerical_evaluation_contract import (
    build_w7aq_numerical_evaluation_contract,
)
from mcm_field_organism.w7ar_numerical_resolution_evaluator import (
    W7ARNumericalResolutionEvaluation,
)


def _state():
    p0 = SimpleNamespace(
        p0_zero_start_measurement_reference_digest=_P0_REFERENCE_DIGEST
    )
    state = _start_w7an_staged_r124_coordinator(
        *(object() for _ in range(6)),
        p0,
    )
    state.role_index = len(_ROLES)
    state.completed_phase_count = _TOTAL_PHASES
    state.receipts = [object()] * _TOTAL_PHASES
    state.primary_results = {
        resolution_id: SimpleNamespace(
            resolution_id=resolution_id,
            resolution_result_digest=digest,
            p0_references=p0,
        )
        for resolution_id, digest in _CANONICAL_STAGED_RESOLUTION_DIGESTS.items()
    }
    state.repeat_results = {
        resolution_id: SimpleNamespace(
            resolution_result_digest=item.resolution_result_digest
        )
        for resolution_id, item in state.primary_results.items()
    }
    return state


def _results():
    container = object.__new__(W7ANR124ResolutionContainer)
    object.__setattr__(
        container,
        "resolution_container_digest",
        handoff._W7AN_CONTAINER_DIGEST,
    )
    composition = object.__new__(W7APRawResolutionDistanceComposition)
    object.__setattr__(
        composition,
        "w7an_container_digest",
        handoff._W7AN_CONTAINER_DIGEST,
    )
    object.__setattr__(
        composition,
        "w7ao_contract_digest",
        handoff._W7AO_CONTRACT_DIGEST,
    )
    object.__setattr__(
        composition,
        "raw_resolution_distance_composition_digest",
        "a" * 64,
    )
    object.__setattr__(
        composition,
        "field_function_decision_allowed",
        False,
    )
    evaluation = object.__new__(W7ARNumericalResolutionEvaluation)
    object.__setattr__(
        evaluation,
        "w7aq_contract_digest",
        handoff._W7AQ_CONTRACT_DIGEST,
    )
    object.__setattr__(
        evaluation,
        "raw_resolution_distance_composition_digest",
        "a" * 64,
    )
    object.__setattr__(evaluation, "evaluation_result_digest", "b" * 64)
    object.__setattr__(evaluation, "field_function_decision_allowed", False)
    object.__setattr__(evaluation, "memory_claim_allowed", False)
    return container, composition, evaluation


class W7ASTerminalInMemoryHandoffTests(unittest.TestCase):
    def test_terminal_handoff_calls_each_stage_once_in_order(self):
        state = _state()
        container, composition, evaluation = _results()
        comparison = build_w7ao_resolution_comparison_contract()
        contract = build_w7aq_numerical_evaluation_contract()
        calls = []

        def finalize(*args):
            calls.append("w7an")
            state.resolution_container = container
            return container

        def compose(*args):
            calls.append("w7ap")
            return composition

        def evaluate(*args):
            calls.append("w7ar")
            return evaluation

        with patch.object(
            handoff,
            "_finalize_w7an_staged_r124_coordinator",
            side_effect=finalize,
        ), patch.object(
            handoff,
            "compose_w7ap_raw_resolution_distances",
            side_effect=compose,
        ), patch.object(
            handoff,
            "evaluate_w7ar_numerical_resolution",
            side_effect=evaluate,
        ):
            result = handoff._finalize_w7as_terminal_in_memory_handoff(
                state,
                *(object() for _ in range(3)),
                comparison,
                contract,
            )
        self.assertEqual(["w7an", "w7ap", "w7ar"], calls)
        self.assertIs(container, result.resolution_container)
        self.assertIs(composition, result.distance_composition)
        self.assertIs(evaluation, result.numerical_evaluation)
        self.assertIs(result, state.w7as_terminal_result)

    def test_result_binds_digest_chain_and_claim_locks(self):
        state = _state()
        container, composition, evaluation = _results()
        with patch.object(
            handoff,
            "_finalize_w7an_staged_r124_coordinator",
            return_value=container,
        ), patch.object(
            handoff,
            "compose_w7ap_raw_resolution_distances",
            return_value=composition,
        ), patch.object(
            handoff,
            "evaluate_w7ar_numerical_resolution",
            return_value=evaluation,
        ):
            result = handoff._finalize_w7as_terminal_in_memory_handoff(
                state,
                *(object() for _ in range(3)),
                build_w7ao_resolution_comparison_contract(),
                build_w7aq_numerical_evaluation_contract(),
            )
        self.assertEqual("a" * 64, result.w7ap_composition_digest)
        self.assertEqual("b" * 64, result.w7ar_evaluation_digest)
        self.assertFalse(result.persisted)
        self.assertFalse(result.field_function_decision_allowed)
        self.assertFalse(result.memory_claim_allowed)

    def test_incomplete_coordinator_is_rejected_before_finalization(self):
        state = _state()
        state.completed_phase_count = 35
        with patch.object(
            handoff,
            "_finalize_w7an_staged_r124_coordinator",
        ) as finalize:
            with self.assertRaisesRegex(
                handoff.W7ASTerminalHandoffError,
                "prerequisites",
            ):
                handoff._finalize_w7as_terminal_in_memory_handoff(
                    state,
                    *(object() for _ in range(3)),
                    build_w7ao_resolution_comparison_contract(),
                    build_w7aq_numerical_evaluation_contract(),
                )
        finalize.assert_not_called()

    def test_failed_terminal_stage_is_locked_and_cannot_retry(self):
        state = _state()
        container, _, _ = _results()
        with patch.object(
            handoff,
            "_finalize_w7an_staged_r124_coordinator",
            return_value=container,
        ), patch.object(
            handoff,
            "compose_w7ap_raw_resolution_distances",
            side_effect=ValueError("stop"),
        ):
            with self.assertRaisesRegex(
                handoff.W7ASTerminalHandoffError,
                "ValueError: stop",
            ):
                handoff._finalize_w7as_terminal_in_memory_handoff(
                    state,
                    *(object() for _ in range(3)),
                    build_w7ao_resolution_comparison_contract(),
                    build_w7aq_numerical_evaluation_contract(),
                )
        self.assertTrue(state.w7as_terminal_error)
        with self.assertRaisesRegex(
            handoff.W7ASTerminalHandoffError,
            "already attempted",
        ):
            handoff._finalize_w7as_terminal_in_memory_handoff(
                state,
                *(object() for _ in range(3)),
                build_w7ao_resolution_comparison_contract(),
                build_w7aq_numerical_evaluation_contract(),
            )

    def test_successful_terminal_handoff_cannot_repeat(self):
        state = _state()
        container, composition, evaluation = _results()
        with patch.object(
            handoff,
            "_finalize_w7an_staged_r124_coordinator",
            return_value=container,
        ), patch.object(
            handoff,
            "compose_w7ap_raw_resolution_distances",
            return_value=composition,
        ), patch.object(
            handoff,
            "evaluate_w7ar_numerical_resolution",
            return_value=evaluation,
        ):
            handoff._finalize_w7as_terminal_in_memory_handoff(
                state,
                *(object() for _ in range(3)),
                build_w7ao_resolution_comparison_contract(),
                build_w7aq_numerical_evaluation_contract(),
            )
        with self.assertRaisesRegex(
            handoff.W7ASTerminalHandoffError,
            "already attempted",
        ):
            handoff._finalize_w7as_terminal_in_memory_handoff(
                state,
                *(object() for _ in range(3)),
                build_w7ao_resolution_comparison_contract(),
                build_w7aq_numerical_evaluation_contract(),
            )

    def test_tampering_and_public_export_are_rejected(self):
        state = _state()
        container, composition, evaluation = _results()
        with patch.object(
            handoff,
            "_finalize_w7an_staged_r124_coordinator",
            return_value=container,
        ), patch.object(
            handoff,
            "compose_w7ap_raw_resolution_distances",
            return_value=composition,
        ), patch.object(
            handoff,
            "evaluate_w7ar_numerical_resolution",
            return_value=evaluation,
        ):
            result = handoff._finalize_w7as_terminal_in_memory_handoff(
                state,
                *(object() for _ in range(3)),
                build_w7ao_resolution_comparison_contract(),
                build_w7aq_numerical_evaluation_contract(),
            )
        with self.assertRaises(handoff.W7ASTerminalHandoffError):
            replace(result, persisted=True)
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "_finalize_w7as_terminal_in_memory_handoff")
        )

    def test_handoff_source_has_no_execution_or_persistence_path(self):
        source = inspect.getsource(
            handoff._finalize_w7as_terminal_in_memory_handoff
        )
        self.assertNotIn(".advance(", source)
        self.assertNotIn("open(", source)
        self.assertNotIn("reports", source)
        self.assertNotIn("write", source)


if __name__ == "__main__":
    unittest.main()
