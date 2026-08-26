from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._ppb1_receptor_profiles import bind_ppb1_receptor_profile
from mcm_field_organism._ppb1_s2bd_active_static_prototype_baseline import (
    S2BDStaticPrototypeBaselineError,
    form_s2bb_active_static_prototype_baseline,
    probe_s2bb_static_prototype_read_only,
)
import mcm_field_organism._ppb1_s2bd_paired_recognition_comparator as pairing
from mcm_field_organism._ppb1_s2bd_paired_recognition_comparator import (
    BASELINE_EXPLAINS_CURRENT_FIXTURE,
    S2BDPairedRecognitionComparatorError,
    compare_s2bd_ppb1_with_static_prototype_baseline,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from tests.test_s2aw_private_formation_probe_handoff import _fixture, _parameters


ROOT = Path(__file__).resolve().parents[1]
BASELINE_SOURCE = (
    ROOT
    / "mcm_field_organism"
    / "_ppb1_s2bd_active_static_prototype_baseline.py"
)


def _compare(values):
    return compare_s2bd_ppb1_with_static_prototype_baseline(
        "pair.synthetic.s2bd",
        *values,
        "candidate.probe.auditory",
        "candidate.probe.visual",
        "baseline.probe.auditory",
        "baseline.probe.visual",
    )


class S2BDPrivateActiveStaticPrototypeComparatorTests(unittest.TestCase):
    def test_positive_pair_is_completely_baseline_explained(self) -> None:
        values = _fixture()
        result = _compare(values)
        self.assertEqual(BASELINE_EXPLAINS_CURRENT_FIXTURE, result.comparator_result)
        self.assertEqual(2, len(result.candidate_finding_digests))
        self.assertEqual(2, len(result.baseline_finding_digests))
        self.assertEqual(2, len(result.baseline_formation_receipt_digests))

    def test_negative_pair_is_completely_baseline_explained(self) -> None:
        result = _compare(_fixture(probe_values=0.5))
        self.assertEqual(BASELINE_EXPLAINS_CURRENT_FIXTURE, result.comparator_result)

    def test_baseline_forms_independently_and_probe_is_read_only(self) -> None:
        _, formation, profile, probe = _fixture()
        bundle = form_s2bb_active_static_prototype_baseline(formation, profile)
        before = bundle.auditory_state.digest()
        finding = probe_s2bb_static_prototype_read_only(
            bundle.auditory_state,
            probe.auditory_stream,
            profile.auditory_config,
        )
        self.assertTrue(finding.recognized)
        self.assertEqual(before, finding.postprobe_state_digest)
        self.assertEqual(before, bundle.auditory_state.digest())

    def test_unstabilized_candidate_and_wrong_source_fail_closed(self) -> None:
        with self.assertRaises(S2BDPairedRecognitionComparatorError):
            _compare(_fixture(formation_count=2))
        values = _fixture()
        wrong_profile = bind_ppb1_receptor_profile("controlled", _parameters())
        with self.assertRaises(S2BDPairedRecognitionComparatorError):
            _compare((values[0], values[1], wrong_profile, values[3]))

    def test_second_baseline_probe_failure_emits_no_paired_receipt(self) -> None:
        values = _fixture()
        bundle = form_s2bb_active_static_prototype_baseline(values[1], values[2])
        auditory = probe_s2bb_static_prototype_read_only(
            bundle.auditory_state,
            values[3].auditory_stream,
            values[2].auditory_config,
        )
        before = (
            values[0].auditory_poststate.digest(),
            values[0].visual_poststate.digest(),
            bundle.auditory_state.digest(),
            bundle.visual_state.digest(),
        )
        with patch.object(
            pairing,
            "probe_s2bb_static_prototype_read_only",
            side_effect=(auditory, RuntimeError("injected second probe failure")),
        ):
            with self.assertRaises(S2BDPairedRecognitionComparatorError):
                _compare(values)
        self.assertEqual(
            before,
            (
                values[0].auditory_poststate.digest(),
                values[0].visual_poststate.digest(),
                bundle.auditory_state.digest(),
                bundle.visual_state.digest(),
            ),
        )

    def test_receipt_tampering_and_identifier_reuse_fail_closed(self) -> None:
        result = _compare(_fixture())
        with self.assertRaises(S2BDPairedRecognitionComparatorError):
            replace(result, comparator_result="ADVANTAGE")
        values = _fixture()
        with self.assertRaises(S2BDPairedRecognitionComparatorError):
            compare_s2bd_ppb1_with_static_prototype_baseline(
                "pair.synthetic.s2bd",
                *values,
                "probe.same",
                "candidate.probe.visual",
                "probe.same",
                "baseline.probe.visual",
            )

    def test_baseline_has_no_candidate_import_and_boundaries_stay_private(self) -> None:
        tree = ast.parse(BASELINE_SOURCE.read_text(encoding="ascii"))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertNotIn("PPB1ActiveBatchFormationResult", imports)
        self.assertNotIn("PPB1BankState", imports)
        self.assertNotIn("advance_ppb1_bank", calls)
        self.assertNotIn("advance_s1wq_perceptual_state", calls)
        self.assertNotIn("probe_s1wu_perceptual_state", calls)
        for name in (
            "S2BBStaticPrototypeState",
            "S2BBPairedRecognitionReceipt",
            "compare_s2bd_ppb1_with_static_prototype_baseline",
        ):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertFalse(hasattr(current_api, name))
            self.assertNotIn(name, ROOT_LAZY_EXPORTS)


if __name__ == "__main__":
    unittest.main()
