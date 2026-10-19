"""Actual Windows job admission, rejected bootstraps and neutral process closure."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.test_s2uc_source_execution import fixture
from tools import _s2uc_source_execution_binding as binding
from tools import s2uc_source_process_once as process


class SourceProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inv = binding.current()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path, self.rid, self.output = fixture(self.root, self.inv)

    def test_limited_nonzero_success_before_imports(self):
        folder = self.root / "observer"
        result = process.run_neutral(self.path, folder=folder)
        self.assertEqual(result["exit_code"], 0, (folder / "stderr.txt").read_text())
        self.assertTrue(result["product"]["evaluation_allowed"], result["product"]["primary_error"])
        parent = json.loads((folder / "parent-admission.json").read_text())
        child = json.loads((folder / "child-admission.json").read_text())
        imports = json.loads((folder / "after-imports.json").read_text())
        self.assertEqual(parent["limit"], 671088640)
        self.assertEqual(child["flags"], 0x2100)
        self.assertTrue(child["member"] and child["product_numpy_absent"])
        self.assertLess(child["ns"], imports["ns"])
        facts = json.loads((folder / "facts.json").read_text())
        self.assertEqual(facts, {"calls": 58, "gate": False, "public_gate": False, "real_production_calls": 0})

    def test_limited_memoryerror_58_is_not_evaluable(self):
        folder = self.root / "observer"
        result = process.run_neutral(self.path, case="memoryerror", folder=folder)
        self.assertEqual(result["exit_code"], 0, (folder / "stderr.txt").read_text())
        product = result["product"]
        self.assertFalse(product["evaluation_allowed"])
        self.assertEqual(product["primary_error"], "MemoryError")
        self.assertEqual(product["source_completion"]["successes"], 57)
        self.assertEqual(product["source_completion"]["attempts"], 58)

    def test_missing_or_false_admission_stops_before_imports(self):
        for index, token in enumerate(("", "admit\n")):
            folder = self.root / str(index)
            folder.mkdir()
            config = {"binding": str(self.path), "run_id": self.rid, "output": str(self.output),
                      "folder": str(folder), "job": "Local\\MCM-NONEXISTENT-V9", "case": "success",
                      "inventory_sha256": binding.discovery.sha(binding.old.canonical(self.inv))}
            cfg = folder / "config.json"
            process.save(cfg, config)
            result = subprocess.run([sys.executable, "-S", str(Path(process.__file__)), "child", str(cfg)],
                                    input=token, text=True, capture_output=True, cwd=process.ROOT, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((folder / "bootstrap.json").exists())
            self.assertFalse((folder / "after-imports.json").exists())
            self.assertFalse((folder / "result.json").exists())
            self.assertFalse(self.output.exists())

    def test_missing_parent_or_child_inventory_prevents_process(self):
        for name in binding.TOOLS:
            wrong = copy.deepcopy(self.inv)
            wrong["files"] = [r for r in wrong["files"] if r["path"] != name]
            from tests.test_s2uc_source_execution import write, seal
            write(self.path.parent / "dependency-inventory.json", wrong)
            seal(self.path.parent, wrong, self.rid, self.output)
            with patch.object(subprocess, "Popen") as start:
                with self.assertRaises(ValueError):
                    process.run_neutral(self.path, folder=self.root / "observer")
                start.assert_not_called()

    def test_public_cli_has_no_real_mode(self):
        result = subprocess.run([sys.executable, "-S", str(Path(process.__file__)), "real"],
                                capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("V9_PUBLIC_REAL_ENTRY_DISABLED", result.stderr)

    def test_external_child_abort_never_substitutes_product_closure(self):
        original = subprocess.Popen
        def changed_config(args, **kwargs):
            cfg = Path(args[-1])
            value = json.loads(cfg.read_text())
            value["job"] = "Local\\MCM-V9-WRONG-JOB"
            process.save(cfg, value)
            return original(args, **kwargs)
        folder = self.root / "observer"
        with patch.object(subprocess, "Popen", changed_config):
            result = process.run_neutral(self.path, folder=folder)
        self.assertNotEqual(result["exit_code"], 0)
        self.assertEqual(result["status"], "EXTERNAL_ABORT_NO_PRODUCT_SUCCESS")
        self.assertFalse(result["evaluation_allowed"])
        self.assertNotIn("product", result)
        self.assertFalse(self.output.exists())
        self.assertFalse((folder / "after-imports.json").exists())
