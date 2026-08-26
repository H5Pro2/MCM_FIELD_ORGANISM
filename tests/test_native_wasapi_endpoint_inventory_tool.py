from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
CAPTURE_PATH = ROOT / "tools" / "run_native_wasapi_capture_probe.py"
INVENTORY_PATH = ROOT / "tools" / "run_native_wasapi_endpoint_inventory.py"


def load_tool():
    capture_spec = importlib.util.spec_from_file_location(
        "run_native_wasapi_capture_probe", CAPTURE_PATH
    )
    capture = importlib.util.module_from_spec(capture_spec)
    sys.modules[capture_spec.name] = capture
    capture_spec.loader.exec_module(capture)
    inventory_spec = importlib.util.spec_from_file_location(
        "native_wasapi_endpoint_inventory_under_test", INVENTORY_PATH
    )
    inventory = importlib.util.module_from_spec(inventory_spec)
    sys.modules[inventory_spec.name] = inventory
    inventory_spec.loader.exec_module(inventory)
    return inventory


class NativeWasapiEndpointInventoryToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = load_tool()

    def sounddevice_module(self):
        module = types.ModuleType("sounddevice")
        module.query_devices = lambda index: {
            "name": "Microphone (C920)",
            "hostapi": 2,
            "max_input_channels": 2,
            "max_output_channels": 0,
            "default_samplerate": 48_000.0,
            "default_low_input_latency": 0.01,
            "default_high_input_latency": 0.04,
        }
        module.query_hostapis = lambda index: {"name": "Windows DirectSound"}
        return module

    def native_rows(self):
        return (
            self.tool.NativeEndpointInventoryRow(
                endpoint_id="{NATIVE-C920-ID}",
                display_name="Microphone (C920)",
                data_flow="capture",
                device_state=1,
                default_roles=("communications",),
                mix_format_channels=2,
                mix_format_sample_rate_hz=48_000,
                mix_format_bits_per_sample=32,
            ),
        )

    def test_sounddevice_metadata_is_copied_without_endpoint_selection(self) -> None:
        row = self.tool.sounddevice_inventory_row(self.sounddevice_module())
        self.assertEqual(5, row.index)
        self.assertEqual("Microphone (C920)", row.name)
        self.assertEqual("Windows DirectSound", row.hostapi_name)
        self.assertEqual(2, row.max_input_channels)
        self.assertEqual(48_000.0, row.default_samplerate)

    def test_document_keeps_native_and_sounddevice_inventories_separate(self) -> None:
        sounddevice_row = self.tool.sounddevice_inventory_row(
            self.sounddevice_module()
        )
        result = self.tool.inventory_document(self.native_rows(), sounddevice_row)
        self.assertEqual(
            "{NATIVE-C920-ID}",
            result["native_active_capture_endpoints"][0]["endpoint_id"],
        )
        self.assertEqual(5, result["sounddevice_comparison_device"]["index"])
        self.assertEqual(
            "UNDECIDED_REQUIRES_EXPLICIT_REVIEW", result["mapping_decision"]
        )
        self.assertFalse(result["automatic_endpoint_selection_performed"])

    def test_document_denies_stream_packet_support_and_field_actions(self) -> None:
        result = self.tool.inventory_document(
            self.native_rows(),
            self.tool.sounddevice_inventory_row(self.sounddevice_module()),
        )
        self.assertFalse(result["audio_client_initialize_called"])
        self.assertFalse(result["stream_start_called"])
        self.assertFalse(result["packet_capture_performed"])
        self.assertFalse(result["support_mapping_applied"])
        self.assertFalse(result["field_advance_performed"])

    def test_explicit_review_reports_one_local_metadata_match(self) -> None:
        result = self.tool.inventory_document(
            self.native_rows(),
            self.tool.sounddevice_inventory_row(self.sounddevice_module()),
            run_number=159,
            review_mapping=True,
        )
        self.assertEqual(159, result["run_number"])
        self.assertEqual(
            "LOCALLY_UNIQUE_METADATA_MATCH_NOT_API_IDENTITY",
            result["mapping_decision"],
        )
        self.assertEqual(
            "{NATIVE-C920-ID}", result["mapping_review"]["mapped_endpoint_id"]
        )
        self.assertFalse(result["mapping_review"]["evidence"]["api_identity_proven"])

    def test_explicit_review_rejects_ambiguous_metadata_matches(self) -> None:
        duplicate = self.tool.NativeEndpointInventoryRow(
            endpoint_id="{SECOND-C920-ID}",
            display_name="Microphone (C920)",
            data_flow="capture",
            device_state=1,
            default_roles=(),
            mix_format_channels=2,
            mix_format_sample_rate_hz=16_000,
            mix_format_bits_per_sample=32,
        )
        result = self.tool.inventory_document(
            self.native_rows() + (duplicate,),
            self.tool.sounddevice_inventory_row(self.sounddevice_module()),
            run_number=159,
            review_mapping=True,
        )
        self.assertEqual("NOT_UNIQUELY_MAPPABLE", result["mapping_decision"])
        self.assertIsNone(result["mapping_review"]["mapped_endpoint_id"])
        self.assertEqual(2, result["mapping_review"]["evidence"]["candidate_count"])

    def test_main_emits_inventory_without_automatic_mapping(self) -> None:
        sounddevice = self.sounddevice_module()
        inventory = types.SimpleNamespace(collect=lambda: self.native_rows())
        output = io.StringIO()
        with (
            patch.dict(sys.modules, {"sounddevice": sounddevice}),
            patch.object(self.tool, "NativeEndpointInventory", return_value=inventory),
            patch("sys.stdout", output),
        ):
            self.assertEqual(0, self.tool.main())
        result = json.loads(output.getvalue())
        self.assertEqual(120, result["run_number"])
        self.assertFalse(result["packet_capture_performed"])
        self.assertEqual(
            "UNDECIDED_REQUIRES_EXPLICIT_REVIEW", result["mapping_decision"]
        )


if __name__ == "__main__":
    unittest.main()
