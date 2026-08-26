from __future__ import annotations

import ast
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s2bd_paired_recognition_comparator as s2bd
from mcm_field_organism._ppb1_s2bd_paired_recognition_comparator import (
    BASELINE_EXPLAINS_CURRENT_FIXTURE,
)
from mcm_field_organism._ppb1_s2bf_corrected_paired_recognition_comparator import (
    compare_s2bf_ppb1_with_static_prototype_baseline,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from tests.test_s2aw_private_formation_probe_handoff import _fixture


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "mcm_field_organism"
    / "_ppb1_s2bf_corrected_paired_recognition_comparator.py"
)


def _compare(values):
    return compare_s2bf_ppb1_with_static_prototype_baseline(
        "pair.synthetic.s2bf",
        *values,
        "candidate.s2bf.auditory",
        "candidate.s2bf.visual",
        "baseline.s2bf.auditory",
        "baseline.s2bf.visual",
    )


class S2BFCorrectedSourcePreflightOrderTests(unittest.TestCase):
    def test_positive_and_negative_valid_pairs_remain_baseline_explained(self) -> None:
        positive = _compare(_fixture())
        negative = _compare(_fixture(probe_values=0.5))
        self.assertEqual(
            BASELINE_EXPLAINS_CURRENT_FIXTURE,
            positive.comparator_result,
        )
        self.assertEqual(
            BASELINE_EXPLAINS_CURRENT_FIXTURE,
            negative.comparator_result,
        )

    def test_foreign_stabilized_candidate_rejects_before_baseline_formation(self) -> None:
        foreign_result = _fixture(formation_count=3)[0]
        _, bound_envelope, bound_profile, bound_probe = _fixture(formation_count=4)
        with patch.object(
            s2bd,
            "form_s2bb_active_static_prototype_baseline",
            wraps=s2bd.form_s2bb_active_static_prototype_baseline,
        ) as baseline_formation:
            with self.assertRaises(ValueError):
                _compare(
                    (
                        foreign_result,
                        bound_envelope,
                        bound_profile,
                        bound_probe,
                    )
                )
        self.assertEqual(0, baseline_formation.call_count)

    def test_preflight_calls_precede_the_single_deriving_comparator_call(self) -> None:
        tree = ast.parse(SOURCE.read_text(encoding="ascii"))
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name
            == "compare_s2bf_ppb1_with_static_prototype_baseline"
        )
        lines = {
            name: [
                node.lineno
                for node in ast.walk(function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == name
            ]
            for name in (
                "_validate_formation",
                "_validate_probe_envelope",
                "compare_s2bd_ppb1_with_static_prototype_baseline",
            )
        }
        self.assertEqual(1, len(lines["_validate_formation"]))
        self.assertEqual(1, len(lines["_validate_probe_envelope"]))
        self.assertEqual(
            1,
            len(lines["compare_s2bd_ppb1_with_static_prototype_baseline"]),
        )
        self.assertLess(
            max(lines["_validate_formation"] + lines["_validate_probe_envelope"]),
            lines["compare_s2bd_ppb1_with_static_prototype_baseline"][0],
        )

    def test_corrected_entry_remains_private(self) -> None:
        name = "compare_s2bf_ppb1_with_static_prototype_baseline"
        self.assertFalse(hasattr(mcm_field_organism, name))
        self.assertFalse(hasattr(current_api, name))
        self.assertNotIn(name, ROOT_LAZY_EXPORTS)


if __name__ == "__main__":
    unittest.main()
