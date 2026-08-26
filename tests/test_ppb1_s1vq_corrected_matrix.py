from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._ppb1_s1vn_matrix import (
    S1VN_BASELINE_IDS,
    S1VN_FAMILY_IDS,
    prepare_s1vn_matrix_runner,
    s1vn_config,
    s1vn_matrix_plan,
)
from mcm_field_organism._ppb1_s1vq_corrected_matrix import (
    S1VQ_EXPECTED_BASELINE_CALLS,
    S1VQ_EXPECTED_CASE_COUNT,
    S1VQ_EXPECTED_PPB_CALLS,
    S1VQ_EXPECTED_TOTAL_CALLS,
    S1VQ_MATRIX_EXECUTION_BLOCKED,
    S1VQ_PARENT_PLAN_DIGEST,
    S1VQ_REPEAT_FIXTURE_IDS,
    S1VQBaselineCarry,
    S1VQMatrixError,
    advance_s1vq_baseline,
    execute_s1vq_corrected_matrix,
    initial_s1vq_baseline_carry,
    prepare_s1vq_corrected_runner,
    run_s1vq_miniature_contract,
    s1vq_corrected_matrix_plan,
)
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]


def frames(config, values=(0.2, 0.2, 0.8)) -> tuple[ReceptorContactFrame, ...]:
    return tuple(
        ReceptorContactFrame(
            config.modality_id,
            config.geometry_id,
            f"s1vq.contract.{config.modality_id}.{index:02d}",
            f"s1vq.contract.{config.modality_id}.clock",
            index - 1,
            index,
            config.carrier_ids,
            (value,) * len(config.carrier_ids),
        )
        for index, value in enumerate(values, start=1)
    )


class PPB1S1VQCorrectedMatrixTests(unittest.TestCase):
    def test_parent_plan_and_digest_remain_bit_equal(self) -> None:
        self.assertEqual(S1VQ_PARENT_PLAN_DIGEST, prepare_s1vn_matrix_runner().plan_digest)
        self.assertEqual(384, len(s1vn_matrix_plan()))

    def test_corrected_plan_has_exact_528_unique_paths(self) -> None:
        plan = s1vq_corrected_matrix_plan()
        self.assertEqual(S1VQ_EXPECTED_CASE_COUNT, len(plan))
        self.assertEqual(len(plan), len({path.path_id for path in plan}))
        self.assertEqual(384, sum(path.repeat_id == "R0" for path in plan))
        self.assertEqual(144, sum(path.repeat_id == "R1" for path in plan))

    def test_every_parent_has_r0_and_only_repeat_fixtures_have_r1(self) -> None:
        plan = s1vq_corrected_matrix_plan()
        by_parent = {}
        for path in plan:
            by_parent.setdefault(path.parent_path_id, []).append(path)
        self.assertEqual(384, len(by_parent))
        for paths in by_parent.values():
            self.assertEqual("R0", paths[0].repeat_id)
            if paths[0].fixture_id in S1VQ_REPEAT_FIXTURE_IDS:
                self.assertEqual(("R0", "R1"), tuple(item.repeat_id for item in paths))
            else:
                self.assertEqual(("R0",), tuple(item.repeat_id for item in paths))

    def test_each_r1_is_immediately_after_its_r0(self) -> None:
        plan = s1vq_corrected_matrix_plan()
        for index, path in enumerate(plan):
            if path.repeat_id == "R1":
                previous = plan[index - 1]
                self.assertEqual("R0", previous.repeat_id)
                self.assertEqual(path.parent_path_id, previous.parent_path_id)
                self.assertEqual(path.expected_call_count, previous.expected_call_count)
                self.assertEqual(path.config_digest, previous.config_digest)

    def test_corrected_budget_is_exact_and_zero_is_executed(self) -> None:
        receipt = prepare_s1vq_corrected_runner()
        self.assertEqual(S1VQ_EXPECTED_PPB_CALLS, receipt.ppb_call_count)
        self.assertEqual(S1VQ_EXPECTED_BASELINE_CALLS, receipt.baseline_call_count)
        self.assertEqual(S1VQ_EXPECTED_TOTAL_CALLS, receipt.total_call_count)
        self.assertEqual(0, receipt.accepted_call_count)
        self.assertFalse(receipt.execution_authorized)

    def test_corrected_plan_digest_is_canonical_and_deterministic(self) -> None:
        first = prepare_s1vq_corrected_runner()
        second = prepare_s1vq_corrected_runner()
        self.assertEqual(first, second)
        self.assertEqual(64, len(first.corrected_plan_digest))
        self.assertNotEqual(first.parent_plan_digest, first.corrected_plan_digest)

    def test_b01_match_and_write_identities_are_separate(self) -> None:
        config = s1vn_config("P0", "auditory")
        carry = initial_s1vq_baseline_carry("B01", config)
        vector = (0.2,) * len(config.carrier_ids)
        first = advance_s1vq_baseline("B01", config, carry, vector)
        second = advance_s1vq_baseline("B01", config, first.postcarry, vector)
        self.assertIsNone(first.readout.selected_entry_id)
        self.assertEqual("b01.slot.000.g000001", first.readout.written_entry_id)
        self.assertEqual("b01.slot.000.g000001", second.readout.selected_entry_id)
        self.assertEqual("b01.slot.001.g000001", second.readout.written_entry_id)

    def test_b01_ring_reuse_increments_generation(self) -> None:
        config = s1vn_config("P0", "visual")
        carry = initial_s1vq_baseline_carry("B01", config)
        for index in range(config.capacity + 1):
            vector = (0.1 + 0.1 * index,) * len(config.carrier_ids)
            result = advance_s1vq_baseline("B01", config, carry, vector)
            carry = result.postcarry
        self.assertEqual("b01.slot.000.g000002", result.readout.written_entry_id)
        self.assertIn("b01.slot.000.g000002", carry.entry_ids)
        self.assertNotIn("b01.slot.000.g000001", carry.entry_ids)

    def test_b03_fixed_identity_is_never_rewritten_on_match(self) -> None:
        config = s1vn_config("P0", "auditory")
        carry = initial_s1vq_baseline_carry("B03", config)
        vector = (0.2,) * len(config.carrier_ids)
        first = advance_s1vq_baseline("B03", config, carry, vector)
        second = advance_s1vq_baseline("B03", config, first.postcarry, vector)
        self.assertEqual("b03.slot.000.g000001", first.readout.written_entry_id)
        self.assertEqual("b03.slot.000.g000001", second.readout.selected_entry_id)
        self.assertIsNone(second.readout.written_entry_id)

    def test_single_state_adapters_use_exact_bound_identity(self) -> None:
        config = s1vn_config("P0", "auditory")
        expected = {
            "B02": "b02.window.000",
            "B04": "b04.trace.000",
            "B05": "b05.trace.000",
            "B06": "b06.trace.000",
        }
        vector = (0.2,) * len(config.carrier_ids)
        for adapter_id, identity in expected.items():
            carry = initial_s1vq_baseline_carry(adapter_id, config)
            first = advance_s1vq_baseline(adapter_id, config, carry, vector)
            second = advance_s1vq_baseline(adapter_id, config, first.postcarry, vector)
            self.assertEqual(identity, first.readout.written_entry_id)
            self.assertEqual(identity, second.readout.selected_entry_id)
            self.assertEqual(identity, second.readout.written_entry_id)

    def test_b07_remains_state_and_identity_free(self) -> None:
        config = s1vn_config("P0", "auditory")
        carry = initial_s1vq_baseline_carry("B07", config)
        result = advance_s1vq_baseline(
            "B07", config, carry, (0.2,) * len(config.carrier_ids)
        )
        self.assertEqual((), result.postcarry.entry_ids)
        self.assertIsNone(result.readout.selected_entry_id)
        self.assertIsNone(result.readout.written_entry_id)
        self.assertEqual(0, result.readout.active_identity_count)

    def test_invalid_identity_alignment_fails_closed(self) -> None:
        config = s1vn_config("P0", "auditory")
        carry = initial_s1vq_baseline_carry("B01", config)
        with self.assertRaises(S1VQMatrixError):
            replace(carry, entry_ids=("b01.slot.000.g000001",))

    def test_miniature_r0_r1_receipts_are_bit_equal_without_path_id(self) -> None:
        config = s1vn_config("P0", "auditory")
        fixture = frames(config)
        for family_id in ("PPB1",) + S1VN_BASELINE_IDS:
            r0 = run_s1vq_miniature_contract(family_id, config, fixture, "R0")
            r1 = run_s1vq_miniature_contract(family_id, config, fixture, "R1")
            self.assertNotEqual(r0.path.path_id, r1.path.path_id)
            self.assertEqual(r0.repeat_comparison_digest(), r1.repeat_comparison_digest())

    def test_miniature_contract_rejects_registered_frames(self) -> None:
        config = s1vn_config("P0", "auditory")
        bad = tuple(
            replace(frame, snapshot_id=frame.snapshot_id.replace("s1vq", "s1vn"))
            for frame in frames(config)
        )
        with self.assertRaises(S1VQMatrixError):
            run_s1vq_miniature_contract("PPB1", config, bad)

    def test_corrected_matrix_execution_is_unconditionally_blocked(self) -> None:
        with self.assertRaises(S1VQMatrixError) as caught:
            execute_s1vq_corrected_matrix()
        self.assertEqual(S1VQ_MATRIX_EXECUTION_BLOCKED, caught.exception.code)

    def test_corrected_roles_remain_private_and_snapshot_free(self) -> None:
        names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        names |= {item.name for item in fields(SharedMCMFieldSnapshot)}
        for name in (
            "s1vq_corrected_matrix_plan",
            "prepare_s1vq_corrected_runner",
            "execute_s1vq_corrected_matrix",
        ):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertNotIn(name, names)

    def test_corrected_module_imports_no_field_or_media_runtime(self) -> None:
        source = (
            ROOT / "mcm_field_organism" / "_ppb1_s1vq_corrected_matrix.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "shared_mcm_field",
            "public_av_receptor_run",
            "live_audio_video_field",
            "neutral_local_field_substrate",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
