from __future__ import annotations

from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import unittest

from mcm_field_organism.four_node_fresh_manifest import (
    FourNodeFreshManifestError,
    load_four_node_fresh_manifest,
    parse_four_node_fresh_manifest,
)


MANIFEST_PATH = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "s1rk_four_node_fresh_manifest.json"
)


def _source() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


class FourNodeFreshManifestTests(unittest.TestCase):
    def test_registered_manifest_is_accepted(self) -> None:
        manifest = load_four_node_fresh_manifest(MANIFEST_PATH)
        self.assertEqual(
            "ae7a7356a3e06776a000b6e9fafef75b717944f1d75da62d4418be98cc439c68",
            manifest.manifest_digest,
        )

    def test_manifest_view_is_recursively_immutable(self) -> None:
        manifest = load_four_node_fresh_manifest(MANIFEST_PATH)
        with self.assertRaises(TypeError):
            manifest.root["schema_id"] = "changed"  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            manifest.root = {}  # type: ignore[misc]
        nodes = manifest.public_fresh_projection["payload"]["nodes"]  # type: ignore[index]
        self.assertIsInstance(nodes, tuple)

    def test_non_bytes_and_invalid_json_fail_closed(self) -> None:
        with self.assertRaisesRegex(FourNodeFreshManifestError, "FRESH_MANIFEST_BYTES_INVALID"):
            parse_four_node_fresh_manifest("not-bytes")  # type: ignore[arg-type]
        with self.assertRaisesRegex(FourNodeFreshManifestError, "FRESH_MANIFEST_BYTES_INVALID"):
            parse_four_node_fresh_manifest(b"{")

    def test_duplicate_and_unknown_root_keys_fail_closed(self) -> None:
        duplicate = b'{"schema_id":"a","schema_id":"b"}'
        with self.assertRaisesRegex(FourNodeFreshManifestError, "FRESH_MANIFEST_SHAPE_INVALID"):
            parse_four_node_fresh_manifest(duplicate)
        value = _source()
        value["unknown"] = None
        with self.assertRaisesRegex(FourNodeFreshManifestError, "FRESH_MANIFEST_SHAPE_INVALID"):
            parse_four_node_fresh_manifest(_encoded(value))

    def test_schema_identity_change_fails_closed(self) -> None:
        value = _source()
        value["schema_id"] = "mcm.changed"
        with self.assertRaisesRegex(FourNodeFreshManifestError, "FRESH_MANIFEST_SCHEMA_INVALID"):
            parse_four_node_fresh_manifest(_encoded(value))

    def test_common_payload_digest_change_fails_closed(self) -> None:
        value = _source()
        value["physical_geometry"]["payload"]["field_id"] = "mcm.changed"  # type: ignore[index]
        with self.assertRaisesRegex(FourNodeFreshManifestError, "FRESH_MANIFEST_DIGEST_INVALID"):
            parse_four_node_fresh_manifest(_encoded(value))

    def test_private_payload_digest_change_fails_closed(self) -> None:
        value = _source()
        value["private_fresh_states"][0]["payload"]["state_payload"][  # type: ignore[index]
            "base_rate_per_second"
        ] = 9.0
        with self.assertRaisesRegex(FourNodeFreshManifestError, "FRESH_MANIFEST_DIGEST_INVALID"):
            parse_four_node_fresh_manifest(_encoded(value))

    def test_role_axis_change_fails_closed(self) -> None:
        value = _source()
        value["private_fresh_states"][0]["position"] = 4  # type: ignore[index]
        with self.assertRaisesRegex(FourNodeFreshManifestError, "FRESH_MANIFEST_ROLE_AXIS_INVALID"):
            parse_four_node_fresh_manifest(_encoded(value))

    def test_dependency_change_fails_closed(self) -> None:
        value = _source()
        value["cross_identity_audit"]["model_role_count"] = 13  # type: ignore[index]
        with self.assertRaisesRegex(FourNodeFreshManifestError, "FRESH_MANIFEST_DEPENDENCY_INVALID"):
            parse_four_node_fresh_manifest(_encoded(value))

    def test_manifest_digest_change_fails_closed(self) -> None:
        value = _source()
        value["manifest_digest"] = "0" * 64
        with self.assertRaisesRegex(FourNodeFreshManifestError, "FRESH_MANIFEST_DIGEST_INVALID"):
            parse_four_node_fresh_manifest(_encoded(value))


if __name__ == "__main__":
    unittest.main()
