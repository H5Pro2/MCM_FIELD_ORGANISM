from __future__ import annotations

import ast
from dataclasses import fields
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest


_PROJECT_ROOT = Path(__file__).parents[1]
_PACKAGE_ROOT = _PROJECT_ROOT / "mcm_field_organism"
_CLOSED_MODULE_PREFIXES = (
    "_acm1h",
    "acm1h",
    "e1_",
    "g2_d3_",
    "dynamic_substrate_",
    "lrd",
)
_CLOSED_NAME_PATTERN = re.compile(
    r"(?:^|_)(?:lrd|e1)(?:_|$)|acm1h|g2_d3|dts1|dynamic_substrate",
    re.IGNORECASE,
)


def _is_closed_module(module_name: str) -> bool:
    leaf = module_name.rsplit(".", maxsplit=1)[-1].lower()
    return leaf.startswith(_CLOSED_MODULE_PREFIXES)


def _module_path(module_name: str) -> Path:
    return _PACKAGE_ROOT.joinpath(*module_name.split(".")).with_suffix(".py")


def _local_imports(module_name: str) -> set[str]:
    path = _module_path(module_name)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    parent_parts = module_name.split(".")[:-1]
    imports: set[str] = set()
    for node in ast.walk(tree):
        candidates: list[str] = []
        if isinstance(node, ast.ImportFrom):
            if node.level:
                base = parent_parts[: len(parent_parts) - (node.level - 1)]
                if node.module:
                    candidates.append(".".join((*base, node.module)))
                else:
                    candidates.extend(".".join((*base, alias.name)) for alias in node.names)
            elif (node.module or "").startswith("mcm_field_organism."):
                candidates.append((node.module or "").removeprefix("mcm_field_organism."))
        elif isinstance(node, ast.Import):
            candidates.extend(
                alias.name.removeprefix("mcm_field_organism.")
                for alias in node.names
                if alias.name.startswith("mcm_field_organism.")
            )
        imports.update(candidate for candidate in candidates if _module_path(candidate).is_file())
    return imports


def _active_origin_modules() -> set[str]:
    from mcm_field_organism import current_api

    path = _PACKAGE_ROOT / "current_api.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    active = set(current_api.CURRENT_CONTROLLED_FIELD_EXPORTS)
    origins: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or node.level != 1 or not node.module:
            continue
        if any((alias.asname or alias.name) in active for alias in node.names):
            origins.add(node.module)
    return origins


def _active_import_closure() -> set[str]:
    pending = list(_active_origin_modules())
    visited: set[str] = set()
    while pending:
        module_name = pending.pop()
        if module_name in visited:
            continue
        visited.add(module_name)
        pending.extend(_local_imports(module_name) - visited)
    return visited


def _single_current_api_import(test_filename: str) -> set[str]:
    consumer_path = Path(__file__).with_name(test_filename)
    tree = ast.parse(consumer_path.read_text(encoding="utf-8"))
    project_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        and (
            (
                isinstance(node, ast.ImportFrom)
                and (node.module or "").startswith("mcm_field_organism")
            )
            or (
                isinstance(node, ast.Import)
                and any(
                    alias.name.startswith("mcm_field_organism")
                    for alias in node.names
                )
            )
        )
    ]
    if len(project_imports) != 1:
        raise AssertionError(f"expected one project import, got {len(project_imports)}")
    project_import = project_imports[0]
    if not isinstance(project_import, ast.ImportFrom):
        raise AssertionError("project import must use from ... import ...")
    if project_import.module != "mcm_field_organism.current_api":
        raise AssertionError("consumer must import only from current_api")
    return {alias.name for alias in project_import.names}


def _called_names(module_filename: str, function_name: str) -> set[str]:
    module_path = Path(__file__).parents[1] / "mcm_field_organism" / module_filename
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    functions = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == function_name
    ]
    if len(functions) != 1:
        raise AssertionError(f"expected one function named {function_name}")
    return {
        node.func.id
        for node in ast.walk(functions[0])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }


class ActiveEngineeringSurfaceBoundaryTests(unittest.TestCase):
    def test_machine_readable_drift_contract_matches_active_boundary(self) -> None:
        from mcm_field_organism import current_api
        from mcm_field_organism.architecture_contract import RuntimePermission
        from mcm_field_organism.architecture_readiness import (
            reference_architecture_plan,
        )
        from mcm_field_organism.root_lazy_exports import (
            CURRENT_API_ALLOWED_MODULES_SHA256,
            CURRENT_API_IMPORT_EDGES_SHA256,
            CURRENT_API_SOURCE_SHA256,
            S1PT_ROOT_ALL_SHA256,
            S1PT_SORTED_RECORDS_SHA256,
        )
        from mcm_field_organism.shared_mcm_field import (
            SNAPSHOT_REFERENCE_STATE_FIELDS,
        )

        artifact_path = _PROJECT_ROOT / "docs" / "S1UY_ACTIVE_CORE_DRIFT_CONTRACT_V1.json"
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

        self.assertEqual("mcm.s1uy.active-core-drift-contract.v1", artifact["contract_id"])
        self.assertEqual(
            "ACTIVE_CORE_BOUND_NO_CLOSED_BRANCH_ACTIVATION",
            artifact["status"],
        )
        self.assertEqual(
            ["LRD", "ACM1H", "E1", "G2_D3", "DTS1_DYNAMIC_SUBSTRATE"],
            artifact["closed_families"],
        )
        self.assertEqual(list(_CLOSED_MODULE_PREFIXES), artifact["module_prefixes"])
        self.assertEqual(
            current_api.active_field_state_contract_digest(),
            artifact["active_field_contract_digest"],
        )
        self.assertEqual(
            {
                "current_api_allowed_modules_sha256": CURRENT_API_ALLOWED_MODULES_SHA256,
                "current_api_import_edges_sha256": CURRENT_API_IMPORT_EDGES_SHA256,
                "current_api_source_sha256": CURRENT_API_SOURCE_SHA256,
                "s1pt_root_all_sha256": S1PT_ROOT_ALL_SHA256,
                "s1pt_sorted_records_sha256": S1PT_SORTED_RECORDS_SHA256,
            },
            artifact["root_lazy_digests"],
        )
        self.assertEqual(
            list(SNAPSHOT_REFERENCE_STATE_FIELDS),
            artifact["snapshot_reference_state_fields"],
        )

        boundary = reference_architecture_plan().boundary("field.topology_memory")
        self.assertIs(RuntimePermission.RESEARCH_CLOSED, boundary.permission)
        self.assertFalse(boundary.writes_back)
        self.assertEqual(
            {
                "boundary_id": boundary.boundary_id,
                "permission": boundary.permission.value,
                "writes_back": boundary.writes_back,
            },
            artifact["closed_architecture_boundary"],
        )

        for record in artifact["source_records"]:
            path = _PROJECT_ROOT / record["path"]
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                record["sha256"],
                record["path"],
            )

        digest_payload = dict(artifact)
        artifact_digest = digest_payload.pop("artifact_digest")
        encoded = json.dumps(
            digest_payload,
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
        self.assertEqual(hashlib.sha256(encoded).hexdigest(), artifact_digest)

    def test_closed_family_classifier_is_bound_and_specific(self) -> None:
        closed = (
            "lrd_e1_runtime",
            "_acm1h_field_runtime",
            "e1_local_edge_plasticity",
            "g2_d3_atomic_commit",
            "dynamic_substrate_dts1_coupled_step",
        )
        allowed = (
            "neutral_local_field_substrate",
            "mcm_f3_runtime",
            "s1b_asynchronous_field_runtime",
            "shared_mcm_field",
        )
        self.assertTrue(all(_is_closed_module(name) for name in closed))
        self.assertFalse(any(_is_closed_module(name) for name in allowed))

    def test_closed_research_families_are_not_current_api_roles(self) -> None:
        from mcm_field_organism import current_api

        active = set(current_api.CURRENT_CONTROLLED_FIELD_EXPORTS)
        references = set(
            current_api.PASSIVE_COMPARISON_EXPORTS
            + current_api.CI_REFERENCE_EXPORTS
            + current_api.F3_REFERENCE_EXPORTS
            + current_api.S1B_REFERENCE_EXPORTS
        )
        self.assertFalse(active & references)
        self.assertEqual(
            [],
            sorted(name for name in active | references if _CLOSED_NAME_PATTERN.search(name)),
        )

        direct_modules = _local_imports("current_api")
        self.assertEqual(
            [],
            sorted(module for module in direct_modules if _is_closed_module(module)),
        )

    def test_closed_research_families_have_no_root_lazy_exports(self) -> None:
        from mcm_field_organism.root_lazy_exports import (
            ROOT_LAZY_EXPORTS,
        )

        exported = {
            name: module_name
            for name, (module_name, _) in ROOT_LAZY_EXPORTS.items()
            if _is_closed_module(module_name)
        }
        self.assertEqual({}, exported)

    def test_active_import_closure_excludes_closed_research_modules(self) -> None:
        closure = _active_import_closure()
        self.assertTrue(closure)
        self.assertEqual(
            [],
            sorted(module for module in closure if _is_closed_module(module)),
        )

    def test_active_snapshot_has_no_closed_candidate_state_slot(self) -> None:
        from mcm_field_organism import current_api
        from mcm_field_organism.shared_mcm_field import (
            SNAPSHOT_REFERENCE_STATE_FIELDS,
            SharedMCMFieldSnapshot,
        )

        snapshot_fields = {item.name for item in fields(SharedMCMFieldSnapshot)}
        contract_snapshot = current_api.active_field_state_contract()["snapshot"]
        names = snapshot_fields | set(contract_snapshot["root_keys"])
        names |= set(contract_snapshot["reference_state_fields"])
        self.assertEqual(("substrate", "development"), SNAPSHOT_REFERENCE_STATE_FIELDS)
        self.assertEqual(
            [],
            sorted(name for name in names if _CLOSED_NAME_PATTERN.search(name)),
        )

    def test_hypothetical_memory_boundary_remains_research_closed(self) -> None:
        from mcm_field_organism.architecture_contract import RuntimePermission
        from mcm_field_organism.architecture_readiness import (
            reference_architecture_plan,
        )

        boundary = reference_architecture_plan().boundary("field.topology_memory")
        self.assertIs(RuntimePermission.RESEARCH_CLOSED, boundary.permission)
        self.assertFalse(boundary.writes_back)

    def test_fresh_active_import_does_not_load_closed_research_modules(self) -> None:
        script = f"""
import json
import sys
sys.path.insert(0, {str(_PROJECT_ROOT)!r})
import mcm_field_organism.current_api
prefixes = {list(_CLOSED_MODULE_PREFIXES)!r}
loaded = []
for name in sys.modules:
    if not name.startswith('mcm_field_organism.'):
        continue
    leaf = name.rsplit('.', 1)[-1].lower()
    if leaf.startswith(tuple(prefixes)):
        loaded.append(name)
print(json.dumps(sorted(loaded)))
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            cwd=_PROJECT_ROOT,
            text=True,
        )
        self.assertEqual([], json.loads(result.stdout))

    def test_current_api_does_not_export_archived_or_private_roles(self) -> None:
        from mcm_field_organism import current_api

        exported = set(getattr(current_api, "__all__", ()))
        forbidden_fragments = (
            "camera",
            "live_audio",
            "live_video",
            "memory",
            "synaptic",
            "w7bn",
            "w7bm",
            "w7bo",
            "w7bp",
        )
        violations = sorted(
            name
            for name in exported
            if any(fragment in name.lower() for fragment in forbidden_fragments)
        )
        self.assertEqual([], violations)

    def test_current_api_remains_the_curated_entrypoint(self) -> None:
        from mcm_field_organism import current_api

        self.assertTrue(hasattr(current_api, "advance_audio_video_receptor_sequences"))
        self.assertTrue(hasattr(current_api, "BrowserWorldContract"))
        self.assertTrue(hasattr(current_api, "SharedMCMField"))

    def test_ci_baseline_is_not_part_of_active_engineering_manifest(self) -> None:
        from mcm_field_organism import current_api

        core = set(current_api.CURRENT_CONTROLLED_FIELD_EXPORTS)
        ci_reference = set(current_api.CI_REFERENCE_EXPORTS)
        self.assertTrue(ci_reference)
        self.assertTrue(ci_reference.isdisjoint(core))
        self.assertIn("advance_ci_accommodation", current_api.__all__)
        self.assertNotIn("advance_ci_accommodation", core)

    def test_passive_comparisons_are_not_active_field_operations(self) -> None:
        from mcm_field_organism import current_api

        core = set(current_api.CURRENT_CONTROLLED_FIELD_EXPORTS)
        comparisons = set(current_api.PASSIVE_COMPARISON_EXPORTS)
        self.assertTrue(comparisons)
        self.assertTrue(comparisons.isdisjoint(core))
        self.assertIn("compare_controlled_probe_snapshots", current_api.__all__)
        self.assertNotIn("compare_controlled_probe_snapshots", core)

    def test_end_to_end_consumer_imports_only_active_core_roles(self) -> None:
        from mcm_field_organism import current_api

        imported_names = _single_current_api_import(
            "test_current_api_end_to_end_consumer.py"
        )
        active_core = set(current_api.CURRENT_CONTROLLED_FIELD_EXPORTS)
        self.assertTrue(imported_names)
        self.assertTrue(imported_names.issubset(active_core))

    def test_browser_payload_consumer_imports_only_active_core_roles(self) -> None:
        from mcm_field_organism import current_api

        imported_names = _single_current_api_import(
            "test_current_api_browser_payload_consumer.py"
        )
        active_core = set(current_api.CURRENT_CONTROLLED_FIELD_EXPORTS)
        self.assertEqual(13, len(imported_names))
        self.assertTrue(imported_names.issubset(active_core))

    def test_active_world_inputs_share_sequence_handoff_and_field_path(self) -> None:
        capture_calls = _called_names(
            "audio_video_neutral_field_runtime.py",
            "capture_audio_video_into_neutral_field",
        )
        advance_calls = _called_names(
            "audio_video_neutral_field_runtime.py",
            "advance_audio_video_receptor_sequences",
        )
        field_calls = _called_names(
            "neutral_asynchronous_field_runtime.py",
            "run_neutral_asynchronous_field",
        )
        browser_imports = _single_current_api_import(
            "test_current_api_browser_payload_consumer.py"
        )

        self.assertIn("advance_audio_video_receptor_sequences", capture_calls)
        self.assertIn("advance_audio_video_receptor_sequences", browser_imports)
        self.assertIn("run_neutral_asynchronous_field", advance_calls)
        self.assertTrue(
            {
                "handoff_receptor_completion_groups",
                "map_proposal_batch_to_transient_docks",
                "project_transient_docks_to_neuron_inputs",
            }.issubset(field_calls)
        )


if __name__ == "__main__":
    unittest.main()
