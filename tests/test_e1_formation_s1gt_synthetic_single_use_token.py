from __future__ import annotations

import copy
from dataclasses import replace
import inspect
import pickle
import unittest

from mcm_field_organism.e1_formation_s1gs_real_single_batch_gate_contract import (
    build_e1_formation_s1gs_real_single_batch_gate_contract,
)
from mcm_field_organism.e1_formation_s1gt_synthetic_single_use_token import (
    E1FormationS1GTSyntheticSingleUseTokenError,
    build_e1_formation_s1gt_synthetic_authorization_fixture,
    exercise_e1_formation_s1gt_synthetic_token_lifecycle,
    issue_e1_formation_s1gt_synthetic_single_use_token,
)


class E1FormationS1GTSyntheticSingleUseTokenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = build_e1_formation_s1gs_real_single_batch_gate_contract()
        self.fixture = build_e1_formation_s1gt_synthetic_authorization_fixture(
            self.gate
        )

    def test_fixture_is_not_owner_authorization_or_real_permission(self) -> None:
        self.assertFalse(self.fixture.external_owner_authorization)
        self.assertFalse(self.fixture.real_token_creation_permitted)
        self.assertFalse(self.fixture.execution_permitted)
        self.assertEqual(
            "synthetic-fixture-only-no-owner-authorization",
            self.fixture.authorization_scope,
        )
        with self.assertRaises(E1FormationS1GTSyntheticSingleUseTokenError):
            replace(self.fixture, external_owner_authorization=True)

    def test_success_path_requires_consumption_then_retirement(self) -> None:
        token = issue_e1_formation_s1gt_synthetic_single_use_token(self.fixture)
        self.assertEqual("issued", token.status)
        token.consume()
        self.assertTrue(token.consumed)
        token.retire("synthetic-success")
        self.assertTrue(token.retired)
        self.assertEqual("synthetic-success", token.outcome)

    def test_failure_can_retire_before_or_after_consumption(self) -> None:
        before = issue_e1_formation_s1gt_synthetic_single_use_token(self.fixture)
        before.retire("synthetic-failure")
        self.assertTrue(before.retired)

        after = issue_e1_formation_s1gt_synthetic_single_use_token(self.fixture)
        after.consume()
        after.retire("synthetic-failure")
        self.assertTrue(after.retired)

    def test_replay_and_premature_success_fail_closed(self) -> None:
        token = issue_e1_formation_s1gt_synthetic_single_use_token(self.fixture)
        with self.assertRaises(E1FormationS1GTSyntheticSingleUseTokenError):
            token.retire("synthetic-success")
        token.consume()
        with self.assertRaises(E1FormationS1GTSyntheticSingleUseTokenError):
            token.consume()
        token.retire("synthetic-success")
        with self.assertRaises(E1FormationS1GTSyntheticSingleUseTokenError):
            token.retire("synthetic-success")

    def test_token_cannot_be_copied_deepcopied_or_serialized(self) -> None:
        token = issue_e1_formation_s1gt_synthetic_single_use_token(self.fixture)
        for operation in (
            lambda: copy.copy(token),
            lambda: copy.deepcopy(token),
            lambda: pickle.dumps(token),
        ):
            with self.assertRaises(E1FormationS1GTSyntheticSingleUseTokenError):
                operation()
        with self.assertRaises(E1FormationS1GTSyntheticSingleUseTokenError):
            token.authorization_scope = "real"

    def test_complete_lifecycle_has_zero_real_calls_and_steps(self) -> None:
        result = exercise_e1_formation_s1gt_synthetic_token_lifecycle()
        self.assertTrue(result.success_token_retired)
        self.assertTrue(result.failure_before_consumption_retired)
        self.assertTrue(result.failure_after_consumption_retired)
        self.assertTrue(result.replay_after_consumption_rejected)
        self.assertTrue(result.replay_after_retirement_rejected)
        self.assertEqual((0, 0), (result.adapter_calls, result.field_steps_executed))
        self.assertFalse(result.external_owner_authorization)
        self.assertFalse(result.real_token_created)

    def test_lifecycle_calls_no_adapter_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            exercise_e1_formation_s1gt_synthetic_token_lifecycle
        )
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
