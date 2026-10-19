"""Bound development test runner and byte evidence collector; not qualification authority."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import _s2uc_source_execution_binding as binding
from tools import _s2uc_publication_v7 as publication
from tools import s2uc_source_process_once as process
from tools import _s2uc_qualification_v9 as qualification
from tools import _s2uc_source_context_v9 as context


def save(path, value):
    path.write_bytes(binding.old.canonical(value))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--focused", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    inv = binding.current()
    save(args.output / "dependency-inventory.json", inv)
    names = binding.TESTS[-2:] if args.focused else binding.TESTS
    suite = unittest.defaultTestLoader.loadTestsFromNames([name[:-3].replace("/", ".") for name in names])
    statuses = {}
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            statuses[test.id()] = "PASS"
            super().addSuccess(test)
        def addFailure(self, test, err):
            statuses[test.id()] = "FAIL"
            super().addFailure(test, err)
        def addError(self, test, err):
            statuses[test.id()] = "ERROR"
            super().addError(test, err)
        def addSkip(self, test, reason):
            statuses[test.id()] = "SKIP"
            super().addSkip(test, reason)
    closures = []
    blobs = args.output / "blobs"
    blobs.mkdir()
    def retain(result, output):
        observations = []
        refs = result["inputs"] + [{**r, "root": str(output)} for r in result["result_inventory"]]
        for row in refs:
            try:
                data = (Path(row["root"]) / row["path"]).read_bytes()
                digest = binding.discovery.sha(data)
                dest = blobs / digest
                if not dest.exists():
                    dest.write_bytes(data)
                observations.append({"path": row["path"], "sha256": digest, "bytes": len(data),
                                     "matches_report": digest == row["sha256"] and len(data) == row["bytes"]})
            except OSError as exc:
                observations.append({"path": row["path"], "error": str(exc)})
        return observations
    original = publication._Publication.finish
    def collect(pub):
        result = original(pub)
        folder = args.output / "closures" / f"{len(closures)+1:03}"
        folder.mkdir(parents=True)
        save(folder / "result.json", result)
        save(folder / "retained-inputs-and-outputs.json", retain(result, pub.directory))
        shutil.copytree(pub.path.parent, folder / "bundle")
        shutil.copytree(pub.directory, folder / "output")
        closures.append({"path": folder.relative_to(args.output).as_posix(), "version": result["version"],
                         "status": result["status"], "actual": result["actual"],
                         "accounting_complete": result["accounting_complete"]})
        return result
    original_process = process.run_neutral
    process_results = []
    def collect_process(*a, **kw):
        result = original_process(*a, **kw)
        folder = args.output / f"process-{len(process_results)+1}"
        shutil.copytree(kw["folder"], folder)
        if "product" in result:
            config = json.loads((folder / "config.json").read_text())
            shutil.copytree(config["output"], folder / "product")
            shutil.copytree(Path(config["binding"]).parent, folder / "bundle")
            save(folder / "retained-inputs-and-outputs.json", retain(result["product"], config["output"]))
        process_results.append(result)
        return result
    begin = time.monotonic()
    with (args.output / "unittest.log").open("w", encoding="utf-8") as log:
        with patch.object(publication._Publication, "finish", collect), patch.object(process, "run_neutral", collect_process):
            result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=Result).run(suite)
    unchanged = binding.current() == inv
    complete = args.focused or sorted(statuses) == binding.test_ids()
    code = 0 if result.wasSuccessful() and unchanged and complete else 1
    log = args.output / "tests.log"
    log.write_text("".join(name + " " + status + "\n" for name, status in sorted(statuses.items())), newline="\n")
    ref, _, _ = binding.discovery.read_file(args.output, log.name)
    evidence = {"version": "s2uc.executed-neutral-evidence.v9", "scope": "EXECUTED_NEUTRAL_DEVELOPMENT",
                "inventory_sha256": binding.discovery.sha(binding.old.canonical(inv)), "test_ids": sorted(statuses),
                "results": statuses, "log": ref, "tests_run": result.testsRun, "exit_code": code,
                "real_execution_authorized": False, "formal_qualification": False}
    save(args.output / "test-result.json", evidence)
    save(args.output / "measurements.json", {"closures": closures, "process_results": process_results,
                                            "code_unchanged": unchanged, "seconds": time.monotonic()-begin})
    if code == 0 and not args.focused:
        inventory_ref, _, _ = binding.discovery.read_file(args.output, "dependency-inventory.json")
        summary = {k: v for k, v in evidence.items() if k not in ("test_ids", "results")}
        summary.update(version="s2uc.executed-neutral-summary.v9", inventory=inventory_ref,
                       test_ids_sha256=binding.discovery.sha(binding.old.canonical(sorted(statuses))))
        summary_path = args.output / "qualification-summary.json"
        save(summary_path, summary)
        source_path = args.output / "source-context.json"
        save(source_path, context.source_context())
        preparation = binding.read_source_preparation(source_path, summary_path)
        save(args.output / "source-preparation-check.json", preparation)
        checks = {"evidence_reader": qualification.read(summary_path),
                  "code_files": len(inv["files"]), "code_bytes": inv["code_bytes"],
                  "code_limit": binding.resources.LIMITS["code"],
                  "code_free": binding.resources.LIMITS["code"]-inv["code_bytes"],
                  "all_test_ids_complete": complete, "code_unchanged": unchanged,
                  "real_execution_authorized": False, "independent_acceptance": "OPEN"}
        save(args.output / "final-checks.json", checks)
    archived = []
    for path in sorted(args.output.rglob("*")):
        if path.is_file():
            data = path.read_bytes()
            archived.append({"path": path.relative_to(args.output).as_posix(), "bytes": len(data),
                             "sha256": binding.discovery.sha(data)})
    save(args.output / "evidence-hashes.json", archived)
    print(json.dumps({"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
                      "skips": len(result.skipped), "exit_code": code, "code_bytes": inv["code_bytes"]}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
