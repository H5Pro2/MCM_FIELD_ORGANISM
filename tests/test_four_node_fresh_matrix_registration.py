from __future__ import annotations

from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import unittest

from mcm_field_organism.four_node_fresh_manifest import FourNodeFreshManifest
from mcm_field_organism.four_node_fresh_matrix_registration import (
    FourNodeFreshMatrixRegistrationError,
    load_four_node_fresh_matrix_registration,
    parse_four_node_fresh_matrix_registration,
    validate_four_node_fresh_matrix_registration_against_manifest,
)
from mcm_field_organism.four_node_fresh_manifest import load_four_node_fresh_manifest


ROOT = Path(__file__).resolve().parents[1]
REGISTRATION_PATH = ROOT / "reports" / "s1sd_four_node_fresh_matrix_registration.json"
MANIFEST_PATH = ROOT / "reports" / "s1rk_four_node_fresh_manifest.json"


def _source() -> dict[str, object]:
    return json.loads(REGISTRATION_PATH.read_text(encoding="utf-8"))


def _encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


class FourNodeFreshMatrixRegistrationTests(unittest.TestCase):
    def test_registered_matrix_is_accepted(self) -> None:
        registration = load_four_node_fresh_matrix_registration(REGISTRATION_PATH)
        self.assertEqual(
            "edd3414b3dcc082c0ab7bec66f8dd278cedecd76d11e649ca7aff46a9317a4ba",
            registration.registration_digest,
        )
        self.assertEqual(17, len(registration.replica_roles))
        self.assertEqual("U_FRESH_B_EARLY", registration.replica_roles[-2])
        self.assertEqual("U_FRESH_B_LATE", registration.replica_roles[-1])

    def test_registration_view_is_recursively_immutable(self) -> None:
        registration = load_four_node_fresh_matrix_registration(REGISTRATION_PATH)
        with self.assertRaises(TypeError):
            registration.root["schema_id"] = "changed"  # type: ignore[index]
        with self.assertRaises(FrozenInstanceError):
            registration.root = {}  # type: ignore[misc]
        self.assertIsInstance(registration.root["exposure_replica_axis"], tuple)

    def test_invalid_bytes_json_and_duplicate_keys_fail_closed(self) -> None:
        for value in ("not-bytes", b"{"):
            with self.assertRaisesRegex(
                FourNodeFreshMatrixRegistrationError,
                "FRESH_MATRIX_REGISTRATION_BYTES_INVALID",
            ):
                parse_four_node_fresh_matrix_registration(value)  # type: ignore[arg-type]
        duplicate = b'{"schema_id":"a","schema_id":"b"}'
        with self.assertRaisesRegex(
            FourNodeFreshMatrixRegistrationError,
            "FRESH_MATRIX_REGISTRATION_SHAPE_INVALID",
        ):
            parse_four_node_fresh_matrix_registration(duplicate)

    def test_unknown_missing_and_changed_schema_fields_fail_closed(self) -> None:
        for mutation in ("unknown", "missing", "schema"):
            value = _source()
            if mutation == "unknown":
                value["unknown"] = None
            elif mutation == "missing":
                value.pop("source_contract_id")
            else:
                value["schema_id"] = "mcm.changed"
            with self.assertRaises(FourNodeFreshMatrixRegistrationError):
                parse_four_node_fresh_matrix_registration(_encoded(value))

    def test_registration_digest_change_fails_closed(self) -> None:
        value = _source()
        value["registration_digest"] = "0" * 64
        with self.assertRaisesRegex(
            FourNodeFreshMatrixRegistrationError,
            "FRESH_MATRIX_REGISTRATION_DIGEST_INVALID",
        ):
            parse_four_node_fresh_matrix_registration(_encoded(value))

    def test_replica_axis_order_duplicate_and_length_fail_closed(self) -> None:
        for mutation in ("order", "duplicate", "length"):
            value = _source()
            axis = value["exposure_replica_axis"]  # type: ignore[assignment]
            if mutation == "order":
                axis[0], axis[1] = axis[1], axis[0]  # type: ignore[index]
            elif mutation == "duplicate":
                axis[1] = axis[0]  # type: ignore[index]
            else:
                axis.pop()  # type: ignore[union-attr]
            with self.assertRaisesRegex(
                FourNodeFreshMatrixRegistrationError,
                "FRESH_MATRIX_REGISTRATION_REPLICA_AXIS_INVALID",
            ):
                parse_four_node_fresh_matrix_registration(_encoded(value))

    def test_matrix_cardinality_change_fails_closed(self) -> None:
        for key, changed in (
            ("exposure_replica_count", 16),
            ("matrix_cell_count", 224),
            ("total_checkpoint_count", 532),
        ):
            value = _source()
            value["matrix_cardinality"][key] = changed  # type: ignore[index]
            with self.assertRaisesRegex(
                FourNodeFreshMatrixRegistrationError,
                "FRESH_MATRIX_REGISTRATION_CARDINALITY_INVALID",
            ):
                parse_four_node_fresh_matrix_registration(_encoded(value))

    def test_base_identity_change_fails_closed(self) -> None:
        value = _source()
        value["base_fresh_manifest"]["manifest_digest"] = "0" * 64  # type: ignore[index]
        with self.assertRaisesRegex(
            FourNodeFreshMatrixRegistrationError,
            "FRESH_MATRIX_REGISTRATION_BASE_IDENTITY_INVALID",
        ):
            parse_four_node_fresh_matrix_registration(_encoded(value))

    def test_public_binding_change_fails_closed(self) -> None:
        value = _source()
        value["public_fresh_projection_binding"]["shared_matrix_cell_count"] = 224  # type: ignore[index]
        with self.assertRaisesRegex(
            FourNodeFreshMatrixRegistrationError,
            "FRESH_MATRIX_REGISTRATION_CARDINALITY_INVALID",
        ):
            parse_four_node_fresh_matrix_registration(_encoded(value))

    def test_registration_matches_validated_v1_manifest(self) -> None:
        registration = load_four_node_fresh_matrix_registration(REGISTRATION_PATH)
        manifest = load_four_node_fresh_manifest(MANIFEST_PATH)
        self.assertIsNone(
            validate_four_node_fresh_matrix_registration_against_manifest(
                registration,
                manifest,
            )
        )

    def test_unvalidated_manifest_is_rejected(self) -> None:
        registration = load_four_node_fresh_matrix_registration(REGISTRATION_PATH)
        forged = FourNodeFreshManifest({"manifest_digest": "0" * 64})
        with self.assertRaisesRegex(
            FourNodeFreshMatrixRegistrationError,
            "FRESH_MATRIX_REGISTRATION_MANIFEST_MISMATCH",
        ):
            validate_four_node_fresh_matrix_registration_against_manifest(
                registration,
                forged,
            )


if __name__ == "__main__":
    unittest.main()
