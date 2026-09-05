from __future__ import annotations

import hashlib
import json
import threading
import time
import unittest

import numpy as np

import tools._s2mp_private_feature_sparse_correspondence as subject
from tools._s2mm_private_sparse_lk_preflight import (
    _bind_process_memory_api,
    _working_set_bytes,
)


def _frame_digest(value: np.ndarray) -> str:
    return hashlib.sha256(memoryview(value).cast("B")).hexdigest()


def _structured_pair() -> tuple[np.ndarray, np.ndarray]:
    first = np.empty((subject.HEIGHT, subject.WIDTH, 3), dtype=np.uint8)
    rows, columns = np.ogrid[: subject.HEIGHT, : subject.WIDTH]
    checker = (((columns // 12) + (rows // 12)) & 1).astype(np.uint8)
    first[:, :, 0] = 24 + checker * 196
    first[:, :, 1] = 52 + (1 - checker) * 148
    first[:, :, 2] = 36 + checker * 112
    second = np.empty_like(first)
    second[:, :, :] = np.asarray((24, 52, 36), dtype=np.uint8)
    second[3:, 5:, :] = first[:-3, :-5, :]
    first.setflags(write=False)
    second.setflags(write=False)
    return first, second


def _pair(first: np.ndarray, second: np.ndarray) -> subject.SparseVisualPairV1:
    return subject.SparseVisualPairV1(
        pair_id="neutral-pair-001",
        frame_0_payload_digest=_frame_digest(first),
        frame_1_payload_digest=_frame_digest(second),
        visual_source_clock_id="neutral-clock-001",
        frame_0_window_start_tick=0,
        frame_0_window_end_tick=1,
        frame_1_window_start_tick=1,
        frame_1_window_end_tick=2,
    )


class S2MPFeatureSparseCorrespondenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        kernel32, psapi = _bind_process_memory_api()
        baseline = _working_set_bytes(kernel32, psapi)
        samples = [baseline]
        errors: list[BaseException] = []
        stop = threading.Event()

        def sample() -> None:
            try:
                while not stop.is_set():
                    samples.append(_working_set_bytes(kernel32, psapi))
                    time.sleep(0.001)
            except BaseException as exc:
                errors.append(exc)
                stop.set()

        thread = threading.Thread(target=sample, daemon=True)
        thread.start()
        try:
            cls.runtime = subject.qualified_runtime_binding()
            cls.first, cls.second = _structured_pair()
            cls.pair = _pair(cls.first, cls.second)
            first_y = subject._rgb_to_y(np, cls.first)
            cls.points_0, cls.cells_0, cls.cell_counts_0 = subject.detect_candidate_points(first_y)
            cls.points_1, cls.cells_1, cls.cell_counts_1 = subject.detect_candidate_points(first_y)
            cls.result = subject.measure_sparse_pair(cls.pair, cls.first, cls.second)
        finally:
            stop.set()
            thread.join(timeout=2.0)
        if thread.is_alive():
            raise RuntimeError("memory sampler did not terminate")
        if errors:
            raise errors[0]
        cls.peak_delta = max(samples) - baseline

    def test_01_runtime_and_algorithm_binding(self) -> None:
        self.assertEqual(self.runtime["algorithm_binding_digest"], subject.algorithm_binding_digest())
        self.assertEqual(self.runtime["thread_count"], 1)
        self.assertFalse(self.runtime["opencl_enabled"])

    def test_02_candidate_selection_is_bit_deterministic(self) -> None:
        self.assertEqual(self.points_0.tobytes(), self.points_1.tobytes())
        self.assertEqual(self.cells_0.tobytes(), self.cells_1.tobytes())
        self.assertEqual(self.cell_counts_0, self.cell_counts_1)

    def test_03_candidates_are_bounded_unique_and_ordered(self) -> None:
        self.assertGreater(self.points_0.shape[0], 0)
        self.assertLessEqual(self.points_0.shape[0], subject.MAX_POINT_COUNT)
        flattened = self.points_0.reshape(-1, 2)
        self.assertEqual(np.unique(flattened, axis=0).shape[0], flattened.shape[0])
        self.assertTrue(bool(np.all(self.cells_0[1:] >= self.cells_0[:-1])))
        for cell_index in np.unique(self.cells_0):
            local = flattened[self.cells_0 == cell_index]
            observed = [(float(y), float(x)) for x, y in local]
            self.assertEqual(observed, sorted(observed))

    def test_04_translation_produces_available_evidence(self) -> None:
        self.assertEqual(self.result.evidence_status, "MOTION_EVIDENCE_AVAILABLE")
        self.assertEqual((self.result.forward_lk_calls, self.result.reverse_lk_calls), (1, 1))
        self.assertGreaterEqual(self.result.valid_track_count, subject.MIN_VALID_TRACKS)

    def test_05_status_and_valid_components_are_bound(self) -> None:
        components = dict(self.result.component_digests)
        expected = {
            "candidate_points",
            "candidate_cells",
            "forward_status",
            "backward_status",
            "valid_indices",
            "forward_valid_points",
            "backward_valid_points",
            "forward_valid_errors",
            "backward_valid_errors",
            "displacement",
            "cycle_residual",
            "rgb_residual",
        }
        self.assertEqual(set(components), expected)
        self.assertTrue(all(len(value) == 64 for value in components.values()))

    def test_06_spatial_coverage_is_complete_and_consistent(self) -> None:
        self.assertEqual(sum(self.result.candidate_cell_counts), self.result.candidate_count)
        self.assertEqual(sum(self.result.valid_cell_counts), self.result.valid_track_count)
        self.assertGreaterEqual(self.result.valid_covered_cell_count, subject.MIN_VALID_CELLS)
        self.assertEqual(len(self.result.valid_cell_counts), 96)

    def test_07_structure_poverty_is_a_regular_insufficient_result(self) -> None:
        first = np.full((subject.HEIGHT, subject.WIDTH, 3), 64, dtype=np.uint8)
        second = np.full_like(first, 64)
        first.setflags(write=False)
        second.setflags(write=False)
        result = subject.measure_sparse_pair(_pair(first, second), first, second)
        self.assertEqual(result.evidence_status, "INSUFFICIENT_MOTION_EVIDENCE")
        self.assertEqual(result.candidate_count, 0)
        self.assertEqual((result.forward_lk_calls, result.reverse_lk_calls), (0, 0))

    def test_08_source_time_type_and_digest_errors_fail_closed(self) -> None:
        with self.assertRaises(subject.S2MPMeasurementError):
            subject.SparseVisualPairV1(
                pair_id="neutral-pair-002",
                frame_0_payload_digest=_frame_digest(self.first),
                frame_1_payload_digest=_frame_digest(self.second),
                visual_source_clock_id="neutral-clock-002",
                frame_0_window_start_tick=0,
                frame_0_window_end_tick=2,
                frame_1_window_start_tick=1,
                frame_1_window_end_tick=3,
            )
        with self.assertRaises(subject.S2MPMeasurementError):
            subject.measure_sparse_pair(
                subject.SparseVisualPairV1(
                    pair_id="neutral-pair-003",
                    frame_0_payload_digest="0" * 64,
                    frame_1_payload_digest=_frame_digest(self.second),
                    visual_source_clock_id="neutral-clock-003",
                    frame_0_window_start_tick=0,
                    frame_0_window_end_tick=1,
                    frame_1_window_start_tick=1,
                    frame_1_window_end_tick=2,
                ),
                self.first,
                self.second,
            )
        with self.assertRaises(subject.S2MPMeasurementError):
            subject.measure_sparse_pair(self.pair, self.first.astype(np.float32), self.second)

    def test_09_inputs_are_read_only_and_output_has_no_raw_arrays(self) -> None:
        self.assertFalse(self.first.flags.writeable)
        self.assertFalse(self.second.flags.writeable)
        payload = self.result.canonical_payload()
        self.assertFalse(payload["raw_frames_present"])
        self.assertFalse(payload["point_arrays_present"])
        self.assertFalse(payload["error_arrays_present"])
        encoded = json.dumps(payload, sort_keys=True)
        self.assertNotIn("frame_values", encoded)
        self.assertNotIn("point_values", encoded)

    def test_10_process_peak_stays_below_bound(self) -> None:
        self.assertGreater(self.peak_delta, 0)
        self.assertLess(self.peak_delta, subject.MAX_PEAK_BYTES)


if __name__ == "__main__":
    unittest.main()
