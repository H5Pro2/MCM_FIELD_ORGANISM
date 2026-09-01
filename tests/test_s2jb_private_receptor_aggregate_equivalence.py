"""One-shot 50-case qualification for the private S2-JB boundary."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import unittest

import numpy as np

from mcm_field_organism._ppb1_reference import PPB1BankConfig, initial_ppb1_bank_state
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.receptor_contract import from_visual_receptor_state
from tools import _s2jb_private_receptor_aggregate_equivalence as subject


QUALIFICATION_ID = "s2jc-aggregate-equivalence-qualification-20260901-01"
Q1_SUMS = (0, 1, 1599, 1600, 1601, 203199, 203200, 203201, 204799, 204800, 407999, 408000)
Q2_SUMS = (1600, 3200, 203200, 204800, 404800, 406400)
Q3_PAIRS = ((0, 1), (1, 0), (1599, 1600), (1600, 1599), (1600, 1601), (1601, 1600), (203199, 203200), (203200, 203199), (204799, 204800), (204800, 204799), (407999, 408000), (408000, 407999))
Q4_CASES = ((0, 2), (0, 31), (1, 2), (1, 31), (1600, 2), (1600, 31), (203201, 2), (203201, 31), (407999, 2), (407999, 31), (408000, 2), (408000, 31))


def _digest(label: str) -> str:
    encoded = json.dumps(
        {"neutral": label},
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _frame_for_sum(byte_sum: int, *, alternative: bool = False) -> np.ndarray:
    if isinstance(byte_sum, bool) or not isinstance(byte_sum, int) or not 0 <= byte_sum <= 408000:
        raise AssertionError("qualification byte sum differs")
    frame = np.zeros((80, 120, 3), dtype=np.uint8)
    quotient, remainder = divmod(byte_sum, 1600)
    values = np.full(1600, quotient, dtype=np.uint8)
    if remainder:
        values[:remainder] = quotient + 1
    if alternative:
        if remainder != 0 or not 1 <= quotient <= 254:
            raise AssertionError("alternative block requires an interior constant value")
        values[0] = quotient - 1
        values[1] = quotient + 1
    frame[:40, :40, 0] = values.reshape(40, 40)
    return frame


class S2JBAggregateEquivalenceQualification(unittest.TestCase):
    source_materializations = 0
    aggregate_code_formations = 0
    ppb_formation_steps = 0
    aggregate_comparisons = 0
    baseline_comparisons = 0
    lineage_validations = 0

    @classmethod
    def setUpClass(cls) -> None:
        cls.source_materializations = 0
        cls.aggregate_code_formations = 0
        cls.ppb_formation_steps = 0
        cls.aggregate_comparisons = 0
        cls.baseline_comparisons = 0
        cls.lineage_validations = 0
        cls.receptor = LocalChannelGridReceptor(VisualGridConfig(120, 80, 3, 2, 30.0))

    @classmethod
    def tearDownClass(cls) -> None:
        observed = {
            "source_materializations": cls.source_materializations,
            "aggregate_code_formations": cls.aggregate_code_formations,
            "ppb_formation_steps": cls.ppb_formation_steps,
            "aggregate_comparisons": cls.aggregate_comparisons,
            "diagnostic_baseline_comparisons": cls.baseline_comparisons,
            "validated_ppb_lineage_steps": cls.lineage_validations,
        }
        for role, value in observed.items():
            expected = subject.QUALIFICATION_LIMITS[role]
            if value != expected:
                raise AssertionError(f"{role} differs: {value} != {expected}")

    def _analyze(
        self,
        byte_sum: int,
        *,
        frame_index: int,
        alternative: bool = False,
    ):
        type(self).source_materializations += 1
        type(self).aggregate_code_formations += 1
        return subject.analyze_uint8_frame_with_aggregate_codes(
            _frame_for_sum(byte_sum, alternative=alternative),
            self.receptor,
            frame_index=frame_index,
        )

    def _compare_codes(self, first: object, second: object) -> str:
        type(self).aggregate_comparisons += 1
        return subject.aggregate_codes_equivalent(first, second)

    def _compare_lineage(self, lineage: object, codes: object) -> str:
        type(self).aggregate_comparisons += 1
        return subject.lineage_equivalent_to_codes(lineage, codes)

    def _baselines(
        self,
        first: tuple[float, ...],
        second: tuple[float, ...],
    ) -> tuple[bool, bool, bool]:
        type(self).baseline_comparisons += 3
        return subject.diagnostic_float_and_l1_baselines(first, second)

    def _config(self, suffix: str) -> PPB1BankConfig:
        return PPB1BankConfig(
            f"s2jb.visual.{suffix}",
            "visual",
            self.receptor.config.geometry_id,
            self.receptor.config.carrier_ids,
            4,
            0.01,
            0.05,
            3,
            64,
        )

    def _advance(self, config, state, receptor_state, codes, lineages):
        type(self).ppb_formation_steps += 1
        type(self).lineage_validations += 1
        return subject.advance_visual_ppb_with_aggregate_lineage(
            config,
            state,
            from_visual_receptor_state(receptor_state),
            codes,
            lineages,
        )

    def _run_q1(self, byte_sum: int) -> None:
        state, codes = self._analyze(byte_sum, frame_index=0)
        self.assertEqual(byte_sum, codes[0].byte_sum)
        self.assertEqual(subject.SAME_RECEPTOR_AGGREGATE, self._compare_codes(codes[0], codes[0]))
        self.assertEqual((True, True, True), self._baselines(state.channel_values, state.channel_values))

    def _run_q2(self, byte_sum: int) -> None:
        first_state, first_codes = self._analyze(byte_sum, frame_index=0)
        second_state, second_codes = self._analyze(byte_sum, frame_index=1, alternative=True)
        self.assertNotEqual(first_codes[0].raw_block_digest, second_codes[0].raw_block_digest)
        self.assertNotEqual(first_codes[0].evidence_digest, second_codes[0].evidence_digest)
        self.assertEqual(first_codes[0].aggregate_code_digest, second_codes[0].aggregate_code_digest)
        self.assertEqual(subject.SAME_RECEPTOR_AGGREGATE, self._compare_codes(first_codes[0], second_codes[0]))
        self.assertEqual((True, True, True), self._baselines(first_state.channel_values, second_state.channel_values))

    def _run_q3(self, first_sum: int, second_sum: int) -> None:
        first_state, first_codes = self._analyze(first_sum, frame_index=0)
        second_state, second_codes = self._analyze(second_sum, frame_index=1)
        self.assertEqual(1, abs(first_codes[0].byte_sum - second_codes[0].byte_sum))
        self.assertEqual(subject.DIFFERENT_RECEPTOR_AGGREGATE, self._compare_codes(first_codes[0], second_codes[0]))
        exact, native, functional = self._baselines(first_state.channel_values, second_state.channel_values)
        self.assertFalse(exact)
        self.assertTrue(native)
        self.assertTrue(functional)

    def _run_q4(self, byte_sum: int, updates: int) -> None:
        config = self._config(f"q4-{byte_sum}-{updates}")
        state = initial_ppb1_bank_state(config)
        lineages = ()
        for frame_index in range(updates + 1):
            receptor_state, codes = self._analyze(byte_sum, frame_index=frame_index)
            result, lineages = self._advance(config, state, receptor_state, codes, lineages)
            state = result.poststate
        probe_state, probe_codes = self._analyze(byte_sum, frame_index=updates + 100)
        self.assertEqual(1, len(lineages))
        lineage = lineages[0]
        self.assertEqual(min(3, updates + 1), lineage.final_support)
        self.assertEqual(subject.SAME_RECEPTOR_AGGREGATE, self._compare_lineage(lineage, probe_codes))
        exact, native, functional = self._baselines(
            result.readout.prototype_values,
            probe_state.channel_values,
        )
        self.assertIsInstance(exact, bool)
        self.assertTrue(native)
        self.assertTrue(functional)

    def _two_q5_sources(self, first_sum: int = 1600, second_sum: int = 1600):
        first = self._analyze(first_sum, frame_index=0)
        second = self._analyze(second_sum, frame_index=1)
        return first, second

    def _synthetic_lineage(self, codes, *, length: int) -> subject.PPBAggregateLineageV1:
        carrier_ids = tuple(item.carrier_id for item in codes)
        code_digests = tuple(item.aggregate_code_digest for item in codes)
        states = tuple(_digest(f"synthetic-state-{index}") for index in range(length + 1))
        return subject.PPBAggregateLineageV1.build(
            "s2jb.synthetic.lineage",
            "s2jb.synthetic.bank",
            "s2jb.synthetic.slot",
            _digest("synthetic-config"),
            carrier_ids,
            code_digests,
            tuple(_digest(f"synthetic-formation-{index}") for index in range(length)),
            tuple(_digest(f"synthetic-source-{index}") for index in range(length)),
            states[:-1],
            states[1:],
            tuple(min(3, index + 1) for index in range(length)),
            _digest("synthetic-prototype"),
        )

    def _q5_count(self, lineage_steps: int) -> None:
        type(self).aggregate_comparisons += 1
        type(self).lineage_validations += lineage_steps

    def test_001_q1_sum_0(self):
        self.assertEqual(1192, sum(value for key, value in subject.QUALIFICATION_LIMITS.items() if key not in {"cases", "logical_work_items"}))
        self._run_q1(Q1_SUMS[0])

    def test_002_q1_sum_1(self): self._run_q1(Q1_SUMS[1])
    def test_003_q1_sum_1599(self): self._run_q1(Q1_SUMS[2])
    def test_004_q1_sum_1600(self): self._run_q1(Q1_SUMS[3])
    def test_005_q1_sum_1601(self): self._run_q1(Q1_SUMS[4])
    def test_006_q1_sum_203199(self): self._run_q1(Q1_SUMS[5])
    def test_007_q1_sum_203200(self): self._run_q1(Q1_SUMS[6])
    def test_008_q1_sum_203201(self): self._run_q1(Q1_SUMS[7])
    def test_009_q1_sum_204799(self): self._run_q1(Q1_SUMS[8])
    def test_010_q1_sum_204800(self): self._run_q1(Q1_SUMS[9])
    def test_011_q1_sum_407999(self): self._run_q1(Q1_SUMS[10])
    def test_012_q1_sum_408000(self): self._run_q1(Q1_SUMS[11])

    def test_013_q2_sum_1600(self): self._run_q2(Q2_SUMS[0])
    def test_014_q2_sum_3200(self): self._run_q2(Q2_SUMS[1])
    def test_015_q2_sum_203200(self): self._run_q2(Q2_SUMS[2])
    def test_016_q2_sum_204800(self): self._run_q2(Q2_SUMS[3])
    def test_017_q2_sum_404800(self): self._run_q2(Q2_SUMS[4])
    def test_018_q2_sum_406400(self): self._run_q2(Q2_SUMS[5])

    def test_019_q3_0_to_1(self): self._run_q3(*Q3_PAIRS[0])
    def test_020_q3_1_to_0(self): self._run_q3(*Q3_PAIRS[1])
    def test_021_q3_1599_to_1600(self): self._run_q3(*Q3_PAIRS[2])
    def test_022_q3_1600_to_1599(self): self._run_q3(*Q3_PAIRS[3])
    def test_023_q3_1600_to_1601(self): self._run_q3(*Q3_PAIRS[4])
    def test_024_q3_1601_to_1600(self): self._run_q3(*Q3_PAIRS[5])
    def test_025_q3_203199_to_203200(self): self._run_q3(*Q3_PAIRS[6])
    def test_026_q3_203200_to_203199(self): self._run_q3(*Q3_PAIRS[7])
    def test_027_q3_204799_to_204800(self): self._run_q3(*Q3_PAIRS[8])
    def test_028_q3_204800_to_204799(self): self._run_q3(*Q3_PAIRS[9])
    def test_029_q3_407999_to_408000(self): self._run_q3(*Q3_PAIRS[10])
    def test_030_q3_408000_to_407999(self): self._run_q3(*Q3_PAIRS[11])

    def test_031_q4_sum_0_updates_2(self): self._run_q4(*Q4_CASES[0])
    def test_032_q4_sum_0_updates_31(self): self._run_q4(*Q4_CASES[1])
    def test_033_q4_sum_1_updates_2(self): self._run_q4(*Q4_CASES[2])
    def test_034_q4_sum_1_updates_31(self): self._run_q4(*Q4_CASES[3])
    def test_035_q4_sum_1600_updates_2(self): self._run_q4(*Q4_CASES[4])
    def test_036_q4_sum_1600_updates_31(self): self._run_q4(*Q4_CASES[5])
    def test_037_q4_sum_203201_updates_2(self): self._run_q4(*Q4_CASES[6])
    def test_038_q4_sum_203201_updates_31(self): self._run_q4(*Q4_CASES[7])
    def test_039_q4_sum_407999_updates_2(self): self._run_q4(*Q4_CASES[8])
    def test_040_q4_sum_407999_updates_31(self): self._run_q4(*Q4_CASES[9])
    def test_041_q4_sum_408000_updates_2(self): self._run_q4(*Q4_CASES[10])
    def test_042_q4_sum_408000_updates_31(self): self._run_q4(*Q4_CASES[11])

    def test_043_q5_mixed_1600_to_1601(self):
        config = self._config("q5-mixed-forward")
        state = initial_ppb1_bank_state(config)
        first, second = self._two_q5_sources(1600, 1601)
        result, lineages = self._advance(config, state, first[0], first[1], ())
        type(self).aggregate_comparisons += 1
        with self.assertRaisesRegex(subject.S2JBError, "mixed or missing"):
            self._advance(config, result.poststate, second[0], second[1], lineages)

    def test_044_q5_mixed_1601_to_1600(self):
        config = self._config("q5-mixed-reverse")
        state = initial_ppb1_bank_state(config)
        first, second = self._two_q5_sources(1601, 1600)
        result, lineages = self._advance(config, state, first[0], first[1], ())
        type(self).aggregate_comparisons += 1
        with self.assertRaisesRegex(subject.S2JBError, "mixed or missing"):
            self._advance(config, result.poststate, second[0], second[1], lineages)

    def test_045_q5_missing_formation_step(self):
        first, _ = self._two_q5_sources()
        lineage = self._synthetic_lineage(first[1], length=2)
        self._q5_count(2)
        with self.assertRaises(subject.S2JBError):
            replace(lineage, ordered_formation_receipt_digests=lineage.ordered_formation_receipt_digests[:1])

    def test_046_q5_duplicate_formation_step(self):
        first, _ = self._two_q5_sources()
        lineage = self._synthetic_lineage(first[1], length=2)
        self._q5_count(2)
        duplicate = (lineage.ordered_formation_receipt_digests[0],) * 2
        with self.assertRaises(subject.S2JBError):
            replace(lineage, ordered_formation_receipt_digests=duplicate)

    def test_047_q5_swapped_formation_order(self):
        first, _ = self._two_q5_sources()
        lineage = self._synthetic_lineage(first[1], length=3)
        self._q5_count(3)
        with self.assertRaises(subject.S2JBError):
            replace(lineage, ordered_prestate_digests=tuple(reversed(lineage.ordered_prestate_digests)))

    def test_048_q5_foreign_slot_or_config(self):
        first, _ = self._two_q5_sources()
        lineage = self._synthetic_lineage(first[1], length=3)
        self._q5_count(3)
        with self.assertRaises(subject.S2JBError):
            subject.validate_ppb_aggregate_lineage(
                lineage,
                bank_id=lineage.bank_id,
                slot_id="s2jb.foreign.slot",
                ppb_config_digest=lineage.ppb_config_digest,
                carrier_ids=lineage.carrier_ids,
            )

    def test_049_q5_wrong_geometry_or_coordinate_role(self):
        first, second = self._two_q5_sources()
        self._q5_count(3)
        with self.assertRaises(subject.S2JBError):
            subject.aggregate_codes_equivalent(first[1][0], second[1][1])

    def test_050_q5_float_without_prospective_evidence(self):
        self._two_q5_sources()
        self._q5_count(3)
        with self.assertRaises(subject.S2JBError):
            subject.aggregate_codes_equivalent(1600.0 / 408000.0, 1600.0 / 408000.0)


if __name__ == "__main__":
    unittest.main()
