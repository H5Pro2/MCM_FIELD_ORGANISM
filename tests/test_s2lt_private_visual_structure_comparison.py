"""Neutral qualification of the private S2-LT visual comparison boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2lt_private_visual_structure_comparison as comparison
from tools import _s2lt_private_visual_structure_corpus as corpus


ROOT = Path(__file__).resolve().parents[1]


class S2LTVisualStructureComparisonTests(unittest.TestCase):
    def test_01_plan_is_canonical_and_digest_bound(self) -> None:
        plan = comparison._load_plan(ROOT)
        self.assertEqual(comparison.EXPECTED_PLAN_DIGEST, plan["plan_digest"])
        self.assertEqual(12, len(plan["generation_root"]["source_bindings"]))

    def test_02_sources_are_unique_with_identical_brightness_histograms(self) -> None:
        plan = comparison._load_plan(ROOT)
        bindings = plan["generation_root"]["source_bindings"]
        self.assertEqual(12, len({item["payload_sha256"] for item in bindings}))
        self.assertEqual(1, len({item["histogram_digest"] for item in bindings}))
        self.assertEqual(1, len({item["rgb_value_sum"] for item in bindings}))

    def test_03_one_frame_has_all_three_bound_dimensions(self) -> None:
        frame = corpus.render_frame(corpus.CONTENT_RECIPES[0])
        baseline = LocalChannelGridReceptor(VisualGridConfig()).analyze(frame, frame_index=0)
        self.assertEqual((288, 1728, 576), (len(baseline.channel_values), len(comparison._subblock_means(frame)), len(comparison._local_gradients(frame))))

    def test_04_representations_are_deterministic(self) -> None:
        first = corpus.render_frame(corpus.CONTENT_RECIPES[1])
        second = corpus.render_frame(corpus.CONTENT_RECIPES[1])
        self.assertEqual(first.tobytes(), second.tobytes())
        self.assertEqual(comparison._subblock_means(first), comparison._subblock_means(second))
        self.assertEqual(comparison._local_gradients(first), comparison._local_gradients(second))

    def test_05_one_changed_pixel_remains_distinguishable(self) -> None:
        original = corpus.render_frame(corpus.CONTENT_RECIPES[0])
        changed = np.array(original, copy=True)
        changed[0, 0, 0] += 1
        receptor = LocalChannelGridReceptor(VisualGridConfig())
        self.assertNotEqual(receptor.analyze(original, frame_index=0).digest(), receptor.analyze(changed, frame_index=1).digest())
        self.assertNotEqual(comparison._subblock_means(original), comparison._subblock_means(changed))
        self.assertNotEqual(comparison._local_gradients(original), comparison._local_gradients(changed))

    def test_06_metric_evaluation_accepts_negative_results(self) -> None:
        vectors = {
            "a1": (0.0,), "a2": (1.0,), "a3": (0.0,), "a4": (1.0,), "ah": (0.5,),
            "b1": (0.0,), "b2": (1.0,), "b3": (0.0,), "b4": (1.0,), "bh": (0.5,),
        }
        families = (
            {"family_id": "f1", "training_content_ids": ["a1", "a2", "a3", "a4"], "holdout_content_ids": ["ah"]},
            {"family_id": "f2", "training_content_ids": ["b1", "b2", "b3", "b4"], "holdout_content_ids": ["bh"]},
        )
        result = comparison._representation_evaluation("neutral", vectors, families)
        self.assertFalse(result["meets_presealed_criteria"])

    def test_07_plan_retains_no_raw_payload(self) -> None:
        serialized = json.dumps(comparison._load_plan(ROOT), sort_keys=True)
        for forbidden in ("raw_bytes", "rgb_bytes", "image_bytes", "pixel_values"):
            self.assertNotIn(forbidden, serialized)
        self.assertIn('"raw_payload_retained": false', serialized)

    def test_08_execution_gates_are_closed(self) -> None:
        self.assertIs(corpus.PLAN_ENABLED, False)
        self.assertIs(comparison.COMPARISON_ENABLED, False)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(comparison.S2LTComparisonError):
                comparison.write_comparison_once(ROOT, Path(directory), comparison_id=comparison.COMPARISON_ID)
            self.assertEqual([], list(Path(directory).iterdir()))
        self.assertEqual(
            comparison.EXPECTED_PLAN_SHA256,
            hashlib.sha256((ROOT / comparison.PLAN_RELATIVE_PATH).read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
