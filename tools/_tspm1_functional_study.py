"""Private local recording for one explicitly bound TSPM-1 functional attempt."""

from __future__ import annotations

import argparse
import base64
import hashlib
import os
from pathlib import Path
import platform
import re
import sys
import time
import traceback

from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "tspm1.functional-local.v1"
PLAN = "docs/TSPM1_VERHAELTNISMAESSIGER_FUNKTIONSPRUEFPLAN.md"
_FUNCTIONAL_STUDY_RELEASE_ENABLED = False
_AUTHORIZED_RUN_ID = "functional-20260828-01"
_AUTHORIZED_TEXT_SHA256 = "adb824b76289b399f756ec0fdd0a9952295761f5b6f4dc6ac1041e967d05ea5e"
_ID = re.compile(r"[a-z0-9][a-z0-9.-]{0,95}\Z")


class RecordingError(RuntimeError):
    pass


def _require(condition, message):
    if not condition:
        raise RecordingError(message)


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _authorize_single_study(run_id, authorization):
    _require(_FUNCTIONAL_STUDY_RELEASE_ENABLED and run_id == _AUTHORIZED_RUN_ID
             and type(authorization) is str
             and _sha(authorization.encode("utf-8")) == _AUTHORIZED_TEXT_SHA256,
             "only the explicitly authorized single attempt may start")
    _require(not (ROOT / "reports/tspm1_functional" / run_id).exists(),
             "authorized attempt already exists; no retry or resume")


def _seal(kind, payload):
    body = {"schema": SCHEMA, "kind": kind, "payload": comparison._canonical(payload)}
    return {**body, "digest": comparison._digest(body)}


def _read(path, kind):
    value = comparison._loads(path.read_bytes())
    _require(type(value) is dict and set(value) == {"schema", "kind", "payload", "digest"},
             "invalid recording envelope")
    _require(value["schema"] == SCHEMA and value["kind"] == kind
             and value["digest"] == comparison._digest({k: v for k, v in value.items() if k != "digest"}),
             "recording identity or digest differs")
    return value


def _write_new(path, value):
    raw = comparison._json_bytes(value)
    with path.open("xb") as handle:
        written = handle.write(raw)
        _require(written == len(raw), "short recording write")
        handle.flush()
        os.fsync(handle.fileno())
    _require(path.read_bytes() == raw, "recording readback differs")


def _publish(path, value):
    _require(not path.exists(), "publication target already exists")
    temporary = path.with_name("." + path.name + ".tmp")
    _write_new(temporary, value)
    # The attempt owns this directory; no replacement of an existing result.
    _require(not path.exists(), "publication target appeared")
    os.rename(temporary, path)
    _require(path.read_bytes() == comparison._json_bytes(value), "publication readback differs")


def _source_manifest():
    paths = {item["repository_relative_path"] for item in comparison._project_source_inventory()}
    paths.update({PLAN, "tools/_tspm1_functional_study.py", "tests/test_tspm1_functional_study.py",
                  "docs/S2EE_TSPM1_STATISCHER_KORREKTUR_UND_AUSFUEHRUNGSBINDUNGSVERTRAG_V1.json",
                  comparison._ee_contract()["fixed_registry"]["fixture_contract"]})
    sources = []
    for relative in sorted(paths):
        raw = (ROOT / relative).read_bytes()
        sources.append({"path": relative, "sha256": _sha(raw),
                        "bytes_base64": base64.b64encode(raw).decode("ascii")})
    dependencies = []
    for name, module in sorted(sys.modules.copy().items()):
        filename = getattr(module, "__file__", None)
        if filename and not name.startswith(("mcm_field_organism", "tools.", "tests.")):
            path = Path(filename)
            if path.is_file():
                dependencies.append({"module": name, "path": str(path.resolve()),
                                     "sha256": _sha(path.read_bytes()),
                                     "version": str(getattr(module, "__version__", "bundled"))})
    return {"git_commit": comparison._git("rev-parse", "HEAD"),
            "git_status": comparison._git("status", "--porcelain", "--untracked-files=all"),
            "sources": sources, "runtime": {"executable": sys.executable,
                "sha256": _sha(Path(sys.executable).read_bytes()), "version": sys.version,
                "platform": platform.platform(), "dependencies": dependencies}}


def _check_sources(manifest):
    for item in manifest["sources"]:
        raw = base64.b64decode(item["bytes_base64"], validate=True)
        _require(_sha(raw) == item["sha256"] == _sha((ROOT / item["path"]).read_bytes()),
                 "project source changed during attempt")


def _runtime_observation(start):
    # RSS is ancillary, not a fabricated logical-memory or native-platform proof.
    return {"elapsed_seconds": time.perf_counter() - start,
            "process_memory_high_water_bytes": None, "process_memory_status": "NOT_MEASURED"}


def _error_payload(exc):
    chain = []
    current = exc
    while current is not None:
        chain.append({"type": type(current).__name__, "message": str(current),
                      "code": getattr(current, "code", None),
                      "owner": getattr(current, "owner_snapshot", None)})
        current = current.__cause__
    return {"chain": chain, "traceback": "".join(traceback.format_exception(exc))}


def _validate_expected(scope, expected):
    _require(type(expected) in (list, tuple) and all(type(item) is dict for item in expected),
             "invalid expected cell table")
    _require(all(type(item[key]) is int and item[key] >= 0 for item in expected
                 for key in ("formation_count", "probe_count")), "invalid expected count")
    ids = [item["cell_id"] for item in expected]
    _require(ids and len(ids) == len(set(ids)), "missing or duplicate expected cell")
    if scope == "QUALIFICATION":
        _require(len(ids) <= 2 and all(_ID.fullmatch(i) and i.startswith("unit.") for i in ids),
                 "qualification cannot contain study identities")
        _require(all(0 <= item["formation_count"] <= 3 and 0 <= item["probe_count"] <= 2
                     for item in expected), "qualification exceeds miniature budget")
    elif scope == "H1_H7":
        _require(len(ids) == 56 and sum(e["formation_count"] for e in expected) == 336
                 and sum(e["probe_count"] for e in expected) == 144, "incomplete study plan")
    else:
        raise RecordingError("unknown recording scope")


def _validate_packet(start, packet, expected):
    _require(packet["cell_id"] == start["cell_id"] == expected["cell_id"]
             and packet["owner_id"] == start["owner_id"]
             and packet["consumption_id"] == start["consumption_id"], "foreign cell or owner")
    _require(len(packet["events"]) == expected["formation_count"]
             and len(packet["findings"]) == expected["probe_count"], "incomplete cell observations")


class _AttemptLog:
    """One local attempt. A failed or incomplete attempt is never resumed."""

    def __init__(self, root, run_id, authorization, source_manifest, expected, *, scope):
        if scope == "H1_H7":
            _authorize_single_study(run_id, authorization)
            _require(Path(root).resolve() == (ROOT / "reports/tspm1_functional").resolve(),
                     "authorized study directory differs")
        _require(type(run_id) is str and _ID.fullmatch(run_id), "invalid attempt ID")
        _require(type(authorization) is str and authorization.strip(), "explicit authorization required")
        _validate_expected(scope, expected)
        self.directory = Path(root) / run_id
        self.directory.parent.mkdir(parents=True, exist_ok=True)
        self.directory.mkdir(exist_ok=False)
        self.started = time.perf_counter()
        self.status = "RUNNING"
        self.entries = []
        self.expected = comparison._canonical(expected)
        self.manifest = _seal("manifest", {"run_id": run_id, "scope": scope,
            "authorization": authorization, "authorization_digest": comparison._digest(authorization),
            "sources": source_manifest, "expected": self.expected,
            "retry_policy": "NO_AUTOMATIC_RETRY_OR_RESUME"})
        if scope == "H1_H7":
            reservation = self.directory.parent / ("authorization-" + comparison._digest(authorization) + ".json")
            _write_new(reservation, _seal("authorization_consumed", {
                "run_id": run_id, "manifest_digest": self.manifest["digest"]}))
        _write_new(self.directory / "manifest.json", self.manifest)

    def fail(self, exc):
        self.status = "FAILED"
        failure = _seal("failure", {"manifest_digest": self.manifest["digest"],
            "recording_status": "NOT_EVALUABLE", "error": _error_payload(exc),
            "completed_cells": len(self.entries), "runtime": _runtime_observation(self.started)})
        # Recording failure is allowed to propagate; never turn it into a success.
        _write_new(self.directory / "failure.json", failure)

    def record_cell(self, producer):
        _require(self.status == "RUNNING" and len(self.entries) < len(self.expected), "attempt is terminal")
        ordinal = len(self.entries) + 1
        expected = self.expected[ordinal - 1]
        suffix = self.manifest["digest"] + f".{ordinal:03d}"
        start = _seal("cell_start", {"manifest_digest": self.manifest["digest"],
            "ordinal": ordinal, "cell_id": expected["cell_id"], "plan": expected["plan"],
            "owner_id": "functional.owner." + suffix,
            "consumption_id": "functional.consume." + suffix})
        try:
            _write_new(self.directory / f"start-{ordinal:03d}.json", start)
            packet = comparison._canonical(producer(start["payload"]))
            _validate_packet(start["payload"], packet, expected)
            evidence = _seal("cell_evidence", {"manifest_digest": self.manifest["digest"],
                "start_digest": start["digest"], "packet": packet})
            _write_new(self.directory / f"cell-{ordinal:03d}.json", evidence)
            self.entries.append((start, evidence))
            return packet
        except BaseException as exc:
            self.fail(exc)
            raise

    def finish(self, summary):
        _require(self.status == "RUNNING", "attempt is terminal")
        try:
            _require(len(self.entries) == len(self.expected), "attempt is incomplete")
            errors = _seal("errors", {"manifest_digest": self.manifest["digest"], "errors": []})
            _write_new(self.directory / "errors.json", errors)
            report = _seal("result", {"manifest_digest": self.manifest["digest"],
                "scope": self.manifest["payload"]["scope"],
                "recording_status": "COMPLETE", "cell_count": len(self.entries),
                "formation_count": sum(len(e[1]["payload"]["packet"]["events"]) for e in self.entries),
                "probe_count": sum(len(e[1]["payload"]["packet"]["findings"]) for e in self.entries),
                "start_digests": [s["digest"] for s, _ in self.entries],
                "evidence_digests": [e["digest"] for _, e in self.entries],
                "errors_digest": errors["digest"], "summary": summary,
                "runtime": _runtime_observation(self.started)})
            _publish(self.directory / "result.json", report)
            _verify_files(self.directory, require_terminal=False)
            terminal = _seal("terminal", {"manifest_digest": self.manifest["digest"],
                "result_digest": report["digest"], "exit_code": 0, "status": "OK"})
            _publish(self.directory / "terminal.json", terminal)
            result = _verify_files(self.directory)
            self.status = "COMPLETED"
            return result
        except BaseException as exc:
            self.fail(exc)
            raise


def _check_digest_record(record, key):
    _require(record[key] == comparison._digest({k: v for k, v in record.items() if k != key}),
             f"invalid {key}")


def _verify_study_packet(packet, start, expected):
    result, owner, plan = packet["result"], packet["owner"], expected["plan"]
    receipt, budget = result["cell_receipt"], result["budget_receipt"]
    for record, key in ((plan, "cell_plan_digest"), (result, "cell_result_digest"),
                        (receipt, "cell_receipt_digest"), (budget, "budget_receipt_digest")):
        _check_digest_record(record, key)
    _require(result["cell_id"] == receipt["cell_id"] == budget["cell_id"] == plan["cell_id"]
             and result["cell_plan_digest"] == receipt["cell_plan_digest"]
             == budget["cell_plan_digest"] == plan["cell_plan_digest"], "cell plan/result differs")
    _require(result["event_payloads"] == packet["events"] and result["finding_payloads"] == packet["findings"]
             and receipt["event_digest"] == comparison._digest(packet["events"])
             and receipt["finding_digest"] == comparison._digest(packet["findings"])
             and receipt["budget_receipt_digest"] == budget["budget_receipt_digest"], "cell payload binding differs")
    _require(owner["status"] == receipt["owner_terminal_state"] == "COMMITTED"
             and owner["owner_id"] == receipt["owner_id"] == start["owner_id"]
             and owner["consumption_id"] == start["consumption_id"]
             and owner["cell_id"] == plan["cell_id"]
             and owner["cell_plan_digest"] == plan["cell_plan_digest"]
             and owner["authorization_digest"] == plan["authorization_digest"]
             and owner["committed_result_digest"] == result["cell_result_digest"]
             and owner["internal_error_code"] is receipt["internal_error_code"] is None,
             "owner did not commit this result")
    _require(result["prestate_digest"] == receipt["prestate_digest"] == plan["initial_state_digest"]
             and result["poststate_digest"] == receipt["poststate_digest"]
             == comparison._digest(result["poststate_payload"]), "state chain binding differs")
    for key in ("config_digest", "fixture_digest", "arm_spec_digest"):
        _require(receipt[key] == plan[key], "cell source binding differs")


def _verify_files(directory, *, require_terminal=True):
    directory = Path(directory)
    _require(not (directory / "failure.json").exists(), "attempt has a failure record")
    manifest = _read(directory / "manifest.json", "manifest")
    m = manifest["payload"]
    _require(m["authorization_digest"] == comparison._digest(m["authorization"]), "authorization changed")
    _validate_expected(m["scope"], m["expected"])
    _require(m["retry_policy"] == "NO_AUTOMATIC_RETRY_OR_RESUME", "retry policy differs")
    for source in m["sources"]["sources"]:
        _require(_sha(base64.b64decode(source["bytes_base64"], validate=True)) == source["sha256"],
                 "archived source bytes differ")
    report = _read(directory / "result.json", "result")
    r = report["payload"]
    errors = _read(directory / "errors.json", "errors")
    _require(r["recording_status"] == "COMPLETE" and r["scope"] == m["scope"]
             and r["manifest_digest"] == manifest["digest"]
             and errors["digest"] == r["errors_digest"]
             and errors["payload"] == {"manifest_digest": manifest["digest"], "errors": []},
             "incomplete or contradictory completion")
    starts, evidence, packets = [], [], []
    for ordinal, expected in enumerate(m["expected"], 1):
        start = _read(directory / f"start-{ordinal:03d}.json", "cell_start")
        cell = _read(directory / f"cell-{ordinal:03d}.json", "cell_evidence")
        s, e = start["payload"], cell["payload"]
        suffix = manifest["digest"] + f".{ordinal:03d}"
        _require(s == {"manifest_digest": manifest["digest"], "ordinal": ordinal,
                      "cell_id": expected["cell_id"], "plan": expected["plan"],
                      "owner_id": "functional.owner." + suffix, "consumption_id": "functional.consume." + suffix}
                 and e["manifest_digest"] == manifest["digest"] and e["start_digest"] == start["digest"],
                 "foreign start or evidence")
        _validate_packet(s, e["packet"], expected)
        if m["scope"] == "H1_H7":
            _verify_study_packet(e["packet"], s, expected)
        starts.append(start["digest"])
        evidence.append(cell["digest"])
        packets.append(e["packet"])
    _require(r["start_digests"] == starts and r["evidence_digests"] == evidence
             and r["cell_count"] == len(packets)
             and r["formation_count"] == sum(len(p["events"]) for p in packets)
             and r["probe_count"] == sum(len(p["findings"]) for p in packets), "completion counts differ")
    if m["scope"] == "H1_H7":
        registry = m["sources"]["registry"]
        _require(registry["cell_plans"] == [e["plan"] for e in m["expected"]]
                 and [(p["history_id"], p["arm_id"]) for p in registry["cell_plans"]]
                 == [(h, a) for h in comparison.HISTORY_IDS for a in comparison.ARM_IDS],
                 "registry role order differs")
        for expected in m["expected"]:
            _require((expected["formation_count"], expected["probe_count"])
                     == (expected["plan"]["formation_call_count"], expected["plan"]["probe_call_count"]),
                     "registry count differs")
        reservation = _read(directory.parent / ("authorization-" + m["authorization_digest"] + ".json"),
                            "authorization_consumed")
        _require(reservation["payload"] == {"run_id": m["run_id"], "manifest_digest": manifest["digest"]},
                 "authorization reservation differs")
        aggregate = r["summary"]["comparison"]
        _check_digest_record(aggregate, "comparison_result_digest")
        _require(aggregate["registry_digest"] == comparison._digest(registry)
                 and aggregate["ordered_cell_evidence_digests"] == evidence
                 and aggregate["ordered_cell_result_digests"] == [p["result"]["cell_result_digest"] for p in packets]
                 and aggregate["decision"] != "METHOD_INVALID"
                 and aggregate["r0_exact_equivalence"] is True, "invalid functional aggregation")
    if require_terminal:
        terminal = _read(directory / "terminal.json", "terminal")
        _require(terminal["payload"] == {"manifest_digest": manifest["digest"],
            "result_digest": report["digest"], "exit_code": 0, "status": "OK"}, "missing normal completion")
    return report


def verify_result(directory):
    """Read recorded bytes only. This never imports a recorded source or calls a model."""
    try:
        report = _verify_files(directory)
        return {"recording_status": "COMPLETE", "report": report}
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError, RecordingError) as exc:
        return {"recording_status": "NOT_EVALUABLE", "error": str(exc)}


def run_study_once(run_id, authorization):
    """Reserved for a separate explicit release of the same 56-cell study."""
    _authorize_single_study(run_id, authorization)
    source_manifest = _source_manifest()
    registry = comparison.build_s2dr_registry()
    config, fixtures, arms, plans, _ = registry
    source_manifest["registry"] = comparison._registry_payload(registry)
    registry_digest = comparison._digest(source_manifest["registry"])
    expected = [{"cell_id": p.cell_id, "plan": comparison._canonical(p),
                 "formation_count": p.formation_call_count, "probe_count": p.probe_call_count} for p in plans]
    log = _AttemptLog(ROOT / "reports/tspm1_functional", run_id, authorization, source_manifest,
                      expected, scope="H1_H7")
    results = []
    fixture_map, arm_map = {f.history_id: f for f in fixtures}, {a.arm_id: a for a in arms}
    try:
        for plan in plans:
            _check_sources(source_manifest)

            def produce(start):
                owner = comparison.S2DRCellOwner(start["owner_id"], plan.cell_id, plan.authorization_digest,
                    start["consumption_id"], plan.cell_plan_digest, plan.config_digest,
                    plan.fixture_digest, plan.arm_spec_digest, plan.initial_state_digest)
                try:
                    result = owner.consume_once(config, fixture_map[plan.history_id], arm_map[plan.arm_id], plan)
                    comparison.validate_s2dr_cell_result(config, fixture_map[plan.history_id], arm_map[plan.arm_id], plan, result)
                    packet = comparison._canonical({"cell_id": plan.cell_id, "owner_id": start["owner_id"],
                        "consumption_id": start["consumption_id"], "owner": owner.snapshot(), "result": result,
                        "events": result.event_payloads, "findings": result.finding_payloads})
                    _verify_study_packet(packet, start, {"plan": comparison._canonical(plan)})
                    results.append(result)
                    return packet
                except BaseException as exc:
                    exc.owner_snapshot = comparison._canonical(owner.snapshot())
                    raise

            log.record_cell(produce)
        _check_sources(source_manifest)
        aggregate = comparison._compare_s2dr_functional_results(config, plans, tuple(results), registry_digest,
            evidence_digests=tuple(e["digest"] for _, e in log.entries))
        _require(aggregate.decision != "METHOD_INVALID", "method-invalid comparison")
        summary = {"comparison": comparison._canonical(aggregate),
                   "engineering_groups": comparison._engineering_groups(dict(aggregate.per_arm_metrics)),
                   "structural_representation_status": "NOT_ASSESSED_BY_BOUND_FIXTURES"}
        return log.finish(summary)
    except BaseException as exc:
        if log.status == "RUNNING":
            log.fail(exc)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--authorization")
    args = parser.parse_args()
    if args.verify is not None:
        result = verify_result(args.verify)
        print(comparison._json_bytes(result).decode("ascii"))
        return 0 if result["recording_status"] == "COMPLETE" else 1
    if not args.run_id or not args.authorization:
        parser.error("--run-id and --authorization are required for a separately released study")
    result = run_study_once(args.run_id, args.authorization)
    print(comparison._json_bytes(result).decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
