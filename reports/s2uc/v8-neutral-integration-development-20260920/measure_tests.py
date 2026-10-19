"""Development evidence observer; no real sources, no qualification writer."""
import hashlib
import json
import shutil
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import _s2uc_binding_v8 as binding
from tools import _s2uc_execution_v8 as execution
from tools import _s2uc_inventory_v7 as inventory

DEST = Path(__file__).resolve().parent / "final"
DEST.mkdir(exist_ok=False)

def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def sha(data):
    return hashlib.sha256(data).hexdigest()

inv = binding.current()
save(DEST / "dependency-inventory.json", inv)
save(DEST / "v7-inventory.json", inventory.current())
for row in inv["files"]:
    dest = DEST / "code" / row["path"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / row["path"], dest)

measurements, test_rows = [], []
active = None
original = execution.run_neutral

def observed(*args, **kwargs):
    result = original(*args, **kwargs)
    dest = DEST / "closures" / f"{len(measurements)+1:03}"
    dest.mkdir(parents=True)
    save(dest / "measurement.json", result)
    rows = []
    for i, ref in enumerate(result["inputs"]):
        if ref["category"] == "code":
            data = (DEST / "code" / ref["path"]).read_bytes()
            target = (DEST / "code" / ref["path"]).relative_to(DEST).as_posix()
        else:
            data = (Path(ref["root"]) / ref["path"]).read_bytes()
            target = (dest / "inputs" / f"{i:02}-{Path(ref['path']).name}").relative_to(DEST).as_posix()
            (DEST / target).parent.mkdir(exist_ok=True)
            (DEST / target).write_bytes(data)
        assert len(data) == ref["bytes"] and sha(data) == ref["sha256"]
        rows.append({"archive": target, "category": ref["category"], "bytes": len(data), "sha256": sha(data)})
    for ref in result["result_inventory"]:
        data = (Path(kwargs["output_directory"]) / ref["path"]).read_bytes()
        target = dest / "results" / ref["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        assert len(data) == ref["bytes"] and sha(data) == ref["sha256"]
        rows.append({"archive": target.relative_to(DEST).as_posix(), "category": ref["category"], "bytes": len(data), "sha256": sha(data)})
    assert sum(r["bytes"] for r in rows) == result["actual"]["total_bytes"]
    save(dest / "archive-files.json", rows)
    measurements.append({"test_id": active, "archive": dest.relative_to(DEST).as_posix(),
                         "status": result["status"], "primary_error": result["primary_error"],
                         "actual": result["actual"], "source_completion": result["source_completion"],
                         "owners_closed": all(r["closed"] for r in result["owner_cleanup"]),
                         "gate": execution.GATE, "files": len(rows)})
    save(DEST / "closure-measurements.json", measurements)
    return result

execution.run_neutral = observed

class Result(unittest.TextTestResult):
    def startTest(self, test):
        global active
        active = test.id()
        super().startTest(test)
    def addSuccess(self, test):
        test_rows.append({"id": test.id(), "status": "PASS"})
        super().addSuccess(test)
    def addFailure(self, test, err):
        test_rows.append({"id": test.id(), "status": "FAIL"})
        super().addFailure(test, err)
    def addError(self, test, err):
        test_rows.append({"id": test.id(), "status": "ERROR"})
        super().addError(test, err)

started = time.time()
suite = unittest.defaultTestLoader.loadTestsFromNames([p[:-3].replace("/", ".") for p in binding.TESTS])
with (DEST / "tests.log").open("w", encoding="utf-8") as log:
    result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=Result).run(suite)
ids = sorted(r["id"] for r in test_rows)
save(DEST / "test-result.json", {"scope": "NEUTRAL_DEVELOPMENT_ONLY", "formal_qualification": False,
     "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
     "skipped": result.skipped, "duration_seconds": time.time()-started,
     "expected_ids": binding.test_ids(), "exact_id_match": ids == binding.test_ids(), "tests": test_rows,
     "code_unchanged": binding.current() == inv, "gate": execution.GATE})
sys.exit(0 if result.wasSuccessful() and ids == binding.test_ids() and binding.current() == inv else 1)
