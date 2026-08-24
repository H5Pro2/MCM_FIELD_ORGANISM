from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import unittest

from mcm_field_organism import current_api
from mcm_field_organism._ppb1_active_receptor_batch_binding import (
    PPB1_ACTIVE_BATCH_CONTRACT_SOURCE_MISMATCH,
    PPB1_ACTIVE_BATCH_INPUT_MISMATCH,
    PPB1_ACTIVE_BATCH_PROVENANCE_MISMATCH,
    PPB1_ACTIVE_BATCH_SOURCE_CLOCK_CHANGED,
    PPB1ActiveReceptorBatchBindingError,
    bind_ppb1_active_receptor_batch,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
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


def parameters() -> PPB1ProfileParameters:
    return PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
        PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
    )


def world_contract(
    *,
    contract_id: str = "synthetic.browser.world.v1",
) -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id=contract_id,
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=100.0,
        phases=(
            BrowserWorldPhase("rest.before", 10, "static", 0.0),
            BrowserWorldPhase("change", 10, "moving", 0.2),
            BrowserWorldPhase("rest.after", 10, "static", 0.0),
        ),
    )


def sequence_for(
    config,
    *,
    source_clocks: tuple[str, str] | None = None,
    source_windows: tuple[tuple[int, int], tuple[int, int]] = ((0, 10), (5, 20)),
) -> ReceptorTimeSequence:
    clocks = source_clocks or (
        f"source.{config.modality_id}",
        f"source.{config.modality_id}",
    )
    frames = tuple(
        OrganismTimedReceptorFrame(
            ReceptorContactFrame(
                config.modality_id,
                config.geometry_id,
                f"synthetic.{config.modality_id}.{index}",
                clocks[index],
                source_windows[index][0],
                source_windows[index][1],
                config.carrier_ids,
                tuple(
                    (index + carrier) / 100.0
                    for carrier in range(len(config.carrier_ids))
                ),
            ),
            CommonFieldTime("field.synthetic", index * 10, (index + 1) * 10),
        )
        for index in range(2)
    )
    return ReceptorTimeSequence(
        config.modality_id,
        config.geometry_id,
        "field.synthetic",
        frames,
    )


def fixture(
    *,
    auditory_source_clocks: tuple[str, str] | None = None,
    auditory_source_windows: tuple[
        tuple[int, int], tuple[int, int]
    ] = ((0, 10), (5, 20)),
):
    contract = world_contract()
    profile = bind_ppb1_receptor_profile("browser", parameters())
    auditory = sequence_for(
        profile.auditory_config,
        source_clocks=auditory_source_clocks,
        source_windows=auditory_source_windows,
    )
    visual = sequence_for(profile.visual_config)
    batch = BrowserReceptorSequenceBatch(
        contract.contract_id,
        contract.digest(),
        (auditory, visual),
    )
    return contract, batch, profile


class S2ALPrivateActiveReceptorBatchBindingTests(unittest.TestCase):
    def test_valid_binding_is_complete_digest_bound_and_read_only(self) -> None:
        contract, batch, profile = fixture()
        before = (contract.digest(), batch.digest(), profile.digest())

        envelope = bind_ppb1_active_receptor_batch(
            "binding.synthetic.v1", contract, batch, profile
        )

        self.assertEqual(64, len(envelope.envelope_digest))
        self.assertEqual(
            (2, 2),
            (
                envelope.auditory_stream.frame_count,
                envelope.visual_stream.frame_count,
            ),
        )
        self.assertEqual("source.auditory", envelope.auditory_stream.source_clock_id)
        self.assertEqual("source.visual", envelope.visual_stream.source_clock_id)
        self.assertEqual("field.synthetic", envelope.common_field_clock_id)
        self.assertEqual(before, (contract.digest(), batch.digest(), profile.digest()))
        self.assertIs(
            batch.sequences[0].frames[0],
            envelope.auditory_stream.timed_frames[0].timed_frame,
        )

    def test_output_records_are_frozen(self) -> None:
        contract, batch, profile = fixture()
        envelope = bind_ppb1_active_receptor_batch(
            "binding.synthetic.v1", contract, batch, profile
        )
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            envelope.binding_id = "changed"  # type: ignore[misc]
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            envelope.auditory_stream.source_clock_id = "changed"  # type: ignore[misc]

    def test_contract_id_and_digest_mismatch_fail_closed(self) -> None:
        contract, batch, profile = fixture()
        wrong_id = world_contract(contract_id="synthetic.other.world.v1")
        with self.assertRaises(PPB1ActiveReceptorBatchBindingError) as caught:
            bind_ppb1_active_receptor_batch(
                "binding.synthetic.v1", wrong_id, batch, profile
            )
        self.assertEqual(
            PPB1_ACTIVE_BATCH_CONTRACT_SOURCE_MISMATCH,
            caught.exception.code,
        )

        changed = replace(contract, tone_frequency_hz=101.0)
        with self.assertRaises(PPB1ActiveReceptorBatchBindingError) as caught:
            bind_ppb1_active_receptor_batch(
                "binding.synthetic.v1", changed, batch, profile
            )
        self.assertEqual(
            PPB1_ACTIVE_BATCH_CONTRACT_SOURCE_MISMATCH,
            caught.exception.code,
        )

    def test_nonbrowser_profile_and_geometry_mismatch_fail_closed(self) -> None:
        contract, batch, browser = fixture()
        controlled = bind_ppb1_receptor_profile("controlled", parameters())
        with self.assertRaises(PPB1ActiveReceptorBatchBindingError) as caught:
            bind_ppb1_active_receptor_batch(
                "binding.synthetic.v1", contract, batch, controlled
            )
        self.assertEqual(PPB1_ACTIVE_BATCH_PROVENANCE_MISMATCH, caught.exception.code)

        auditory = batch.sequences[0]
        wrong_geometry = "synthetic.wrong.geometry"
        changed_frames = tuple(
            replace(item, frame=replace(item.frame, geometry_id=wrong_geometry))
            for item in auditory.frames
        )
        changed_auditory = ReceptorTimeSequence(
            auditory.modality_id,
            wrong_geometry,
            auditory.clock_id,
            changed_frames,
        )
        changed_batch = BrowserReceptorSequenceBatch(
            batch.contract_id,
            batch.contract_digest,
            (changed_auditory, batch.sequences[1]),
        )
        with self.assertRaises(PPB1ActiveReceptorBatchBindingError) as caught:
            bind_ppb1_active_receptor_batch(
                "binding.synthetic.v1", contract, changed_batch, browser
            )
        self.assertEqual(PPB1_ACTIVE_BATCH_INPUT_MISMATCH, caught.exception.code)

    def test_source_clock_change_within_modality_fails_closed(self) -> None:
        contract, batch, profile = fixture(
            auditory_source_clocks=("source.auditory", "source.auditory.changed")
        )
        with self.assertRaises(PPB1ActiveReceptorBatchBindingError) as caught:
            bind_ppb1_active_receptor_batch(
                "binding.synthetic.v1", contract, batch, profile
            )
        self.assertEqual(PPB1_ACTIVE_BATCH_SOURCE_CLOCK_CHANGED, caught.exception.code)

    def test_nonadvancing_source_window_end_fails_closed(self) -> None:
        contract, batch, profile = fixture(
            auditory_source_windows=((0, 10), (0, 9))
        )
        with self.assertRaises(PPB1ActiveReceptorBatchBindingError) as caught:
            bind_ppb1_active_receptor_batch(
                "binding.synthetic.v1", contract, batch, profile
            )
        self.assertEqual(PPB1_ACTIVE_BATCH_INPUT_MISMATCH, caught.exception.code)

    def test_private_module_has_no_state_probe_field_or_public_export(self) -> None:
        source = (
            ROOT
            / "mcm_field_organism"
            / "_ppb1_active_receptor_batch_binding.py"
        ).read_text(encoding="ascii")
        for forbidden in (
            "advance_ppb1_bank",
            "probe_s1wu_perceptual_state",
            "SharedMCMField",
            "current_api",
            "root_lazy_exports",
            "open(",
        ):
            self.assertNotIn(forbidden, source)
        public_names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        self.assertFalse(
            any("active_receptor_batch" in name.lower() for name in public_names)
        )


if __name__ == "__main__":
    unittest.main()
