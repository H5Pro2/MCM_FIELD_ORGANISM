from __future__ import annotations

import copy
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_dataflow_contract import (
    E1ConfirmationCanonicalDataflowContractError,
    S1_EB28_CLOSED_GATES,
    S1_EB28_DIGEST_EDGES,
    S1_EB28_PARAMETER_EDGES,
    S1_EB28_REFINEMENTS,
    prepare_e1_confirmation_canonical_dataflow_contract,
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


def _binding():
    audit = audit_e1_confirmation_released_worker_contract(
        *_prepare_worker_inputs()
    )
    return bind_e1_confirmation_canonical_worker_functions(audit)


class E1ConfirmationCanonicalDataflowContractTests(unittest.TestCase):
    def test_contract_binds_six_artifact_types_and_fields(self) -> None:
        result = prepare_e1_confirmation_canonical_dataflow_contract(_binding())

        self.assertEqual(6, len(result.type_inventory))
        self.assertEqual(6, len(result.type_fields))
        self.assertTrue(result.type_fields_complete)
        self.assertFalse(result.objects_constructed)

    def test_contract_binds_parameter_and_digest_edges(self) -> None:
        result = prepare_e1_confirmation_canonical_dataflow_contract(_binding())

        self.assertEqual(S1_EB28_PARAMETER_EDGES, result.parameter_edges)
        self.assertEqual(S1_EB28_DIGEST_EDGES, result.digest_edges)
        self.assertTrue(result.digest_continuity_bound)

    def test_contract_requires_three_ordered_refinement_results(self) -> None:
        result = prepare_e1_confirmation_canonical_dataflow_contract(_binding())

        self.assertEqual(S1_EB28_REFINEMENTS, result.refinements)
        self.assertEqual(3, result.probe_result_count)

    def test_probe_result_and_chain_result_sources_are_bound(self) -> None:
        result = prepare_e1_confirmation_canonical_dataflow_contract(_binding())

        self.assertEqual(
            ("probe_result", "chain_result"),
            tuple(role for role, _ in result.external_type_digests),
        )

    def test_all_handoff_and_execution_gates_remain_closed(self) -> None:
        result = prepare_e1_confirmation_canonical_dataflow_contract(_binding())

        self.assertEqual(S1_EB28_CLOSED_GATES, result.closed_gates)
        self.assertTrue(result.closed_gates_bound)
        for role in (
            "objects_constructed",
            "canonical_calls_performed",
            "marker_creation_permitted",
            "canonical_execution_permitted",
            "canonical_persistence_permitted",
            "claims_permitted",
        ):
            self.assertFalse(getattr(result, role))

    def test_changed_function_binding_fails_closed(self) -> None:
        changed = copy.deepcopy(_binding())
        object.__setattr__(changed, "binding_digest", "0" * 64)

        with self.assertRaises(E1ConfirmationCanonicalDataflowContractError):
            prepare_e1_confirmation_canonical_dataflow_contract(changed)

    def test_contract_is_repeatable_and_targets_stay_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = prepare_e1_confirmation_canonical_dataflow_contract(_binding())
        second = prepare_e1_confirmation_canonical_dataflow_contract(_binding())

        self.assertEqual(first, second)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_contract_has_no_constructor_runtime_marker_or_writer_call(self) -> None:
        source = inspect.getsource(
            prepare_e1_confirmation_canonical_dataflow_contract
        )
        for forbidden in (
            "E1ConfirmationCanonicalFormationProduction(",
            "E1ConfirmationCanonicalProbeHandoff(",
            "E1ConfirmationProbeResult(",
            "E1ConfirmationCanonicalResultHandoff(",
            "E1ConfirmationChainResult(",
            "E1ConfirmationCanonicalReportHandoff(",
            "produce_e1_confirmation_canonical_formation(",
            "_exclusive_marker(",
            "_atomic_publish(",
        ):
            self.assertNotIn(forbidden, source)

    def test_contract_roles_remain_private(self) -> None:
        for role in (
            "E1ConfirmationCanonicalDataflowContract",
            "prepare_e1_confirmation_canonical_dataflow_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
