from __future__ import annotations

import ast
from pathlib import Path
import unittest


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
