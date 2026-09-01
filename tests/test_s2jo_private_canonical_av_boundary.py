from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from pathlib import Path
import struct
import unittest

from tools import _s2jo_private_canonical_av_boundary as boundary


def _assert_no_bytes(test: unittest.TestCase, value: object, path: str = "root") -> None:
    if isinstance(value, bytes):
        test.fail(f"raw bytes retained at {path}")
    if is_dataclass(value):
        for item in fields(value):
            _assert_no_bytes(test, getattr(value, item.name), f"{path}.{item.name}")
    elif isinstance(value, (tuple, list)):
        for index, item in enumerate(value):
            _assert_no_bytes(test, item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            _assert_no_bytes(test, item, f"{path}.{key}")


class S2JOCanonicalAVBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reference_a = boundary.run_s2jo_simulation_reference("reference-a")
        cls.reference_b = boundary.run_s2jo_simulation_reference("reference-b")
        cls.pixel_changed = boundary.run_s2jo_simulation_reference(
            "pixel-changed",
            pixel_mutation=(0, 0, 0, 0, 17),
        )
        cls.sample_changed = boundary.run_s2jo_simulation_reference(
            "sample-changed",
            sample_mutation=(10, 0, 0.25),
        )

    def test_01_exact_episode_inventory_and_receptor_outputs(self) -> None:
        reduction = self.reference_a.reduction
        roles = tuple(item.role for item in reduction.episode_receipt.bindings)
        self.assertEqual(boundary.S2JO_FRAME_COUNT, roles.count("VISUAL_FRAME"))
        self.assertEqual(boundary.S2JO_HOP_COUNT, roles.count("AUDIO_HOP"))
        self.assertEqual(6, len(reduction.visual_states))
        self.assertEqual(11, len(reduction.auditory_states))
        self.assertEqual(288, len(reduction.visual_states[0].channel_values))
        self.assertEqual(48, len(reduction.auditory_states[0].energy))
        self.assertEqual(
            boundary.S2JO_DURATION_TICKS,
            reduction.episode_receipt.bindings[-1].window_end_tick,
        )

    def test_02_streaming_and_resource_budget(self) -> None:
        ledger = self.reference_a.reduction.ledger
        self.assertEqual(37_324_800, ledger.visual_payload_bytes)
        self.assertEqual(38_400, ledger.audio_payload_bytes)
        self.assertEqual(37_363_200, ledger.raw_payload_bytes)
        self.assertLessEqual(ledger.max_live_visual_frames, 1)
        self.assertLessEqual(ledger.max_live_audio_hops, 1)
        self.assertLessEqual(ledger.max_live_payloads, 1)
        self.assertEqual(55, ledger.operation_count)
        self.assertFalse(ledger.raw_payloads_retained)
        stream = boundary.iter_s2jo_simulation_episode()
        self.assertIs(iter(stream), stream)

    def test_03_provenance_is_separate_from_functional_results(self) -> None:
        first = self.reference_a
        second = self.reference_b
        self.assertNotEqual(
            first.visual_provenance.provenance_digest,
            second.visual_provenance.provenance_digest,
        )
        self.assertNotEqual(
            first.audio_provenance.provenance_digest,
            second.audio_provenance.provenance_digest,
        )
        self.assertEqual(
            first.reduction.episode_receipt.functional_episode_digest,
            second.reduction.episode_receipt.functional_episode_digest,
        )
        self.assertEqual(
            first.reduction.reduced_receipt.reduced_sequence_digest,
            second.reduction.reduced_receipt.reduced_sequence_digest,
        )
        self.assertEqual(first.reduction.visual_states, second.reduction.visual_states)
        self.assertEqual(
            first.reduction.auditory_states,
            second.reduction.auditory_states,
        )

    def test_04_one_changed_pixel_remains_distinguishable(self) -> None:
        original = self.reference_a.reduction
        changed = self.pixel_changed.reduction
        self.assertNotEqual(
            original.episode_receipt.bindings[0].payload_digest,
            changed.episode_receipt.bindings[0].payload_digest,
        )
        self.assertNotEqual(
            original.visual_states[0].channel_values,
            changed.visual_states[0].channel_values,
        )
        self.assertNotEqual(
            original.reduced_receipt.reduced_sequence_digest,
            changed.reduced_receipt.reduced_sequence_digest,
        )

    def test_05_one_changed_sample_remains_distinguishable(self) -> None:
        original = self.reference_a.reduction
        changed = self.sample_changed.reduction
        original_audio = tuple(
            item.payload_digest
            for item in original.episode_receipt.bindings
            if item.role == "AUDIO_HOP"
        )
        changed_audio = tuple(
            item.payload_digest
            for item in changed.episode_receipt.bindings
            if item.role == "AUDIO_HOP"
        )
        self.assertNotEqual(original_audio[10], changed_audio[10])
        self.assertNotEqual(
            original.auditory_states,
            changed.auditory_states,
        )
        self.assertNotEqual(
            original.reduced_receipt.reduced_sequence_digest,
            changed.reduced_receipt.reduced_sequence_digest,
        )

    def test_06_wrong_visual_and_audio_forms_fail_closed(self) -> None:
        visual = boundary.build_s2jo_visual_frame(0)
        with self.assertRaises(boundary.S2JOCanonicalBoundaryError) as visual_error:
            replace(visual, shape=(1079, 1920, 3))
        self.assertEqual("S2JO_INVALID_VISUAL_FORM", visual_error.exception.code)

        invalid_pcm = struct.pack("<480f", float("nan"), *([0.0] * 479))
        with self.assertRaises(boundary.S2JOCanonicalBoundaryError) as audio_error:
            boundary.CanonicalPCMAudioHopV1.build(
                episode_id=boundary.S2JO_EPISODE_ID,
                hop_index=0,
                clock_id=boundary.S2JO_CLOCK_ID,
                window_start_tick=0,
                window_end_tick=10_000_000,
                pcm_bytes=invalid_pcm,
            )
        self.assertEqual("S2JO_INVALID_AUDIO_VALUE", audio_error.exception.code)

    def test_07_wrong_order_and_nonstreaming_input_fail_closed(self) -> None:
        def wrong_order():
            yield boundary.build_s2jo_audio_hop(1)

        with self.assertRaises(boundary.S2JOCanonicalBoundaryError) as order_error:
            boundary.reduce_canonical_av_stream(wrong_order())
        self.assertEqual("S2JO_SEQUENCE_MISMATCH", order_error.exception.code)

        with self.assertRaises(boundary.S2JOCanonicalBoundaryError) as stream_error:
            boundary.reduce_canonical_av_stream([])
        self.assertEqual("S2JO_STREAM_REQUIRED", stream_error.exception.code)

    def test_08_wrong_time_and_incomplete_inventory_fail_closed(self) -> None:
        def wrong_time():
            yield boundary.build_s2jo_visual_frame(0, window=(0, 33_333_334))

        with self.assertRaises(boundary.S2JOCanonicalBoundaryError) as time_error:
            boundary.reduce_canonical_av_stream(wrong_time())
        self.assertEqual("S2JO_TIME_MISMATCH", time_error.exception.code)

        def incomplete():
            yield boundary.build_s2jo_visual_frame(0)

        with self.assertRaises(boundary.S2JOCanonicalBoundaryError) as count_error:
            boundary.reduce_canonical_av_stream(incomplete())
        self.assertEqual("S2JO_INVENTORY_MISMATCH", count_error.exception.code)

    def test_09_metadata_coupling_and_bad_provenance_fail_closed(self) -> None:
        visual = boundary.build_s2jo_visual_frame(0)
        coupled = self.reference_a.visual_provenance.provenance_digest
        with self.assertRaises(boundary.S2JOCanonicalBoundaryError) as digest_error:
            replace(visual, functional_input_digest=coupled)
        self.assertEqual(
            "S2JO_FUNCTIONAL_DIGEST_MISMATCH",
            digest_error.exception.code,
        )

        provenance = self.reference_a.visual_provenance
        with self.assertRaises(boundary.S2JOCanonicalBoundaryError) as source_error:
            replace(provenance, source_class="DOM_DOCUMENT")
        self.assertEqual("S2JO_INVALID_PROVENANCE", source_error.exception.code)

    def test_10_results_receipts_and_states_retain_no_raw_payload(self) -> None:
        _assert_no_bytes(self, self.reference_a)
        result_fields = {
            item.name for item in fields(boundary.SimulationReferenceResultV1)
        }
        self.assertNotIn("pixel_bytes", result_fields)
        self.assertNotIn("pcm_bytes", result_fields)
        receipt_payload = self.reference_a.reduction.episode_receipt.canonical_payload()
        self.assertNotIn("pixel_bytes", repr(receipt_payload))
        self.assertNotIn("pcm_bytes", repr(receipt_payload))

    def test_11_functional_digests_and_reduced_types_are_source_neutral(self) -> None:
        episode_payload = self.reference_a.reduction.episode_receipt.canonical_payload()
        reduced_payload = self.reference_a.reduction.reduced_receipt.canonical_payload()
        forbidden = ("source_class", "provenance", "url", "dom", "label", "reward")
        encoded = repr((episode_payload, reduced_payload)).lower()
        for role in forbidden:
            self.assertNotIn(role, encoded)
        for state in (
            *self.reference_a.reduction.visual_states,
            *self.reference_a.reduction.auditory_states,
        ):
            for role in forbidden:
                self.assertNotIn(role, repr(state).lower())
        with self.assertRaises(FrozenInstanceError):
            self.reference_a.visual_provenance.source_class = "VIDEO_DECODE"  # type: ignore[misc]

    def test_12_module_has_no_memory_context_or_field_dependency(self) -> None:
        path = Path(boundary.__file__).resolve()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        project_imports = tuple(
            name for name in imported if name.startswith("mcm_field_organism")
        )
        self.assertEqual(
            {
                "mcm_field_organism.broadband_hearing_path",
                "mcm_field_organism.finite_video_path",
                "mcm_field_organism.log_spectral_receptor",
                "mcm_field_organism.receptor_contract",
            },
            set(project_imports),
        )
        for name in project_imports:
            module_role = name.removeprefix("mcm_field_organism.")
            self.assertNotIn("memory", module_role)
            self.assertNotIn("context", module_role)
            self.assertNotIn("field", module_role)
            self.assertNotIn("ppb", module_role)
            self.assertNotIn("tspm", module_role)


if __name__ == "__main__":
    unittest.main()
