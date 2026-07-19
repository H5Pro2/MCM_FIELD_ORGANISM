"""Explicit finite OpenCV camera source with a visible startup boundary."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
import time
from typing import Any, Callable

import numpy as np

from .finite_video_path import VisualGridConfig


class CameraCaptureError(RuntimeError):
    """Raised when a camera cannot satisfy the finite source contract."""


@dataclass(frozen=True, slots=True)
class CameraStartupSummary:
    """Technical startup result without retained or exposed raw frames."""

    device_index: int
    requested_frames: int
    consumed_frames: int
    exact_zero_frames: int
    active_frames: int
    reported_width: float
    reported_height: float
    reported_frames_per_second: float
    observed_frames_per_second: float | None = None

    def __post_init__(self) -> None:
        observed = self.observed_frames_per_second
        if observed is not None:
            value = float(observed)
            if not math.isfinite(value) or value <= 0.0:
                raise CameraCaptureError(
                    "observed_frames_per_second must be finite and positive"
                )
            object.__setattr__(self, "observed_frames_per_second", value)


def _positive_finite(value: object, role: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise CameraCaptureError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result <= 0.0:
        raise CameraCaptureError(f"{role} must be finite and greater than zero")
    return result


class OpenCVVideoFrameSource:
    """Optional S1 source that never guesses a device or hides startup reads."""

    def __init__(
        self,
        *,
        device_index: int,
        config: VisualGridConfig,
        startup_frame_count: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if isinstance(device_index, bool) or not isinstance(device_index, int) or device_index < 0:
            raise CameraCaptureError("device_index must be an explicit non-negative integer")
        if not isinstance(config, VisualGridConfig):
            raise CameraCaptureError("config must be a VisualGridConfig")
        if (
            isinstance(startup_frame_count, bool)
            or not isinstance(startup_frame_count, int)
            or startup_frame_count < 0
        ):
            raise CameraCaptureError("startup_frame_count must be a non-negative integer")
        self.device_index = device_index
        self.config = config
        self.startup_frame_count = startup_frame_count
        if not callable(clock):
            raise CameraCaptureError("clock must be callable")
        self._clock = clock
        self._capture: Any | None = None
        self._cv2: Any | None = None
        self._prepared = False
        self._startup_frames_read = 0
        self._capture_frames_read = 0

    @property
    def startup_frames_read(self) -> int:
        return self._startup_frames_read

    @property
    def capture_frames_read(self) -> int:
        return self._capture_frames_read

    @property
    def is_open(self) -> bool:
        return self._capture is not None

    @property
    def is_prepared(self) -> bool:
        return self._prepared

    def __enter__(self) -> "OpenCVVideoFrameSource":
        if self._capture is not None:
            raise CameraCaptureError("camera source is already open")
        try:
            import cv2  # type: ignore[import-not-found]
        except ImportError as exc:
            raise CameraCaptureError("optional dependency 'opencv-python' is not installed") from exc

        capture = None
        try:
            capture = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
            if not capture.isOpened():
                raise CameraCaptureError(
                    f"cannot open explicit camera device {self.device_index}"
                )
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.source_width)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.source_height)
            capture.set(cv2.CAP_PROP_FPS, self.config.frames_per_second)
            capture.set(
                cv2.CAP_PROP_FOURCC,
                cv2.VideoWriter_fourcc(*"MJPG"),
            )
        except Exception as exc:
            if capture is not None:
                capture.release()
            if isinstance(exc, CameraCaptureError):
                raise
            raise CameraCaptureError(
                f"cannot configure explicit camera device {self.device_index}"
            ) from exc

        self._capture = capture
        self._cv2 = cv2
        self._prepared = False
        self._startup_frames_read = 0
        self._capture_frames_read = 0
        return self

    def _read_valid_frame(self, role: str) -> np.ndarray:
        if self._capture is None:
            raise CameraCaptureError("camera source is not open")
        try:
            ok, frame = self._capture.read()
        except Exception as exc:
            raise CameraCaptureError(f"{role} read failed") from exc
        if not ok or frame is None:
            raise CameraCaptureError(f"{role} read failed")
        if not isinstance(frame, np.ndarray):
            raise CameraCaptureError(f"{role} must be a numpy array")
        expected_shape = (
            self.config.source_height,
            self.config.source_width,
            3,
        )
        if frame.shape != expected_shape:
            raise CameraCaptureError(
                f"{role} must have exact shape {expected_shape}, got {frame.shape}"
            )
        if frame.dtype != np.uint8:
            raise CameraCaptureError(f"{role} must use uint8 channel values")
        stored = np.array(frame, copy=True)
        stored.setflags(write=False)
        return stored

    def prepare(self) -> CameraStartupSummary:
        """Consume exactly the declared startup phase before receptor capture."""

        if self._capture is None or self._cv2 is None:
            raise CameraCaptureError("camera source is not open")
        if self._prepared or self._startup_frames_read:
            raise CameraCaptureError("camera startup phase has already been consumed")

        zero_count = 0
        completion_times = []
        for frame_index in range(self.startup_frame_count):
            frame = self._read_valid_frame(f"startup frame {frame_index}")
            completion_times.append(float(self._clock()))
            zero_count += 1 if not np.any(frame) else 0
            self._startup_frames_read += 1

        observed_rate = None
        if len(completion_times) >= 2:
            elapsed = completion_times[-1] - completion_times[0]
            if not math.isfinite(elapsed) or elapsed <= 0.0:
                raise CameraCaptureError(
                    "camera startup clock must advance between completed frames"
                )
            observed_rate = (len(completion_times) - 1) / elapsed

        self._prepared = True
        capture = self._capture
        cv2 = self._cv2
        return CameraStartupSummary(
            device_index=self.device_index,
            requested_frames=self.startup_frame_count,
            consumed_frames=self._startup_frames_read,
            exact_zero_frames=zero_count,
            active_frames=self._startup_frames_read - zero_count,
            reported_width=_positive_finite(
                capture.get(cv2.CAP_PROP_FRAME_WIDTH),
                "reported_width",
            ),
            reported_height=_positive_finite(
                capture.get(cv2.CAP_PROP_FRAME_HEIGHT),
                "reported_height",
            ),
            reported_frames_per_second=_positive_finite(
                capture.get(cv2.CAP_PROP_FPS),
                "reported_frames_per_second",
            ),
            observed_frames_per_second=observed_rate,
        )

    def read_frame(self) -> np.ndarray:
        if not self._prepared:
            raise CameraCaptureError("camera startup phase must be prepared explicitly")
        frame = self._read_valid_frame(f"capture frame {self._capture_frames_read}")
        self._capture_frames_read += 1
        return frame

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        capture = self._capture
        self._capture = None
        self._cv2 = None
        self._prepared = False
        if capture is not None:
            capture.release()


def camera_startup_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(CameraStartupSummary))
