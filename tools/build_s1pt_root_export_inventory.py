"""Build the static S1-PT root export inventory without project imports."""

from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_INIT = ROOT / "mcm_field_organism" / "__init__.py"
CURRENT_API = ROOT / "mcm_field_organism" / "current_api.py"
OUTPUT = ROOT / "docs" / "S1PT_ROOT_EXPORT_INVENTORY_V1.json"

API_GROUPS = {
    "CURRENT_CONTROLLED_FIELD_EXPORTS",
    "PASSIVE_COMPARISON_EXPORTS",
    "CI_REFERENCE_EXPORTS",
    "F3_REFERENCE_EXPORTS",
    "S1B_REFERENCE_EXPORTS",
}

INACTIVE_SENSOR_MODULES = {
    "common_receptor_window",
    "independent_visual_target_presenter",
    "live_audio_adapter",
    "live_audio_video_field",
    "live_video_adapter",
    "receptor_time_alignment",
    "visual_mcm_effector_presenter",
    "visual_mcm_effector_sequence",
    "visual_mcm_effector_sequence_presenter",
    "visual_mcm_effector_surface",
}

CLOSED_CANDIDATE_MODULES = {
    "abu_interaction_ground_null",
    "condensed_field_form_null_probe",
    "contact_material_admissibility",
    "continuous_two_relation_world",
    "controlled_endogenous_source",
    "current_field_history_null_probe",
    "endogenous_external_overlap_null_probe",
    "endogenous_receptor",
    "field_passivity_null_probe",
    "instantaneous_field_flow_null_probe",
    "local_deformation_world",
    "local_synaptic_memory_candidate",
    "local_transition_evidence_probe",
    "occluded_continuation_world",
    "occluded_world_intervention_probe",
    "passive_synaptic_memory_comparison",
    "radial_contact_morphology",
    "radial_transport_admissibility",
    "radial_transport_cause_audit",
    "relationship_persistence_contract",
    "s1b_reciprocal_accommodation",
    "signed_field_flow_transport_counterfactual",
    "structural_contact_drive",
    "structural_contact_substrate",
    "synaptic_memory_lifecycle_probe",
    "transition_disposition_falsification_probe",
}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _literal_assignment(tree: ast.Module, name: str) -> object:
    matches = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            matches.append(node.value)
    if len(matches) != 1:
        raise RuntimeError(f"expected one static assignment for {name}, got {len(matches)}")
    return ast.literal_eval(matches[0])


def _root_imports(tree: ast.Module) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or node.level != 1 or not node.module:
            continue
        for alias in node.names:
            bound_name = alias.asname or alias.name
            result.setdefault(bound_name, []).append((node.module, alias.name))
    return result


def _api_groups(tree: ast.Module) -> dict[str, tuple[str, ...]]:
    groups: dict[str, tuple[str, ...]] = {}
    for name in sorted(API_GROUPS):
        value = _literal_assignment(tree, name)
        if not isinstance(value, tuple) or not all(isinstance(item, str) for item in value):
            raise RuntimeError(f"{name} must be a static tuple of strings")
        if len(value) != len(set(value)):
            raise RuntimeError(f"{name} contains duplicate names")
        groups[name] = value
    memberships: dict[str, str] = {}
    for group_name, names in groups.items():
        for export_name in names:
            previous = memberships.setdefault(export_name, group_name)
            if previous != group_name:
                raise RuntimeError(
                    f"current_api name {export_name!r} occurs in {previous} and {group_name}"
                )
    return groups


def _surface_class(
    export_name: str,
    source_module: str,
    active_names: set[str],
    reference_names: set[str],
) -> str:
    if export_name in active_names:
        return "ACTIVE_FIELD_CORE"
    if export_name in reference_names:
        return "REFERENCE_BASELINE"
    if source_module in CLOSED_CANDIDATE_MODULES:
        return "CLOSED_CANDIDATE"
    if source_module in INACTIVE_SENSOR_MODULES:
        return "INACTIVE_SENSOR"
    return "HISTORICAL_RUNNER"


def build_inventory() -> dict[str, object]:
    package_bytes = PACKAGE_INIT.read_bytes()
    package_tree = ast.parse(package_bytes.decode("utf-8"), filename=str(PACKAGE_INIT))
    current_tree = ast.parse(CURRENT_API.read_text(encoding="utf-8"), filename=str(CURRENT_API))

    root_all = _literal_assignment(package_tree, "__all__")
    if not isinstance(root_all, list) or not all(isinstance(item, str) for item in root_all):
        raise RuntimeError("root __all__ must be a static list of strings")
    duplicate_all = sorted(name for name, count in Counter(root_all).items() if count > 1)
    if duplicate_all:
        raise RuntimeError(f"duplicate root __all__ names: {duplicate_all}")

    imported = _root_imports(package_tree)
    missing = sorted(set(root_all) - set(imported))
    unused = sorted(set(imported) - set(root_all))
    ambiguous = {
        name: sorted(set(origins))
        for name, origins in imported.items()
        if name in root_all and len(set(origins)) != 1
    }
    if missing or unused or ambiguous:
        raise RuntimeError(
            f"root export mismatch: missing={missing}, unused={unused}, ambiguous={ambiguous}"
        )

    groups = _api_groups(current_tree)
    active_names = set(groups["CURRENT_CONTROLLED_FIELD_EXPORTS"])
    reference_names = set().union(
        *(set(names) for name, names in groups.items() if name != "CURRENT_CONTROLLED_FIELD_EXPORTS")
    )

    records = []
    for export_name in root_all:
        source_module, source_attribute = imported[export_name][0]
        records.append(
            {
                "export_name": export_name,
                "source_attribute": source_attribute,
                "source_module": source_module,
                "surface_class": _surface_class(
                    export_name,
                    source_module,
                    active_names,
                    reference_names,
                ),
            }
        )
    records.sort(
        key=lambda item: (
            item["export_name"],
            item["source_module"],
            item["source_attribute"],
            item["surface_class"],
        )
    )

    class_counts = Counter(record["surface_class"] for record in records)
    return {
        "contract_id": "mcm.s1pt.root_export_inventory.v1",
        "audit_mode": "static_ast_no_project_import",
        "source": "mcm_field_organism/__init__.py",
        "current_api_source": "mcm_field_organism/current_api.py",
        "classification_precedence": [
            "ACTIVE_FIELD_CORE",
            "REFERENCE_BASELINE",
            "CLOSED_CANDIDATE",
            "INACTIVE_SENSOR",
            "HISTORICAL_RUNNER",
        ],
        "inactive_sensor_modules": sorted(INACTIVE_SENSOR_MODULES),
        "closed_candidate_modules": sorted(CLOSED_CANDIDATE_MODULES),
        "counts": {
            "root_exports": len(root_all),
            "root_source_modules": len({record["source_module"] for record in records}),
            "surface_classes": dict(sorted(class_counts.items())),
            "current_api_groups": {
                name: len(values) for name, values in sorted(groups.items())
            },
        },
        "current_api_names_not_in_root": {
            "active": sorted(active_names - set(root_all)),
            "reference": sorted(reference_names - set(root_all)),
        },
        "digests": {
            "root_source_sha256": _sha256(package_bytes),
            "root_all_sha256": _sha256(_canonical_json_bytes(root_all)),
            "sorted_records_sha256": _sha256(_canonical_json_bytes(records)),
        },
        "root_all": root_all,
        "records": records,
    }


def main() -> None:
    inventory = build_inventory()
    OUTPUT.write_text(
        json.dumps(inventory, allow_nan=False, ensure_ascii=True, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"output": str(OUTPUT), **inventory["counts"], **inventory["digests"]}, sort_keys=True))


if __name__ == "__main__":
    main()
