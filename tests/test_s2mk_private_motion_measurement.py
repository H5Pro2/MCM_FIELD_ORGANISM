from __future__ import annotations

import ast
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import threading
import time
import unittest
from unittest import mock

import numpy as np

from tools import _s2mk_private_motion_measurement as s2mk


QUALIFICATION_ID = "s2mk-neutral-motion-measurement-qualification-20260905-01"


class _ProcessMemoryCounters(ctypes.Structure):
    _fields_ = (
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    )


def _working_set_bytes() -> int:
    counters = _ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    process = ctypes.windll.kernel32.GetCurrentProcess()
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(
        process,
        ctypes.byref(counters),
        counters.cb,
    )
    if not ok:
        raise OSError("GetProcessMemoryInfo failed")
    return int(counters.WorkingSetSize)


def _payload_digest(frame: np.ndarray) -> str:
    return hashlib.sha256(frame.tobytes(order="C")).hexdigest()


def _full_format_fixture() -> tuple[np.ndarray, np.ndarray]:
    first = np.empty((s2mk.HEIGHT, s2mk.WIDTH, 3), dtype=np.uint8)
    first[:, :, :] = np.asarray((18, 30, 42), dtype=np.uint8)
    rows, columns = np.ogrid[: s2mk.HEIGHT, : s2mk.WIDTH]
    panel = (columns >= 510) & (columns < 990) & (rows >= 350) & (rows < 730)
    texture = (((columns // 12) + (rows // 12)) & 1) == 0
    first[panel & texture, :] = np.asarray((224, 72, 48), dtype=np.uint8)
    first[panel & ~texture, :] = np.asarray((248, 188, 64), dtype=np.uint8)
    second = np.empty_like(first)
    second[:, :, :] = np.asarray((18, 30, 42), dtype=np.uint8)
    second[7:, 11:, :] = first[:-7, :-11, :]
    first.setflags(write=False)
    second.setflags(write=False)
    return first, second


def _contains_forbidden_payload(value: object) -> bool:
    if isinstance(value, (bytes, bytearray, memoryview, np.ndarray)):
        return True
    if isinstance(value, dict):
        return any(_contains_forbidden_payload(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_forbidden_payload(item) for item in value)
    return False


class S2MKPrivateMotionMeasurementQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frame_0, cls.frame_1 = _full_format_fixture()
        cls.algorithm = s2mk.qualified_algorithm_binding()
        cls.pair = s2mk.VisualMotionPairV1(
            pair_id="neutral-pair-001",
            frame_0_payload_digest=_payload_digest(cls.frame_0),
            frame_1_payload_digest=_payload_digest(cls.frame_1),
            visual_source_clock_id="neutral-visual-clock",
            frame_0_window_start_tick=0,
            frame_0_window_end_tick=33_333_333,
            frame_1_window_start_tick=33_333_333,
            frame_1_window_end_tick=66_666_666,
            algorithm_binding_digest=cls.algorithm.digest(),
        )
        baseline_working_set = _working_set_bytes()
        samples = [baseline_working_set]
        stop = threading.Event()

        def sample_memory() -> None:
            while not stop.is_set():
                samples.append(_working_set_bytes())
                time.sleep(0.001)

        sampler = threading.Thread(target=sample_memory, daemon=True)
        sampler.start()
        try:
            cls.result = s2mk.measure_and_compare(
                cls.frame_0,
                cls.frame_1,
                cls.pair,
                cls.algorithm,
            )
        finally:
            stop.set()
            sampler.join(timeout=2.0)
        cls.process_peak_delta_bytes = max(samples) - baseline_working_set
        cls.measured_peak_with_inputs_bytes = max(
            cls.result.measurement.peak_owned_array_bytes,
            cls.process_peak_delta_bytes + cls.frame_0.nbytes + cls.frame_1.nbytes,
        )
        print(
            "S2MK_METRICS "
            + json.dumps(
                {
                    "qualification_id": QUALIFICATION_ID,
                    "process_peak_delta_bytes": cls.process_peak_delta_bytes,
                    "measured_peak_with_inputs_bytes": cls.measured_peak_with_inputs_bytes,
                    "owned_array_peak_bytes": cls.result.measurement.peak_owned_array_bytes,
                    "result_canonical_bytes": len(s2mk._canonical_bytes(cls.result.canonical_payload())),
                    "valid_correspondence_count": cls.result.measurement.valid_correspondence_count,
                    "forward_flow_digest": cls.result.measurement.forward_flow_digest,
                    "reverse_flow_digest": cls.result.measurement.reverse_flow_digest,
                },
                allow_nan=False,
                sort_keys=True,
            )
        )

    def test_01_qualified_runtime_binding(self) -> None:
        self.assertEqual(self.algorithm.python_version, "3.14.4")
        self.assertEqual(self.algorithm.opencv_version, "4.13.0")
        self.assertEqual(self.algorithm.numpy_version, "2.5.1")
        self.assertEqual(self.algorithm.thread_count, 1)
        self.assertFalse(self.algorithm.opencl_enabled)

    def test_02_rgb_to_y_uses_exact_integer_rule(self) -> None:
        levels = np.arange(256, dtype=np.uint8)
        grey = np.stack((levels, levels, levels), axis=1).reshape(1, 256, 3)
        self.assertTrue(np.array_equal(s2mk._rgb_to_y(grey), levels.reshape(1, 256)))
        colors = np.asarray([[[255, 0, 0], [0, 255, 0], [0, 0, 255], [17, 91, 203]]], dtype=np.uint8)
        expected = np.asarray(
            [[
                (77 * 255 + 128) >> 8,
                (150 * 255 + 128) >> 8,
                (29 * 255 + 128) >> 8,
                (77 * 17 + 150 * 91 + 29 * 203 + 128) >> 8,
            ]],
            dtype=np.uint8,
        )
        self.assertTrue(np.array_equal(s2mk._rgb_to_y(colors), expected))

    def test_03_flow_is_canonical_finite_float32(self) -> None:
        measurement = self.result.measurement
        self.assertRegex(measurement.forward_flow_digest, r"^[0-9a-f]{64}$")
        self.assertRegex(measurement.reverse_flow_digest, r"^[0-9a-f]{64}$")
        self.assertNotEqual(measurement.forward_flow_digest, measurement.reverse_flow_digest)
        self.assertEqual(measurement.magnitude.count, s2mk.PIXEL_COUNT)

    def test_04_bilinear_sampling_and_edges(self) -> None:
        source = np.asarray([[0.0, 2.0], [4.0, 6.0]], dtype=np.float32)
        x = np.asarray([0.0, 1.0, 0.5, 1.0], dtype=np.float32)
        y = np.asarray([0.0, 1.0, 0.5, 0.0], dtype=np.float32)
        actual = s2mk._bilinear_sample_points(source, x, y)
        expected = np.asarray([0.0, 6.0, 3.0, 2.0], dtype=np.float32)
        self.assertTrue(np.array_equal(actual, expected))
        with self.assertRaises(s2mk.S2MKMeasurementError):
            s2mk._bilinear_sample_points(source, np.asarray([2.0], dtype=np.float32), np.asarray([0.0], dtype=np.float32))

    def test_05_correspondence_cycle_and_rgb_residuals(self) -> None:
        measurement = self.result.measurement
        self.assertGreater(measurement.valid_correspondence_count, 0)
        self.assertLessEqual(measurement.valid_correspondence_count, s2mk.PIXEL_COUNT)
        self.assertEqual(measurement.cycle_residual.count, measurement.valid_correspondence_count)
        self.assertEqual(measurement.warped_rgb_residual.count, measurement.valid_correspondence_count)
        self.assertGreaterEqual(measurement.cycle_residual.mean, 0.0)
        self.assertGreaterEqual(measurement.warped_rgb_residual.mean, 0.0)

    def test_06_cells_cover_full_grid_once(self) -> None:
        cells = self.result.measurement.cells
        self.assertEqual(len(cells), 96)
        self.assertEqual(len({(cell.row, cell.column) for cell in cells}), 96)
        self.assertEqual(sum(cell.pixel_count for cell in cells), s2mk.PIXEL_COUNT)
        self.assertEqual(
            tuple((cell.row, cell.column) for cell in cells),
            tuple((row, column) for row in range(8) for column in range(12)),
        )

    def test_07_percentile_and_sum_rules_are_fixed(self) -> None:
        summary = s2mk._summary(np.asarray([0.0, 1.0, 2.0, 3.0], dtype=np.float32))
        self.assertEqual(summary.count, 4)
        self.assertEqual(summary.mean, 1.5)
        self.assertEqual(summary.median, 1.5)
        self.assertAlmostEqual(summary.p95, 2.85, places=12)
        self.assertEqual(summary.canonical_payload()["percentile_rule"], "NUMPY_LINEAR_V1")
        self.assertEqual(summary.canonical_payload()["summation_rule"], "NUMPY_C_ORDER_FLOAT64_SUM_V1")

    def test_08_baselines_are_independent_of_flow(self) -> None:
        with mock.patch.object(s2mk, "_calculate_flow", side_effect=AssertionError("flow called")):
            baseline = s2mk.compute_independent_baselines(self.frame_0, self.frame_1, self.pair)
        self.assertGreater(baseline.pixel_mean_l1, 0.0)
        self.assertGreater(baseline.receptor_mean_l1, 0.0)
        self.assertGreaterEqual(baseline.form_mean_l1, 0.0)
        self.assertEqual(len(baseline.pose_absolute_differences), 14)

    def test_09_output_contains_no_raw_or_flow_arrays(self) -> None:
        payload = self.result.canonical_payload()
        self.assertFalse(_contains_forbidden_payload(payload))
        self.assertFalse(payload["measurement"]["raw_frames_present"])
        self.assertFalse(payload["measurement"]["flow_fields_present"])
        self.assertLessEqual(len(s2mk._canonical_bytes(payload)), s2mk.MAX_RESULT_BYTES)

    def test_10_source_digest_mutation_fails_closed(self) -> None:
        broken = s2mk.VisualMotionPairV1(
            pair_id=self.pair.pair_id,
            frame_0_payload_digest="0" * 64,
            frame_1_payload_digest=self.pair.frame_1_payload_digest,
            visual_source_clock_id=self.pair.visual_source_clock_id,
            frame_0_window_start_tick=self.pair.frame_0_window_start_tick,
            frame_0_window_end_tick=self.pair.frame_0_window_end_tick,
            frame_1_window_start_tick=self.pair.frame_1_window_start_tick,
            frame_1_window_end_tick=self.pair.frame_1_window_end_tick,
            algorithm_binding_digest=self.algorithm.digest(),
        )
        with self.assertRaisesRegex(s2mk.S2MKMeasurementError, "payload digest"):
            s2mk.compute_independent_baselines(self.frame_0, self.frame_1, broken)

    def test_11_time_and_algorithm_binding_fail_closed(self) -> None:
        with self.assertRaisesRegex(s2mk.S2MKMeasurementError, "overlap or regress"):
            s2mk.VisualMotionPairV1(
                pair_id="neutral-pair-002",
                frame_0_payload_digest=self.pair.frame_0_payload_digest,
                frame_1_payload_digest=self.pair.frame_1_payload_digest,
                visual_source_clock_id=self.pair.visual_source_clock_id,
                frame_0_window_start_tick=0,
                frame_0_window_end_tick=10,
                frame_1_window_start_tick=9,
                frame_1_window_end_tick=20,
                algorithm_binding_digest=self.algorithm.digest(),
            )
        wrong_pair = s2mk.VisualMotionPairV1(
            pair_id="neutral-pair-003",
            frame_0_payload_digest=self.pair.frame_0_payload_digest,
            frame_1_payload_digest=self.pair.frame_1_payload_digest,
            visual_source_clock_id=self.pair.visual_source_clock_id,
            frame_0_window_start_tick=0,
            frame_0_window_end_tick=10,
            frame_1_window_start_tick=10,
            frame_1_window_end_tick=20,
            algorithm_binding_digest="1" * 64,
        )
        with self.assertRaisesRegex(s2mk.S2MKMeasurementError, "algorithm binding"):
            s2mk.measure_motion(self.frame_0, self.frame_1, wrong_pair, self.algorithm)

    def test_12_geometry_and_dtype_fail_closed(self) -> None:
        wrong_shape = np.zeros((10, 10, 3), dtype=np.uint8)
        with self.assertRaisesRegex(s2mk.S2MKMeasurementError, "geometry"):
            s2mk._validate_frame(wrong_shape, _payload_digest(wrong_shape), "wrong frame")
        wrong_type = np.zeros((s2mk.HEIGHT, s2mk.WIDTH, 3), dtype=np.float32)
        with self.assertRaisesRegex(s2mk.S2MKMeasurementError, "dtype"):
            s2mk._validate_frame(wrong_type, _payload_digest(wrong_type), "wrong frame")

    def test_13_malformed_flows_fail_closed(self) -> None:
        with self.assertRaisesRegex(s2mk.S2MKMeasurementError, "geometry"):
            s2mk._validate_flow(np.zeros((4, 5, 3), dtype=np.float32), height=4, width=5, role="bad flow")
        nonfinite = np.zeros((4, 5, 2), dtype=np.float32)
        nonfinite[0, 0, 0] = np.nan
        with self.assertRaisesRegex(s2mk.S2MKMeasurementError, "non-finite"):
            s2mk._validate_flow(nonfinite, height=4, width=5, role="bad flow")

    def test_14_import_and_corpus_boundaries_are_static(self) -> None:
        source_path = Path(s2mk.__file__).resolve()
        source = source_path.read_text(encoding="ascii")
        tree = ast.parse(source, filename=str(source_path))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        forbidden = ("memory", "context", "field_substrate", "neutral_local_field")
        self.assertFalse(any(any(token in name for token in forbidden) for name in imports))
        self.assertNotIn("_s2mj_private_presealed_motion_corpus", source)
        self.assertNotIn("reports/s2mj", source.replace("\\", "/"))

    def test_15_measured_peak_is_below_bound(self) -> None:
        self.assertLess(self.result.measurement.peak_owned_array_bytes, s2mk.MAX_PEAK_OWNED_ARRAY_BYTES)
        self.assertLess(self.measured_peak_with_inputs_bytes, s2mk.MAX_PEAK_OWNED_ARRAY_BYTES)


if __name__ == "__main__":
    unittest.main()
