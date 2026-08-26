from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "run_native_wasapi_capture_probe.py"


def load_tool():
    spec = importlib.util.spec_from_file_location(
        "native_wasapi_capture_probe_under_test", TOOL_PATH
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SyntheticBackend:
    def __init__(self, tool, packets):
        self.endpoint = tool.EndpointMetadata(
            "{EXPLICIT-ENDPOINT-ID}", "Synthetic Capture", "capture", 1
        )
        self.packets = iter(packets)
        self.opened = False
        self.closed = False

    def open(self):
        self.opened = True

    def next_packet(self):
        return next(self.packets)

    def close(self):
        self.closed = True


class NativeWasapiCaptureProbeToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = load_tool()

    def packet(self, index, *, frames=480, device=None, qpc=None, flags=0):
        return self.tool.NativePacket(
            packet_index=index,
            frame_count=frames,
            device_position=index * frames if device is None else device,
            qpc_position_100ns=(index + 1) * 100_000 if qpc is None else qpc,
            flags=flags,
            get_buffer_hresult=0,
            release_buffer_hresult=0,
        )

    def test_exact_contiguous_raw_sequence_is_accepted(self) -> None:
        packets = tuple(self.packet(index) for index in range(3))
        self.tool.validate_packet_sequence(packets, expected_count=3)

    def test_device_position_gap_is_rejected_without_tolerance(self) -> None:
        packets = (self.packet(0), self.packet(1, device=481))
        with self.assertRaisesRegex(
            self.tool.ProbeContractError, "not packet-contiguous"
        ):
            self.tool.validate_packet_sequence(packets, expected_count=2)

    def test_non_monotonic_qpc_is_rejected(self) -> None:
        packets = (self.packet(0), self.packet(1, qpc=100_000))
        with self.assertRaisesRegex(self.tool.ProbeContractError, "QPC"):
            self.tool.validate_packet_sequence(packets, expected_count=2)

    def test_discontinuity_and_timestamp_error_are_rejected(self) -> None:
        for flag, message in (
            (self.tool.AUDCLNT_BUFFERFLAGS_DATA_DISCONTINUITY, "DISCONTINUITY"),
            (self.tool.AUDCLNT_BUFFERFLAGS_TIMESTAMP_ERROR, "TIMESTAMP_ERROR"),
        ):
            with self.subTest(flag=flag):
                with self.assertRaisesRegex(self.tool.ProbeContractError, message):
                    self.tool.validate_packet_sequence(
                        (self.packet(0, flags=flag),), expected_count=1
                    )

    def test_silent_flag_is_preserved_and_accepted(self) -> None:
        packet = self.packet(0, flags=self.tool.AUDCLNT_BUFFERFLAGS_SILENT)
        self.tool.validate_packet_sequence((packet,), expected_count=1)
        self.assertEqual(self.tool.AUDCLNT_BUFFERFLAGS_SILENT, packet.flags)

    def test_zero_frames_and_failed_release_are_rejected(self) -> None:
        with self.assertRaisesRegex(self.tool.ProbeContractError, "zero frames"):
            self.tool.validate_packet_sequence(
                (self.packet(0, frames=0),), expected_count=1
            )
        failed = self.tool.NativePacket(0, 480, 0, 100_000, 0, 0, 0x80004005)
        with self.assertRaisesRegex(self.tool.ProbeContractError, "ReleaseBuffer"):
            self.tool.validate_packet_sequence((failed,), expected_count=1)

    def test_capture_uses_fixed_limit_and_closes_backend(self) -> None:
        packets = tuple(self.packet(index) for index in range(self.tool.PACKET_LIMIT))
        backend = SyntheticBackend(self.tool, packets)
        result = self.tool.capture_packets(
            backend, clock=lambda: 0.0, sleep=lambda _: None
        )
        self.assertEqual(self.tool.PACKET_LIMIT, len(result))
        self.assertTrue(backend.opened)
        self.assertTrue(backend.closed)

    def test_capture_abort_preserves_raw_packets_received_before_failure(self) -> None:
        packets = (self.packet(0), self.packet(1, device=481))
        backend = SyntheticBackend(self.tool, packets)
        with self.assertRaisesRegex(
            self.tool.ProbeRunError, "not packet-contiguous"
        ) as error:
            self.tool.capture_packets(
                backend, clock=lambda: 0.0, sleep=lambda _: None
            )
        self.assertEqual(packets, error.exception.packets)
        self.assertTrue(backend.closed)

    def test_result_document_denies_support_and_field_actions(self) -> None:
        endpoint = self.tool.EndpointMetadata("id", "name", "capture", 1)
        result = self.tool.result_document(
            endpoint=endpoint,
            packets=(self.packet(0),),
            decision="PAKETPOSITION_KANDIDAT",
            end_reason="packet_limit_reached",
        )
        self.assertEqual(48_000, result["requested_format"]["sample_rate_hz"])
        self.assertFalse(result["audio_payload_retained"])
        self.assertFalse(result["support_mapping_applied"])
        self.assertFalse(result["field_advance_performed"])

    def test_cli_requires_explicit_endpoint_id(self) -> None:
        with patch.object(sys, "argv", ["probe"]):
            with self.assertRaises(SystemExit) as error:
                self.tool.main()
        self.assertEqual(2, error.exception.code)

    def test_cli_emits_only_preregistered_fixed_configuration(self) -> None:
        backend = SyntheticBackend(self.tool, ())
        packets = tuple(self.packet(index) for index in range(self.tool.PACKET_LIMIT))
        output = io.StringIO()
        with (
            patch.object(sys, "argv", ["probe", "--endpoint-id", "{ID}"]),
            patch.object(self.tool, "NativeWasapiBackend", return_value=backend),
            patch.object(self.tool, "capture_packets", return_value=packets),
            patch("sys.stdout", output),
        ):
            self.assertEqual(0, self.tool.main())
        result = json.loads(output.getvalue())
        self.assertEqual("PAKETPOSITION_KANDIDAT", result["decision"])
        self.assertEqual(100, result["packet_limit"])
        self.assertEqual(10.0, result["timeout_seconds"])
        self.assertEqual("float32", result["requested_format"]["sample_format"])
        self.assertFalse(result["support_mapping_applied"])


if __name__ == "__main__":
    unittest.main()
