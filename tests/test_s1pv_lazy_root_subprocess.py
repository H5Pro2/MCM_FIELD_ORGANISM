from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest


ROOT = Path(__file__).parents[1]


def _run_fresh(script: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(script)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"fresh interpreter failed ({completed.returncode}):\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return json.loads(completed.stdout)


class S1PVLazyRootSubprocessTests(unittest.TestCase):
    def test_01_plain_package_import_loads_only_lazy_root_support(self) -> None:
        result = _run_fresh(
            """
            import json
            import sys
            import mcm_field_organism
            modules = sorted(
                name for name in sys.modules
                if name == "mcm_field_organism"
                or name.startswith("mcm_field_organism.")
            )
            print(json.dumps({"modules": modules}, sort_keys=True))
            """
        )
        self.assertEqual(
            [
                "mcm_field_organism",
                "mcm_field_organism.root_lazy_exports",
            ],
            result["modules"],
        )

    def test_02_current_api_import_stays_within_static_allowlist(self) -> None:
        result = _run_fresh(
            """
            import json
            import sys
            import mcm_field_organism.current_api
            from mcm_field_organism.root_lazy_exports import CURRENT_API_ALLOWED_MODULES
            prefix = "mcm_field_organism."
            actual = {
                name[len(prefix):] for name in sys.modules
                if name.startswith(prefix)
                and name != "mcm_field_organism.root_lazy_exports"
            }
            allowed = set(CURRENT_API_ALLOWED_MODULES)
            print(json.dumps({
                "unexpected": sorted(actual - allowed),
                "current_api_loaded": "current_api" in actual,
                "loaded_count": len(actual),
                "allowed_count": len(allowed),
            }, sort_keys=True))
            """
        )
        self.assertEqual([], result["unexpected"])
        self.assertTrue(result["current_api_loaded"])
        self.assertLessEqual(result["loaded_count"], result["allowed_count"])

    def test_03_single_active_root_access_loads_origin_and_keeps_identity(self) -> None:
        result = _run_fresh(
            """
            import importlib
            import json
            import sys
            import mcm_field_organism as root
            module_name = "mcm_field_organism.shared_mcm_field"
            before = module_name in sys.modules
            value = root.SharedMCMField
            source = importlib.import_module(module_name)
            print(json.dumps({
                "before": before,
                "after": module_name in sys.modules,
                "identity": value is source.SharedMCMField,
            }, sort_keys=True))
            """
        )
        self.assertFalse(result["before"])
        self.assertTrue(result["after"])
        self.assertTrue(result["identity"])

    def test_04_closed_root_name_remains_deferred_until_access(self) -> None:
        result = _run_fresh(
            """
            import importlib
            import json
            import sys
            import mcm_field_organism as root
            module_name = "mcm_field_organism.local_synaptic_memory_candidate"
            before = module_name in sys.modules
            value = root.LocalSynapticMemoryState
            source = importlib.import_module(module_name)
            print(json.dumps({
                "before": before,
                "after": module_name in sys.modules,
                "identity": value is source.LocalSynapticMemoryState,
            }, sort_keys=True))
            """
        )
        self.assertFalse(result["before"])
        self.assertTrue(result["after"])
        self.assertTrue(result["identity"])

    def test_05_explicit_star_import_preserves_complete_root_surface(self) -> None:
        result = _run_fresh(
            """
            import json
            import mcm_field_organism as root
            namespace = {}
            exec("from mcm_field_organism import *", namespace)
            exported = {name for name in namespace if not name.startswith("__")}
            expected = set(root.__all__)
            print(json.dumps({
                "count": len(exported),
                "missing": sorted(expected - exported),
                "extra": sorted(exported - expected),
            }, sort_keys=True))
            """
        )
        self.assertEqual(1267, result["count"])
        self.assertEqual([], result["missing"])
        self.assertEqual([], result["extra"])


if __name__ == "__main__":
    unittest.main()
