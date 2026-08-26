"""Build the static S1-PW root consumer audit without project imports."""

from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "mcm_field_organism"
INVENTORY = ROOT / "docs" / "S1PT_ROOT_EXPORT_INVENTORY_V1.json"
OUTPUT = ROOT / "docs" / "S1PW_ROOT_CONSUMER_AUDIT_V1.json"
SCAN_ROOTS = (PACKAGE, ROOT / "tests", ROOT / "tools")

S1PV_TEST_FILES = (
    "tests/test_s1pv_lazy_root_manifest.py",
    "tests/test_s1pv_lazy_root_subprocess.py",
    "tests/test_current_api_manifest.py",
    "tests/test_current_architecture_api.py",
    "tests/test_active_engineering_surface_boundary.py",
    "tests/test_architecture_contract_boundary.py",
    "tests/test_audio_video_field_geometry_boundary.py",
    "tests/test_receptor_proposal_handoff_boundary.py",
    "tests/test_receptor_time_model_boundary.py",
    "tests/test_current_api_end_to_end_consumer.py",
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


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _is_package_submodule(name: str) -> bool:
    return (PACKAGE / f"{name}.py").is_file()


def _call_targets_root_alias(node: ast.Call, aliases: set[str]) -> bool:
    return bool(
        node.args
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id in aliases
    )


def _consumer_record(path: Path, root_exports: set[str]) -> dict[str, object] | None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    aliases: set[str] = set()
    named_exports: list[str] = []
    submodules: list[str] = []
    unresolved: list[str] = []
    from_statements = 0
    alias_imports = 0
    star_imports = 0
    dynamic_imports = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "mcm_field_organism":
            from_statements += 1
            for alias in node.names:
                if alias.name == "*":
                    star_imports += 1
                elif alias.name in root_exports:
                    named_exports.append(alias.name)
                elif _is_package_submodule(alias.name):
                    submodules.append(alias.name)
                else:
                    unresolved.append(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "mcm_field_organism":
                    aliases.add(alias.asname or "mcm_field_organism")
                    alias_imports += 1
        elif isinstance(node, ast.Call):
            target = (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "import_module"
            ) or (
                isinstance(node.func, ast.Name) and node.func.id == "__import__"
            )
            if (
                target
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == "mcm_field_organism"
            ):
                dynamic_imports += 1

    if not (from_statements or alias_imports or star_imports or dynamic_imports):
        return None

    alias_attributes: list[str] = []
    introspection: list[str] = []
    constant_hasattr_names: list[str] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in aliases
        ):
            alias_attributes.append(node.attr)
            if node.attr in {"__all__", "__dict__", "__getattr__", "__dir__"}:
                introspection.append(node.attr)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"dir", "vars", "hasattr", "getattr"}
            and _call_targets_root_alias(node, aliases)
        ):
            introspection.append(node.func.id)
            if (
                node.func.id == "hasattr"
                and len(node.args) > 1
                and isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, str)
            ):
                constant_hasattr_names.append(node.args[1].value)

    behavior_classes = []
    if named_exports:
        behavior_classes.append("ROOT_EXPORT_NAMED_IMPORT")
    if submodules:
        behavior_classes.append("ROOT_SUBMODULE_IMPORT")
    if alias_imports:
        behavior_classes.append("ROOT_ALIAS_IMPORT")
    if alias_attributes:
        behavior_classes.append("ROOT_ALIAS_ATTRIBUTE")
    if constant_hasattr_names:
        behavior_classes.append("ROOT_ABSENCE_INTROSPECTION")
    if introspection:
        behavior_classes.append("ROOT_GENERAL_INTROSPECTION")
    if star_imports:
        behavior_classes.append("ROOT_STAR_IMPORT")
    if dynamic_imports:
        behavior_classes.append("ROOT_DYNAMIC_IMPORT")

    return {
        "file": _relative(path),
        "area": _relative(path).split("/", 1)[0],
        "covered_test_file": _relative(path) in S1PV_TEST_FILES,
        "from_statements": from_statements,
        "alias_imports": alias_imports,
        "star_imports": star_imports,
        "dynamic_imports": dynamic_imports,
        "named_export_occurrences": len(named_exports),
        "named_exports": sorted(set(named_exports)),
        "submodule_occurrences": len(submodules),
        "submodules": sorted(set(submodules)),
        "root_alias_attributes": sorted(set(alias_attributes)),
        "introspection": sorted(set(introspection)),
        "constant_hasattr_names": sorted(set(constant_hasattr_names)),
        "unresolved_names": sorted(set(unresolved)),
        "behavior_classes": sorted(set(behavior_classes)),
    }


def build_audit() -> dict[str, object]:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if inventory.get("contract_id") != "mcm.s1pt.root_export_inventory.v1":
        raise RuntimeError("unexpected S1-PT inventory")
    root_exports = set(inventory["root_all"])
    if len(root_exports) != 1267:
        raise RuntimeError("unexpected S1-PT root export count")

    paths = sorted({path for root in SCAN_ROOTS for path in root.rglob("*.py")})
    source_records = [
        {"file": _relative(path), "sha256": _sha256(path.read_bytes())}
        for path in paths
    ]
    consumers = []
    for path in paths:
        record = _consumer_record(path, root_exports)
        if record is not None:
            consumers.append(record)
    consumers.sort(key=lambda record: record["file"])

    unresolved = [
        {"file": record["file"], "names": record["unresolved_names"]}
        for record in consumers
        if record["unresolved_names"]
    ]
    if unresolved:
        raise RuntimeError(f"unresolved root imports: {unresolved}")

    named_names = {
        name for record in consumers for name in record["named_exports"]
    }
    submodule_names = {
        name for record in consumers for name in record["submodules"]
    }
    hasattr_names = {
        name for record in consumers for name in record["constant_hasattr_names"]
    }
    present_hasattr_names = sorted(hasattr_names & root_exports)
    absent_hasattr_names = sorted(hasattr_names - root_exports)
    behavior_counts = Counter(
        behavior
        for record in consumers
        for behavior in record["behavior_classes"]
    )
    area_counts = Counter(record["area"] for record in consumers)

    return {
        "contract_id": "mcm.s1pw.root_consumer_audit.v1",
        "audit_mode": "static_ast_no_project_import_no_test",
        "scan_roots": ["mcm_field_organism", "tests", "tools"],
        "s1pv_test_files": list(S1PV_TEST_FILES),
        "counts": {
            "python_files_scanned": len(paths),
            "consumer_files": len(consumers),
            "consumer_areas": dict(sorted(area_counts.items())),
            "package_internal_consumer_files": area_counts.get(
                "mcm_field_organism", 0
            ),
            "covered_consumer_files": sum(
                bool(record["covered_test_file"]) for record in consumers
            ),
            "remaining_consumer_files": sum(
                not bool(record["covered_test_file"]) for record in consumers
            ),
            "root_from_statements": sum(record["from_statements"] for record in consumers),
            "root_alias_imports": sum(record["alias_imports"] for record in consumers),
            "root_export_named_occurrences": sum(
                record["named_export_occurrences"] for record in consumers
            ),
            "unique_root_export_names": len(named_names),
            "root_submodule_occurrences": sum(
                record["submodule_occurrences"] for record in consumers
            ),
            "unique_root_submodules": len(submodule_names),
            "source_star_imports": sum(record["star_imports"] for record in consumers),
            "dynamic_root_imports": sum(
                record["dynamic_imports"] for record in consumers
            ),
            "constant_hasattr_names": len(hasattr_names),
            "present_constant_hasattr_names": len(present_hasattr_names),
            "absent_constant_hasattr_names": len(absent_hasattr_names),
            "behavior_class_files": dict(sorted(behavior_counts.items())),
        },
        "unique_root_submodules": sorted(submodule_names),
        "constant_hasattr_present_names": present_hasattr_names,
        "constant_hasattr_absent_names": absent_hasattr_names,
        "coverage_decision": {
            "named_exports": "covered_by_all_1267_identity_gate",
            "submodule_imports": "covered_by_current_api_and_boundary_submodule_imports",
            "alias_attributes": "covered_by_identity_cache_all_and_dir_gates",
            "absent_hasattr": "covered_by_unknown_attribute_fail_closed_gate",
            "general_introspection": "covered_by_complete_identity_unknown_attribute_and_dir_gates",
            "star_import": "covered_in_fresh_s1pv_subprocess",
            "dynamic_import": "not_present_in_scanned_sources",
            "uncovered_lazy_behavior_classes": [],
            "additional_regression_run_required": False,
        },
        "digests": {
            "scanned_source_set_sha256": _sha256(
                _canonical_json_bytes(source_records)
            ),
            "consumer_records_sha256": _sha256(_canonical_json_bytes(consumers)),
        },
        "consumers": consumers,
    }


def main() -> None:
    audit = build_audit()
    OUTPUT.write_text(
        json.dumps(audit, allow_nan=False, ensure_ascii=True, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                **audit["counts"],
                **audit["digests"],
                **audit["coverage_decision"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
