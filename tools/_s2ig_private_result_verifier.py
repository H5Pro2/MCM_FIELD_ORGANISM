"""Independent stdlib-only read-only verifier for one S2-IG run."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


VERIFIER_SCHEMA = "s2ig.private.result-verifier.v1"
RECORDER_SCHEMA = "s2ig.private.append-only-recorder.v1"
SUCCESS_OPERATION_COUNT = 223
SUCCESS_EVENT_COUNT = 446
MAX_FAILURE_EVENT_COUNT = 450
MAX_EVENT_BYTES = 1_536
MAX_INDIVIDUAL_BYTES = 4_095
PARENT_SET_SCHEMA = "s2ij.parent-set.v1"
COMPACT_DUAL_PROBE_BINDING_SCHEMA = "s2it.compact-dual-probe-binding-receipt.v1"
COMPACT_SIGNAL_ARM_SCHEMA = "s2ig.signal-arm-receipt.v1"
S2IC_SCHEMA = "s2ic.two-area-conflict-signal.v1"
COMPACT_DUAL_PROBE_BINDING_MAX_BYTES = 1_299
COMPACT_SIGNAL_ARM_MAX_BYTES = 1_999
MAX_PARENT_SET_PREIMAGE_BYTES = 2_816
START_REJECTED_SCHEMA = "s2im.start-rejected.v1"
START_REJECTED_MAX_BYTES = 768
ATOMIC_BOOTSTRAP_MAX_BYTES = 11_264
EARLIEST_POST_RESERVATION_FAILURE_MAX_BYTES = 22_528
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")

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

EXPECTED_CONTEXT_OUTCOMES = (
    ("c01", "ADMITTED_EQUIVALENT_CONTEXT_COMPLETED", "p1"),
    ("c02", "CONTEXT_WITHHELD", None),
    ("c03", "CONTEXT_WITHHELD", None),
    ("c04", "ADMITTED_SINGLE_SOURCE_COMPLETED", "p11"),
    ("c05", "ADMITTED_SINGLE_SOURCE_COMPLETED", "p1"),
    ("c06", "CONTEXT_WITHHELD", None),
    ("c07", "CONTEXT_WITHHELD", None),
    ("c08", "CONTEXT_WITHHELD", None),
)

_CASE_METADATA = (
    ("c01", "h-c", "p1", "p1"),
    ("c02", "h-x0", "q0", "q0"),
    ("c03", "h-x1", "q1", "q1"),
    ("c04", "h-sa", "p11", "p11"),
    ("c05", "h-sb", "p1", "p1"),
    ("c06", "h-n", "p11", "p11"),
    ("c07", "h-x0", "z0", "q0"),
    ("c08", "h-x1", "z1", "q1"),
)

_VISIBLE_POSITIONS = (0, 2, 4, 6, 8, 10, 12, 14, 16)
_MASKED_POSITIONS = (1, 3, 5, 7, 9, 11, 13, 15, 17)

_TARGET_VISUAL_VALUES = {
    "p1": (
        0.8235294117647058, 0.8235294117647058, 0.8235294117647058,
        0.8235294117647058, 0.8235294117647058, 0.8235294117647058,
        0.8235294117647058, 0.8235294117647058, 0.8235294117647058,
        0.11764705882352941, 0.11764705882352941, 0.11764705882352941,
        0.11764705882352941, 0.11764705882352941, 0.11764705882352941,
        0.11764705882352941, 0.11764705882352941, 0.11764705882352941,
    ),
    "p11": (
        0.11764705882352941, 0.11764705882352941, 0.11764705882352941,
        0.8235294117647058, 0.8235294117647058, 0.8235294117647058,
        0.8235294117647058, 0.8235294117647058, 0.8235294117647058,
        0.8235294117647058, 0.8235294117647058, 0.8235294117647058,
        0.11764705882352941, 0.11764705882352941, 0.11764705882352941,
        0.11764705882352941, 0.11764705882352941, 0.11764705882352941,
    ),
}

_FUNCTIONAL_BUDGET = {
    "visual_receptor_analyses": 52,
    "composite_formations": 38,
    "composite_read_only_probes": 6,
    "s2gc_projections": 6,
    "s2gi_projections": 6,
    "masked_probe_projections": 8,
    "signal_calls": 8,
    "baseline_calls": 8,
    "context_admission_calls": 8,
    "current_only_projections": 8,
    "admitted_context_calls": 8,
    "direct_context_baseline_calls": 8,
    "status_recomputation_count": 0,
    "applicability_recomputation_count": 0,
    "formation_write_words": 23_446,
    "formation_distance_terms": 17_784,
    "formation_control_terms": 2_052,
    "probe_write_words": 84,
    "probe_distance_terms": 2_808,
    "probe_control_terms": 288,
}

_DUAL_SOURCE_LEDGER = {
    "case_plan_validation_count": 1,
    "typed_probe_validation_count": 2,
    "source_binding_validation_count": 2,
    "receptor_receipt_validation_count": 2,
    "configuration_binding_validation_count": 2,
    "context_native_probe_relation_count": 1,
    "signal_native_probe_relation_count": 1,
    "bundle_context_probe_relation_count": 1,
    "arm_input_relation_count": 2,
    "context_value_reference_count": 26,
    "signal_position_validation_count": 18,
    "digest_validation_count": 39,
    "owner_transition_count": 1,
    "new_digest_operation_count": 8,
    "storage_or_learning_call_count": 0,
}

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
    "CONTEXT_ADMISSION_INVOKE": 3_072,
    "CURRENT_PERCEPTION_ONLY_PROJECT": 1_536,
    "ADMITTED_CONTEXT_USE_INVOKE": 3_584,
    "DIRECT_CONTEXT_USE_BASELINE_INVOKE": 3_584,
    "CONTEXT_USE_CASE_EVIDENCE_SEAL": 3_584,
    "EXECUTION_EVIDENCE_SEAL": 3_072,
    "EVALUATION_RUN_BIND": 1_024,
    "CASE_EVALUATE": 1_536,
    "AGGREGATE_EVALUATION": 1_280,
    "TERMINAL_PREPARE": 1_024,
    "COMPLETION_MARKER_PUBLISH": 1_024,
}

_RECEIPT_ROLES = {
    "RUN_PREPARE": "S2IGRunPreparationReceipt",
    "SOURCE_MANIFEST": "S2IGSourceManifestReceipt",
    "HISTORY_INITIALIZE": "S2IGHistoryInitialReceipt",
    "FORMATION_RECEPTOR_ANALYSIS": "S2IGReceptorReceipt",
    "COMPOSITE_FORMATION": "S2IGFormationReceipt",
    "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS": "S2IGReceptorReceipt",
    "COMPOSITE_READ_ONLY_PROBE": "S2IGReadOnlyReceipt",
    "S2GC_PROJECT": "S2IGS2GCProjectionReceipt",
    "S2GI_PROJECT": "S2IGS2GIProjectionReceipt",
    "HISTORY_EVIDENCE_SEAL": "S2IGHistoryEvidenceReceipt",
    "SIGNAL_PROBE_RECEPTOR": "S2IGReceptorReceipt",
    "MASKED_SIGNAL_PROBE_PROJECT": "S2IGMaskedSignalProbeReceipt",
    "DUAL_PROBE_AND_ARM_INPUTS_BIND": "S2IGDualProbeBindingReceipt",
    "SIGNAL_INVOKE": "S2IGSignalArmReceipt",
    "BASELINE_INVOKE": "S2IGBaselineArmReceipt",
    "DUAL_PROBE_CASE_OWNER_COMMIT": "S2IGDualOwnerCommitReceipt",
    "CASE_EVIDENCE_SEAL": "S2IGCaseEvidenceReceipt",
    "CONTEXT_ADMISSION_INVOKE": "S2IGContextAdmissionReceipt",
    "CURRENT_PERCEPTION_ONLY_PROJECT": "S2IGCurrentOnlyReceipt",
    "ADMITTED_CONTEXT_USE_INVOKE": "S2IGAdmittedContextUseReceipt",
    "DIRECT_CONTEXT_USE_BASELINE_INVOKE": "S2IGDirectContextUseBaselineReceipt",
    "CONTEXT_USE_CASE_EVIDENCE_SEAL": "S2IGContextUseCaseEvidenceReceipt",
    "EXECUTION_EVIDENCE_SEAL": "S2IGExecutionEvidencePackage",
    "EVALUATION_RUN_BIND": "S2IGEvaluationRunBinding",
    "CASE_EVALUATE": "S2IGEvaluationFinding",
    "AGGREGATE_EVALUATION": "S2IGAggregateFinding",
    "TERMINAL_PREPARE": "S2IGTerminalFinding",
    "COMPLETION_MARKER_PUBLISH": "S2IGCompletionMarker",
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
    outcomes = {case_id: (completion, target) for case_id, completion, target in EXPECTED_CONTEXT_OUTCOMES}
    for case_id, status in EXPECTED_STATUSES:
        completion, target = outcomes[case_id]
        payload = {
            "schema": "s2ie.evaluation-case-binding.v1",
            "case_id": case_id,
            "expected_status": status,
            "expected_completion_status": completion,
            "expected_target_visual_id": target,
        }
        bindings.append((case_id, status, completion, target, _digest(payload)))
    seal_payload = {
        "schema": "s2ie.evaluation-plan-seal.v1",
        "plan_id": "s2ie-evaluation-plan-01",
        "case_binding_digests": tuple(item[4] for item in bindings),
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
                "receipt_type": _RECEIPT_ROLES[operation_class],
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
    case_signals: dict[str, str] = {}
    case_masked: dict[str, str] = {}
    for index, history_id in enumerate(case_histories, 1):
        case_id = f"c{index:02d}"
        receptor = add("SIGNAL_PROBE_RECEPTOR", (seals[history_id],), history_id=history_id, case_id=case_id)
        masked = add("MASKED_SIGNAL_PROBE_PROJECT", (receptor,), history_id=history_id, case_id=case_id)
        case_masked[case_id] = masked
        dual = add("DUAL_PROBE_AND_ARM_INPUTS_BIND", (seals[history_id], masked), history_id=history_id, case_id=case_id)
        signal = add("SIGNAL_INVOKE", (dual,), history_id=history_id, case_id=case_id)
        case_signals[case_id] = signal
        baseline = add("BASELINE_INVOKE", (dual,), history_id=history_id, case_id=case_id)
        commit = add("DUAL_PROBE_CASE_OWNER_COMMIT", (signal, baseline), history_id=history_id, case_id=case_id)
        case_seals[case_id] = add("CASE_EVIDENCE_SEAL", (commit,), history_id=history_id, case_id=case_id)
    context_seals: dict[str, str] = {}
    for index, history_id in enumerate(case_histories, 1):
        case_id = f"c{index:02d}"
        admission = add(
            "CONTEXT_ADMISSION_INVOKE",
            (case_seals[case_id], case_signals[case_id]),
            history_id=history_id,
            case_id=case_id,
        )
        current = add(
            "CURRENT_PERCEPTION_ONLY_PROJECT",
            (case_seals[case_id], case_masked[case_id]),
            history_id=history_id,
            case_id=case_id,
        )
        plus = add(
            "ADMITTED_CONTEXT_USE_INVOKE",
            (admission, current),
            history_id=history_id,
            case_id=case_id,
        )
        direct = add(
            "DIRECT_CONTEXT_USE_BASELINE_INVOKE",
            (admission, current),
            history_id=history_id,
            case_id=case_id,
        )
        context_seals[case_id] = add(
            "CONTEXT_USE_CASE_EVIDENCE_SEAL",
            (case_seals[case_id], admission, current, plus, direct),
            history_id=history_id,
            case_id=case_id,
        )
    execution = add(
        "EXECUTION_EVIDENCE_SEAL",
        tuple(context_seals.values()),
        target="evidence/execution.json",
    )
    binding = add(
        "EVALUATION_RUN_BIND",
        (execution, "external-evaluation-plan-seal"),
        target="evaluation/binding.json",
    )
    findings = tuple(
        add(
            "CASE_EVALUATE",
            (binding, case_seals[case_id], context_seals[case_id]),
            case_id=case_id,
            target=f"evaluation/{case_id}.json",
        )
        for case_id, _ in EXPECTED_STATUSES
    )
    aggregate = add("AGGREGATE_EVALUATION", findings, target="evaluation/aggregate.json")
    terminal = add("TERMINAL_PREPARE", (aggregate,), target="terminal/prepared.json")
    add("COMPLETION_MARKER_PUBLISH", (terminal,), target="terminal/complete/COMPLETE")
    if len(rows) != SUCCESS_OPERATION_COUNT:
        raise AssertionError("independent registry count differs")
    return tuple(rows)


def _reconstruct_parent_set(
    child: dict[str, object],
    rows_by_id: dict[str, dict[str, object]],
    artifact_digests: dict[str, str],
    registry_bundle_digest: str,
    reservation_digest: str,
) -> tuple[str, int] | None:
    if (
        _DIGEST.fullmatch(registry_bundle_digest) is None
        or _DIGEST.fullmatch(reservation_digest) is None
    ):
        return None
    parent_ids = tuple(
        item
        for item in child["parents"]
        if isinstance(item, str) and item.startswith("ie-op-")
    )
    if len(parent_ids) < 2 or len(set(parent_ids)) != len(parent_ids):
        return None
    if any(item not in rows_by_id or item not in artifact_digests for item in parent_ids):
        return None
    ordered = tuple(
        sorted(parent_ids, key=lambda item: (int(rows_by_id[item]["index"]), item))
    )
    if any(int(rows_by_id[item]["index"]) >= int(child["index"]) for item in ordered):
        return None
    parent_digests = tuple(artifact_digests[item] for item in ordered)
    if len(set(parent_digests)) != len(parent_digests):
        return None
    payload = {
        "schema": PARENT_SET_SCHEMA,
        "registry_bundle_digest": registry_bundle_digest,
        "reservation_digest": reservation_digest,
        "child_operation_id": child["operation_id"],
        "parent_count": len(ordered),
        "parents": [
            {
                "parent_role": rows_by_id[item]["receipt_type"],
                "parent_operation_id": item,
                "parent_artifact_digest": artifact_digests[item],
            }
            for item in ordered
        ],
    }
    encoded_size = len(_canonical_bytes(payload, newline=True))
    if encoded_size > MAX_PARENT_SET_PREIMAGE_BYTES:
        return None
    return _digest(payload), encoded_size


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


def _start_input(
    events: list[dict[str, object]],
    operation_index: int,
) -> dict[str, object] | None:
    offset = (operation_index - 1) * 2
    if offset >= len(events):
        return None
    payload = events[offset].get("payload")
    if not isinstance(payload, dict):
        return None
    value = payload.get("input")
    return value if isinstance(value, dict) else None


def _validate_s2it_arm_receipt(
    *,
    case_id: str,
    role: str,
    operation_id: str,
    operation_index: int,
    compact_dual: dict[str, object],
    masked_probe: dict[str, object],
    history_evidence: dict[str, object],
    artifact: dict[str, object] | None,
    events: list[dict[str, object]],
    errors: list[str],
) -> None:
    receipt = _artifact_result(artifact)
    expected_keys = {
        "schema",
        "invocation_id",
        "function_role",
        "owner_prestate_digest",
        "input_digest",
        "status",
        "probe_digest",
        "bundle_digest",
        "a_applicability_finding_digest",
        "b_applicability_finding_digest",
        "comparison_digest",
        "present_areas",
        "applicable_areas",
        "differing_masked_positions",
        "prestate_digest",
        "poststate_digest",
        "resource_ledger_digest",
        "result_digest",
        "receipt_digest",
        "owner_poststate_digest",
        "selected_area",
        "recommended_area",
        "automatic_selection",
        "visibility",
    }
    if (
        receipt is None
        or set(receipt) != expected_keys
        or receipt.get("schema") != COMPACT_SIGNAL_ARM_SCHEMA
    ):
        errors.append(f"compact arm receipt shape differs: {operation_id}")
        return
    if artifact is None or len(_canonical_bytes(artifact, newline=True)) > COMPACT_SIGNAL_ARM_MAX_BYTES:
        errors.append(f"compact arm receipt exceeds S2-IT bound: {operation_id}")

    role_key = "signal" if role == "SIGNAL" else "baseline"
    expected_invocation = f"s2ig-case-{case_id}-{role_key}-invocation"
    expected_owner = f"s2ig-case-{case_id}-{role_key}-owner"
    expected_input = compact_dual.get(f"{role_key}_input_digest")
    start_input = _start_input(events, operation_index)
    expected_start_keys = {
        "dual_probe_binding_digest",
        "aggregate_visibility_binding_digest",
    }
    aggregate_visibility_binding_digest = (
        start_input.get("aggregate_visibility_binding_digest")
        if isinstance(start_input, dict)
        else None
    )
    if (
        receipt.get("invocation_id") != expected_invocation
        or _RUN_ID.fullmatch(expected_invocation) is None
        or receipt.get("function_role") != role
        or receipt.get("status") not in {
            "NO_CONTEXT",
            "NO_APPLICABLE_CONTEXT",
            "SINGLE_SOURCE",
            "CONSISTENT",
            "CONFLICT",
        }
        or receipt.get("input_digest") != expected_input
        or receipt.get("probe_digest") != masked_probe.get("masked_visual_probe_digest")
        or receipt.get("bundle_digest") != history_evidence.get("s2gi_bundle_digest")
        or receipt.get("prestate_digest") != history_evidence.get("state_digest")
        or receipt.get("poststate_digest") != history_evidence.get("state_digest")
        or receipt.get("selected_area") is not None
        or receipt.get("recommended_area") is not None
        or receipt.get("automatic_selection") is not None
        or receipt.get("visibility") != "PRIVATE_CANDIDATE_NOT_CASE_FINDING"
        or not isinstance(start_input, dict)
        or set(start_input) != expected_start_keys
        or start_input.get("dual_probe_binding_digest")
        != compact_dual.get("dual_probe_binding_digest")
        or not isinstance(aggregate_visibility_binding_digest, str)
        or _DIGEST.fullmatch(aggregate_visibility_binding_digest) is None
    ):
        errors.append(f"compact arm source relation differs: {operation_id}")
    present = receipt.get("present_areas")
    applicable = receipt.get("applicable_areas")
    differing = receipt.get("differing_masked_positions")
    if (
        not isinstance(present, list)
        or present != [area for area in ("A_RECENT", "B_STABLE") if area in present]
        or any(type(area) is not str for area in present)
        or not isinstance(applicable, list)
        or applicable != [area for area in ("A_RECENT", "B_STABLE") if area in applicable]
        or any(type(area) is not str for area in applicable)
        or not set(applicable).issubset(present)
        or not isinstance(differing, list)
        or any(type(position) is not int or position not in _MASKED_POSITIONS for position in differing)
        or differing != sorted(set(differing))
    ):
        errors.append(f"compact arm functional shape differs: {operation_id}")

    digest_fields = (
        "owner_prestate_digest",
        "input_digest",
        "probe_digest",
        "bundle_digest",
        "a_applicability_finding_digest",
        "b_applicability_finding_digest",
        "comparison_digest",
        "prestate_digest",
        "poststate_digest",
        "resource_ledger_digest",
        "result_digest",
        "receipt_digest",
        "owner_poststate_digest",
    )
    if any(
        not isinstance(receipt.get(field), str)
        or _DIGEST.fullmatch(str(receipt.get(field))) is None
        for field in digest_fields
    ):
        errors.append(f"compact arm digest field differs: {operation_id}")
        return

    owner_prestate_payload = {
        "schema": S2IC_SCHEMA,
        "owner_id": expected_owner,
        "invocation_id": expected_invocation,
        "function_role": role,
        "input_digest": expected_input,
        "state": "READY",
    }
    if receipt.get("owner_prestate_digest") != _digest(owner_prestate_payload):
        errors.append(f"compact arm owner prestate differs: {operation_id}")

    result_payload = {
        "schema": S2IC_SCHEMA,
        "function_role": role,
        "status": receipt.get("status"),
        "input_digest": receipt.get("input_digest"),
        "probe_digest": receipt.get("probe_digest"),
        "bundle_digest": receipt.get("bundle_digest"),
        "a_applicability_finding_digest": receipt.get("a_applicability_finding_digest"),
        "b_applicability_finding_digest": receipt.get("b_applicability_finding_digest"),
        "comparison_digest": receipt.get("comparison_digest"),
        "present_areas": receipt.get("present_areas"),
        "applicable_areas": receipt.get("applicable_areas"),
        "differing_masked_positions": receipt.get("differing_masked_positions"),
        "selected_area": None,
        "recommended_area": None,
        "automatic_selection": None,
        "prestate_digest": receipt.get("prestate_digest"),
        "poststate_digest": receipt.get("poststate_digest"),
        "resource_ledger_digest": receipt.get("resource_ledger_digest"),
    }
    result_digest = _digest(result_payload)
    if receipt.get("result_digest") != result_digest:
        errors.append(f"compact arm native result reconstruction differs: {operation_id}")

    owner_poststate_payload = {
        "schema": S2IC_SCHEMA,
        "owner_id": expected_owner,
        "invocation_id": expected_invocation,
        "function_role": role,
        "input_digest": expected_input,
        "prior_owner_digest": receipt.get("owner_prestate_digest"),
        "terminal_binding_digest": result_digest,
        "state": "CONSUMED",
    }
    owner_poststate_digest = _digest(owner_poststate_payload)
    if receipt.get("owner_poststate_digest") != owner_poststate_digest:
        errors.append(f"compact arm owner poststate differs: {operation_id}")

    native_receipt_payload = {
        "schema": S2IC_SCHEMA,
        "invocation_id": expected_invocation,
        "function_role": role,
        "owner_prestate_digest": receipt.get("owner_prestate_digest"),
        "input_digest": expected_input,
        "a_applicability_finding_digest": receipt.get("a_applicability_finding_digest"),
        "b_applicability_finding_digest": receipt.get("b_applicability_finding_digest"),
        "comparison_digest": receipt.get("comparison_digest"),
        "resource_ledger_digest": receipt.get("resource_ledger_digest"),
        "result_digest": result_digest,
        "owner_poststate_digest": owner_poststate_digest,
    }
    if receipt.get("receipt_digest") != _digest(native_receipt_payload):
        errors.append(f"compact arm native receipt reconstruction differs: {operation_id}")


def _validate_s2je_aggregate_start_pair(
    *,
    case_id: str,
    dual_probe_binding_digest: object,
    signal_start_input: object,
    baseline_start_input: object,
    case_evidence: object,
    errors: list[str],
) -> None:
    expected_keys = {
        "dual_probe_binding_digest",
        "aggregate_visibility_binding_digest",
    }
    if (
        not isinstance(dual_probe_binding_digest, str)
        or _DIGEST.fullmatch(dual_probe_binding_digest) is None
        or not isinstance(signal_start_input, dict)
        or not isinstance(baseline_start_input, dict)
        or set(signal_start_input) != expected_keys
        or set(baseline_start_input) != expected_keys
        or signal_start_input.get("dual_probe_binding_digest")
        != dual_probe_binding_digest
        or baseline_start_input.get("dual_probe_binding_digest")
        != dual_probe_binding_digest
    ):
        errors.append(f"aggregate START binding shape differs: {case_id}")
        return
    signal_digest = signal_start_input.get("aggregate_visibility_binding_digest")
    baseline_digest = baseline_start_input.get(
        "aggregate_visibility_binding_digest"
    )
    if (
        not isinstance(signal_digest, str)
        or _DIGEST.fullmatch(signal_digest) is None
        or not isinstance(baseline_digest, str)
        or _DIGEST.fullmatch(baseline_digest) is None
        or signal_digest == baseline_digest
    ):
        errors.append(f"aggregate START role binding differs: {case_id}")
        return
    pair_digest = (
        case_evidence.get("aggregate_visibility_binding_pair_digest")
        if isinstance(case_evidence, dict)
        else None
    )
    if (
        not isinstance(pair_digest, str)
        or _DIGEST.fullmatch(pair_digest) is None
        or pair_digest != _digest((signal_digest, baseline_digest))
    ):
        errors.append(f"aggregate START pair digest differs: {case_id}")


def _validate_s2it_compact_receipts(
    artifacts: dict[str, dict[str, object]],
    artifact_digests: dict[str, str],
    events: list[dict[str, object]],
    rows_by_id: dict[str, dict[str, object]],
    execution_plan: dict[str, object] | None,
    errors: list[str],
) -> None:
    reverse_artifacts: dict[str, str] = {}
    duplicate_artifact_digests: set[str] = set()
    for operation_id, artifact_digest in artifact_digests.items():
        if artifact_digest in reverse_artifacts:
            duplicate_artifact_digests.add(artifact_digest)
        reverse_artifacts[artifact_digest] = operation_id
    if duplicate_artifact_digests:
        errors.append("compact receipt reconstruction has duplicate artifact digests")

    registry_digest = execution_plan.get("registry_bundle_digest") if isinstance(execution_plan, dict) else None
    functional_budget_digest = _digest(_FUNCTIONAL_BUDGET)
    source_ledger_digest = _digest(_DUAL_SOURCE_LEDGER)
    for case_offset, (case_id, history_id, signal_fixture_id, context_fixture_id) in enumerate(_CASE_METADATA):
        receptor_index = 115 + 7 * case_offset
        masked_index = receptor_index + 1
        dual_index = receptor_index + 2
        signal_index = receptor_index + 3
        baseline_index = receptor_index + 4
        receptor_id = f"ie-op-{receptor_index:03d}"
        masked_id = f"ie-op-{masked_index:03d}"
        dual_id = f"ie-op-{dual_index:03d}"
        signal_id = f"ie-op-{signal_index:03d}"
        baseline_id = f"ie-op-{baseline_index:03d}"

        compact_dual = _artifact_result(artifacts.get(dual_id))
        expected_dual_keys = {
            "schema",
            "case_plan_digest",
            "context_retrieval_probe_digest",
            "masked_signal_probe_digest",
            "dual_probe_binding_digest",
            "signal_input_digest",
            "baseline_input_digest",
            "source_ledger_digest",
            "dual_owner_id",
            "dual_owner_prestate_digest",
        }
        dual_artifact = artifacts.get(dual_id)
        if (
            compact_dual is None
            or set(compact_dual) != expected_dual_keys
            or compact_dual.get("schema") != COMPACT_DUAL_PROBE_BINDING_SCHEMA
        ):
            errors.append(f"compact dual receipt shape differs: {dual_id}")
            continue
        if dual_artifact is None or len(_canonical_bytes(dual_artifact, newline=True)) > COMPACT_DUAL_PROBE_BINDING_MAX_BYTES:
            errors.append(f"compact dual receipt exceeds S2-IT bound: {dual_id}")

        digest_fields = tuple(expected_dual_keys - {"schema", "dual_owner_id"})
        if (
            any(
                not isinstance(compact_dual.get(field), str)
                or _DIGEST.fullmatch(str(compact_dual.get(field))) is None
                for field in digest_fields
            )
            or not isinstance(compact_dual.get("dual_owner_id"), str)
            or _RUN_ID.fullmatch(str(compact_dual.get("dual_owner_id"))) is None
        ):
            errors.append(f"compact dual field differs: {dual_id}")
            continue

        dual_row = rows_by_id.get(dual_id)
        masked_row = rows_by_id.get(masked_id)
        if not isinstance(dual_row, dict) or not isinstance(masked_row, dict):
            errors.append(f"compact dual registry source differs: {dual_id}")
            continue
        dual_parents = tuple(dual_row.get("parents", ()))
        masked_parents = tuple(masked_row.get("parents", ()))
        if (
            len(dual_parents) != 2
            or dual_parents[1] != masked_id
            or masked_parents != (receptor_id,)
        ):
            errors.append(f"compact dual parent roles differ: {dual_id}")
            continue
        history_seal_id = dual_parents[0]
        history_seal_row = rows_by_id.get(str(history_seal_id))
        history_evidence = _artifact_result(artifacts.get(str(history_seal_id)))
        masked_result = _artifact_result(artifacts.get(masked_id))
        signal_receptor = _artifact_result(artifacts.get(receptor_id))
        if history_evidence is None or masked_result is None or signal_receptor is None:
            errors.append(f"compact dual reconstruction source is missing: {dual_id}")
            continue
        masked_probe = masked_result.get("masked_signal_probe")
        context_receptor_digest = history_evidence.get("context_receptor_receipt_digest")
        context_receptor_id = reverse_artifacts.get(str(context_receptor_digest))
        context_receptor = _artifact_result(artifacts.get(context_receptor_id or ""))
        history_seal_parents = (
            tuple(history_seal_row.get("parents", ()))
            if isinstance(history_seal_row, dict)
            else ()
        )
        context_receptor_row = rows_by_id.get(context_receptor_id or "")
        if (
            not isinstance(masked_probe, dict)
            or context_receptor is None
            or context_receptor_id not in history_seal_parents
            or not isinstance(context_receptor_row, dict)
            or context_receptor_row.get("operation_class")
            != "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS"
            or context_receptor_row.get("history_id") != history_id
        ):
            errors.append(f"compact dual typed source is missing: {dual_id}")
            continue

        config_digest = masked_probe.get("config_digest")
        case_plan_payload = {
            "schema": "s2if.case-probe-plan.v1",
            "plan_id": f"s2ig.case-plan.{case_id}",
            "history_id": history_id,
            "context_fixture_id": context_fixture_id,
            "signal_fixture_id": signal_fixture_id,
            "config_digest": config_digest,
            "registry_digest": registry_digest,
            "context_role": "CONTEXT_RETRIEVAL_PROBE",
            "signal_role": "MASKED_SIGNAL_PROBE",
            "visible_positions": _VISIBLE_POSITIONS,
            "masked_positions": _MASKED_POSITIONS,
            "functional_budget_digest": functional_budget_digest,
        }
        case_plan_digest = _digest(case_plan_payload)

        masked_core = dict(masked_probe)
        masked_digest = masked_core.pop("masked_signal_probe_digest", None)
        context_window = context_receptor.get("window")
        signal_window = signal_receptor.get("window")
        if (
            not isinstance(context_window, list)
            or len(context_window) != 2
            or not isinstance(signal_window, list)
            or len(signal_window) != 2
        ):
            errors.append(f"compact dual context window differs: {dual_id}")
            continue
        context_probe_payload = {
            "schema": "s2if.context-retrieval-probe.v1",
            "case_plan_digest": case_plan_digest,
            "role": "CONTEXT_RETRIEVAL_PROBE",
            "probe_id": f"s2ig.{history_id}.context-probe",
            "source_id": context_receptor.get("source_id"),
            "source_digest": context_receptor.get("source_digest"),
            "receptor_receipt_digest": context_receptor_digest,
            "config_digest": config_digest,
            "auditory_values_digest": context_receptor.get("auditory_values_digest"),
            "visual_values_digest": context_receptor.get("visual_values_digest"),
            "av_values_digest": context_receptor.get("av_values_digest"),
            "function_probe_digest": history_evidence.get("context_function_probe_digest"),
            "value_dimension": 26,
            "window_start_tick": context_window[0],
            "window_end_tick": context_window[1],
        }
        context_probe_digest = _digest(context_probe_payload)
        expected_owner_id = f"s2ig-case-{case_id}-dual-owner"
        start_input = _start_input(events, dual_index)
        if (
            compact_dual.get("case_plan_digest") != case_plan_digest
            or signal_receptor.get("role") != "READ_ONLY"
            or signal_receptor.get("visual_fixture_id") != signal_fixture_id
            or masked_probe.get("source_id") != signal_receptor.get("source_id")
            or masked_probe.get("source_digest") != signal_receptor.get("source_digest")
            or masked_probe.get("receptor_receipt_digest") != artifact_digests.get(receptor_id)
            or masked_probe.get("visual_values_digest")
            != signal_receptor.get("visual_values_digest")
            or masked_probe.get("window_start_tick") != signal_window[0]
            or masked_probe.get("window_end_tick") != signal_window[1]
            or context_receptor.get("role") != "READ_ONLY"
            or context_receptor.get("visual_fixture_id") != context_fixture_id
            or masked_probe.get("case_plan_digest") != case_plan_digest
            or masked_digest != _digest(masked_core)
            or masked_result.get("masked_visual_probe_digest")
            != masked_probe.get("masked_visual_probe_digest")
            or compact_dual.get("masked_signal_probe_digest") != masked_digest
            or compact_dual.get("context_retrieval_probe_digest") != context_probe_digest
            or compact_dual.get("source_ledger_digest") != source_ledger_digest
            or compact_dual.get("dual_owner_id") != expected_owner_id
            or start_input
            != {
                "case_plan_digest": case_plan_digest,
                "context_retrieval_probe_digest": context_probe_digest,
                "masked_signal_probe_digest": masked_digest,
            }
        ):
            errors.append(f"compact dual source reconstruction differs: {dual_id}")

        binding_payload = {
            "schema": "s2if.dual-probe-case-binding.v1",
            "case_plan_digest": case_plan_digest,
            "context_retrieval_probe_digest": context_probe_digest,
            "context_function_probe_digest": history_evidence.get("context_function_probe_digest"),
            "masked_signal_probe_digest": masked_digest,
            "masked_visual_probe_digest": masked_probe.get("masked_visual_probe_digest"),
            "context_source_digest": context_receptor.get("source_digest"),
            "signal_source_digest": masked_probe.get("source_digest"),
            "two_area_bundle_digest": history_evidence.get("s2gi_bundle_digest"),
            "bundle_context_probe_digest": history_evidence.get("context_function_probe_digest"),
            "signal_input_digest": compact_dual.get("signal_input_digest"),
            "baseline_input_digest": compact_dual.get("baseline_input_digest"),
            "source_ledger_digest": source_ledger_digest,
        }
        binding_digest = _digest(binding_payload)
        owner_prestate_payload = {
            "schema": "s2if.dual-probe-case-owner.v1",
            "owner_id": expected_owner_id,
            "case_plan_digest": case_plan_digest,
            "dual_probe_binding_digest": binding_digest,
            "context_retrieval_probe_digest": context_probe_digest,
            "masked_signal_probe_digest": masked_digest,
            "two_area_bundle_digest": history_evidence.get("s2gi_bundle_digest"),
            "signal_input_digest": compact_dual.get("signal_input_digest"),
            "baseline_input_digest": compact_dual.get("baseline_input_digest"),
            "state": "READY",
            "prior_owner_digest": None,
            "signal_result_digest": None,
            "baseline_result_digest": None,
            "terminal_pair_digest": None,
        }
        if (
            compact_dual.get("dual_probe_binding_digest") != binding_digest
            or compact_dual.get("dual_owner_prestate_digest") != _digest(owner_prestate_payload)
        ):
            errors.append(f"compact dual digest reconstruction differs: {dual_id}")

        _validate_s2it_arm_receipt(
            case_id=case_id,
            role="SIGNAL",
            operation_id=signal_id,
            operation_index=signal_index,
            compact_dual=compact_dual,
            masked_probe=masked_probe,
            history_evidence=history_evidence,
            artifact=artifacts.get(signal_id),
            events=events,
            errors=errors,
        )
        case_evidence = _artifact_result(
            artifacts.get(f"ie-op-{receptor_index + 6:03d}")
        )
        _validate_s2je_aggregate_start_pair(
            case_id=case_id,
            dual_probe_binding_digest=compact_dual.get(
                "dual_probe_binding_digest"
            ),
            signal_start_input=_start_input(events, signal_index),
            baseline_start_input=_start_input(events, baseline_index),
            case_evidence=case_evidence,
            errors=errors,
        )
        _validate_s2it_arm_receipt(
            case_id=case_id,
            role="DIRECT_BASELINE",
            operation_id=baseline_id,
            operation_index=baseline_index,
            compact_dual=compact_dual,
            masked_probe=masked_probe,
            history_evidence=history_evidence,
            artifact=artifacts.get(baseline_id),
            events=events,
            errors=errors,
        )


def verify_start_rejected_read_only(
    output_root: Path,
    payload: dict[str, object],
) -> VerificationFinding:
    """Verify one pre-run rejection without treating it as a run."""

    errors: list[str] = []
    expected_keys = {
        "schema",
        "status",
        "run_id",
        "owner_id",
        "plan_digest",
        "target_path_role",
        "target_preexisted",
        "publication_performed",
        "error_code",
        "reservation_digest",
        "event_count",
        "artifact_count",
        "start_rejected_digest",
    }
    if not isinstance(output_root, Path) or not output_root.is_absolute():
        errors.append("start rejection output root differs")
    if not isinstance(payload, dict) or set(payload) != expected_keys:
        return _finding("LIFECYCLE_INVALID", None, 0, 0, 0, None, ["start rejection shape differs"])
    run_id = payload.get("run_id")
    owner_id = payload.get("owner_id")
    if (
        payload.get("schema") != START_REJECTED_SCHEMA
        or payload.get("status") != "START_REJECTED"
        or not isinstance(run_id, str)
        or _RUN_ID.fullmatch(run_id) is None
        or not isinstance(owner_id, str)
        or _RUN_ID.fullmatch(owner_id) is None
        or not isinstance(payload.get("plan_digest"), str)
        or _DIGEST.fullmatch(str(payload.get("plan_digest"))) is None
        or payload.get("target_path_role") != "RUN_DIRECTORY"
        or type(payload.get("target_preexisted")) is not bool
        or payload.get("publication_performed") is not False
        or payload.get("error_code") not in {"IG-E001", "IG-E010"}
        or payload.get("reservation_digest") is not None
        or payload.get("event_count") != 0
        or payload.get("artifact_count") != 0
    ):
        errors.append("start rejection binding differs")
    core = dict(payload)
    observed_digest = core.pop("start_rejected_digest", None)
    if not isinstance(observed_digest, str) or observed_digest != _digest(core):
        errors.append("start rejection digest differs")
    if len(_canonical_bytes(payload, newline=True)) > START_REJECTED_MAX_BYTES:
        errors.append("start rejection exceeds bound")
    if (
        isinstance(run_id, str)
        and payload.get("target_preexisted") is False
        and isinstance(output_root, Path)
        and output_root.is_absolute()
        and (output_root / run_id).exists()
    ):
        errors.append("start rejection published a final run path")
    status = "START_REJECTED" if not errors else "LIFECYCLE_INVALID"
    return _finding(status, run_id if isinstance(run_id, str) else None, 0, 0, 0, None, errors)


def verify_lifecycle_read_only(
    workspace_root: Path,
    output_root: Path,
    outcome: Path | dict[str, object],
) -> VerificationFinding:
    """Distinguish a pre-run rejection from one reserved run directory."""

    if isinstance(outcome, Path):
        return verify_run_read_only(workspace_root, outcome)
    if isinstance(outcome, dict):
        return verify_start_rejected_read_only(output_root, outcome)
    return _finding("LIFECYCLE_INVALID", None, 0, 0, 0, None, ["lifecycle outcome differs"])


def _validate_bootstrap(
    workspace_root: Path,
    events: list[dict[str, object]],
    reservation: dict[str, object] | None,
    reservation_bytes: int,
    reservation_artifact_digest: str | None,
    manifest: dict[str, object] | None,
    manifest_bytes: int,
    manifest_artifact_digest: str | None,
) -> tuple[str | None, dict[str, object] | None, list[str]]:
    errors: list[str] = []
    reservation_result = _artifact_result(reservation)
    manifest_result = _artifact_result(manifest)
    run_id = reservation_result.get("run_id") if isinstance(reservation_result, dict) else None
    execution_plan = (
        manifest_result.get("execution_plan") if isinstance(manifest_result, dict) else None
    )
    if reservation_result is None or manifest_result is None:
        errors.append("lifecycle bootstrap is incomplete")
        return run_id if isinstance(run_id, str) else None, None, errors
    if reservation_bytes > _LIMITS["RUN_PREPARE"] or manifest_bytes > _LIMITS["SOURCE_MANIFEST"]:
        errors.append("bootstrap artifact exceeds bound")
    reservation_keys = {
        "schema",
        "run_id",
        "owner_id",
        "plan_digest",
        "registry_bundle_digest",
        "state",
        "reservation_digest",
    }
    reservation_digest = reservation_result.get("reservation_digest")
    reservation_core = dict(reservation_result)
    reservation_core.pop("reservation_digest", None)
    if (
        set(reservation_result) != reservation_keys
        or reservation_result.get("schema") != RECORDER_SCHEMA
        or not isinstance(run_id, str)
        or _RUN_ID.fullmatch(run_id) is None
        or not isinstance(reservation_result.get("owner_id"), str)
        or _RUN_ID.fullmatch(str(reservation_result.get("owner_id"))) is None
        or reservation_result.get("state") != "BOOTSTRAPPING"
        or not isinstance(reservation_digest, str)
        or reservation_digest != _digest(reservation_core)
    ):
        errors.append("reservation bootstrap binding differs")
    manifest_keys = {
        "schema",
        "execution_plan",
        "registry_bundle_digest",
        "execution_fixture_digest",
        "context_role",
        "signal_role",
        "evaluation_plan_digest",
    }
    if (
        set(manifest_result) != manifest_keys
        or manifest_result.get("schema") != "s2ig.source-manifest.v1"
        or manifest_result.get("registry_bundle_digest")
        != reservation_result.get("registry_bundle_digest")
        or manifest_result.get("context_role") != "CONTEXT_RETRIEVAL_PROBE"
        or manifest_result.get("signal_role") != "MASKED_SIGNAL_PROBE"
        or manifest_result.get("evaluation_plan_digest") is not None
        or not isinstance(execution_plan, dict)
    ):
        errors.append("source manifest bootstrap binding differs")
        execution_plan = None
    if isinstance(execution_plan, dict):
        plan_keys = {
            "schema",
            "run_id",
            "owner_id",
            "fixture_digest",
            "execution_contract_digest",
            "registry_bundle_digest",
            "source_digests",
            "operation_count",
            "event_count",
            "maximum_success_bytes",
            "maximum_failure_bytes",
            "plan_digest",
        }
        plan_core = dict(execution_plan)
        plan_digest = plan_core.pop("plan_digest", None)
        source_digests = execution_plan.get("source_digests")
        if (
            set(execution_plan) != plan_keys
            or execution_plan.get("schema") != RECORDER_SCHEMA
            or not isinstance(plan_digest, str)
            or plan_digest != _digest(plan_core)
            or execution_plan.get("run_id") != run_id
            or execution_plan.get("owner_id") != reservation_result.get("owner_id")
            or execution_plan.get("registry_bundle_digest")
            != reservation_result.get("registry_bundle_digest")
            or execution_plan.get("fixture_digest")
            != manifest_result.get("execution_fixture_digest")
            or execution_plan.get("operation_count") != SUCCESS_OPERATION_COUNT
            or execution_plan.get("event_count") != SUCCESS_EVENT_COUNT
            or type(execution_plan.get("maximum_success_bytes")) is not int
            or type(execution_plan.get("maximum_failure_bytes")) is not int
            or int(execution_plan.get("maximum_success_bytes")) <= 0
            or int(execution_plan.get("maximum_failure_bytes")) <= 0
            or not isinstance(execution_plan.get("execution_contract_digest"), str)
            or _DIGEST.fullmatch(str(execution_plan.get("execution_contract_digest"))) is None
            or not isinstance(source_digests, list)
            or not 1 <= len(source_digests) <= 24
        ):
            errors.append("execution plan bootstrap binding differs")
        else:
            for item in source_digests:
                if (
                    not isinstance(item, list)
                    or len(item) != 2
                    or not isinstance(item[0], str)
                    or not isinstance(item[1], str)
                    or _DIGEST.fullmatch(item[1]) is None
                    or ".." in Path(item[0]).parts
                ):
                    errors.append("bootstrap source binding shape differs")
                    continue
                try:
                    actual = _file_digest(workspace_root / item[0])
                except OSError:
                    errors.append(f"bootstrap source is missing: {item[0]}")
                    continue
                if actual != item[1]:
                    errors.append(f"bootstrap source digest differs: {item[0]}")
    if len(events) < 4:
        errors.append("bootstrap event sequence is incomplete")
        return run_id if isinstance(run_id, str) else None, execution_plan, errors
    first_start, first_result, second_start, second_result = events[:4]
    event_keys = {
        "schema",
        "event_index",
        "phase",
        "operation_id",
        "operation_index",
        "operation_class",
        "owner_id",
        "reservation_digest",
        "previous_event_digest",
        "payload",
        "event_digest",
    }
    if (
        any(set(item) != event_keys or item.get("schema") != RECORDER_SCHEMA for item in events[:4])
        or tuple(item.get("phase") for item in events[:4])
        != ("START", "RESULT", "START", "RESULT")
        or tuple(item.get("operation_id") for item in events[:4])
        != ("ie-op-001", "ie-op-001", "ie-op-002", "ie-op-002")
        or tuple(item.get("operation_index") for item in events[:4]) != (1, 1, 2, 2)
        or tuple(item.get("operation_class") for item in events[:4])
        != ("RUN_PREPARE", "RUN_PREPARE", "SOURCE_MANIFEST", "SOURCE_MANIFEST")
    ):
        errors.append("bootstrap event operation sequence differs")
    for event in events[:4]:
        if (
            event.get("owner_id") != reservation_result.get("owner_id")
            or event.get("reservation_digest") != reservation_digest
        ):
            errors.append("bootstrap event owner or reservation differs")
            break
    first_result_payload = first_result.get("payload")
    first_start_payload = first_start.get("payload")
    second_start_payload = second_start.get("payload")
    second_result_payload = second_result.get("payload")
    plan_digest_value = execution_plan.get("plan_digest") if isinstance(execution_plan, dict) else None
    envelope_keys = {
        "schema",
        "operation_id",
        "owner_id",
        "reservation_digest",
        "start_event_digest",
        "artifact",
    }
    if (
        not isinstance(reservation, dict)
        or set(reservation) != envelope_keys
        or reservation.get("schema") != RECORDER_SCHEMA
        or not isinstance(reservation.get("artifact"), dict)
        or set(reservation["artifact"]) != {"result"}
        or reservation.get("operation_id") != "ie-op-001"
        or reservation.get("owner_id") != reservation_result.get("owner_id")
        or reservation.get("reservation_digest") != reservation_digest
        or reservation.get("start_event_digest") != first_start.get("event_digest")
        or not isinstance(first_start_payload, dict)
        or set(first_start_payload)
        != {"internal_parent_result_digests", "external_parent_digest", "input"}
        or first_start_payload.get("internal_parent_result_digests") != []
        or first_start_payload.get("external_parent_digest") is not None
        or first_start_payload.get("input")
        != {"plan_digest": plan_digest_value, "reservation_digest": reservation_digest}
        or not isinstance(first_result_payload, dict)
        or set(first_result_payload) != {"artifact_digest", "artifact_bytes"}
        or first_result_payload.get("artifact_digest") != reservation_artifact_digest
        or first_result_payload.get("artifact_bytes") != reservation_bytes
    ):
        errors.append("reservation event or artifact binding differs")
    expected_parent = [reservation_artifact_digest]
    if (
        not isinstance(manifest, dict)
        or set(manifest) != envelope_keys
        or manifest.get("schema") != RECORDER_SCHEMA
        or not isinstance(manifest.get("artifact"), dict)
        or set(manifest["artifact"]) != {"result"}
        or manifest.get("operation_id") != "ie-op-002"
        or manifest.get("owner_id") != reservation_result.get("owner_id")
        or manifest.get("reservation_digest") != reservation_digest
        or manifest.get("start_event_digest") != second_start.get("event_digest")
        or not isinstance(second_start_payload, dict)
        or set(second_start_payload)
        != {"internal_parent_result_digests", "external_parent_digest", "input"}
        or second_start_payload.get("internal_parent_result_digests") != expected_parent
        or second_start_payload.get("external_parent_digest") is not None
        or second_start_payload.get("input") != {"plan_digest": plan_digest_value}
        or not isinstance(second_result_payload, dict)
        or set(second_result_payload) != {"artifact_digest", "artifact_bytes"}
        or second_result_payload.get("artifact_digest") != manifest_artifact_digest
        or second_result_payload.get("artifact_bytes") != manifest_bytes
    ):
        errors.append("manifest event or artifact binding differs")
    if reservation_bytes + manifest_bytes + sum(
        len(_canonical_bytes(item, newline=True)) for item in events[:4]
    ) > ATOMIC_BOOTSTRAP_MAX_BYTES:
        errors.append("atomic bootstrap exceeds bound")
    return run_id if isinstance(run_id, str) else None, execution_plan, errors


def _validate_s2jk_context_use_case(
    *,
    case_id: str,
    expected_target: str | None,
    evidence: dict[str, object],
    context_evidence: dict[str, object],
    admission: dict[str, object] | None,
    current: dict[str, object] | None,
    plus: dict[str, object] | None,
    direct: dict[str, object] | None,
    artifact_digests: dict[str, str],
    operation_ids: tuple[str, str, str, str, str],
    errors: list[str],
) -> None:
    admission_id, current_id, plus_id, direct_id, _seal_id = operation_ids
    if any(item is None for item in (admission, current, plus, direct)):
        errors.append(f"context-use receipt is missing: {case_id}")
        return
    assert admission is not None and current is not None and plus is not None and direct is not None
    if (
        admission.get("schema") != "s2ig.compact-context-admission-receipt.v1"
        or current.get("schema") != "s2ig.current-perception-only-receipt.v1"
        or current.get("function_schema") != "s2ig.current-perception-only.v1"
        or plus.get("schema") != "s2ig.compact-context-use-receipt.v1"
        or direct.get("schema") != "s2ig.compact-context-use-receipt.v1"
        or plus.get("function_schema") != "s2jk.end-to-end-admitted-context-use.v1"
        or direct.get("function_schema") != "s2jk.end-to-end-admitted-context-use.v1"
        or plus.get("function_role") != "END_TO_END_ADAPTER"
        or direct.get("function_role") != "DIRECT_COMPOSITION_BASELINE"
    ):
        errors.append(f"context-use receipt role differs: {case_id}")
        return
    if (
        admission.get("source_signal_status") != evidence.get("signal_status")
        or plus.get("source_signal_status") != evidence.get("signal_status")
        or direct.get("source_signal_status") != evidence.get("signal_status")
        or admission.get("result_digest") != context_evidence.get("admission_result_digest")
        or plus.get("admission_result_digest") != admission.get("result_digest")
        or direct.get("admission_result_digest") != admission.get("result_digest")
        or plus.get("probe_digest") != context_evidence.get("probe_digest")
        or direct.get("probe_digest") != context_evidence.get("probe_digest")
        or current.get("probe_digest") != context_evidence.get("probe_digest")
        or plus.get("bundle_digest") != context_evidence.get("bundle_digest")
        or direct.get("bundle_digest") != context_evidence.get("bundle_digest")
    ):
        errors.append(f"context-use source binding differs: {case_id}")
    current_values = tuple(current.get("output_values", ()))
    probe_values = tuple(context_evidence.get("probe_values", ()))
    plus_values = tuple(plus.get("output_values", ()))
    direct_values = tuple(direct.get("output_values", ()))
    if (
        len(current_values) != 18
        or len(probe_values) != 18
        or len(plus_values) != 18
        or len(direct_values) != 18
        or current_values != probe_values
        or tuple(context_evidence.get("current_only_values", ())) != current_values
        or tuple(context_evidence.get("plus_values", ())) != plus_values
        or tuple(context_evidence.get("direct_baseline_values", ())) != direct_values
        or plus_values != direct_values
        or context_evidence.get("plus_equals_direct_baseline") is not True
    ):
        errors.append(f"context-use functional projection differs: {case_id}")
        return
    expected_values = list(probe_values)
    if expected_target is not None:
        target = _TARGET_VISUAL_VALUES.get(expected_target)
        if target is None:
            errors.append(f"context-use target binding differs: {case_id}")
            return
        for position in _MASKED_POSITIONS:
            expected_values[position] = target[position]
    expected_positions = _MASKED_POSITIONS if expected_target is not None else ()
    if (
        plus_values != tuple(expected_values)
        or tuple(direct.get("completed_positions", ())) != expected_positions
        or tuple(plus.get("completed_positions", ())) != expected_positions
        or any(plus_values[position] != probe_values[position] for position in _VISIBLE_POSITIONS)
    ):
        errors.append(f"context-use expected completion differs: {case_id}")
    if (
        context_evidence.get("admission_artifact_digest") != artifact_digests.get(admission_id)
        or context_evidence.get("current_only_artifact_digest") != artifact_digests.get(current_id)
        or context_evidence.get("plus_artifact_digest") != artifact_digests.get(plus_id)
        or context_evidence.get("direct_baseline_artifact_digest") != artifact_digests.get(direct_id)
        or context_evidence.get("all_read_only") is not True
        or context_evidence.get("status_recomputation_count") != 0
        or context_evidence.get("applicability_recomputation_count") != 0
        or plus.get("prestate_digest") != plus.get("poststate_digest")
        or direct.get("prestate_digest") != direct.get("poststate_digest")
        or current.get("prestate_digest") != current.get("poststate_digest")
    ):
        errors.append(f"context-use read-only or successor binding differs: {case_id}")


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
    reservation, reservation_bytes, reservation_artifact_digest = _load_artifact(
        run_directory / "reservation.json"
    )
    manifest, manifest_bytes, manifest_artifact_digest = _load_artifact(
        run_directory / "manifest.json"
    )
    reservation_result = _artifact_result(reservation)
    manifest_result = _artifact_result(manifest)
    run_id = reservation_result.get("run_id") if isinstance(reservation_result, dict) else None
    if not isinstance(run_id, str):
        run_id = None

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

    bootstrap_run_id, _, bootstrap_errors = _validate_bootstrap(
        workspace_root,
        events,
        reservation,
        reservation_bytes,
        reservation_artifact_digest,
        manifest,
        manifest_bytes,
        manifest_artifact_digest,
    )
    errors.extend(bootstrap_errors)
    if bootstrap_run_id is not None:
        run_id = bootstrap_run_id

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
        operation_count = max(0, (len(events) - 4) // 2)
        if operation_count < 3:
            errors.append("failure occurred before active lifecycle")
        if operation_count == 3 and total > EARLIEST_POST_RESERVATION_FAILURE_MAX_BYTES:
            errors.append("earliest post-reservation failure exceeds bound")
        return _finding(
            "NOT_EVALUABLE",
            run_id,
            operation_count,
            len(events),
            total,
            prior if events else None,
            errors,
        )
    if failure_path.exists() and complete_path.exists():
        errors.append("success and failure terminals coexist")
    if len(events) != SUCCESS_EVENT_COUNT:
        errors.append("event count differs")

    execution_plan = manifest_result.get("execution_plan") if isinstance(manifest_result, dict) else None
    if not isinstance(execution_plan, dict):
        errors.append("execution plan is absent from manifest")
    else:
        if execution_plan.get("operation_count") != 223 or execution_plan.get("event_count") != 446:
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
    expected_root = expected_evaluation_root(workspace_root)
    execution_package = _artifact_result(artifacts.get("ie-op-211"))
    evaluation_binding = _artifact_result(artifacts.get("ie-op-212"))
    if (
        execution_package is None
        or execution_package.get("evaluation_plan_digest") is not None
        or evaluation_binding is None
        or evaluation_binding.get("evaluation_plan_digest") != expected_root["seal_digest"]
    ):
        errors.append("execution/evaluation root separation differs")
    if execution_package is not None:
        expected_history_artifacts = tuple(
            artifact_digests.get(f"ie-op-{index:03d}")
            for index in (89, 94, 99, 104, 109, 114)
        )
        expected_case_artifacts = tuple(
            artifact_digests.get(f"ie-op-{121 + 7 * index:03d}")
            for index in range(8)
        )
        expected_context_artifacts = tuple(
            artifact_digests.get(f"ie-op-{175 + 5 * index:03d}")
            for index in range(8)
        )
        if (
            tuple(execution_package.get("history_evidence_artifact_digests", ()))
            != expected_history_artifacts
            or tuple(execution_package.get("case_evidence_artifact_digests", ()))
            != expected_case_artifacts
            or tuple(execution_package.get("context_use_evidence_artifact_digests", ()))
            != expected_context_artifacts
        ):
            errors.append("execution evidence transitive source binding differs")
    if len(events) >= 423:
        binding_start = events[422]
        binding_payload = binding_start.get("payload")
        if (
            not isinstance(binding_payload, dict)
            or binding_payload.get("external_parent_digest") != expected_root["seal_digest"]
        ):
            errors.append("evaluation parent is not independently bound")

    case_evidence_ops = tuple(f"ie-op-{121 + 7 * index:03d}" for index in range(8))
    expected_by_case = dict(EXPECTED_STATUSES)
    outcomes_by_case = {
        case_id: (completion, target)
        for case_id, completion, target in EXPECTED_CONTEXT_OUTCOMES
    }
    for offset, ((case_id, expected), evidence_op) in enumerate(zip(EXPECTED_STATUSES, case_evidence_ops, strict=True), 213):
        evidence = _artifact_result(artifacts.get(evidence_op))
        evaluation = _artifact_result(artifacts.get(f"ie-op-{offset:03d}"))
        context_offset = int(case_id.removeprefix("c")) - 1
        admission_op = f"ie-op-{171 + 5 * context_offset:03d}"
        current_op = f"ie-op-{172 + 5 * context_offset:03d}"
        plus_op = f"ie-op-{173 + 5 * context_offset:03d}"
        direct_context_op = f"ie-op-{174 + 5 * context_offset:03d}"
        context_evidence_op = f"ie-op-{175 + 5 * context_offset:03d}"
        context_evidence = _artifact_result(artifacts.get(context_evidence_op))
        if evidence is None or context_evidence is None or evaluation is None:
            errors.append(f"case evidence is missing: {case_id}")
            continue
        if (
            context_evidence.get("legacy_case_evidence_artifact_digest")
            != artifact_digests.get(evidence_op)
        ):
            errors.append(f"context-use legacy successor binding differs: {case_id}")
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
        evidence_index = int(evidence_op.removeprefix("ie-op-"))
        dual_op = f"ie-op-{evidence_index - 4:03d}"
        signal_op = f"ie-op-{evidence_index - 3:03d}"
        baseline_op = f"ie-op-{evidence_index - 2:03d}"
        compact_dual = _artifact_result(artifacts.get(dual_op))
        signal_receipt = _artifact_result(artifacts.get(signal_op))
        baseline_receipt = _artifact_result(artifacts.get(baseline_op))
        if (
            compact_dual is None
            or signal_receipt is None
            or baseline_receipt is None
            or evidence.get("dual_binding_artifact_digest") != artifact_digests.get(dual_op)
            or evidence.get("signal_artifact_digest") != artifact_digests.get(signal_op)
            or evidence.get("baseline_artifact_digest") != artifact_digests.get(baseline_op)
            or evidence.get("dual_probe_binding_digest")
            != compact_dual.get("dual_probe_binding_digest")
            or evidence.get("owner_prestate_digest")
            != compact_dual.get("dual_owner_prestate_digest")
            or evidence.get("signal_input_digest") != signal_receipt.get("input_digest")
            or evidence.get("signal_result_digest") != signal_receipt.get("result_digest")
            or evidence.get("signal_receipt_digest") != signal_receipt.get("receipt_digest")
            or evidence.get("baseline_input_digest") != baseline_receipt.get("input_digest")
            or evidence.get("baseline_result_digest") != baseline_receipt.get("result_digest")
            or evidence.get("baseline_receipt_digest") != baseline_receipt.get("receipt_digest")
        ):
            errors.append(f"compact receipt successor binding differs: {case_id}")
        observed = evidence.get("signal_status")
        expected_completion, expected_target = outcomes_by_case[case_id]
        if (
            evaluation.get("case_id") != case_id
            or evaluation.get("expected_status") != expected
            or evaluation.get("observed_status") != observed
            or evaluation.get("status_matches") != (observed == expected)
            or evaluation.get("expected_completion_status") != expected_completion
            or evaluation.get("observed_completion_status")
            != context_evidence.get("completion_status")
            or evaluation.get("completion_status_matches")
            != (context_evidence.get("completion_status") == expected_completion)
            or evaluation.get("plus_equals_direct_baseline")
            != context_evidence.get("plus_equals_direct_baseline")
        ):
            errors.append(f"evaluation projection differs: {case_id}")
        _validate_s2jk_context_use_case(
            case_id=case_id,
            expected_target=expected_target,
            evidence=evidence,
            context_evidence=context_evidence,
            admission=_artifact_result(artifacts.get(admission_op)),
            current=_artifact_result(artifacts.get(current_op)),
            plus=_artifact_result(artifacts.get(plus_op)),
            direct=_artifact_result(artifacts.get(direct_context_op)),
            artifact_digests=artifact_digests,
            operation_ids=(admission_op, current_op, plus_op, direct_context_op, context_evidence_op),
            errors=errors,
        )

    rows_by_id = {str(row["operation_id"]): row for row in rows}
    registry_bundle_digest = (
        execution_plan.get("registry_bundle_digest")
        if isinstance(execution_plan, dict)
        else None
    )
    reservation_digest = (
        reservation_result.get("reservation_digest")
        if isinstance(reservation_result, dict)
        else None
    )
    _validate_s2it_compact_receipts(
        artifacts,
        artifact_digests,
        events,
        rows_by_id,
        execution_plan if isinstance(execution_plan, dict) else None,
        errors,
    )
    for row in rows:
        operation_id = str(row["operation_id"])
        start_offset = (int(row["index"]) - 1) * 2
        if start_offset >= len(events):
            continue
        start_payload = events[start_offset].get("payload")
        if not isinstance(start_payload, dict):
            errors.append(f"parent payload is missing: {operation_id}")
            continue
        internal_ids = tuple(
            item
            for item in row["parents"]
            if isinstance(item, str) and item.startswith("ie-op-")
        )
        internal_keys = {
            key for key in start_payload if isinstance(key, str) and key.startswith("internal_parent_")
        }
        if len(internal_ids) >= 2:
            expected_keys = {
                "internal_parent_projection_schema",
                "internal_parent_count",
                "internal_parent_set_digest",
            }
            reconstructed = None
            if isinstance(registry_bundle_digest, str) and isinstance(reservation_digest, str):
                reconstructed = _reconstruct_parent_set(
                    row,
                    rows_by_id,
                    artifact_digests,
                    registry_bundle_digest,
                    reservation_digest,
                )
            if (
                internal_keys != expected_keys
                or start_payload.get("internal_parent_projection_schema") != PARENT_SET_SCHEMA
                or start_payload.get("internal_parent_count") != len(internal_ids)
                or reconstructed is None
                or start_payload.get("internal_parent_set_digest") != reconstructed[0]
            ):
                errors.append(f"compact parent binding differs: {operation_id}")
        else:
            expected_parents = tuple(
                artifact_digests[parent]
                for parent in internal_ids
                if parent in artifact_digests
            )
            parents = start_payload.get("internal_parent_result_digests")
            normalized = tuple(parents) if isinstance(parents, list) else parents
            if (
                internal_keys != {"internal_parent_result_digests"}
                or normalized != expected_parents
                or len(expected_parents) != len(internal_ids)
            ):
                errors.append(f"parent binding differs: {operation_id}")

    marker = _artifact_result(artifacts.get("ie-op-223"))
    if (
        marker is None
        or marker.get("status") != "COMPLETE"
        or marker.get("operation_count") != 223
        or marker.get("event_count") != 446
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
