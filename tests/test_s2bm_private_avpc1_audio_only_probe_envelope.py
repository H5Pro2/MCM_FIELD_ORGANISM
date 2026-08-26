from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import unittest

from mcm_field_organism import current_api
from mcm_field_organism._avpc1_audio_only_probe_envelope import (
    AVPC1_AUDIO_ONLY_INPUT_MISMATCH,
    AVPC1_AUDIO_ONLY_PROFILE_OR_CONFIG_MISMATCH,
    AVPC1_AUDIO_ONLY_SOURCE_MISMATCH,
    AVPC1_AUDIO_ONLY_TIME_OR_PARTITION_MISMATCH,
    AVPC1AudioOnlyProbeEnvelopeError,
    bind_avpc1_frozen_relation_history_partition,
    bind_avpc1_private_auditory_only_probe_envelope,
    bind_avpc1_private_auditory_probe_source,
)
from mcm_field_organism._ppb1_active_receptor_batch_binding import (
    bind_ppb1_active_receptor_batch,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from mcm_field_organism._ppb1_reference import (
    PPB1BankState,
    PPB1PrototypeSlot,
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


def _parameters() -> PPB1ProfileParameters:
    return PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
        PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
    )


def _contract() -> BrowserWorldContract:
    return BrowserWorldContract(
        "synthetic.avpc1.world.v1",
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
    *,
    phase: str,
    source_start: int,
    field_start: int,
    value: float,
    count: int = 1,
) -> ReceptorTimeSequence:
    frames = tuple(
        OrganismTimedReceptorFrame(
            ReceptorContactFrame(
                config.modality_id,
                config.geometry_id,
                f"synthetic.{phase}.{config.modality_id}.{index}",
                f"source.{config.modality_id}",
                source_start + index * 10,
                source_start + (index + 1) * 10,
                config.carrier_ids,
                tuple(value for _ in config.carrier_ids),
            ),
            CommonFieldTime(
                "field.synthetic",
                field_start + index * 10,
                field_start + (index + 1) * 10,
            ),
        )
        for index in range(count)
    )
    return ReceptorTimeSequence(
        config.modality_id,
        config.geometry_id,
        "field.synthetic",
        frames,
    )


def _batch(contract, auditory, visual) -> BrowserReceptorSequenceBatch:
    return BrowserReceptorSequenceBatch(
        contract.contract_id,
        contract.digest(),
        (auditory, visual),
    )


def _state(config) -> PPB1BankState:
    slots = (
        PPB1PrototypeSlot(
            f"{config.bank_id}.slot.000",
            True,
            tuple(0.0 for _ in config.carrier_ids),
            3,
            3,
        ),
        *(
            PPB1PrototypeSlot.free(f"{config.bank_id}.slot.{index:03d}")
            for index in range(1, config.capacity)
        ),
    )
    return PPB1BankState(
        config.bank_id,
        config.digest(),
        3,
        "source.auditory",
        30,
        slots,
    )


def _fixture(*, probe_source_start: int = 30, probe_field_start: int = 40):
    contract = _contract()
    profile = bind_ppb1_receptor_profile("browser", _parameters())
    relation_audio = _sequence(
        profile.auditory_config,
        phase="relation",
        source_start=0,
        field_start=0,
        value=0.0,
    )
    relation_visual = _sequence(
        profile.visual_config,
        phase="relation",
        source_start=0,
        field_start=10,
        value=0.0,
    )
    relation_envelope = bind_ppb1_active_receptor_batch(
        "binding.synthetic.relation.v1",
        contract,
        _batch(contract, relation_audio, relation_visual),
        profile,
    )
    partition = bind_avpc1_frozen_relation_history_partition(
        (
            ("auditory", relation_envelope.auditory_stream.timed_frames[0]),
            ("visual", relation_envelope.visual_stream.timed_frames[0]),
        )
    )
    probe_audio = _sequence(
        profile.auditory_config,
        phase="probe",
        source_start=probe_source_start,
        field_start=probe_field_start,
        value=0.0,
    )
    probe_visual = _sequence(
        profile.visual_config,
        phase="probe.parent",
        source_start=30,
        field_start=50,
        value=0.25,
    )
    probe_batch = _batch(contract, probe_audio, probe_visual)
    source = bind_avpc1_private_auditory_probe_source(contract, probe_batch)
    state = _state(profile.auditory_config)
    return (
        contract,
        profile,
        partition,
        probe_audio,
        probe_visual,
        probe_batch,
        source,
        state,
    )


class S2BMPrivateAVPC1AudioOnlyProbeEnvelopeTests(unittest.TestCase):
    def test_valid_source_partition_and_envelope_are_digest_bound(self) -> None:
        values = _fixture()
        before = (
            values[0].digest(),
            values[5].digest(),
            values[1].digest(),
            values[7].digest(),
        )
        envelope = bind_avpc1_private_auditory_only_probe_envelope(
            "binding.synthetic.audio-only.v1",
            values[6],
            values[3],
            values[1],
            values[7],
            values[2],
        )
        self.assertEqual(1, envelope.auditory_input_count)
        self.assertEqual(0, envelope.visual_input_count)
        self.assertEqual(64, len(envelope.envelope_digest))
        self.assertIs(
            values[3].frames[0],
            envelope.timed_frame_binding.timed_frame,
        )
        self.assertEqual(
            before,
            (
                values[0].digest(),
                values[5].digest(),
                values[1].digest(),
                values[7].digest(),
            ),
        )

    def test_source_binding_is_independent_of_parent_visual_content(self) -> None:
        values = _fixture()
        changed_visual = _sequence(
            values[1].visual_config,
            phase="probe.parent",
            source_start=30,
            field_start=50,
            value=-0.5,
        )
        changed_batch = _batch(values[0], values[3], changed_visual)
        changed = bind_avpc1_private_auditory_probe_source(values[0], changed_batch)
        self.assertNotEqual(values[5].digest(), changed_batch.digest())
        self.assertEqual(values[6].canonical_payload(), changed.canonical_payload())

    def test_outputs_are_frozen(self) -> None:
        values = _fixture()
        envelope = bind_avpc1_private_auditory_only_probe_envelope(
            "binding.synthetic.audio-only.v1",
            values[6],
            values[3],
            values[1],
            values[7],
            values[2],
        )
        for output in (values[6], values[2], envelope):
            with self.assertRaises((FrozenInstanceError, AttributeError)):
                output.schema_version = "changed"  # type: ignore[misc]

    def test_zero_or_multiple_auditory_probe_frames_fail_closed(self) -> None:
        values = _fixture()
        multiple = _sequence(
            values[1].auditory_config,
            phase="probe.multiple",
            source_start=30,
            field_start=40,
            value=0.0,
            count=2,
        )
        batch = _batch(values[0], multiple, values[4])
        with self.assertRaises(AVPC1AudioOnlyProbeEnvelopeError) as caught:
            bind_avpc1_private_auditory_probe_source(values[0], batch)
        self.assertEqual(AVPC1_AUDIO_ONLY_INPUT_MISMATCH, caught.exception.code)

    def test_source_sequence_substitution_fails_closed(self) -> None:
        values = _fixture()
        changed = _sequence(
            values[1].auditory_config,
            phase="probe.changed",
            source_start=30,
            field_start=40,
            value=0.5,
        )
        with self.assertRaises(AVPC1AudioOnlyProbeEnvelopeError) as caught:
            bind_avpc1_private_auditory_only_probe_envelope(
                "binding.synthetic.audio-only.v1",
                values[6],
                changed,
                values[1],
                values[7],
                values[2],
            )
        self.assertEqual(AVPC1_AUDIO_ONLY_SOURCE_MISMATCH, caught.exception.code)

    def test_wrong_profile_or_state_fails_closed(self) -> None:
        values = _fixture()
        controlled = bind_ppb1_receptor_profile("controlled", _parameters())
        with self.assertRaises(AVPC1AudioOnlyProbeEnvelopeError) as caught:
            bind_avpc1_private_auditory_only_probe_envelope(
                "binding.synthetic.audio-only.v1",
                values[6],
                values[3],
                controlled,
                values[7],
                values[2],
            )
        self.assertEqual(
            AVPC1_AUDIO_ONLY_PROFILE_OR_CONFIG_MISMATCH,
            caught.exception.code,
        )
        wrong_state = replace(values[7], config_digest="0" * 64)
        with self.assertRaises(AVPC1AudioOnlyProbeEnvelopeError) as caught:
            bind_avpc1_private_auditory_only_probe_envelope(
                "binding.synthetic.audio-only.v1",
                values[6],
                values[3],
                values[1],
                wrong_state,
                values[2],
            )
        self.assertEqual(
            AVPC1_AUDIO_ONLY_PROFILE_OR_CONFIG_MISMATCH,
            caught.exception.code,
        )

    def test_source_and_field_time_violations_fail_closed(self) -> None:
        for fixture in (
            _fixture(probe_source_start=20),
            _fixture(probe_field_start=10),
        ):
            with self.assertRaises(AVPC1AudioOnlyProbeEnvelopeError) as caught:
                bind_avpc1_private_auditory_only_probe_envelope(
                    "binding.synthetic.audio-only.v1",
                    fixture[6],
                    fixture[3],
                    fixture[1],
                    fixture[7],
                    fixture[2],
                )
            self.assertEqual(
                AVPC1_AUDIO_ONLY_TIME_OR_PARTITION_MISMATCH,
                caught.exception.code,
            )

    def test_private_module_has_no_probe_field_or_public_path(self) -> None:
        source = (
            ROOT / "mcm_field_organism" / "_avpc1_audio_only_probe_envelope.py"
        ).read_text(encoding="ascii")
        for forbidden in (
            "advance_ppb1_bank",
            "probe_s1wu_perceptual_state",
            "SharedMCMField",
            "current_api",
            "root_lazy_exports",
            "live_audio",
            "live_video",
        ):
            self.assertNotIn(forbidden, source)
        public_names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        self.assertFalse(any("avpc1" in name.lower() for name in public_names))


if __name__ == "__main__":
    unittest.main()
