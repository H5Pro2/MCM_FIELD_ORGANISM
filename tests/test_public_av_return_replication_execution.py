from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mcm_field_organism.public_av_return_permutation_contract import public_av_return_permutation_contract
from mcm_field_organism.public_av_return_replication_execution import (
    PublicAVReturnReplicationExecutionError,
    bind_public_av_return_replication_executor,
    execute_public_av_return_replication,
    public_av_return_replication_execution_public_roles,
)
from mcm_field_organism.public_av_return_replication_preflight import (
    audit_public_av_return_replication_preflight,
)
from mcm_field_organism.public_av_return_replication_runner import wire_public_av_return_replication_runner
from mcm_field_organism.public_media_source_contract import (
    PublicMediaSourceAudit,
    nasa_earthrise_av_source_contract,
)


MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


class FakeNeuron:
    def __init__(self, activation: float, afterimage: float) -> None:
        self.activation = activation
        self.afterimage = afterimage


class FakeLayer:
    def __init__(self, tag: str) -> None:
        self.tag = tag
        self.neurons = (FakeNeuron(float(len(tag)), float(len(tag)) / 10.0), FakeNeuron(float(len(tag)) + 1.0, 0.5))

    def digest(self) -> str:
        return f"layer-{self.tag}"


class FakeSnapshot:
    def __init__(self, tag: str) -> None:
        self.tag = tag

    def digest(self) -> str:
        return f"snapshot-{self.tag}"


class FakeField:
    def __init__(self, tag: str) -> None:
        self.tag = tag
        self.layer = FakeLayer(tag)
        self.last_distribution = object()

    def snapshot(self) -> FakeSnapshot:
        return FakeSnapshot(self.tag)


def accepted_source_audit() -> PublicMediaSourceAudit:
    contract = nasa_earthrise_av_source_contract()
    return PublicMediaSourceAudit(
        contract.source_id,
        True,
        True,
        True,
        True,
        contract.expected_size_bytes,
        contract.expected_sha1,
    )


class PublicAVReturnReplicationExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = nasa_earthrise_av_source_contract()
        self.permutation = public_av_return_permutation_contract()
        self.wiring = wire_public_av_return_replication_runner(permutation_contract=self.permutation)
        self.preflight = audit_public_av_return_replication_preflight(
            MEDIA,
            self.contract,
            source_audit=accepted_source_audit(),
            permutation_contract=self.permutation,
            wiring=self.wiring,
        )

    def execute_with_stubs(self):
        calls = {"run": 0, "gap": 0}

        def fake_run(field, sequences, steps, substrate, *, afterimage_config):
            calls["run"] += 1
            return SimpleNamespace(field=FakeField(f"run-{calls['run']}"), source_support_count=56)

        def fake_gap(field, start, end, substrate, afterimage):
            calls["gap"] += 1
            return FakeField(f"gap-{calls['gap']}-{start}-{end}")

        def fake_intervention(field, mode):
            return SimpleNamespace(
                field=FakeField(f"intervention-{mode}"),
                audit=SimpleNamespace(intervention_id=f"observer.shared-field-component.{mode}.v1"),
            )

        with (
            patch("mcm_field_organism.public_av_return_replication_execution._sequences", return_value=("stage-one",)),
            patch("mcm_field_organism.public_av_return_replication_execution.shift_receptor_time_sequences", return_value=("stage-two",)),
            patch("mcm_field_organism.public_av_return_replication_execution._permuted_stage_two_sequences", return_value=("permuted",)),
            patch("mcm_field_organism.public_av_return_replication_execution._steps", return_value=("step",)),
            patch("mcm_field_organism.public_av_return_replication_execution._fresh_field", return_value=FakeField("fresh")),
            patch("mcm_field_organism.public_av_return_replication_execution.run_neutral_asynchronous_field", side_effect=fake_run),
            patch("mcm_field_organism.public_av_return_replication_execution._advance_contact_free", side_effect=fake_gap),
            patch("mcm_field_organism.public_av_return_replication_execution.intervene_shared_field_component", side_effect=fake_intervention),
        ):
            return execute_public_av_return_replication(
                MEDIA,
                self.contract,
                self.wiring,
                self.preflight,
                self.permutation,
            )

    def test_execution_returns_all_six_technical_arm_results(self) -> None:
        result = self.execute_with_stubs()
        by_id = {arm.arm_id: arm for arm in result.arms}
        self.assertEqual(6, len(result.arms))
        self.assertEqual(0, by_id["control.stage_two_sequence_withheld"].stage_two_source_event_count)
        self.assertEqual("withheld_contact_free", by_id["control.stage_two_sequence_withheld"].stage_two_contact_mode)
        self.assertEqual("permuted_reduced_sequence", by_id["control.stage_two_order_permuted"].stage_two_contact_mode)
        self.assertIn(
            "reset_afterimage_preserve_activation",
            by_id["control.activation_only_carry"].intervention_audit_id,
        )
        self.assertIn(
            "reset_activation_preserve_afterimage",
            by_id["control.afterimage_only_carry"].intervention_audit_id,
        )

    def test_pairwise_matrices_are_six_by_six_and_claims_remain_blocked(self) -> None:
        result = self.execute_with_stubs()
        self.assertEqual(6, len(result.pairwise_activation_linf))
        self.assertTrue(all(len(row) == 6 for row in result.pairwise_activation_linf))
        self.assertEqual(6, len(result.pairwise_afterimage_linf))
        self.assertFalse(result.memory_claim_allowed)
        self.assertFalse(result.organization_claim_allowed)
        with self.assertRaisesRegex(PublicAVReturnReplicationExecutionError, "cannot retain"):
            replace(result, memory_claim_allowed=True)

    def test_positive_preflight_and_contract_identity_are_required(self) -> None:
        blocked = replace(self.preflight, single_bounded_replication_run_release_granted=False, source_audit_accepted=False)
        with self.assertRaisesRegex(PublicAVReturnReplicationExecutionError, "not released"):
            execute_public_av_return_replication(MEDIA, self.contract, self.wiring, blocked, self.permutation)
        altered_wiring = replace(self.wiring, permutation_contract_digest="0" * 64)
        with self.assertRaisesRegex(PublicAVReturnReplicationExecutionError, "digest differs"):
            execute_public_av_return_replication(MEDIA, self.contract, altered_wiring, self.preflight, self.permutation)

    def test_bound_executor_matches_one_shot_entrypoint_signature(self) -> None:
        executor = bind_public_av_return_replication_executor(self.preflight, self.permutation)
        with patch.object(
            __import__(
                "mcm_field_organism.public_av_return_replication_execution",
                fromlist=["execute_public_av_return_replication"],
            ),
            "execute_public_av_return_replication",
            return_value="ok",
        ):
            self.assertEqual("ok", executor(MEDIA, self.contract, self.wiring))

    def test_public_roles_exclude_payloads_and_claim_scores(self) -> None:
        forbidden = {"samples", "pixels", "label", "reward", "memory_score", "organization_score", "field_state"}
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_execution_public_roles()))


if __name__ == "__main__":
    unittest.main()
