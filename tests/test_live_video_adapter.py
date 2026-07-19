from __future__ import annotations

from dataclasses import fields
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from mcm_field_organism import (
    CameraCaptureError,
    CameraStartupSummary,
    LocalChannelGridReceptor,
    OpenCVVideoFrameSource,
    VisualGridConfig,
    camera_startup_public_roles,
    capture_finite_video,
)


class FakeCapture:
    def __init__(self, frames: list[np.ndarray], *, opened: bool = True) -> None:
        self.frames = frames
        self.opened = opened
        self.cursor = 0
        self.released = False
        self.settings: dict[int, float] = {}

    def isOpened(self) -> bool:
        return self.opened

    def set(self, role: int, value: float) -> bool:
        self.settings[role] = float(value)
        return True

    def get(self, role: int) -> float:
        return self.settings[role]

    def read(self) -> tuple[bool, np.ndarray | None]:
        if self.cursor >= len(self.frames):
            return False, None
        frame = self.frames[self.cursor]
        self.cursor += 1
        return True, frame

    def release(self) -> None:
        self.released = True


def fake_cv2(capture: FakeCapture) -> SimpleNamespace:
    return SimpleNamespace(
        CAP_DSHOW=700,
        CAP_PROP_FRAME_WIDTH=3,
        CAP_PROP_FRAME_HEIGHT=4,
        CAP_PROP_FPS=5,
        CAP_PROP_FOURCC=6,
        VideoWriter_fourcc=lambda *characters: 1196444237,
        VideoCapture=lambda device, backend: capture,
    )


class IncrementingClock:
    def __init__(self, step: float) -> None:
        self.value = 0.0
        self.step = step

    def __call__(self) -> float:
        value = self.value
        self.value += self.step
        return value


class LiveVideoAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = VisualGridConfig(
            source_width=8,
            source_height=6,
            grid_columns=4,
            grid_rows=3,
            frames_per_second=25.0,
        )
        self.zero = np.zeros((6, 8, 3), dtype=np.uint8)
        self.light = np.full((6, 8, 3), 80, dtype=np.uint8)

    def source(self, startup: int = 1) -> OpenCVVideoFrameSource:
        return OpenCVVideoFrameSource(
            device_index=2,
            config=self.config,
            startup_frame_count=startup,
        )

    def test_device_and_startup_count_must_be_explicit_valid_values(self) -> None:
        invalid = (
            {"device_index": -1, "startup_frame_count": 0},
            {"device_index": True, "startup_frame_count": 0},
            {"device_index": 0, "startup_frame_count": -1},
            {"device_index": 0, "startup_frame_count": True},
        )
        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(CameraCaptureError):
                    OpenCVVideoFrameSource(config=self.config, **values)

    def test_missing_optional_dependency_blocks_before_device_creation(self) -> None:
        with patch.dict(sys.modules, {"cv2": None}):
            with self.assertRaisesRegex(CameraCaptureError, "not installed"):
                self.source().__enter__()

    def test_open_requests_exact_geometry_and_rate(self) -> None:
        capture = FakeCapture([self.zero])
        module = fake_cv2(capture)
        with patch.dict(sys.modules, {"cv2": module}):
            with self.source() as source:
                self.assertEqual(
                    {3: 8.0, 4: 6.0, 5: 25.0, 6: 1196444237.0},
                    capture.settings,
                )
                self.assertTrue(source.is_open)
        self.assertTrue(capture.released)

    def test_startup_frames_are_counted_but_not_exposed_as_capture(self) -> None:
        capture = FakeCapture([self.zero, self.light, self.light])
        module = fake_cv2(capture)
        source = OpenCVVideoFrameSource(
            device_index=2,
            config=self.config,
            startup_frame_count=2,
            clock=IncrementingClock(0.04),
        )
        with patch.dict(sys.modules, {"cv2": module}):
            with source:
                summary = source.prepare()
                frame = source.read_frame()
                self.assertEqual((1, 1), (summary.exact_zero_frames, summary.active_frames))
                self.assertAlmostEqual(25.0, summary.observed_frames_per_second)
                self.assertEqual(2, source.startup_frames_read)
                self.assertEqual(1, source.capture_frames_read)
                self.assertTrue(np.array_equal(self.light, frame))

    def test_prepare_is_required_and_cannot_be_repeated(self) -> None:
        capture = FakeCapture([self.zero, self.light])
        module = fake_cv2(capture)
        with patch.dict(sys.modules, {"cv2": module}):
            with self.source() as source:
                with self.assertRaisesRegex(CameraCaptureError, "prepared explicitly"):
                    source.read_frame()
                source.prepare()
                with self.assertRaisesRegex(CameraCaptureError, "already been consumed"):
                    source.prepare()

    def test_finite_receptor_capture_starts_after_startup_boundary(self) -> None:
        first = np.full((6, 8, 3), 40, dtype=np.uint8)
        second = np.full((6, 8, 3), 120, dtype=np.uint8)
        capture = FakeCapture([self.zero, first, second])
        module = fake_cv2(capture)
        with patch.dict(sys.modules, {"cv2": module}):
            with self.source() as source:
                source.prepare()
                summary = capture_finite_video(
                    source,
                    LocalChannelGridReceptor(self.config),
                    frame_count=2,
                )
                self.assertEqual(2, summary.input_frames)
                self.assertEqual(2, source.capture_frames_read)
                self.assertEqual(0, summary.active_zero_count)
                self.assertEqual(2, summary.active_light_count)

    def test_invalid_startup_frame_fails_at_exact_boundary(self) -> None:
        invalid = np.zeros((4, 4, 3), dtype=np.uint8)
        capture = FakeCapture([invalid])
        module = fake_cv2(capture)
        with patch.dict(sys.modules, {"cv2": module}):
            with self.source() as source:
                with self.assertRaisesRegex(CameraCaptureError, "startup frame 0"):
                    source.prepare()
        self.assertTrue(capture.released)

    def test_camera_open_failure_releases_backend(self) -> None:
        capture = FakeCapture([], opened=False)
        module = fake_cv2(capture)
        with patch.dict(sys.modules, {"cv2": module}):
            with self.assertRaisesRegex(CameraCaptureError, "cannot open"):
                self.source().__enter__()
        self.assertTrue(capture.released)

    def test_startup_summary_contains_no_raw_frame_role(self) -> None:
        forbidden = {"frame", "frames", "image", "pixels", "raw_frame", "file_path"}
        self.assertTrue(forbidden.isdisjoint(camera_startup_public_roles()))
        self.assertTrue(forbidden.isdisjoint(item.name for item in fields(CameraStartupSummary)))


if __name__ == "__main__":
    unittest.main()
