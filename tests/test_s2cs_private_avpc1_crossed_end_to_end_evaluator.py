from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import unittest
from unittest.mock import patch

from mcm_field_organism import current_api
from mcm_field_organism import _avpc1_crossed_end_to_end_evaluator as evaluator
from mcm_field_organism._avpc1_audio_only_probe_envelope import (
    bind_avpc1_frozen_relation_history_partition,
    bind_avpc1_private_auditory_only_probe_envelope,
    bind_avpc1_private_auditory_probe_source,
)
from mcm_field_organism._ppb1_active_batch_formation_consumer import (
    prepare_ppb1_active_batch_formation_consumer_owner,
)
from mcm_field_organism._ppb1_active_receptor_batch_binding import (
    bind_ppb1_active_receptor_batch,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from mcm_field_organism._ppb1_reference import initial_ppb1_bank_state
from mcm_field_organism._ppb1_s1wu_read_only_perceptual_probe import (
    probe_s1wu_perceptual_state,
)
from mcm_field_organism.browser_receptor_bridge import BrowserReceptorSequenceBatch
from mcm_field_organism.browser_world_contract import (
    BrowserWorldContract,
    BrowserWorldPhase,
)
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS


ROOT = Path(__file__).resolve().parents[1]
MODULE = "mcm_field_organism._avpc1_crossed_end_to_end_evaluator"


def _parameters() -> PPB1ProfileParameters:
    return PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
        PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
    )


def _contract() -> BrowserWorldContract:
    return BrowserWorldContract(
        "synthetic.s2cs.browser.world.v1",
        1,
        1,
        1,
        100.0,
        (
            BrowserWorldPhase("rest.before", 10, "static", 0.0),
            BrowserWorldPhase("change", 10, "moving", 0.2),
            BrowserWorldPhase("rest.after", 10, "static", 0.0),
        ),
    )


def _sequence(
    config,
    values: tuple[float, ...],
    *,
    token: str,
    source_base: int,
    field_base: int,
    field_step: int = 20,
) -> ReceptorTimeSequence:
    frames = tuple(
        OrganismTimedReceptorFrame(
            ReceptorContactFrame(
                config.modality_id,
                config.geometry_id,
                f"synthetic.{token}.{config.modality_id}.{index}",
                f"source.{config.modality_id}",
                source_base + index * 10,
                source_base + (index + 1) * 10,
                config.carrier_ids,
                tuple(value for _ in config.carrier_ids),
            ),
            CommonFieldTime(
                "field.synthetic",
                field_base + index * field_step,
                field_base + index * field_step + 10,
            ),
        )
        for index, value in enumerate(values)
    )
    return ReceptorTimeSequence(
        config.modality_id,
        config.geometry_id,
        "field.synthetic",
        frames,
    )


def _envelope(contract, profile, binding_id, auditory, visual):
    return bind_ppb1_active_receptor_batch(
        binding_id,
        contract,
        BrowserReceptorSequenceBatch(
            contract.contract_id,
            contract.digest(),
            (auditory, visual),
        ),
        profile,
    )


class _Fixture:
    def __init__(self, *, ambiguous_left: bool = False) -> None:
        self.contract = _contract()
        self.profile = bind_ppb1_receptor_profile("browser", _parameters())
        auditory_formation = _sequence(
            self.profile.auditory_config,
            (-0.5, -0.5, -0.5, 0.5, 0.5, 0.5),
            token="formation",
            source_base=0,
            field_base=0,
        )
        visual_formation = _sequence(
            self.profile.visual_config,
            (-0.5, -0.5, -0.5, 0.5, 0.5, 0.5),
            token="formation",
            source_base=0,
            field_base=0,
        )
        self.formation_envelope = _envelope(
            self.contract,
            self.profile,
            "binding.s2cs.formation.v1",
            auditory_formation,
            visual_formation,
        )
        self.auditory_fresh = initial_ppb1_bank_state(
            self.profile.auditory_config
        )
        self.visual_fresh = initial_ppb1_bank_state(self.profile.visual_config)
        self.histories = (
            self._history(
                "h-left",
                (-0.5, 0.5, -0.5, 0.5),
                (-0.5, 0.5, -0.5, 0.5),
                ambiguous=ambiguous_left,
            ),
            self._history(
                "h-right",
                (-0.5, 0.5, -0.5, 0.5),
                (0.5, -0.5, 0.5, -0.5),
            ),
        )
        self.source = evaluator.bind_avpc1_crossed_evaluation_input(
            "evaluation.s2cs.v1",
            self.formation_envelope,
            self.profile,
            self.auditory_fresh,
            self.visual_fresh,
            self.histories,
        )

    def _history(
        self,
        history_id: str,
        auditory_values: tuple[float, ...],
        visual_values: tuple[float, ...],
        *,
        ambiguous: bool = False,
    ) -> evaluator.AVPC1CrossedHistorySource:
        field_step = 10 if ambiguous else 20
        auditory = _sequence(
            self.profile.auditory_config,
            auditory_values,
            token=f"{history_id}.exposure",
            source_base=100,
            field_base=200,
            field_step=field_step,
        )
        visual = _sequence(
            self.profile.visual_config,
            visual_values,
            token=f"{history_id}.exposure",
            source_base=100,
            field_base=205 if ambiguous else 200,
            field_step=field_step,
        )
        envelope = _envelope(
            self.contract,
            self.profile,
            f"binding.s2cs.{history_id}.exposure.v1",
            auditory,
            visual,
        )
        partition_items = tuple(
            (modality, binding)
            for modality, stream in (
                ("auditory", envelope.auditory_stream),
                ("visual", envelope.visual_stream),
            )
            for binding in stream.timed_frames
        )
        partition = bind_avpc1_frozen_relation_history_partition(partition_items)
        pairs = tuple(
            zip(
                envelope.auditory_stream.timed_frames,
                envelope.visual_stream.timed_frames,
            )
        )
        probes = (
            self._probe(history_id, "a-key", -0.5, 300),
            self._probe(history_id, "b-control-key", 0.5, 320),
        )
        return evaluator.AVPC1CrossedHistorySource(
            history_id,
            envelope,
            partition,
            pairs,
            probes,
        )

    def _probe(
        self,
        history_id: str,
        role: str,
        value: float,
        field_start: int,
    ) -> evaluator.AVPC1CrossedProbeSource:
        auditory = _sequence(
            self.profile.auditory_config,
            (value,),
            token=f"{history_id}.{role}.later",
            source_base=200,
            field_base=field_start,
        )
        visual_parent = _sequence(
            self.profile.visual_config,
            (0.0,),
            token=f"{history_id}.{role}.parent",
            source_base=200,
            field_base=field_start + 20,
        )
        batch = BrowserReceptorSequenceBatch(
            self.contract.contract_id,
            self.contract.digest(),
            (auditory, visual_parent),
        )
        binding = bind_avpc1_private_auditory_probe_source(self.contract, batch)
        return evaluator.AVPC1CrossedProbeSource(role, binding, auditory)

    def owner(self):
        return evaluator.prepare_avpc1_crossed_evaluation_owner(
            "owner.s2cs.crossed.v1",
            self.source.input_digest,
        )

    def formation_result(self, token: str):
        owner = prepare_ppb1_active_batch_formation_consumer_owner(
            f"owner.s2cs.{token}.formation",
            f"authorization.s2cs.{token}.formation",
            f"consumption.s2cs.{token}.formation",
            self.formation_envelope.envelope_digest,
            self.profile.digest(),
            self.auditory_fresh.digest(),
            self.visual_fresh.digest(),
        )
        return owner.consume_once(
            self.formation_envelope,
            self.profile,
            self.auditory_fresh,
            self.visual_fresh,
        )


class S2CSPrivateAVPC1CrossedEndToEndEvaluatorTests(unittest.TestCase):
    def test_foreign_valid_initial_relation_is_rejected_before_relation_child(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner()
        original = evaluator.initial_avpc1_bounded_relation_state

        def foreign(table_id, profile, auditory, visual, partition):
            return original(
                f"{table_id}.foreign",
                profile,
                auditory,
                visual,
                partition,
            )

        with patch.object(
            evaluator,
            "initial_avpc1_bounded_relation_state",
            side_effect=foreign,
        ), patch.object(
            evaluator,
            "prepare_avpc1_atomic_relation_formation_consumer_owner",
        ) as relation:
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError):
                owner.consume_once(fixture.source)
        relation.assert_not_called()
        self.assertEqual("FAILED", owner.status)
        self.assertIsNone(owner.result_digest)

    def test_foreign_valid_audio_envelope_is_rejected_before_probe(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner()
        original = evaluator.bind_avpc1_private_auditory_only_probe_envelope

        def foreign(binding_id, source_binding, sequence, profile, state, partition):
            return original(
                f"{binding_id}.foreign",
                source_binding,
                sequence,
                profile,
                state,
                partition,
            )

        with patch.object(
            evaluator,
            "bind_avpc1_private_auditory_only_probe_envelope",
            side_effect=foreign,
        ), patch.object(
            evaluator,
            "probe_s1wu_perceptual_state",
        ) as probe:
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError):
                owner.consume_once(fixture.source)
        probe.assert_not_called()
        self.assertEqual("FAILED", owner.status)
        self.assertIsNone(owner.result_digest)

    def test_foreign_valid_auditory_finding_is_rejected_before_readout(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner()
        original = evaluator.probe_s1wu_perceptual_state

        def foreign(config, state, frame, probe_id):
            return original(config, state, frame, f"{probe_id}.foreign")

        with patch.object(
            evaluator,
            "probe_s1wu_perceptual_state",
            side_effect=foreign,
        ), patch.object(
            evaluator,
            "consume_avpc1_auditory_cued_visual_readout",
        ) as readout:
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError):
                owner.consume_once(fixture.source)
        readout.assert_not_called()
        self.assertEqual("FAILED", owner.status)
        self.assertIsNone(owner.result_digest)

    def test_foreign_valid_formation_child_is_rejected_before_first_track(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner()
        original = evaluator.prepare_ppb1_active_batch_formation_consumer_owner

        def foreign(*args):
            return original(
                "owner.s2cu.foreign.formation",
                "authorization.s2cu.foreign.formation",
                "consumption.s2cu.foreign.formation",
                *args[3:],
            )

        with patch.object(
            evaluator,
            "prepare_ppb1_active_batch_formation_consumer_owner",
            side_effect=foreign,
        ), patch.object(evaluator, "_run_track") as track:
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError):
                owner.consume_once(fixture.source)
        track.assert_not_called()
        self.assertEqual("FAILED", owner.status)
        self.assertIsNone(owner.result_digest)

    def test_foreign_valid_relation_pair_is_rejected_before_readout(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner()
        original = evaluator.prepare_avpc1_atomic_relation_formation_consumer_owner
        prepare_count = 0

        class ForeignPairOwner:
            def consume_once(
                self,
                formation,
                formation_envelope,
                later_envelope,
                profile,
                partition,
                auditory,
                visual,
                relation,
            ):
                foreign_auditory, foreign_visual = (
                    fixture.histories[0].ordered_pairs[2]
                )
                child = original(
                    "owner.s2cu.foreign.relation",
                    "consumption.s2cu.foreign.relation",
                    "probe.s2cu.foreign.auditory",
                    "probe.s2cu.foreign.visual",
                    "exposure.s2cu.foreign",
                    "transition.s2cu.foreign",
                    formation.formation_result_digest,
                    formation_envelope.envelope_digest,
                    later_envelope.envelope_digest,
                    profile.digest(),
                    partition.relation_history_partition_digest,
                    foreign_auditory.timed_frame_provenance_digest,
                    foreign_visual.timed_frame_provenance_digest,
                    relation.state_identity_digest,
                    relation.state_digest,
                )
                return child.consume_once(
                    formation,
                    formation_envelope,
                    later_envelope,
                    profile,
                    partition,
                    foreign_auditory,
                    foreign_visual,
                    relation,
                )

        def substitute(*args):
            nonlocal prepare_count
            prepare_count += 1
            return ForeignPairOwner() if prepare_count == 1 else original(*args)

        with patch.object(
            evaluator,
            "prepare_avpc1_atomic_relation_formation_consumer_owner",
            side_effect=substitute,
        ), patch.object(
            evaluator,
            "consume_avpc1_auditory_cued_visual_readout",
        ) as readout:
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError):
                owner.consume_once(fixture.source)
        readout.assert_not_called()
        self.assertEqual("FAILED", owner.status)
        self.assertIsNone(owner.result_digest)

    def test_foreign_valid_same_target_readout_is_rejected(self) -> None:
        fixture = _Fixture()
        foreign_formation = fixture.formation_result("foreign-readout")
        foreign_probe = fixture.histories[0].probes[0]
        foreign_envelope = bind_avpc1_private_auditory_only_probe_envelope(
            "binding.s2cu.foreign.audio-only.v1",
            foreign_probe.source_binding,
            foreign_probe.source_sequence,
            fixture.profile,
            foreign_formation.auditory_poststate,
            fixture.histories[0].relation_partition,
        )
        foreign_finding = probe_s1wu_perceptual_state(
            fixture.profile.auditory_config,
            foreign_formation.auditory_poststate,
            foreign_probe.source_sequence.frames[0].frame,
            "probe.s2cu.foreign.same-target",
        )
        owner = fixture.owner()
        original = evaluator.consume_avpc1_auditory_cued_visual_readout
        call_count = 0

        def substitute(
            consumer_id,
            relation_probe_id,
            visual_resolver_id,
            envelope,
            finding,
            relation,
            visual_state,
            profile,
        ):
            nonlocal call_count
            call_count += 1
            if call_count != 1:
                return original(
                    consumer_id,
                    relation_probe_id,
                    visual_resolver_id,
                    envelope,
                    finding,
                    relation,
                    visual_state,
                    profile,
                )
            return original(
                "consumer.s2cu.foreign.readout",
                "probe.s2cu.foreign.relation",
                "resolver.s2cu.foreign.visual",
                foreign_envelope,
                foreign_finding,
                relation,
                visual_state,
                profile,
            )

        with patch.object(
            evaluator,
            "consume_avpc1_auditory_cued_visual_readout",
            side_effect=substitute,
        ):
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError):
                owner.consume_once(fixture.source)
        self.assertEqual("FAILED", owner.status)
        self.assertIsNone(owner.result_digest)

    def test_valid_call_budget_is_exact(self) -> None:
        fixture = _Fixture()
        with patch.object(
            evaluator,
            "prepare_ppb1_active_batch_formation_consumer_owner",
            wraps=evaluator.prepare_ppb1_active_batch_formation_consumer_owner,
        ) as formation, patch.object(
            evaluator,
            "prepare_avpc1_atomic_relation_formation_consumer_owner",
            wraps=evaluator.prepare_avpc1_atomic_relation_formation_consumer_owner,
        ) as relation, patch.object(
            evaluator,
            "bind_avpc1_private_auditory_only_probe_envelope",
            wraps=evaluator.bind_avpc1_private_auditory_only_probe_envelope,
        ) as envelope, patch.object(
            evaluator,
            "consume_avpc1_auditory_cued_visual_readout",
            wraps=evaluator.consume_avpc1_auditory_cued_visual_readout,
        ) as readout:
            result = fixture.owner().consume_once(fixture.source)
        self.assertEqual(1, formation.call_count)
        self.assertEqual(16, relation.call_count)
        self.assertEqual(8, envelope.call_count)
        self.assertEqual(8, readout.call_count)
        self.assertEqual("FUNCTION_VALID_BASELINE_EXPLAINS", result.decision)

    def test_valid_crossed_evaluation_returns_expected_decision_and_cells(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner()
        result = owner.consume_once(fixture.source)
        self.assertEqual("FUNCTION_VALID_BASELINE_EXPLAINS", result.decision)
        self.assertEqual("CONSUMED", owner.status)
        self.assertEqual(4, len(result.tracks))
        candidate_left = result.tracks[0].readouts
        candidate_right = result.tracks[2].readouts
        self.assertNotEqual(
            candidate_left[0].visual_target_digest,
            candidate_right[0].visual_target_digest,
        )
        self.assertNotEqual(
            candidate_left[1].visual_target_digest,
            candidate_right[1].visual_target_digest,
        )

    def test_candidate_and_baseline_share_receipts_and_functional_projection(self) -> None:
        fixture = _Fixture()
        result = fixture.owner().consume_once(fixture.source)
        for offset in (0, 2):
            candidate, baseline = result.tracks[offset : offset + 2]
            self.assertEqual(
                candidate.exposure_receipt_digests,
                baseline.exposure_receipt_digests,
            )
            self.assertEqual(
                candidate.functional_payload(),
                baseline.functional_payload(),
            )
            self.assertNotEqual(
                candidate.relation_state_identity_digest,
                baseline.relation_state_identity_digest,
            )

    def test_exact_event_order_and_read_only_state_digests_are_bound(self) -> None:
        fixture = _Fixture()
        before = (
            fixture.auditory_fresh.digest(),
            fixture.visual_fresh.digest(),
            fixture.source.input_digest,
        )
        result = fixture.owner().consume_once(fixture.source)
        for track in result.tracks:
            self.assertEqual(
                evaluator._EXPECTED_EVENTS,
                tuple(item.event for item in track.transitions),
            )
            self.assertEqual(2, len(track.readouts))
            self.assertTrue(all(item.result_role == "MATCH" for item in track.readouts))
        self.assertEqual(
            before,
            (
                fixture.auditory_fresh.digest(),
                fixture.visual_fresh.digest(),
                fixture.source.input_digest,
            ),
        )

    def test_wrong_owner_source_stops_before_formation_child(self) -> None:
        fixture = _Fixture()
        owner = evaluator.prepare_avpc1_crossed_evaluation_owner(
            "owner.s2cs.wrong-source.v1",
            "0" * 64,
        )
        with patch.object(
            evaluator,
            "prepare_ppb1_active_batch_formation_consumer_owner",
        ) as prepare:
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError):
                owner.consume_once(fixture.source)
        prepare.assert_not_called()
        self.assertEqual("FAILED", owner.status)
        self.assertIsNone(owner.result_digest)

    def test_ambiguous_history_stops_before_readout_and_publishes_no_result(self) -> None:
        fixture = _Fixture(ambiguous_left=True)
        owner = fixture.owner()
        with patch.object(
            evaluator,
            "consume_avpc1_auditory_cued_visual_readout",
        ) as readout:
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError):
                owner.consume_once(fixture.source)
        readout.assert_not_called()
        self.assertEqual("FAILED", owner.status)
        self.assertIsNone(owner.result_digest)

    def test_child_exception_is_terminal_and_exposes_no_partial_result(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner()
        with patch.object(evaluator, "_run_track", side_effect=RuntimeError("stop")):
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError):
                owner.consume_once(fixture.source)
        self.assertEqual("FAILED", owner.status)
        self.assertEqual(1, owner.attempt_count)
        self.assertIsNone(owner.result_digest)

    def test_digest_consistent_unfair_baseline_projection_is_method_invalid(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner()
        original = evaluator._run_track

        def unfair(source, formation, history, role):
            result = original(source, formation, history, role)
            if role != "baseline":
                return result
            wrong = replace(
                result.readouts[0],
                visual_target_digest="f" * 64,
            )
            readouts = (wrong, result.readouts[1])
            payload = result.payload_without_digest()
            payload["readouts"] = [item.payload() for item in readouts]
            return replace(
                result,
                readouts=readouts,
                track_digest=evaluator._digest(payload),
            )

        with patch.object(evaluator, "_run_track", side_effect=unfair):
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError):
                owner.consume_once(fixture.source)
        self.assertEqual("FAILED", owner.status)
        self.assertIsNone(owner.result_digest)

    def test_terminal_owner_reuse_reaches_no_extra_formation_child(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner()
        owner.consume_once(fixture.source)
        with patch.object(
            evaluator,
            "prepare_ppb1_active_batch_formation_consumer_owner",
        ) as prepare:
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError) as caught:
                owner.consume_once(fixture.source)
        prepare.assert_not_called()
        self.assertEqual(
            evaluator.AVPC1_CROSSED_EVALUATION_OWNER_TERMINAL,
            caught.exception.code,
        )

    def test_recursive_retry_is_busy_then_outer_attempt_fails_once(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner()
        original = evaluator.prepare_ppb1_active_batch_formation_consumer_owner

        def recursive(*args, **kwargs):
            owner.consume_once(fixture.source)
            return original(*args, **kwargs)

        with patch.object(
            evaluator,
            "prepare_ppb1_active_batch_formation_consumer_owner",
            side_effect=recursive,
        ):
            with self.assertRaises(evaluator.AVPC1CrossedEvaluationError):
                owner.consume_once(fixture.source)
        self.assertEqual("FAILED", owner.status)
        self.assertEqual(1, owner.attempt_count)
        self.assertIsNone(owner.result_digest)

    def test_result_and_source_are_frozen_and_private_surface_is_unchanged(self) -> None:
        fixture = _Fixture()
        result = fixture.owner().consume_once(fixture.source)
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            result.decision = "TECHNICAL_FUNCTION_FAILED"  # type: ignore[misc]
        source = (ROOT / "mcm_field_organism" / (
            "_avpc1_crossed_end_to_end_evaluator.py"
        )).read_text(encoding="ascii")
        for forbidden in (
            "SharedMCMField",
            "MCMNeuronDrive",
            "current_api",
            "root_lazy_exports",
            "live_audio",
            "live_video",
            "open(",
        ):
            self.assertNotIn(forbidden, source)
        public_names = set(getattr(current_api, "__all__", ())) | set(
            ROOT_LAZY_EXPORTS
        )
        self.assertFalse(any("crossed_evaluation" in name for name in public_names))


if __name__ == "__main__":
    unittest.main()
