"""Independent stdlib-only read-only verifier for one S2-IG run."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


VERIFIER_SCHEMA = "s2ig.private.result-verifier.v1"
RECORDER_SCHEMA = "s2ig.private.append-only-recorder.v1"
SUCCESS_OPERATION_COUNT = 183
SUCCESS_EVENT_COUNT = 366
MAX_FAILURE_EVENT_COUNT = 370
MAX_EVENT_BYTES = 1_536
MAX_INDIVIDUAL_BYTES = 4_095
_DIGEST = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_STATUSES = (
    ("c01", "CONSISTENT"),
    ("c02", "CONFLICT"),
    ("c03", "CONFLICT"),
    ("c04", "SINGLE_SOURCE"),
    ("c05", "SINGLE_SOURCE"),
    ("c06", "NO_CONTEXT"),
    ("c07", "NO_APPLICABLE_CONTEXT"),
    ("c08", "NO_APPLICABLE_CONTEXT"),
)

_LIMITS = {
    "RUN_PREPARE": 1_536,
    "SOURCE_MANIFEST": 3_584,
    "HISTORY_INITIALIZE": 1_280,
    "FORMATION_RECEPTOR_ANALYSIS": 2_765,
    "COMPOSITE_FORMATION": 2_801,
    "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS": 2_765,
    "COMPOSITE_READ_ONLY_PROBE": 2_048,
    "S2GC_PROJECT": 3_174,
    "S2GI_PROJECT": 2_978,
    "HISTORY_EVIDENCE_SEAL": 2_048,
    "SIGNAL_PROBE_RECEPTOR": 2_765,
    "MASKED_SIGNAL_PROBE_PROJECT": 1_792,
    "DUAL_PROBE_AND_ARM_INPUTS_BIND": 2_048,
    "SIGNAL_INVOKE": 3_584,
    "BASELINE_INVOKE": 3_584,
    "DUAL_PROBE_CASE_OWNER_COMMIT": 1_792,
    "CASE_EVIDENCE_SEAL": 3_584,
    "EXECUTION_EVIDENCE_SEAL": 3_072,
    "EVALUATION_RUN_BIND": 1_024,
    "CASE_EVALUATE": 1_536,
    "AGGREGATE_EVALUATION": 1_280,
    "TERMINAL_PREPARE": 1_024,
    "COMPLETION_MARKER_PUBLISH": 1_024,
}


@dataclass(frozen=True, slots=True)
class VerificationFinding:
    status: str
    run_id: str | None
    operation_count: int
    event_count: int
    byte_count: int
    last_event_digest: str | None
    errors: tuple[str, ...]
    finding_digest: str
    schema: str = VERIFIER_SCHEMA


def _canonical_bytes(payload: object, *, newline: bool = False) -> bytes:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return encoded + (b"\n" if newline else b"")


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(131_072), b""):
            hasher.update(block)
    return hasher.hexdigest()


def expected_evaluation_root(workspace_root: Path) -> dict[str, object]:
    """Build the independent evaluation root without execution data."""

    verifier_path = workspace_root / "tools/_s2ig_private_result_verifier.py"
    source_digests = (("tools/_s2ig_private_result_verifier.py", _file_digest(verifier_path)),)
    bindings = []
    for case_id, status in EXPECTED_STATUSES:
        payload = {
            "schema": "s2ie.evaluation-case-binding.v1",
            "case_id": case_id,
            "expected_status": status,
        }
        bindings.append((case_id, status, _digest(payload)))
    seal_payload = {
        "schema": "s2ie.evaluation-plan-seal.v1",
        "plan_id": "s2ie-evaluation-plan-01",
        "case_binding_digests": tuple(item[2] for item in bindings),
        "evaluation_source_digests": source_digests,
    }
    return {
        "plan_id": "s2ie-evaluation-plan-01",
        "case_bindings": tuple(bindings),
        "evaluation_source_digests": source_digests,
        "seal_digest": _digest(seal_payload),
    }


def _finding(
    status: str,
    run_id: str | None,
    operation_count: int,
    event_count: int,
    byte_count: int,
    last_event_digest: str | None,
    errors: list[str],
) -> VerificationFinding:
    payload = {
        "schema": VERIFIER_SCHEMA,
        "status": status,
        "run_id": run_id,
        "operation_count": operation_count,
        "event_count": event_count,
        "byte_count": byte_count,
        "last_event_digest": last_event_digest,
        "errors": errors,
    }
    return VerificationFinding(
        status,
        run_id,
        operation_count,
        event_count,
        byte_count,
        last_event_digest,
        tuple(errors),
        _digest(payload),
    )


def _expected_rows() -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []

    def add(
        operation_class: str,
        parents: tuple[str, ...],
        *,
        history_id: str | None = None,
        case_id: str | None = None,
        target: str | None = None,
    ) -> str:
        index = len(rows) + 1
        operation_id = f"ie-op-{index:03d}"
        rows.append(
            {
                "index": index,
                "operation_id": operation_id,
                "operation_class": operation_class,
                "history_id": history_id,
                "case_id": case_id,
                "parents": parents,
                "target": target or f"receipts/{operation_id}.json",
                "limit": _LIMITS[operation_class],
            }
        )
        return operation_id

    prepare = add("RUN_PREPARE", ("ROOT",), target="reservation.json")
    manifest = add("SOURCE_MANIFEST", (prepare,), target="manifest.json")
    history_lengths = (("h-c", 4), ("h-x0", 5), ("h-x1", 5), ("h-sa", 1), ("h-sb", 13), ("h-n", 10))
    initials = {history_id: add("HISTORY_INITIALIZE", (manifest,), history_id=history_id) for history_id, _ in history_lengths}
    finals: dict[str, str] = {}
    for history_id, length in history_lengths:
        state_parent = initials[history_id]
        for _ in range(length):
            receptor = add("FORMATION_RECEPTOR_ANALYSIS", (state_parent,), history_id=history_id)
            state_parent = add("COMPOSITE_FORMATION", (state_parent, receptor), history_id=history_id)
        finals[history_id] = state_parent
    seals: dict[str, str] = {}
    for history_id, _ in history_lengths:
        receptor = add("CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS", (finals[history_id],), history_id=history_id)
        probe = add("COMPOSITE_READ_ONLY_PROBE", (finals[history_id], receptor), history_id=history_id)
        gc = add("S2GC_PROJECT", (probe,), history_id=history_id)
        gi = add("S2GI_PROJECT", (gc,), history_id=history_id)
        seals[history_id] = add("HISTORY_EVIDENCE_SEAL", (finals[history_id], receptor, probe, gc, gi), history_id=history_id)
    case_histories = ("h-c", "h-x0", "h-x1", "h-sa", "h-sb", "h-n", "h-x0", "h-x1")
    case_seals: dict[str, str] = {}
    for index, history_id in enumerate(case_histories, 1):
        case_id = f"c{index:02d}"
        receptor = add("SIGNAL_PROBE_RECEPTOR", (seals[history_id],), history_id=history_id, case_id=case_id)
        masked = add("MASKED_SIGNAL_PROBE_PROJECT", (receptor,), history_id=history_id, case_id=case_id)
        dual = add("DUAL_PROBE_AND_ARM_INPUTS_BIND", (seals[history_id], masked), history_id=history_id, case_id=case_id)
        signal = add("SIGNAL_INVOKE", (dual,), history_id=history_id, case_id=case_id)
        baseline = add("BASELINE_INVOKE", (dual,), history_id=history_id, case_id=case_id)
        commit = add("DUAL_PROBE_CASE_OWNER_COMMIT", (signal, baseline), history_id=history_id, case_id=case_id)
        case_seals[case_id] = add("CASE_EVIDENCE_SEAL", (commit,), history_id=history_id, case_id=case_id)
    execution = add(
        "EXECUTION_EVIDENCE_SEAL",
        tuple(seals.values()) + tuple(case_seals.values()),
        target="evidence/execution.json",
    )
    binding = add(
        "EVALUATION_RUN_BIND",
        (execution, "external-evaluation-plan-seal"),
        target="evaluation/binding.json",
    )
    findings = tuple(
        add("CASE_EVALUATE", (binding, case_seals[case_id]), case_id=case_id, target=f"evaluation/{case_id}.json")
        for case_id, _ in EXPECTED_STATUSES
    )
    aggregate = add("AGGREGATE_EVALUATION", findings, target="evaluation/aggregate.json")
    terminal = add("TERMINAL_PREPARE", (aggregate,), target="terminal/prepared.json")
    add("COMPLETION_MARKER_PUBLISH", (terminal,), target="terminal/complete/COMPLETE")
    if len(rows) != SUCCESS_OPERATION_COUNT:
        raise AssertionError("independent registry count differs")
    return tuple(rows)


def _load_artifact(path: Path) -> tuple[dict[str, object] | None, int, str | None]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("ascii"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None, 0, None
    digest = hashlib.sha256(raw).hexdigest()
    if not isinstance(value, dict) or raw != _canonical_bytes(value, newline=True):
        return None, len(raw), digest
    return value, len(raw), digest


def _artifact_result(value: dict[str, object] | None) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    artifact = value.get("artifact")
    if not isinstance(artifact, dict):
        return None
    result = artifact.get("result")
    return result if isinstance(result, dict) else None


def verify_run_read_only(workspace_root: Path, run_directory: Path) -> VerificationFinding:
    errors: list[str] = []
    if (
        not isinstance(workspace_root, Path)
        or not workspace_root.is_absolute()
        or not isinstance(run_directory, Path)
        or not run_directory.is_absolute()
    ):
        return _finding("NOT_EVALUABLE", None, 0, 0, 0, None, ["path boundary differs"])
    rows = _expected_rows()
    reservation, reservation_bytes, _ = _load_artifact(run_directory / "reservation.json")
    manifest, manifest_bytes, _ = _load_artifact(run_directory / "manifest.json")
    reservation_result = _artifact_result(reservation)
    manifest_result = _artifact_result(manifest)
    run_id = reservation_result.get("run_id") if isinstance(reservation_result, dict) else None
    if not isinstance(run_id, str):
        run_id = None
    if reservation_result is None or manifest_result is None:
        errors.append("reservation or manifest is unreadable")

    events: list[dict[str, object]] = []
    journal_bytes = 0
    try:
        with (run_directory / "journal/operations.jsonl").open("rb") as handle:
            for raw in handle:
                journal_bytes += len(raw)
                if len(raw) > MAX_EVENT_BYTES:
                    errors.append("event exceeds bound")
                    continue
                try:
                    event = json.loads(raw.decode("ascii"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    errors.append("journal contains unreadable event")
                    continue
                if not isinstance(event, dict) or raw != _canonical_bytes(event, newline=True):
                    errors.append("event is not canonical")
                    continue
                events.append(event)
    except OSError:
        errors.append("journal is missing")

    prior = "0" * 64
    for index, event in enumerate(events, 1):
        projection = dict(event)
        event_digest = projection.pop("event_digest", None)
        if (
            event.get("event_index") != index
            or event.get("previous_event_digest") != prior
            or event_digest != _digest(projection)
        ):
            errors.append(f"event chain differs at {index}")
        if isinstance(event_digest, str):
            prior = event_digest

    complete_path = run_directory / "terminal/complete/COMPLETE"
    failure_path = run_directory / "terminal/failure/NOT_EVALUABLE"
    if failure_path.is_file() and not complete_path.exists():
        if len(events) > MAX_FAILURE_EVENT_COUNT or len(events) < 6 or len(events) % 2:
            errors.append("failure event anatomy differs")
        if tuple(event.get("operation_id") for event in events[-4:]) != (
            "ie-err-001",
            "ie-err-001",
            "ie-err-002",
            "ie-err-002",
        ):
            errors.append("failure closure tail differs")
        total = sum(path.stat().st_size for path in run_directory.rglob("*") if path.is_file())
        return _finding("NOT_EVALUABLE", run_id, max(0, (len(events) - 4) // 2), len(events), total, prior if events else None, errors)
    if failure_path.exists() and complete_path.exists():
        errors.append("success and failure terminals coexist")
    if len(events) != SUCCESS_EVENT_COUNT:
        errors.append("event count differs")

    execution_plan = manifest_result.get("execution_plan") if isinstance(manifest_result, dict) else None
    if not isinstance(execution_plan, dict):
        errors.append("execution plan is absent from manifest")
    else:
        if execution_plan.get("operation_count") != 183 or execution_plan.get("event_count") != 366:
            errors.append("execution count binding differs")
        source_digests = execution_plan.get("source_digests")
        if not isinstance(source_digests, list):
            errors.append("execution source bindings differ")
        else:
            for item in source_digests:
                if not isinstance(item, list) or len(item) != 2:
                    errors.append("execution source binding shape differs")
                    continue
                relative, expected = item
                if not isinstance(relative, str) or not isinstance(expected, str) or ".." in Path(relative).parts:
                    errors.append("execution source role is invalid")
                    continue
                try:
                    actual = _file_digest(workspace_root / relative)
                except OSError:
                    errors.append(f"execution source is missing: {relative}")
                    continue
                if actual != expected:
                    errors.append(f"execution source digest differs: {relative}")

    artifacts: dict[str, dict[str, object]] = {}
    artifact_digests: dict[str, str] = {}
    artifact_bytes = reservation_bytes + manifest_bytes
    for row in rows:
        operation_id = str(row["operation_id"])
        value, size, digest = _load_artifact(run_directory / str(row["target"]))
        if int(row["index"]) not in (1, 2):
            artifact_bytes += size
        if value is None or digest is None:
            errors.append(f"artifact is missing or noncanonical: {operation_id}")
            continue
        if size > int(row["limit"]) or size > MAX_INDIVIDUAL_BYTES:
            errors.append(f"artifact exceeds registry ceiling: {operation_id}")
        artifacts[operation_id] = value
        artifact_digests[operation_id] = digest
        if (
            not isinstance(execution_plan, dict)
            or value.get("owner_id") != execution_plan.get("owner_id")
            or not isinstance(reservation_result, dict)
            or value.get("reservation_digest") != reservation_result.get("reservation_digest")
        ):
            errors.append(f"artifact owner or reservation differs: {operation_id}")
        index = int(row["index"])
        start_offset = (index - 1) * 2
        if start_offset + 1 >= len(events):
            continue
        start, result = events[start_offset], events[start_offset + 1]
        if (
            start.get("phase") != "START"
            or result.get("phase") != "RESULT"
            or start.get("operation_id") != operation_id
            or result.get("operation_id") != operation_id
            or start.get("operation_class") != row["operation_class"]
            or value.get("operation_id") != operation_id
            or value.get("start_event_digest") != start.get("event_digest")
            or not isinstance(result.get("payload"), dict)
            or result["payload"].get("artifact_digest") != digest
        ):
            errors.append(f"operation pair or artifact binding differs: {operation_id}")
        start_payload = start.get("payload")
        if isinstance(start_payload, dict):
            parents = start_payload.get("internal_parent_result_digests")
            expected_parents = tuple(
                artifact_digests[parent]
                for parent in row["parents"]
                if isinstance(parent, str) and parent.startswith("ie-op-") and parent in artifact_digests
            )
            normalized = tuple(parents) if isinstance(parents, list) else parents
            if normalized != expected_parents:
                errors.append(f"parent binding differs: {operation_id}")

    expected_root = expected_evaluation_root(workspace_root)
    execution_package = _artifact_result(artifacts.get("ie-op-171"))
    evaluation_binding = _artifact_result(artifacts.get("ie-op-172"))
    if (
        execution_package is None
        or execution_package.get("evaluation_plan_digest") is not None
        or evaluation_binding is None
        or evaluation_binding.get("evaluation_plan_digest") != expected_root["seal_digest"]
    ):
        errors.append("execution/evaluation root separation differs")
    if len(events) >= 343:
        binding_start = events[342]
        binding_payload = binding_start.get("payload")
        if (
            not isinstance(binding_payload, dict)
            or binding_payload.get("external_parent_digest") != expected_root["seal_digest"]
        ):
            errors.append("evaluation parent is not independently bound")

    case_evidence_ops = tuple(f"ie-op-{121 + 7 * index:03d}" for index in range(8))
    expected_by_case = dict(EXPECTED_STATUSES)
    for offset, ((case_id, expected), evidence_op) in enumerate(zip(EXPECTED_STATUSES, case_evidence_ops, strict=True), 173):
        evidence = _artifact_result(artifacts.get(evidence_op))
        evaluation = _artifact_result(artifacts.get(f"ie-op-{offset:03d}"))
        if evidence is None or evaluation is None:
            errors.append(f"case evidence is missing: {case_id}")
            continue
        context_digest = evidence.get("context_function_probe_digest")
        signal_digest = evidence.get("masked_visual_probe_digest")
        if not isinstance(context_digest, str) or not isinstance(signal_digest, str):
            errors.append(f"typed probe digests are missing: {case_id}")
        if evidence.get("bundle_context_probe_digest") != context_digest:
            errors.append(f"context retrieval binding differs: {case_id}")
        if evidence.get("signal_status") != evidence.get("baseline_status"):
            errors.append(f"signal and baseline differ: {case_id}")
        if evidence.get("read_only") is not True:
            errors.append(f"read-only evidence differs: {case_id}")
        observed = evidence.get("signal_status")
        if (
            evaluation.get("case_id") != case_id
            or evaluation.get("expected_status") != expected
            or evaluation.get("observed_status") != observed
            or evaluation.get("status_matches") != (observed == expected)
        ):
            errors.append(f"evaluation projection differs: {case_id}")

    marker = _artifact_result(artifacts.get("ie-op-183"))
    if (
        marker is None
        or marker.get("status") != "COMPLETE"
        or marker.get("operation_count") != 183
        or marker.get("event_count") != 366
    ):
        errors.append("completion marker differs")
    total_bytes = journal_bytes + artifact_bytes
    if isinstance(execution_plan, dict):
        maximum = execution_plan.get("maximum_success_bytes")
        if type(maximum) is not int or total_bytes > maximum:
            errors.append("success path exceeds total budget")
    status = "RECORDING_COMPLETE" if not errors else "NOT_EVALUABLE"
    return _finding(status, run_id, len(artifacts), len(events), total_bytes, prior if events else None, errors)


__all__: tuple[str, ...] = ()
