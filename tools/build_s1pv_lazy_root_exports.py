"""Generate the S1-PV lazy root table without importing project modules."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from pprint import pformat


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "mcm_field_organism"
INVENTORY_PATH = ROOT / "docs" / "S1PT_ROOT_EXPORT_INVENTORY_V1.json"
CURRENT_API_PATH = PACKAGE / "current_api.py"
OUTPUT_PATH = PACKAGE / "root_lazy_exports.py"

EXPECTED_CONTRACT_ID = "mcm.s1pt.root_export_inventory.v1"
EXPECTED_ROOT_SOURCE_SHA256 = (
    "f69cc32fbe7a26a4db6355e87a8b09a6456a2d2839c5036415e0d54d395f39ab"
)
EXPECTED_ROOT_ALL_SHA256 = (
    "4fdf82f4fe480e3180a6447987684093e2336837a329b95ce33b3069beb62639"
)
EXPECTED_SORTED_RECORDS_SHA256 = (
    "d783c5a0d29782c2b8f10d93ba2d048cef4c83468900e1e553050f0d84196cc1"
)
EXPECTED_CURRENT_API_SOURCE_SHA256 = (
    "01daabe43dd52766014926f3ee30d55cd390d9d3ed6651a7bd3664997caa0360"
)
EXPECTED_CURRENT_API_MODULES_SHA256 = (
    "26a6787cb3168074bf48a283dc247e653a8285fc2cba496a263227d50389946b"
)
EXPECTED_CURRENT_API_EDGES_SHA256 = (
    "bcd270da8683c02819cf6db9560eda249c0bed42c3ec4a8b846b51c1b6e5d7f9"
)


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _current_api_graph() -> tuple[list[str], list[tuple[str, str]]]:
    seen: set[str] = set()
    edges: set[tuple[str, str]] = set()
    pending = ["current_api"]
    while pending:
        module_name = pending.pop()
        if module_name in seen:
            continue
        path = PACKAGE.joinpath(*module_name.split(".")).with_suffix(".py")
        if not path.is_file():
            raise RuntimeError(f"missing local module {module_name!r}: {path}")
        seen.add(module_name)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.level != 1 or not node.module:
                continue
            dependency = node.module
            dependency_path = PACKAGE.joinpath(*dependency.split(".")).with_suffix(
                ".py"
            )
            if not dependency_path.is_file():
                continue
            edges.add((module_name, dependency))
            pending.append(dependency)
    return sorted(seen), sorted(edges)


def _validated_inventory() -> tuple[list[str], list[dict[str, str]]]:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    if inventory.get("contract_id") != EXPECTED_CONTRACT_ID:
        raise RuntimeError("unexpected S1-PT contract id")
    digests = inventory.get("digests")
    if not isinstance(digests, dict):
        raise RuntimeError("missing S1-PT digest object")
    if digests.get("root_source_sha256") != EXPECTED_ROOT_SOURCE_SHA256:
        raise RuntimeError("unexpected bound root source digest")

    root_all = inventory.get("root_all")
    records = inventory.get("records")
    if not isinstance(root_all, list) or not all(isinstance(item, str) for item in root_all):
        raise RuntimeError("S1-PT root_all must be a list of strings")
    if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
        raise RuntimeError("S1-PT records must be a list of objects")
    if len(root_all) != 1267 or len(set(root_all)) != 1267:
        raise RuntimeError("S1-PT root_all cardinality changed")
    if len(records) != 1267:
        raise RuntimeError("S1-PT record cardinality changed")
    if _sha256(_canonical_json_bytes(root_all)) != EXPECTED_ROOT_ALL_SHA256:
        raise RuntimeError("S1-PT root_all digest changed")
    if _sha256(_canonical_json_bytes(records)) != EXPECTED_SORTED_RECORDS_SHA256:
        raise RuntimeError("S1-PT record digest changed")

    required = {"export_name", "source_module", "source_attribute", "surface_class"}
    names = []
    for record in records:
        if set(record) != required or not all(isinstance(record[key], str) for key in required):
            raise RuntimeError(f"invalid S1-PT record: {record!r}")
        names.append(record["export_name"])
    if len(set(names)) != 1267 or set(names) != set(root_all):
        raise RuntimeError("S1-PT record names do not match root_all")
    return root_all, records


def _render_module(
    root_all: list[str],
    records: list[dict[str, str]],
    allowed_modules: list[str],
) -> str:
    lazy_exports = {
        record["export_name"]: (
            record["source_module"],
            record["source_attribute"],
        )
        for record in records
    }
    surface_classes = {
        record["export_name"]: record["surface_class"] for record in records
    }
    return "\n".join(
        [
            '"""Generated S1-PV lazy root tables. Do not edit by hand."""',
            "",
            "from __future__ import annotations",
            "",
            "from types import MappingProxyType",
            "",
            f'S1PT_ROOT_ALL_SHA256 = "{EXPECTED_ROOT_ALL_SHA256}"',
            f'S1PT_SORTED_RECORDS_SHA256 = "{EXPECTED_SORTED_RECORDS_SHA256}"',
            f'CURRENT_API_SOURCE_SHA256 = "{EXPECTED_CURRENT_API_SOURCE_SHA256}"',
            f'CURRENT_API_ALLOWED_MODULES_SHA256 = "{EXPECTED_CURRENT_API_MODULES_SHA256}"',
            f'CURRENT_API_IMPORT_EDGES_SHA256 = "{EXPECTED_CURRENT_API_EDGES_SHA256}"',
            "",
            f"ROOT_ALL = {pformat(tuple(root_all), width=100, sort_dicts=False)}",
            "",
            "ROOT_LAZY_EXPORTS = MappingProxyType(",
            f"    {pformat(lazy_exports, width=100, sort_dicts=True)}",
            ")",
            "",
            "ROOT_SURFACE_CLASSES = MappingProxyType(",
            f"    {pformat(surface_classes, width=100, sort_dicts=True)}",
            ")",
            "",
            f"CURRENT_API_ALLOWED_MODULES = frozenset({pformat(allowed_modules, width=100, sort_dicts=False)})",
            "",
            "__all__ = (",
            '    "ROOT_ALL",',
            '    "ROOT_LAZY_EXPORTS",',
            '    "ROOT_SURFACE_CLASSES",',
            '    "CURRENT_API_ALLOWED_MODULES",',
            '    "S1PT_ROOT_ALL_SHA256",',
            '    "S1PT_SORTED_RECORDS_SHA256",',
            '    "CURRENT_API_SOURCE_SHA256",',
            '    "CURRENT_API_ALLOWED_MODULES_SHA256",',
            '    "CURRENT_API_IMPORT_EDGES_SHA256",',
            ")",
            "",
        ]
    )


def main() -> None:
    if _sha256(CURRENT_API_PATH.read_bytes()) != EXPECTED_CURRENT_API_SOURCE_SHA256:
        raise RuntimeError("current_api source digest changed")
    root_all, records = _validated_inventory()
    allowed_modules, edges = _current_api_graph()
    if len(allowed_modules) != 57 or len(edges) != 253:
        raise RuntimeError("current_api graph cardinality changed")
    if _sha256(_canonical_json_bytes(allowed_modules)) != EXPECTED_CURRENT_API_MODULES_SHA256:
        raise RuntimeError("current_api module digest changed")
    if _sha256(_canonical_json_bytes(edges)) != EXPECTED_CURRENT_API_EDGES_SHA256:
        raise RuntimeError("current_api edge digest changed")
    OUTPUT_PATH.write_text(
        _render_module(root_all, records, allowed_modules),
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": str(OUTPUT_PATH),
                "root_exports": len(root_all),
                "current_api_modules": len(allowed_modules),
                "current_api_edges": len(edges),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
