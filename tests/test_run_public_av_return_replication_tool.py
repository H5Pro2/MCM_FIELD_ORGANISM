from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import patch

import tools.run_public_av_return_replication as runner


class RunPublicAVReturnReplicationToolTests(unittest.TestCase):
    def test_rejected_preflight_stops_before_executor_binding(self) -> None:
        blocked = SimpleNamespace(
            single_bounded_replication_run_release_granted=False,
            repeat_count_authorized=1,
            field_run_started=False,
        )
        with (
            patch.object(runner, "nasa_earthrise_av_source_contract", return_value=object()),
            patch.object(runner, "public_av_return_permutation_contract", return_value=object()),
            patch.object(runner, "wire_public_av_return_replication_runner", return_value=object()),
            patch.object(runner, "audit_public_av_return_replication_preflight", return_value=blocked),
            patch.object(runner, "bind_public_av_return_replication_executor", side_effect=AssertionError("executor must not bind")),
        ):
            self.assertEqual(2, runner.main())

    def test_positive_preflight_is_passed_to_one_shot_gate(self) -> None:
        preflight = SimpleNamespace(
            single_bounded_replication_run_release_granted=True,
            repeat_count_authorized=1,
            field_run_started=False,
        )
        receipt = SimpleNamespace(
            preflight_id="preflight", runner_id="runner", source_id="source",
            release_scope="scope", authorized_repeat_count=1,
            execution_started=True, execution_completed=True,
            memory_claim_allowed=False, meaning_claim_allowed=False,
            organization_claim_allowed=False, ai_claim_allowed=False,
        )
        result = SimpleNamespace(
            execution_id="execution", runner_id="runner", preflight_id="preflight",
            source_id="source", clock_id="clock", stage_duration_ticks=1,
            resolution_duration_ticks=1, arms=(), pairwise_activation_linf=(),
            pairwise_afterimage_linf=(), layer_digest_equality=(),
            snapshot_digest_equality=(), memory_threshold_defined=False,
            organization_threshold_defined=False, memory_claim_allowed=False,
            meaning_claim_allowed=False, organization_claim_allowed=False,
            ai_claim_allowed=False,
        )
        gate = SimpleNamespace(start_once=lambda *args: (result, receipt))
        with (
            patch.object(runner, "nasa_earthrise_av_source_contract", return_value="contract"),
            patch.object(runner, "public_av_return_permutation_contract", return_value="permutation"),
            patch.object(runner, "wire_public_av_return_replication_runner", return_value="wiring"),
            patch.object(runner, "audit_public_av_return_replication_preflight", return_value=preflight),
            patch.object(runner, "bind_public_av_return_replication_executor", return_value="executor") as bind,
            patch.object(runner, "PublicAVReturnReplicationEntrypoint", return_value=gate) as gate_factory,
            patch("builtins.print") as output,
        ):
            self.assertEqual(0, runner.main())
        bind.assert_called_once_with(preflight, "permutation")
        gate_factory.assert_called_once_with("executor")
        self.assertIn('"authorized_repeat_count": 1', output.call_args.args[0])

    def test_payload_exposes_no_vectors_or_claim_scores(self) -> None:
        source = __import__("inspect").getsource(runner._payload)
        for forbidden in ("stage_two_activation", "stage_two_afterimage", "memory_score", "organization_score"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
