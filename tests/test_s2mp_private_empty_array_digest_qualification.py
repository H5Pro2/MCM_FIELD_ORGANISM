from __future__ import annotations

import hashlib
import unittest
from unittest.mock import patch

import numpy as np

import tools._s2mp_private_feature_sparse_correspondence as subject


QUALIFICATION_ID = "s2mp-neutral-empty-array-digest-qualification-20260905-01"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def _frame_digest(value: np.ndarray) -> str:
    return hashlib.sha256(memoryview(value).cast("B")).hexdigest()


def _neutral_pair(first: np.ndarray, second: np.ndarray) -> subject.SparseVisualPairV1:
    return subject.SparseVisualPairV1(
        pair_id="neutral-empty-track-pair-001",
        frame_0_payload_digest=_frame_digest(first),
        frame_1_payload_digest=_frame_digest(second),
        visual_source_clock_id="neutral-empty-track-clock-001",
        frame_0_window_start_tick=0,
        frame_0_window_end_tick=1,
        frame_1_window_start_tick=2,
        frame_1_window_end_tick=3,
    )


class S2MPEmptyArrayDigestQualificationTests(unittest.TestCase):
    def test_01_empty_point_projection_has_empty_byte_digest(self) -> None:
        points = np.empty((0, 2), dtype=np.float32)
        self.assertEqual(subject._array_digest(points, "<f4"), EMPTY_SHA256)
        self.assertEqual(points.shape, (0, 2))
        self.assertEqual(points.dtype, np.float32)

    def test_02_empty_index_error_and_residual_vectors_are_regular(self) -> None:
        fixtures = (
            (np.empty((0,), dtype=np.int32), "<i4"),
            (np.empty((0,), dtype=np.float32), "<f4"),
            (np.empty((0,), dtype=np.float64), "<f4"),
        )
        for value, dtype in fixtures:
            with self.subTest(dtype=dtype, source_dtype=str(value.dtype)):
                self.assertEqual(subject._array_digest(value, dtype), EMPTY_SHA256)

    def test_03_candidate_without_valid_track_is_insufficient_evidence(self) -> None:
        first = np.zeros((subject.HEIGHT, subject.WIDTH, 3), dtype=np.uint8)
        second = np.zeros_like(first)
        first.setflags(write=False)
        second.setflags(write=False)
        point = np.asarray([[[80.0, 80.0]]], dtype=np.float32)
        cells = np.asarray([0], dtype=np.int16)
        cell_counts = (1,) + (0,) * 95

        def lk_zero_status(*args: object, **kwargs: object) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            source_points = np.asarray(args[2], dtype=np.float32)
            return source_points.copy(), np.zeros((1, 1), dtype=np.uint8), np.empty((1, 1), dtype=np.float32)

        with (
            patch.object(subject, "detect_candidate_points", return_value=(point, cells, cell_counts)),
            patch.object(subject.cv2, "calcOpticalFlowPyrLK", side_effect=lk_zero_status),
        ):
            result = subject.measure_sparse_pair(_neutral_pair(first, second), first, second)

        self.assertEqual(result.candidate_count, 1)
        self.assertEqual(result.valid_track_count, 0)
        self.assertEqual(result.evidence_status, "INSUFFICIENT_MOTION_EVIDENCE")
        self.assertEqual((result.forward_lk_calls, result.reverse_lk_calls), (1, 1))

    def test_04_empty_valid_components_keep_roles_and_shapes_separate(self) -> None:
        first = np.zeros((subject.HEIGHT, subject.WIDTH, 3), dtype=np.uint8)
        second = np.zeros_like(first)
        point = np.asarray([[[96.0, 96.0]]], dtype=np.float32)
        cells = np.asarray([0], dtype=np.int16)

        def lk_zero_status(*args: object, **kwargs: object) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            source_points = np.asarray(args[2], dtype=np.float32)
            return source_points.copy(), np.zeros((1, 1), dtype=np.uint8), np.zeros((1, 1), dtype=np.float32)

        with (
            patch.object(subject, "detect_candidate_points", return_value=(point, cells, (1,) + (0,) * 95)),
            patch.object(subject.cv2, "calcOpticalFlowPyrLK", side_effect=lk_zero_status),
        ):
            result = subject.measure_sparse_pair(_neutral_pair(first, second), first, second)

        components = dict(result.component_digests)
        empty_roles = {
            "valid_indices",
            "forward_valid_points",
            "backward_valid_points",
            "forward_valid_errors",
            "backward_valid_errors",
            "displacement",
            "cycle_residual",
            "rgb_residual",
        }
        self.assertTrue(empty_roles.issubset(components))
        self.assertEqual({components[role] for role in empty_roles}, {EMPTY_SHA256})
        self.assertEqual(len(result.valid_cell_counts), 96)
        self.assertEqual(sum(result.valid_cell_counts), 0)

    def test_05_nonempty_reference_digests_remain_byte_identical(self) -> None:
        fixtures = (
            (np.asarray([[1.25, -2.5], [3.75, 4.5]], dtype=np.float32), "<f4"),
            (np.asarray([0, 4, 9], dtype=np.int16), "<i2"),
            (np.asarray([0, 4, 9], dtype=np.int32), "<i4"),
            (np.asarray([1, 0, 1], dtype=np.uint8), "u1"),
            (np.asarray([0.0, 0.125, 2.0], dtype=np.float32), "<f4"),
        )
        for value, dtype in fixtures:
            with self.subTest(dtype=dtype, shape=value.shape):
                canonical = np.ascontiguousarray(value, dtype=dtype)
                previous = hashlib.sha256(memoryview(canonical).cast("B")).hexdigest()
                self.assertEqual(subject._array_digest(value, dtype), previous)


if __name__ == "__main__":
    unittest.main()
