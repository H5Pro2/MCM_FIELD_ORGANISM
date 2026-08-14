from __future__ import annotations

import importlib.util
import io
import json
from dataclasses import dataclass
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "run_live_adapter_timing_capability_audit.py"


def load_tool():
    package = types.ModuleType("mcm_field_organism")
    package.__path__ = []

    timing = types.ModuleType("mcm_field_organism.adapter_timing_capability")

    class AudioCallbackTiming:
        def __init__(self, adc, current, organism):
            self.input_buffer_adc_time_seconds = adc
            self.stream_current_time_seconds = current
            self.organism_callback_time_seconds = organism

    class VideoFrameTiming:
        pass

    timing.AudioCallbackTiming = AudioCallbackTiming
    timing.VideoFrameTiming = VideoFrameTiming
    @dataclass(frozen=True)
    class AudioAudit:
        callback_count: int

    @dataclass(frozen=True)
    class VideoAudit:
        frame_count: int = 0

    timing.audit_audio_callback_timing = lambda values, **kwargs: AudioAudit(
        callback_count=len(values)
    )
    timing.audit_video_frame_timing = lambda values, **kwargs: VideoAudit()

    finite_video = types.ModuleType("mcm_field_organism.finite_video_path")
    finite_video.VisualGridConfig = type("VisualGridConfig", (), {})
    spectral = types.ModuleType("mcm_field_organism.log_spectral_receptor")
    spectral.LogSpectralConfig = type(
        "LogSpectralConfig", (), {"sample_rate": 48_000, "hop_size": 480}
    )
    modules = {
        "mcm_field_organism": package,
        timing.__name__: timing,
        finite_video.__name__: finite_video,
        spectral.__name__: spectral,
    }
    spec = importlib.util.spec_from_file_location("audit_tool_under_test", TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return module


class LiveAdapterTimingAuditToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = load_tool()

    def capture(self, *, frames=(480, 480, 480), overflows=(False, False, False)):
        return self.tool.AudioTimingCapture(
            timings=tuple(
                self.tool.AudioCallbackTiming(index * 0.01, index * 0.01, index * 0.01)
                for index in range(3)
            ),
            callback_frame_counts=frames,
            input_overflow_flags=overflows,
            reported_input_latency_seconds=0.01,
            backend_id="TEST",
        )

    def test_complete_hop_metadata_is_accepted(self) -> None:
        self.tool.validate_audio_capture(self.capture(), expected_frame_count=480)

    def test_changed_callback_frame_count_aborts(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "differs from configured hop"):
            self.tool.validate_audio_capture(
                self.capture(frames=(480, 479, 480)), expected_frame_count=480
            )

    def test_input_overflow_aborts(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "input overflow"):
            self.tool.validate_audio_capture(
                self.capture(overflows=(False, True, False)), expected_frame_count=480
            )

    def test_host_blocksize_accepts_variable_callback_frames(self) -> None:
        self.tool.validate_audio_capture(
            self.capture(frames=(1440, 960, 1920)), expected_frame_count=None
        )

    def test_callback_forwards_actual_frames_and_overflow(self) -> None:
        callbacks = (
            (480, 1.00, 1.03, False),
            (479, 1.01, 1.04, True),
            (480, 1.02, 1.05, False),
        )

        class InputStream:
            latency = 0.03

            def __init__(self, **kwargs):
                self.callback = kwargs["callback"]
                type(self).blocksize = kwargs["blocksize"]

            def __enter__(self):
                for frames, adc, current, overflow in callbacks:
                    self.callback(
                        None,
                        frames,
                        types.SimpleNamespace(
                            inputBufferAdcTime=adc, currentTime=current
                        ),
                        types.SimpleNamespace(input_overflow=overflow),
                    )
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

        sounddevice = types.ModuleType("sounddevice")
        sounddevice.InputStream = InputStream
        sounddevice.get_portaudio_version = lambda: (1, "TEST-PORTAUDIO")
        with patch.dict(sys.modules, {"sounddevice": sounddevice}):
            result = self.tool.capture_audio_timing(
                device=7, callback_count=3, blocksize=0
            )
        self.assertEqual(0, InputStream.blocksize)
        self.assertEqual((480, 479, 480), result.callback_frame_counts)
        self.assertEqual((False, True, False), result.input_overflow_flags)
        self.assertEqual("TEST-PORTAUDIO", result.backend_id)

    def test_callback_metadata_preserves_raw_values_and_negative_deltas(self) -> None:
        capture = self.tool.AudioTimingCapture(
            timings=(
                self.tool.AudioCallbackTiming(1.00, 2.00, 3.00),
                self.tool.AudioCallbackTiming(0.99, 2.02, 3.03),
            ),
            callback_frame_counts=(480, 480),
            input_overflow_flags=(False, False),
            reported_input_latency_seconds=0.01,
            backend_id="TEST",
        )

        rows = self.tool.callback_metadata_rows(capture)

        self.assertEqual((0, 1), tuple(row["callback_index"] for row in rows))
        self.assertIsNone(rows[0]["adc_delta_seconds"])
        self.assertIsNone(rows[0]["stream_delta_seconds"])
        self.assertAlmostEqual(-0.01, rows[1]["adc_delta_seconds"])
        self.assertAlmostEqual(0.02, rows[1]["stream_delta_seconds"])
        self.assertEqual(0.99, rows[1]["input_buffer_adc_time_seconds"])
        self.assertEqual(2.02, rows[1]["stream_current_time_seconds"])
        self.assertEqual(3.03, rows[1]["organism_callback_time_seconds"])
        self.assertEqual(480, rows[1]["frame_count"])
        self.assertFalse(rows[1]["input_overflow"])

    def test_audio_only_does_not_open_video_and_emits_passive_metadata(self) -> None:
        argv = ["audit", "--audio-device", "7", "--audio-only", "--runs", "1"]
        output = io.StringIO()
        with (
            patch.object(sys, "argv", argv),
            patch.object(self.tool, "capture_audio_timing", return_value=self.capture()),
            patch.object(self.tool, "capture_video_timing") as video_capture,
            patch("sys.stdout", output),
        ):
            self.assertEqual(0, self.tool.main())
        video_capture.assert_not_called()
        result = json.loads(output.getvalue())
        self.assertEqual([480, 480, 480], result["runs"][0]["audio"]["callback_frame_counts"])
        self.assertEqual([False, False, False], result["runs"][0]["audio"]["input_overflow_flags"])
        callback_metadata = result["runs"][0]["audio"]["callback_metadata"]
        self.assertEqual([0, 1, 2], [row["callback_index"] for row in callback_metadata])
        self.assertIsNone(callback_metadata[0]["adc_delta_seconds"])
        self.assertAlmostEqual(0.01, callback_metadata[1]["adc_delta_seconds"])
        self.assertFalse(result["field_advance_performed"])
        self.assertFalse(result["support_mapping_applied"])

    def test_host_blocksize_is_forwarded_and_reported(self) -> None:
        argv = [
            "audit",
            "--audio-device",
            "7",
            "--audio-only",
            "--audio-blocksize",
            "0",
            "--runs",
            "1",
        ]
        output = io.StringIO()
        capture = self.capture(frames=(1440, 960, 1920))
        with (
            patch.object(sys, "argv", argv),
            patch.object(
                self.tool, "capture_audio_timing", return_value=capture
            ) as audio_capture,
            patch("sys.stdout", output),
        ):
            self.assertEqual(0, self.tool.main())
        audio_capture.assert_called_once_with(
            device=7, callback_count=20, blocksize=0
        )
        result = json.loads(output.getvalue())
        audio = result["runs"][0]["audio"]
        self.assertEqual(0, audio["configured_callback_blocksize"])
        self.assertEqual([1440, 960, 1920], audio["callback_frame_counts"])


if __name__ == "__main__":
    unittest.main()
