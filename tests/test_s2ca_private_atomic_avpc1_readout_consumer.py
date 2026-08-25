from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import unittest
from unittest.mock import patch

from mcm_field_organism import current_api
from mcm_field_organism._avpc1_atomic_readout_consumer import (
    AVPC1_ATOMIC_READOUT_INVALID_INPUT,
    AVPC1_ATOMIC_READOUT_RELATION_FAILURE,
    AVPC1_ATOMIC_READOUT_RELATION_RESULT_MISMATCH,
    AVPC1_ATOMIC_READOUT_SOURCE_MISMATCH,
    AVPC1_ATOMIC_READOUT_VISUAL_RESOLUTION_FAILURE,
    AVPC1AtomicReadoutConsumerError,
    consume_avpc1_auditory_cued_visual_readout,
)
from mcm_field_organism._avpc1_audio_only_probe_envelope import (
    bind_avpc1_private_auditory_only_probe_envelope,
    bind_avpc1_private_auditory_probe_source,
)
from mcm_field_organism._avpc1_bounded_relation import (
    AVPC1_RELATION_CONTENT_MISMATCH,
    AVPC1BoundedRelationError,
    advance_avpc1_bounded_relation_state,
    probe_avpc1_bounded_relation_read_only,
)
from mcm_field_organism._avpc1_visual_prototype_resolver import (
    AVPC1ReadOnlyVisualPrototypeState,
    AVPC1_VISUAL_RESOLVER_CONTENT_MISMATCH,
    AVPC1VisualPrototypeResolverError,
    _digest as _visual_resolver_digest,
    resolve_avpc1_visual_prototype_state,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    bind_ppb1_receptor_profile,
)
from mcm_field_organism._ppb1_s1wu_read_only_perceptual_probe import (
    probe_s1wu_perceptual_state,
)
from mcm_field_organism.browser_receptor_bridge import (
    BrowserReceptorSequenceBatch,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from tests.test_s2bq_private_avpc1_bounded_relation import (
    _Fixture,
    _advance_all,
    _parameters,
    _sequence,
    _timed,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE = "mcm_field_organism._avpc1_atomic_readout_consumer"


def _inputs(fixture: _Fixture, state, value: float):
    field_start = fixture.partition.max_relation_field_window_end_tick + 10
    auditory = _timed(
        fixture.profile.auditory_config,
        token="consumer.later.probe",
        source_start=100,
        field_start=field_start,
        value=value,
    )
    visual = _timed(
        fixture.profile.visual_config,
        token="consumer.later.parent",
        source_start=100,
        field_start=field_start + 10,
        value=0.25,
    )
    auditory_sequence = _sequence(auditory)
    batch = BrowserReceptorSequenceBatch(
        fixture.contract.contract_id,
        fixture.contract.digest(),
        (auditory_sequence, _sequence(visual)),
    )
    source = bind_avpc1_private_auditory_probe_source(
        fixture.contract,
        batch,
    )
    envelope = bind_avpc1_private_auditory_only_probe_envelope(
        "binding.synthetic.consumer.audio-only.v1",
        source,
        auditory_sequence,
        fixture.profile,
        fixture.auditory_state,
        fixture.partition,
    )
    finding = probe_s1wu_perceptual_state(
        fixture.profile.auditory_config,
        fixture.auditory_state,
        auditory.frame,
        "probe.synthetic.consumer.auditory",
    )
    return envelope, finding


def _consume(fixture: _Fixture, state, value: float = -0.5):
    envelope, finding = _inputs(fixture, state, value)
    outcome = consume_avpc1_auditory_cued_visual_readout(
        "consumer.synthetic.avpc1.v1",
        "probe.synthetic.consumer.relation",
        "resolver.synthetic.consumer.visual",
        envelope,
        finding,
        state,
        fixture.visual_state,
        fixture.profile,
    )
    return outcome, envelope, finding


def _forge_visual_state(
    state: AVPC1ReadOnlyVisualPrototypeState,
    **updates,
) -> AVPC1ReadOnlyVisualPrototypeState:
    payload = state.payload_without_digest()
    for key, value in updates.items():
        payload[key] = (
            list(value)
            if key in {"carrier_ids", "prototype_values"}
            else value
        )
    return replace(
        state,
        **updates,
        resolved_state_digest=_visual_resolver_digest(payload),
    )


class S2CAPrivateAtomicAVPC1ReadoutConsumerTests(unittest.TestCase):
    def test_match_calls_both_children_once_and_returns_exact_visual_state(self) -> None:
        fixture = _Fixture(((-0.5, 0.5), (-0.5, 0.5)))
        state, _ = _advance_all(fixture, fixture.state("consumer.match.table"))
        with (
            patch(
                f"{MODULE}.probe_avpc1_bounded_relation_read_only",
                wraps=probe_avpc1_bounded_relation_read_only,
            ) as relation_spy,
            patch(
                f"{MODULE}.resolve_avpc1_visual_prototype_state",
                wraps=resolve_avpc1_visual_prototype_state,
            ) as resolver_spy,
        ):
            outcome, _, _ = _consume(fixture, state)
        self.assertEqual(1, relation_spy.call_count)
        self.assertEqual(1, resolver_spy.call_count)
        self.assertEqual("MATCH", outcome.result_role)
        self.assertIsNotNone(outcome.visual_prototype_state)
        self.assertEqual(
            outcome.relation_finding.visual_prototype_identity_digest,
            outcome.visual_prototype_state.visual_prototype_identity_digest,
        )
        expected = next(
            slot
            for slot in fixture.visual_state.slots
            if slot.slot_id == outcome.visual_prototype_state.visual_prototype_slot_id
        )
        self.assertEqual(expected.prototype_values, outcome.visual_prototype_state.prototype_values)
        self.assertEqual(expected.support_count, outcome.visual_prototype_state.support_count)

    def test_no_match_returns_complete_negative_with_zero_resolver_calls(self) -> None:
        fixture = _Fixture(((-0.5, 0.5),))
        state = fixture.state("consumer.pending.table")
        state = advance_avpc1_bounded_relation_state(
            "transition.consumer.pending.1",
            state,
            fixture.receipt(0, state),
        ).state
        with patch(
            f"{MODULE}.resolve_avpc1_visual_prototype_state",
            wraps=resolve_avpc1_visual_prototype_state,
        ) as resolver_spy:
            outcome, _, _ = _consume(fixture, state)
        self.assertEqual("NO_MATCH", outcome.result_role)
        self.assertIsNone(outcome.visual_prototype_state)
        self.assertEqual(0, resolver_spy.call_count)

    def test_conflict_returns_complete_negative_with_zero_resolver_calls(self) -> None:
        fixture = _Fixture(((-0.5, -0.5), (-0.5, 0.5)))
        state, _ = _advance_all(fixture, fixture.state("consumer.conflict.table"))
        with patch(
            f"{MODULE}.resolve_avpc1_visual_prototype_state",
            wraps=resolve_avpc1_visual_prototype_state,
        ) as resolver_spy:
            outcome, _, _ = _consume(fixture, state)
        self.assertEqual("NO_MATCH_CONFLICT", outcome.result_role)
        self.assertIsNone(outcome.visual_prototype_state)
        self.assertEqual(0, resolver_spy.call_count)

    def test_invalid_or_source_mismatched_input_calls_no_child(self) -> None:
        fixture = _Fixture(((-0.5, 0.5), (-0.5, 0.5)))
        state, _ = _advance_all(fixture, fixture.state("consumer.invalid.table"))
        envelope, finding = _inputs(fixture, state, -0.5)
        controlled = bind_ppb1_receptor_profile("controlled", _parameters())
        cases = (
            (object(), fixture.profile, AVPC1_ATOMIC_READOUT_INVALID_INPUT),
            (envelope, controlled, AVPC1_ATOMIC_READOUT_SOURCE_MISMATCH),
        )
        for supplied_envelope, profile, error_code in cases:
            with self.subTest(error_code=error_code), patch(
                f"{MODULE}.probe_avpc1_bounded_relation_read_only"
            ) as relation_spy, patch(
                f"{MODULE}.resolve_avpc1_visual_prototype_state"
            ) as resolver_spy:
                with self.assertRaises(AVPC1AtomicReadoutConsumerError) as caught:
                    consume_avpc1_auditory_cued_visual_readout(
                        "consumer.synthetic.avpc1.v1",
                        "probe.synthetic.consumer.relation",
                        "resolver.synthetic.consumer.visual",
                        supplied_envelope,
                        finding,
                        state,
                        fixture.visual_state,
                        profile,
                    )
                self.assertEqual(error_code, caught.exception.code)
                self.assertEqual(0, relation_spy.call_count)
                self.assertEqual(0, resolver_spy.call_count)

    def test_relation_failure_returns_no_outcome_and_calls_no_resolver(self) -> None:
        fixture = _Fixture(((-0.5, 0.5), (-0.5, 0.5)))
        state, _ = _advance_all(fixture, fixture.state("consumer.relation-fail.table"))
        envelope, finding = _inputs(fixture, state, -0.5)
        with patch(
            f"{MODULE}.probe_avpc1_bounded_relation_read_only",
            side_effect=AVPC1BoundedRelationError(
                AVPC1_RELATION_CONTENT_MISMATCH,
                "injected relation failure",
            ),
        ) as relation_spy, patch(
            f"{MODULE}.resolve_avpc1_visual_prototype_state"
        ) as resolver_spy:
            with self.assertRaises(AVPC1AtomicReadoutConsumerError) as caught:
                consume_avpc1_auditory_cued_visual_readout(
                    "consumer.synthetic.avpc1.v1",
                    "probe.synthetic.consumer.relation",
                    "resolver.synthetic.consumer.visual",
                    envelope,
                    finding,
                    state,
                    fixture.visual_state,
                    fixture.profile,
                )
        self.assertEqual(AVPC1_ATOMIC_READOUT_RELATION_FAILURE, caught.exception.code)
        self.assertEqual(1, relation_spy.call_count)
        self.assertEqual(0, resolver_spy.call_count)

    def test_visual_failure_after_match_returns_no_outcome(self) -> None:
        fixture = _Fixture(((-0.5, 0.5), (-0.5, 0.5)))
        state, _ = _advance_all(fixture, fixture.state("consumer.visual-fail.table"))
        envelope, finding = _inputs(fixture, state, -0.5)
        with patch(
            f"{MODULE}.probe_avpc1_bounded_relation_read_only",
            wraps=probe_avpc1_bounded_relation_read_only,
        ) as relation_spy, patch(
            f"{MODULE}.resolve_avpc1_visual_prototype_state",
            side_effect=AVPC1VisualPrototypeResolverError(
                AVPC1_VISUAL_RESOLVER_CONTENT_MISMATCH,
                "injected visual failure",
            ),
        ) as resolver_spy:
            with self.assertRaises(AVPC1AtomicReadoutConsumerError) as caught:
                consume_avpc1_auditory_cued_visual_readout(
                    "consumer.synthetic.avpc1.v1",
                    "probe.synthetic.consumer.relation",
                    "resolver.synthetic.consumer.visual",
                    envelope,
                    finding,
                    state,
                    fixture.visual_state,
                    fixture.profile,
                )
        self.assertEqual(
            AVPC1_ATOMIC_READOUT_VISUAL_RESOLUTION_FAILURE,
            caught.exception.code,
        )
        self.assertEqual(1, relation_spy.call_count)
        self.assertEqual(1, resolver_spy.call_count)

    def test_substituted_child_outputs_fail_closed(self) -> None:
        fixture = _Fixture(((-0.5, 0.5), (-0.5, 0.5)))
        state, _ = _advance_all(fixture, fixture.state("consumer.substitute.table"))
        envelope, finding = _inputs(fixture, state, -0.5)
        foreign_relation = probe_avpc1_bounded_relation_read_only(
            "probe.synthetic.consumer.foreign",
            envelope,
            finding,
            state,
            fixture.visual_state,
            fixture.profile,
        )
        with patch(
            f"{MODULE}.probe_avpc1_bounded_relation_read_only",
            return_value=foreign_relation,
        ), patch(f"{MODULE}.resolve_avpc1_visual_prototype_state") as resolver_spy:
            with self.assertRaises(AVPC1AtomicReadoutConsumerError) as caught:
                consume_avpc1_auditory_cued_visual_readout(
                    "consumer.synthetic.avpc1.v1",
                    "probe.synthetic.consumer.relation",
                    "resolver.synthetic.consumer.visual",
                    envelope,
                    finding,
                    state,
                    fixture.visual_state,
                    fixture.profile,
                )
        self.assertEqual(
            AVPC1_ATOMIC_READOUT_RELATION_RESULT_MISMATCH,
            caught.exception.code,
        )
        self.assertEqual(0, resolver_spy.call_count)

        relation = probe_avpc1_bounded_relation_read_only(
            "probe.synthetic.consumer.relation",
            envelope,
            finding,
            state,
            fixture.visual_state,
            fixture.profile,
        )
        foreign_visual = resolve_avpc1_visual_prototype_state(
            "resolver.synthetic.consumer.foreign",
            relation,
            state,
            fixture.profile,
            fixture.visual_state,
        )
        with patch(
            f"{MODULE}.resolve_avpc1_visual_prototype_state",
            return_value=foreign_visual,
        ):
            with self.assertRaises(AVPC1AtomicReadoutConsumerError) as caught:
                consume_avpc1_auditory_cued_visual_readout(
                    "consumer.synthetic.avpc1.v1",
                    "probe.synthetic.consumer.relation",
                    "resolver.synthetic.consumer.visual",
                    envelope,
                    finding,
                    state,
                    fixture.visual_state,
                    fixture.profile,
                )
        self.assertEqual(
            AVPC1_ATOMIC_READOUT_VISUAL_RESOLUTION_FAILURE,
            caught.exception.code,
        )

    def test_digest_consistent_visual_source_substitutions_fail_closed(self) -> None:
        fixture = _Fixture(((-0.5, 0.5), (-0.5, 0.5)))
        state, _ = _advance_all(fixture, fixture.state("consumer.forged-visual.table"))
        envelope, finding = _inputs(fixture, state, -0.5)
        relation = probe_avpc1_bounded_relation_read_only(
            "probe.synthetic.consumer.relation",
            envelope,
            finding,
            state,
            fixture.visual_state,
            fixture.profile,
        )
        visual = resolve_avpc1_visual_prototype_state(
            "resolver.synthetic.consumer.visual",
            relation,
            state,
            fixture.profile,
            fixture.visual_state,
        )
        other_slot = next(
            slot
            for slot in fixture.visual_state.slots
            if slot.slot_id != visual.visual_prototype_slot_id
        )
        for role, forged in (
            (
                "config",
                _forge_visual_state(
                    visual,
                    visual_bank_config_digest="0" * 64,
                ),
            ),
            (
                "geometry",
                _forge_visual_state(
                    visual,
                    geometry_id="foreign.visual.geometry",
                ),
            ),
            (
                "carriers",
                _forge_visual_state(
                    visual,
                    carrier_ids=tuple(
                        f"foreign.visual.carrier.{index}"
                        for index in range(len(visual.carrier_ids))
                    ),
                ),
            ),
            (
                "slot",
                _forge_visual_state(
                    visual,
                    visual_prototype_slot_id=other_slot.slot_id,
                ),
            ),
            (
                "support",
                _forge_visual_state(
                    visual,
                    support_count=visual.support_count + 1,
                ),
            ),
        ):
            with self.subTest(role=role), patch(
                f"{MODULE}.resolve_avpc1_visual_prototype_state",
                return_value=forged,
            ):
                with self.assertRaises(AVPC1AtomicReadoutConsumerError) as caught:
                    consume_avpc1_auditory_cued_visual_readout(
                        "consumer.synthetic.avpc1.v1",
                        "probe.synthetic.consumer.relation",
                        "resolver.synthetic.consumer.visual",
                        envelope,
                        finding,
                        state,
                        fixture.visual_state,
                        fixture.profile,
                    )
                self.assertEqual(
                    AVPC1_ATOMIC_READOUT_VISUAL_RESOLUTION_FAILURE,
                    caught.exception.code,
                )

    def test_all_inputs_remain_unchanged_and_outcome_is_frozen(self) -> None:
        fixture = _Fixture(((-0.5, 0.5), (-0.5, 0.5)))
        state, _ = _advance_all(fixture, fixture.state("consumer.immutable.table"))
        envelope, finding = _inputs(fixture, state, -0.5)
        before = (
            envelope.envelope_digest,
            finding.finding_digest,
            state.state_digest,
            state.relation_history_partition_digest,
            fixture.visual_state.digest(),
            fixture.profile.digest(),
        )
        outcome = consume_avpc1_auditory_cued_visual_readout(
            "consumer.synthetic.avpc1.v1",
            "probe.synthetic.consumer.relation",
            "resolver.synthetic.consumer.visual",
            envelope,
            finding,
            state,
            fixture.visual_state,
            fixture.profile,
        )
        self.assertEqual(before, (
            envelope.envelope_digest,
            finding.finding_digest,
            state.state_digest,
            state.relation_history_partition_digest,
            fixture.visual_state.digest(),
            fixture.profile.digest(),
        ))
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            outcome.result_role = "NO_MATCH"  # type: ignore[misc]

    def test_private_module_has_no_state_public_field_or_filesystem_path(self) -> None:
        source = (
            ROOT / "mcm_field_organism" / "_avpc1_atomic_readout_consumer.py"
        ).read_text(encoding="ascii")
        for forbidden in (
            "advance_ppb1_bank",
            "advance_s1wq_perceptual_state",
            "advance_avpc1_bounded_relation_state",
            "SharedMCMField",
            "MCMNeuronDrive",
            "current_api",
            "root_lazy_exports",
            "live_audio",
            "live_video",
            "open(",
        ):
            self.assertNotIn(forbidden, source)
        public_names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        self.assertFalse(any("avpc1" in name.lower() for name in public_names))


if __name__ == "__main__":
    unittest.main()
