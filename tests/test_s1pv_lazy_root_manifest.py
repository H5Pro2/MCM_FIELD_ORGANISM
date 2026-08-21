from __future__ import annotations

import hashlib
from importlib import import_module
import json
from pathlib import Path
import sys
import unittest

import mcm_field_organism as root_api
from mcm_field_organism import root_lazy_exports


INVENTORY_PATH = (
    Path(__file__).parents[1] / "docs" / "S1PT_ROOT_EXPORT_INVENTORY_V1.json"
)


def _inventory() -> dict[str, object]:
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _project_modules() -> set[str]:
    return {
        name
        for name in sys.modules
        if name == "mcm_field_organism" or name.startswith("mcm_field_organism.")
    }


class S1PVLazyRootManifestTests(unittest.TestCase):
    def test_01_generated_mapping_matches_all_s1pt_records(self) -> None:
        records = _inventory()["records"]
        expected_exports = {
            record["export_name"]: (
                record["source_module"],
                record["source_attribute"],
            )
            for record in records
        }
        expected_classes = {
            record["export_name"]: record["surface_class"] for record in records
        }
        self.assertEqual(expected_exports, dict(root_lazy_exports.ROOT_LAZY_EXPORTS))
        self.assertEqual(
            expected_classes,
            dict(root_lazy_exports.ROOT_SURFACE_CLASSES),
        )

    def test_02_root_all_preserves_bound_content_order_and_digest(self) -> None:
        inventory = _inventory()
        expected = inventory["root_all"]
        self.assertEqual(expected, list(root_lazy_exports.ROOT_ALL))
        self.assertEqual(expected, root_api.__all__)
        digest = hashlib.sha256(_canonical_json_bytes(expected)).hexdigest()
        self.assertEqual(root_lazy_exports.S1PT_ROOT_ALL_SHA256, digest)

    def test_03_generated_name_sets_are_complete_unique_and_equal(self) -> None:
        root_all = root_lazy_exports.ROOT_ALL
        export_names = set(root_lazy_exports.ROOT_LAZY_EXPORTS)
        class_names = set(root_lazy_exports.ROOT_SURFACE_CLASSES)
        self.assertEqual(1267, len(root_all))
        self.assertEqual(1267, len(set(root_all)))
        self.assertEqual(set(root_all), export_names)
        self.assertEqual(export_names, class_names)

    def test_04_unknown_name_raises_without_loading_project_module(self) -> None:
        before = _project_modules()
        with self.assertRaisesRegex(
            AttributeError,
            "has no attribute 'S1PV_UNKNOWN_ROOT_NAME'",
        ):
            getattr(root_api, "S1PV_UNKNOWN_ROOT_NAME")
        self.assertEqual(before, _project_modules())

    def test_05_dir_is_complete_sorted_and_import_free(self) -> None:
        before = _project_modules()
        visible = dir(root_api)
        self.assertEqual(sorted(visible), visible)
        self.assertTrue(set(root_api.__all__).issubset(visible))
        self.assertEqual(before, _project_modules())

    def test_06_repeated_access_uses_cached_identical_object(self) -> None:
        first = root_api.SharedMCMField
        second = root_api.SharedMCMField
        source = import_module("mcm_field_organism.shared_mcm_field")
        self.assertIs(first, second)
        self.assertIs(first, source.SharedMCMField)
        self.assertIs(first, root_api.__dict__["SharedMCMField"])

    def test_07_current_api_additive_names_do_not_expand_root_all(self) -> None:
        inventory = _inventory()
        additive = set(inventory["current_api_names_not_in_root"]["active"])
        additive.update(inventory["current_api_names_not_in_root"]["reference"])
        self.assertEqual(43, len(additive))
        self.assertTrue(additive.isdisjoint(root_api.__all__))
        self.assertTrue(additive.isdisjoint(root_lazy_exports.ROOT_LAZY_EXPORTS))

    def test_08_all_root_exports_preserve_source_object_identity(self) -> None:
        for record in _inventory()["records"]:
            with self.subTest(export_name=record["export_name"]):
                source = import_module(
                    f"mcm_field_organism.{record['source_module']}"
                )
                expected = getattr(source, record["source_attribute"])
                self.assertIs(expected, getattr(root_api, record["export_name"]))


if __name__ == "__main__":
    unittest.main()
