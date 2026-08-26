from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path
import hashlib
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._ppb1_s1vn_matrix import (
    S1VN_BASELINE_IDS,
    S1VN_FAMILY_IDS,
    S1VN_MODALITY_IDS,
    S1VN_PARAMETER_IDS,
    S1VNCaseReceipt,
    S1VNStepObservation,
    s1vn_config,
)
from mcm_field_organism._ppb1_s1vq_corrected_matrix import (
    S1VQCaseReceipt,
    S1VQIdentityObservation,
    s1vq_corrected_matrix_plan,
)
from mcm_field_organism._ppb1_s1vt_result_pipeline import (
    S1VT_EXPECTED_CORRECTED_PLAN_DIGEST,
    S1VT_INVALID_MATRIX_RESULT,
    S1VTArmRecord,
    S1VTCompositionResult,
    S1VTResultPipelineError,
    compose_s1vt_arm_records,
    evaluate_s1vt_composition,
    seal_s1vt_matrix_result,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC_MASK = (True, True, True, False, True, False)
TRACE_FAMILIES = {"B02", "B04", "B05", "B06"}
EXPECTED_MATRIX_DIGEST = (
    "11d3d407bf928fb2c9c93bbbb2f0beefa0e8122740018bb58251bb4159dc0f16"
)
EXPECTED_COMPOSITION_DIGEST = (
    "b3045d745eca08f5f600824109165fd23b5979eb925745f45e2525d5d402d387"
)
EXPECTED_EVALUATION_DIGEST = (
    "8f21368b94595b5e68db4488f61094e60496c92d59c614e48e6b77943e2e21a5"
)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def desired_identity(family: str, fixture: str, index: int) -> str:
    prefix = family.lower()
    if family in TRACE_FAMILIES:
        return f"{prefix}.trace.000"
    if fixture in {"F01", "F02", "F08"}:
        return f"{prefix}.{fixture.lower()}.single"
    if fixture == "F03":
        return f"{prefix}.f03.{'low' if index % 2 == 0 else 'high'}"
    if fixture == "F07":
        suffix = "released" if index < 0 else str(index)
        return f"{prefix}.f07.{suffix}"
    return f"{prefix}.{fixture.lower()}.slot.{index:06d}"


def event_is_match(fixture: str, index: int, count: int) -> bool:
    if fixture in {"F01", "F02", "F08"}:
        return index > 0
    if fixture == "F03":
        return index >= 2
    if fixture == "F04":
        return False
    if fixture == "F05":
        return index == count - 2
    return False


def nonmatch_event(family: str) -> str:
    if family == "PPB1":
        return "CREATED"
    if family in {"B01", "B03"}:
        return "STORED"
    if family in TRACE_FAMILIES:
        return "UPDATED"
    return "OFF"


def active_count(family: str, fixture: str, index: int, capacity: int) -> int:
    if family == "B07":
        return 0
    if family in TRACE_FAMILIES:
        return 1
    if fixture == "F03":
        return min(2, capacity)
    if fixture == "F06":
        return min(index + 1, capacity)
    if fixture == "F07" and index > 0:
        return min(2, capacity)
    return 1


def constructed_receipt(path) -> S1VQCaseReceipt:
    config = s1vn_config(path.parameter_id, path.modality_id)
    events = []
    observations = []
    identities = []
    for index in range(path.expected_call_count):
        matched = event_is_match(path.fixture_id, index, path.expected_call_count)
        event = "MATCHED" if matched else nonmatch_event(path.family_id)
        if path.family_id == "B07":
            matched = False
            event = "OFF"
        identity_index = index
        if path.fixture_id in {"F01", "F02", "F08"}:
            identity_index = 0
        elif path.fixture_id == "F03":
            identity_index = index % 2
        elif path.fixture_id == "F05" and index == path.expected_call_count - 2:
            identity_index = 0
        assignment = desired_identity(
            path.family_id, path.fixture_id, identity_index
        )
        selected = assignment if matched else None
        if path.family_id == "B07":
            written = None
        elif path.family_id == "B03" and matched:
            written = None
        elif path.family_id == "B01" and matched:
            written = f"b01.synthetic.{path.fixture_id.lower()}.{index:06d}"
        else:
            written = assignment
        active = active_count(
            path.family_id, path.fixture_id, index, config.capacity
        )
        if path.family_id == "B02":
            occupied = min(index + 1, config.capacity)
            logical = (occupied + 1) * len(config.carrier_ids)
        elif path.family_id in TRACE_FAMILIES:
            occupied = 0
            logical = len(config.carrier_ids)
        else:
            occupied = active
            logical = active * len(config.carrier_ids)
        events.append(event)
        observations.append(
            S1VNStepObservation(
                index + 1,
                event,
                0.0 if matched else None,
                logical,
                occupied,
                active if path.family_id == "PPB1" else 0,
                selected or written,
                0.0 if path.family_id == "PPB1" else None,
            )
        )
        identities.append(
            S1VQIdentityObservation(
                index + 1,
                selected,
                written,
                digest(f"prestate:{assignment}") if selected else None,
                active,
                digest(
                    f"active:{path.family_id}:{path.parameter_id}:"
                    f"{path.modality_id}:{path.fixture_id}:{index}:{active}"
                ),
            )
        )
    history_digest = digest(
        f"history:{path.parameter_id}:{path.modality_id}:{path.fixture_id}"
    )
    final_digest = digest(
        f"final:{path.family_id}:{path.parameter_id}:"
        f"{path.modality_id}:{path.fixture_id}"
    )
    base = S1VNCaseReceipt(
        path.path_id,
        path.family_id,
        path.expected_call_count,
        tuple(events),
        tuple(observations),
        history_digest,
        final_digest,
    )
    return S1VQCaseReceipt(path, base, tuple(identities))


def constructed_receipts() -> tuple[S1VQCaseReceipt, ...]:
    return tuple(constructed_receipt(path) for path in s1vq_corrected_matrix_plan())


def replace_arms(
    composition: S1VTCompositionResult,
    changes: dict[tuple[str, str, str], dict[str, object]],
) -> S1VTCompositionResult:
    arms = tuple(
        replace(
            arm,
            **changes.get(
                (arm.family_id, arm.parameter_id, arm.modality_id), {}
            ),
        )
        for arm in composition.arms
    )
    return S1VTCompositionResult(
        composition.matrix_result_digest, arms, composition.evidence
    )


def evaluation_fixture(
    composition: S1VTCompositionResult,
    targets: dict[tuple[str, str, str], dict[str, object]],
) -> S1VTCompositionResult:
    changes = {
        (family, parameter, modality): {"lifecycle_mask": (False,) * 4}
        for family in S1VN_FAMILY_IDS
        for parameter in S1VN_PARAMETER_IDS
        for modality in S1VN_MODALITY_IDS
    }
    changes.update(targets)
    return replace_arms(composition, changes)


ADMISSIBLE = {
    "lifecycle_mask": (True,) * 4,
    "diagnostic_match_mask": DIAGNOSTIC_MASK,
    "near_assignment_consistent": True,
    "separated_assignment_distinct": True,
    "repeatability_mask": (True,) * 3,
}


class PPB1S1VTResultPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipts = constructed_receipts()
        cls.matrix = seal_s1vt_matrix_result(cls.receipts)
        cls.composition = compose_s1vt_arm_records(cls.matrix)

    def test_constructed_inventory_seals_all_528_paths_atomically(self) -> None:
        self.assertEqual(528, len(self.matrix.receipts))
        self.assertEqual(144, len(self.matrix.repeat_comparisons))
        self.assertTrue(all(item.bit_equal for item in self.matrix.repeat_comparisons))
        self.assertEqual(
            S1VT_EXPECTED_CORRECTED_PLAN_DIGEST,
            self.matrix.corrected_plan_digest,
        )

    def test_sealed_matrix_binds_exact_call_ledgers(self) -> None:
        self.assertEqual(9476, self.matrix.ppb_call_count)
        self.assertEqual(66332, self.matrix.baseline_call_count)
        self.assertEqual(75808, self.matrix.total_call_count)
        self.assertEqual(64, len(self.matrix.receipt_list_digest))
        self.assertEqual(64, len(self.matrix.comparison_list_digest))

    def test_compositor_produces_exact_ordered_48_arm_cross_product(self) -> None:
        self.assertEqual(48, len(self.composition.arms))
        self.assertEqual(48, len(self.composition.evidence))
        self.assertEqual(
            tuple(
                (family, parameter, modality)
                for family in S1VN_FAMILY_IDS
                for parameter in S1VN_PARAMETER_IDS
                for modality in S1VN_MODALITY_IDS
            ),
            tuple(
                (arm.family_id, arm.parameter_id, arm.modality_id)
                for arm in self.composition.arms
            ),
        )
        self.assertTrue(all(
            len(arm.source_receipt_digests) == 11
            for arm in self.composition.arms
        ))

    def test_arm_call_ledgers_include_r0_and_r1(self) -> None:
        expected = {
            ("P0", "auditory"): (1074, 24, 1098),
            ("P0", "visual"): (302, 20, 322),
            ("P1", "auditory"): (2106, 32, 2138),
            ("P1", "visual"): (562, 24, 586),
            ("P2", "auditory"): (4170, 48, 4218),
            ("P2", "visual"): (1082, 32, 1114),
        }
        for arm in self.composition.arms:
            self.assertEqual(
                expected[(arm.parameter_id, arm.modality_id)],
                (
                    arm.r0_accepted_call_count,
                    arm.r1_accepted_call_count,
                    arm.total_accepted_call_count,
                ),
            )

    def test_ppb_arm_derives_fixed_masks_and_identity_budget(self) -> None:
        arm = self.composition.arms[0]
        self.assertEqual((True,) * 4, arm.lifecycle_mask)
        self.assertEqual(DIAGNOSTIC_MASK, arm.diagnostic_match_mask)
        self.assertTrue(arm.near_assignment_consistent)
        self.assertTrue(arm.separated_assignment_distinct)
        self.assertEqual((True,) * 3, arm.repeatability_mask)
        self.assertGreater(arm.peak_identity_metadata_value_count, 0)
        self.assertTrue(arm.admissible)

    def test_b07_remains_inadmissible_and_identity_free(self) -> None:
        arm = next(
            item
            for item in self.composition.arms
            if (item.family_id, item.parameter_id, item.modality_id)
            == ("B07", "P0", "auditory")
        )
        self.assertEqual(0, arm.peak_identity_metadata_value_count)
        self.assertFalse(arm.admissible)

    def test_evidence_and_arm_digests_are_linked(self) -> None:
        for arm, evidence in zip(
            self.composition.arms, self.composition.evidence, strict=True
        ):
            self.assertEqual(evidence.digest(), arm.evidence_digest)
            self.assertEqual(
                evidence.source_receipt_digests, arm.source_receipt_digests
            )

    def test_matrix_and_composition_digests_are_deterministic(self) -> None:
        self.assertEqual(EXPECTED_MATRIX_DIGEST, self.matrix.digest())
        self.assertEqual(EXPECTED_COMPOSITION_DIGEST, self.composition.digest())
        evaluation = evaluate_s1vt_composition(self.composition)
        self.assertEqual(EXPECTED_EVALUATION_DIGEST, evaluation.digest())

    def test_missing_receipt_fails_closed_before_composition(self) -> None:
        with self.assertRaises(S1VTResultPipelineError) as caught:
            seal_s1vt_matrix_result(self.receipts[:-1])
        self.assertEqual(S1VT_INVALID_MATRIX_RESULT, caught.exception.code)

    def test_baseline_selection_without_prestate_digest_fails_closed(self) -> None:
        receipt_index, receipt = next(
            (index, item)
            for index, item in enumerate(self.receipts)
            if item.path.family_id == "B01" and item.path.fixture_id == "F01"
        )
        identities = list(receipt.identity_observations)
        identities[1] = replace(identities[1], selected_prestate_digest=None)
        changed = replace(receipt, identity_observations=tuple(identities))
        receipts = list(self.receipts)
        receipts[receipt_index] = changed
        with self.assertRaises(S1VTResultPipelineError) as caught:
            seal_s1vt_matrix_result(tuple(receipts))
        self.assertEqual(S1VT_INVALID_MATRIX_RESULT, caught.exception.code)

    def test_different_diagnostic_mask_does_not_reduce_ppb(self) -> None:
        ppb = dict(ADMISSIBLE)
        ppb.update(peak_logical_value_count=100, peak_identity_metadata_value_count=4)
        baseline = dict(ADMISSIBLE)
        baseline.update(
            diagnostic_match_mask=(True, True, False, False, True, False),
            peak_logical_value_count=10,
            peak_identity_metadata_value_count=1,
        )
        fixture = evaluation_fixture(
            self.composition,
            {
                ("PPB1", "P0", "auditory"): ppb,
                ("B01", "P0", "auditory"): baseline,
            },
        )
        self.assertEqual(
            "P0", evaluate_s1vt_composition(fixture).decisions[0].selection
        )

    def test_equal_profile_and_smaller_budget_reduces_ppb(self) -> None:
        ppb = dict(ADMISSIBLE)
        ppb.update(peak_logical_value_count=100, peak_identity_metadata_value_count=4)
        baseline = dict(ADMISSIBLE)
        baseline.update(
            peak_logical_value_count=10,
            peak_identity_metadata_value_count=1,
        )
        fixture = evaluation_fixture(
            self.composition,
            {
                ("PPB1", "P0", "auditory"): ppb,
                ("B01", "P0", "auditory"): baseline,
            },
        )
        decision = evaluate_s1vt_composition(fixture).decisions[0]
        self.assertEqual("NO_ADMISSIBLE_CONFIGURATION", decision.selection)
        self.assertEqual(("P0",), decision.reduced_parameter_ids)
        self.assertEqual(("B01",), decision.explaining_baseline_ids)

    def test_identity_budget_precedes_call_count_in_ppb_selection(self) -> None:
        p0 = dict(ADMISSIBLE)
        p0.update(peak_logical_value_count=100, peak_identity_metadata_value_count=4)
        p1 = dict(ADMISSIBLE)
        p1.update(peak_logical_value_count=100, peak_identity_metadata_value_count=2)
        fixture = evaluation_fixture(
            self.composition,
            {
                ("PPB1", "P0", "auditory"): p0,
                ("PPB1", "P1", "auditory"): p1,
            },
        )
        self.assertEqual(
            "P1", evaluate_s1vt_composition(fixture).decisions[0].selection
        )

    def test_s1vt_remains_private_and_snapshot_free(self) -> None:
        names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        names |= {item.name for item in fields(SharedMCMFieldSnapshot)}
        for name in (
            "seal_s1vt_matrix_result",
            "compose_s1vt_arm_records",
            "evaluate_s1vt_composition",
        ):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertNotIn(name, names)

    def test_s1vt_source_has_no_field_media_or_matrix_execution_call(self) -> None:
        source = (
            ROOT / "mcm_field_organism" / "_ppb1_s1vt_result_pipeline.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "shared_mcm_field",
            "public_av_receptor_run",
            "live_audio_video_field",
            "execute_s1vq_corrected_matrix",
            "_execute_s1vq_corrected_matrix",
            "_execute_s1vq_registered_path",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
