"""One-shot neutral S2-IU qualification of S2-IT and the current run shell."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tests import test_s2id_private_two_area_conflict_signal as s2id
from tests import test_s2ip_joint_qualification as s2ip
from tests import test_s2ir_identifier_regression as s2ir
from tools import _s2ic_private_direct_two_area_conflict_baseline as direct_baseline
from tools import _s2ic_private_two_area_conflict_contract as signal_contract
from tools import _s2ic_private_two_area_conflict_signal as conflict_signal
from tools import _s2ig_private_append_only_recorder as recording
from tools import _s2ig_private_fixture_registry as fixtures
from tools import _s2ig_private_result_verifier as verifier
from tools import _s2ig_private_runner as runner


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2iu-joint-qualification-20260901-01"
MAX_IDENTIFIER = "a" * 96


def _digest(label: str) -> str:
    return fixtures.canonical_digest({"neutral_s2iu": label})


def _receptor_receipt(
    *,
    source_id: str,
    visual_fixture_id: str,
    auditory_fixture_id: str,
    window: tuple[int, int],
) -> dict[str, object]:
    return {
        "schema": "s2ig.compact-receptor-receipt.v1",
        "role": "READ_ONLY",
        "source_id": source_id,
        "visual_fixture_id": visual_fixture_id,
        "auditory_fixture_id": auditory_fixture_id,
        "window": list(window),
        "raw_sha256": _digest(f"{source_id}-raw"),
        "auditory_values_digest": _digest(f"{source_id}-auditory"),
        "visual_values_digest": _digest(f"{source_id}-visual"),
        "av_values_digest": _digest(f"{source_id}-av"),
        "envelope_digest": _digest(f"{source_id}-envelope"),
        "bound_source_digest": _digest(f"{source_id}-bound"),
        "source_digest": _digest(f"{source_id}-source"),
        "raw_payload_retained": False,
    }


def _case_plan_digest(
    case_id: str,
    history_id: str,
    context_fixture_id: str,
    signal_fixture_id: str,
    config_digest: str,
    registry_digest: str,
) -> str:
    return fixtures.canonical_digest(
        {
            "schema": "s2if.case-probe-plan.v1",
            "plan_id": f"s2ig.case-plan.{case_id}",
            "history_id": history_id,
            "context_fixture_id": context_fixture_id,
            "signal_fixture_id": signal_fixture_id,
            "config_digest": config_digest,
            "registry_digest": registry_digest,
            "context_role": "CONTEXT_RETRIEVAL_PROBE",
            "signal_role": "MASKED_SIGNAL_PROBE",
            "visible_positions": fixtures.VISIBLE_POSITIONS,
            "masked_positions": fixtures.MASKED_POSITIONS,
            "functional_budget_digest": fixtures.canonical_digest(fixtures.FUNCTIONAL_BUDGET),
        }
    )


def _masked_probe_receipt(
    *,
    case_id: str,
    case_plan_digest: str,
    source: dict[str, object],
    receptor_artifact_digest: str,
    config_digest: str,
) -> dict[str, object]:
    masked_visual_probe_digest = _digest(f"{case_id}-masked-visual-probe")
    payload = {
        "schema": "s2if.masked-signal-probe.v1",
        "case_plan_digest": case_plan_digest,
        "role": "MASKED_SIGNAL_PROBE",
        "probe_id": f"s2ig.{case_id}.signal-probe",
        "source_id": source["source_id"],
        "source_digest": source["source_digest"],
        "receptor_receipt_digest": receptor_artifact_digest,
        "config_digest": config_digest,
        "visual_values_digest": source["visual_values_digest"],
        "visible_values_digest": _digest(f"{case_id}-visible-values"),
        "mask_digest": _digest("shared-mask"),
        "masked_visual_probe_digest": masked_visual_probe_digest,
        "visible_positions": fixtures.VISIBLE_POSITIONS,
        "masked_positions": fixtures.MASKED_POSITIONS,
        "value_dimension": 18,
        "window_start_tick": source["window"][0],
        "window_end_tick": source["window"][1],
    }
    wrapper = {
        **payload,
        "masked_signal_probe_digest": fixtures.canonical_digest(payload),
    }
    return {
        "schema": "s2if.masked-signal-probe-receipt.v1",
        "masked_signal_probe": wrapper,
        "masked_visual_probe_digest": masked_visual_probe_digest,
    }


def _compact_dual_receipt(
    *,
    case_id: str,
    history_id: str,
    context_fixture_id: str,
    signal_fixture_id: str,
    history_evidence: dict[str, object],
    context_receptor: dict[str, object],
    masked_receipt: dict[str, object],
    registry_digest: str,
) -> dict[str, object]:
    wrapper = masked_receipt["masked_signal_probe"]
    config_digest = wrapper["config_digest"]
    case_plan_digest = _case_plan_digest(
        case_id,
        history_id,
        context_fixture_id,
        signal_fixture_id,
        config_digest,
        registry_digest,
    )
    context_payload = {
        "schema": "s2if.context-retrieval-probe.v1",
        "case_plan_digest": case_plan_digest,
        "role": "CONTEXT_RETRIEVAL_PROBE",
        "probe_id": f"s2ig.{history_id}.context-probe",
        "source_id": context_receptor["source_id"],
        "source_digest": context_receptor["source_digest"],
        "receptor_receipt_digest": history_evidence["context_receptor_receipt_digest"],
        "config_digest": config_digest,
        "auditory_values_digest": context_receptor["auditory_values_digest"],
        "visual_values_digest": context_receptor["visual_values_digest"],
        "av_values_digest": context_receptor["av_values_digest"],
        "function_probe_digest": history_evidence["context_function_probe_digest"],
        "value_dimension": 26,
        "window_start_tick": context_receptor["window"][0],
        "window_end_tick": context_receptor["window"][1],
    }
    context_probe_digest = fixtures.canonical_digest(context_payload)
    signal_input_digest = _digest(f"{case_id}-signal-input")
    baseline_input_digest = _digest(f"{case_id}-baseline-input")
    source_ledger_digest = fixtures.canonical_digest(verifier._DUAL_SOURCE_LEDGER)
    binding_payload = {
        "schema": "s2if.dual-probe-case-binding.v1",
        "case_plan_digest": case_plan_digest,
        "context_retrieval_probe_digest": context_probe_digest,
        "context_function_probe_digest": history_evidence["context_function_probe_digest"],
        "masked_signal_probe_digest": wrapper["masked_signal_probe_digest"],
        "masked_visual_probe_digest": wrapper["masked_visual_probe_digest"],
        "context_source_digest": context_receptor["source_digest"],
        "signal_source_digest": wrapper["source_digest"],
        "two_area_bundle_digest": history_evidence["s2gi_bundle_digest"],
        "bundle_context_probe_digest": history_evidence["context_function_probe_digest"],
        "signal_input_digest": signal_input_digest,
        "baseline_input_digest": baseline_input_digest,
        "source_ledger_digest": source_ledger_digest,
    }
    binding_digest = fixtures.canonical_digest(binding_payload)
    owner_id = f"s2ig-case-{case_id}-dual-owner"
    owner_payload = {
        "schema": "s2if.dual-probe-case-owner.v1",
        "owner_id": owner_id,
        "case_plan_digest": case_plan_digest,
        "dual_probe_binding_digest": binding_digest,
        "context_retrieval_probe_digest": context_probe_digest,
        "masked_signal_probe_digest": wrapper["masked_signal_probe_digest"],
        "two_area_bundle_digest": history_evidence["s2gi_bundle_digest"],
        "signal_input_digest": signal_input_digest,
        "baseline_input_digest": baseline_input_digest,
        "state": "READY",
        "prior_owner_digest": None,
        "signal_result_digest": None,
        "baseline_result_digest": None,
        "terminal_pair_digest": None,
    }
    return {
        "schema": runner.COMPACT_DUAL_PROBE_BINDING_SCHEMA,
        "case_plan_digest": case_plan_digest,
        "context_retrieval_probe_digest": context_probe_digest,
        "masked_signal_probe_digest": wrapper["masked_signal_probe_digest"],
        "dual_probe_binding_digest": binding_digest,
        "signal_input_digest": signal_input_digest,
        "baseline_input_digest": baseline_input_digest,
        "source_ledger_digest": source_ledger_digest,
        "dual_owner_id": owner_id,
        "dual_owner_prestate_digest": fixtures.canonical_digest(owner_payload),
    }


def _arm_receipt(
    *,
    case_id: str,
    role: str,
    expected_status: str,
    compact_dual: dict[str, object],
    masked_receipt: dict[str, object],
    history_evidence: dict[str, object],
) -> dict[str, object]:
    role_key = "signal" if role == "SIGNAL" else "baseline"
    invocation_id = f"s2ig-case-{case_id}-{role_key}-invocation"
    owner_id = f"s2ig-case-{case_id}-{role_key}-owner"
    input_digest = compact_dual[f"{role_key}_input_digest"]
    if expected_status in ("CONSISTENT", "CONFLICT"):
        present = ("A_RECENT", "B_STABLE")
        applicable = present
        differing = (1,) if expected_status == "CONFLICT" else ()
    elif expected_status == "SINGLE_SOURCE":
        applicable = ("A_RECENT",) if case_id == "c04" else ("B_STABLE",)
        present = applicable
        differing = ()
    elif expected_status == "NO_CONTEXT":
        present = ()
        applicable = ()
        differing = ()
    else:
        present = ("A_RECENT", "B_STABLE")
        applicable = ()
        differing = ()
    a_digest = _digest(f"{case_id}-{role_key}-a-finding")
    b_digest = _digest(f"{case_id}-{role_key}-b-finding")
    comparison_digest = _digest(f"{case_id}-{role_key}-comparison")
    ledger_digest = _digest(f"{case_id}-{role_key}-ledger")
    state_digest = history_evidence["state_digest"]
    result_payload = {
        "schema": signal_contract.S2IC_SCHEMA,
        "function_role": role,
        "status": expected_status,
        "input_digest": input_digest,
        "probe_digest": masked_receipt["masked_visual_probe_digest"],
        "bundle_digest": history_evidence["s2gi_bundle_digest"],
        "a_applicability_finding_digest": a_digest,
        "b_applicability_finding_digest": b_digest,
        "comparison_digest": comparison_digest,
        "present_areas": present,
        "applicable_areas": applicable,
        "differing_masked_positions": differing,
        "selected_area": None,
        "recommended_area": None,
        "automatic_selection": None,
        "prestate_digest": state_digest,
        "poststate_digest": state_digest,
        "resource_ledger_digest": ledger_digest,
    }
    result_digest = fixtures.canonical_digest(result_payload)
    owner_prestate_payload = {
        "schema": signal_contract.S2IC_SCHEMA,
        "owner_id": owner_id,
        "invocation_id": invocation_id,
        "function_role": role,
        "input_digest": input_digest,
        "state": "READY",
    }
    owner_prestate_digest = fixtures.canonical_digest(owner_prestate_payload)
    owner_poststate_payload = {
        "schema": signal_contract.S2IC_SCHEMA,
        "owner_id": owner_id,
        "invocation_id": invocation_id,
        "function_role": role,
        "input_digest": input_digest,
        "prior_owner_digest": owner_prestate_digest,
        "terminal_binding_digest": result_digest,
        "state": "CONSUMED",
    }
    owner_poststate_digest = fixtures.canonical_digest(owner_poststate_payload)
    native_receipt_payload = {
        "schema": signal_contract.S2IC_SCHEMA,
        "invocation_id": invocation_id,
        "function_role": role,
        "owner_prestate_digest": owner_prestate_digest,
        "input_digest": input_digest,
        "a_applicability_finding_digest": a_digest,
        "b_applicability_finding_digest": b_digest,
        "comparison_digest": comparison_digest,
        "resource_ledger_digest": ledger_digest,
        "result_digest": result_digest,
        "owner_poststate_digest": owner_poststate_digest,
    }
    return {
        "schema": runner.COMPACT_SIGNAL_ARM_SCHEMA,
        "invocation_id": invocation_id,
        "function_role": role,
        "owner_prestate_digest": owner_prestate_digest,
        "input_digest": input_digest,
        "status": expected_status,
        "probe_digest": masked_receipt["masked_visual_probe_digest"],
        "bundle_digest": history_evidence["s2gi_bundle_digest"],
        "a_applicability_finding_digest": a_digest,
        "b_applicability_finding_digest": b_digest,
        "comparison_digest": comparison_digest,
        "present_areas": present,
        "applicable_areas": applicable,
        "differing_masked_positions": differing,
        "prestate_digest": state_digest,
        "poststate_digest": state_digest,
        "resource_ledger_digest": ledger_digest,
        "result_digest": result_digest,
        "receipt_digest": fixtures.canonical_digest(native_receipt_payload),
        "owner_poststate_digest": owner_poststate_digest,
        "selected_area": None,
        "recommended_area": None,
        "automatic_selection": None,
        "visibility": "PRIVATE_CANDIDATE_NOT_CASE_FINDING",
    }


def _complete_neutral_recording(output_root: Path, run_id: str) -> Path:
    plan, registry = runner.materialize_execution_plan(
        WORKSPACE_ROOT,
        run_id,
        f"{run_id}-owner",
    )
    reserved = recording.AppendOnlyRunRecorder.reserve(output_root, plan, registry)
    if type(reserved) is not recording.AppendOnlyRunRecorder:
        raise AssertionError("neutral S2-IU reservation was rejected")
    recorder = reserved
    evaluation_root = verifier.expected_evaluation_root(WORKSPACE_ROOT)
    expected_status = dict(verifier.EXPECTED_STATUSES)
    case_metadata = {item[0]: item for item in verifier._CASE_METADATA}
    history_context: dict[str, tuple[dict[str, object], str]] = {}
    history_evidence: dict[str, dict[str, object]] = {}
    history_evidence_artifacts: dict[str, str] = {}
    case_runtime: dict[str, dict[str, object]] = {}
    case_evidence_artifacts: dict[str, str] = {}
    observed: dict[str, str] = {}
    rows = {row.operation_id: row for row in fixtures.REGISTRY.rows}

    for index in range(3, fixtures.SUCCESS_OPERATION_COUNT + 1):
        row = recorder.current_row()
        result: dict[str, object] = {
            "schema": "s2iu.neutral-artifact.v1",
            "operation_id": row.operation_id,
            "ordinal": index,
            "neutral_qualification": True,
        }
        input_payload: dict[str, object] = {
            "neutral_qualification": True,
            "ordinal": index,
        }
        external = evaluation_root["seal_digest"] if index == 172 else None

        if row.operation_class == "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS":
            history = fixtures.HISTORY_BY_ID[row.history_id]
            source_id = f"s2ig.{row.history_id}.context-retrieval"
            result = _receptor_receipt(
                source_id=source_id,
                visual_fixture_id=history.retrieval_source.visual_id,
                auditory_fixture_id=history.retrieval_source.auditory_id,
                window=(history.probe_window_start, history.probe_window_end),
            )
        elif row.operation_class == "HISTORY_EVIDENCE_SEAL":
            context_receipt, context_artifact_digest = history_context[row.history_id]
            result = {
                "schema": "s2ig.history-evidence.v1",
                "history_id": row.history_id,
                "history_digest": fixtures.HISTORY_BY_ID[row.history_id].history_digest,
                "generation": len(fixtures.HISTORY_BY_ID[row.history_id].steps),
                "state_digest": _digest(f"{row.history_id}-state"),
                "context_function_probe_digest": _digest(f"{row.history_id}-function-probe"),
                "context_receptor_receipt_digest": context_artifact_digest,
                "finding_digest": _digest(f"{row.history_id}-finding"),
                "s2gc_bundle_digest": _digest(f"{row.history_id}-s2gc-bundle"),
                "s2gi_bundle_digest": _digest(f"{row.history_id}-s2gi-bundle"),
                "a_recent_status": "ABSENT_VALID",
                "b_stable_status": "ABSENT_VALID",
                "read_only": True,
            }
        elif row.operation_class == "SIGNAL_PROBE_RECEPTOR":
            case_id = row.case_id
            _, history_id, signal_fixture_id, _ = case_metadata[case_id]
            history = fixtures.HISTORY_BY_ID[history_id]
            result = _receptor_receipt(
                source_id=f"s2ig.{case_id}.masked-signal-source",
                visual_fixture_id=signal_fixture_id,
                auditory_fixture_id=history.retrieval_source.auditory_id,
                window=(history.probe_window_end, history.probe_window_end + 1),
            )
        elif row.operation_class == "MASKED_SIGNAL_PROBE_PROJECT":
            case_id = row.case_id
            receptor_id = rows[row.operation_id].parent_operations[0]
            receptor_receipt = case_runtime[case_id]["signal_receptor"]
            _, history_id, signal_fixture_id, context_fixture_id = case_metadata[case_id]
            config_digest = _digest("shared-config")
            plan_digest = _case_plan_digest(
                case_id,
                history_id,
                context_fixture_id,
                signal_fixture_id,
                config_digest,
                registry.bundle_digest,
            )
            result = _masked_probe_receipt(
                case_id=case_id,
                case_plan_digest=plan_digest,
                source=receptor_receipt,
                receptor_artifact_digest=recorder.result_digests[receptor_id],
                config_digest=config_digest,
            )
        elif row.operation_class == "DUAL_PROBE_AND_ARM_INPUTS_BIND":
            case_id = row.case_id
            _, history_id, signal_fixture_id, context_fixture_id = case_metadata[case_id]
            context_receipt, _ = history_context[history_id]
            result = _compact_dual_receipt(
                case_id=case_id,
                history_id=history_id,
                context_fixture_id=context_fixture_id,
                signal_fixture_id=signal_fixture_id,
                history_evidence=history_evidence[history_id],
                context_receptor=context_receipt,
                masked_receipt=case_runtime[case_id]["masked_receipt"],
                registry_digest=registry.bundle_digest,
            )
            input_payload = {
                "case_plan_digest": result["case_plan_digest"],
                "context_retrieval_probe_digest": result["context_retrieval_probe_digest"],
                "masked_signal_probe_digest": result["masked_signal_probe_digest"],
            }
        elif row.operation_class in ("SIGNAL_INVOKE", "BASELINE_INVOKE"):
            case_id = row.case_id
            _, history_id, _, _ = case_metadata[case_id]
            role = "SIGNAL" if row.operation_class == "SIGNAL_INVOKE" else "DIRECT_BASELINE"
            result = _arm_receipt(
                case_id=case_id,
                role=role,
                expected_status=expected_status[case_id],
                compact_dual=case_runtime[case_id]["compact_dual"],
                masked_receipt=case_runtime[case_id]["masked_receipt"],
                history_evidence=history_evidence[history_id],
            )
            input_payload = {
                "dual_probe_binding_digest": case_runtime[case_id]["compact_dual"][
                    "dual_probe_binding_digest"
                ]
            }
        elif row.operation_class == "DUAL_PROBE_CASE_OWNER_COMMIT":
            case_id = row.case_id
            signal_receipt = case_runtime[case_id]["signal_receipt"]
            baseline_receipt = case_runtime[case_id]["baseline_receipt"]
            result = {
                "schema": "s2if.dual-probe-case-owner.v1",
                "owner_id": case_runtime[case_id]["compact_dual"]["dual_owner_id"],
                "state": "CONSUMED",
                "signal_result_digest": signal_receipt["result_digest"],
                "baseline_result_digest": baseline_receipt["result_digest"],
                "owner_digest": _digest(f"{case_id}-dual-owner-poststate"),
            }
        elif row.operation_class == "CASE_EVIDENCE_SEAL":
            case_id = row.case_id
            _, history_id, _, _ = case_metadata[case_id]
            compact = case_runtime[case_id]["compact_dual"]
            signal_receipt = case_runtime[case_id]["signal_receipt"]
            baseline_receipt = case_runtime[case_id]["baseline_receipt"]
            result = {
                "schema": "s2if.case-evidence.v1",
                "case_plan_digest": compact["case_plan_digest"],
                "context_retrieval_probe_digest": compact["context_retrieval_probe_digest"],
                "context_function_probe_digest": history_evidence[history_id]["context_function_probe_digest"],
                "masked_signal_probe_digest": compact["masked_signal_probe_digest"],
                "masked_visual_probe_digest": case_runtime[case_id]["masked_receipt"]["masked_visual_probe_digest"],
                "dual_probe_binding_digest": compact["dual_probe_binding_digest"],
                "source_ledger_digest": compact["source_ledger_digest"],
                "owner_prestate_digest": compact["dual_owner_prestate_digest"],
                "owner_poststate_digest": case_runtime[case_id]["owner_receipt"]["owner_digest"],
                "two_area_bundle_digest": history_evidence[history_id]["s2gi_bundle_digest"],
                "bundle_context_probe_digest": history_evidence[history_id]["context_function_probe_digest"],
                "signal_input_digest": signal_receipt["input_digest"],
                "signal_result_digest": signal_receipt["result_digest"],
                "signal_receipt_digest": signal_receipt["receipt_digest"],
                "baseline_input_digest": baseline_receipt["input_digest"],
                "baseline_result_digest": baseline_receipt["result_digest"],
                "baseline_receipt_digest": baseline_receipt["receipt_digest"],
                "composite_prestate_digest": history_evidence[history_id]["state_digest"],
                "composite_poststate_digest": history_evidence[history_id]["state_digest"],
                "signal_ledger_digest": signal_receipt["resource_ledger_digest"],
                "baseline_ledger_digest": baseline_receipt["resource_ledger_digest"],
                "signal_status": signal_receipt["status"],
                "baseline_status": baseline_receipt["status"],
                "signal_equals_baseline": True,
                "read_only": True,
                "selected_area": None,
                "recommended_area": None,
                "automatic_selection": None,
                "dual_binding_artifact_digest": case_runtime[case_id]["dual_artifact_digest"],
                "signal_artifact_digest": case_runtime[case_id]["signal_artifact_digest"],
                "baseline_artifact_digest": case_runtime[case_id]["baseline_artifact_digest"],
                "owner_commit_artifact_digest": case_runtime[case_id]["owner_artifact_digest"],
            }
            observed[case_id] = signal_receipt["status"]
        elif index == 171:
            result = {
                "schema": "s2ie.execution-evidence-package.v1",
                "execution_plan_digest": plan.plan_digest,
                "history_evidence_artifact_digests": tuple(
                    history_evidence_artifacts[item.history_id] for item in fixtures.HISTORIES
                ),
                "case_evidence_artifact_digests": tuple(
                    case_evidence_artifacts[item.case_id] for item in fixtures.FUNCTION_CASES
                ),
                "evaluation_plan_digest": None,
            }
        elif index == 172:
            result = {
                "schema": "s2ie.evaluation-run-binding.v1",
                "evaluation_plan_digest": evaluation_root["seal_digest"],
            }
        elif 173 <= index <= 180:
            case_id = f"c{index - 172:02d}"
            result = {
                "schema": "s2ie.evaluation-finding.v1",
                "case_id": case_id,
                "expected_status": expected_status[case_id],
                "observed_status": observed[case_id],
                "status_matches": observed[case_id] == expected_status[case_id],
            }
        elif index == 183:
            result = {
                "schema": "s2ie.completion-marker.v1",
                "status": "COMPLETE",
                "operation_count": fixtures.SUCCESS_OPERATION_COUNT,
                "event_count": fixtures.SUCCESS_EVENT_COUNT,
            }

        recorder.start(row.operation_id, input_payload, external_parent_digest=external)
        recorder.finish(row.operation_id, {"result": result})
        artifact_digest = recorder.result_digests[row.operation_id]
        if row.operation_class == "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS":
            history_context[row.history_id] = (result, artifact_digest)
        elif row.operation_class == "HISTORY_EVIDENCE_SEAL":
            history_evidence[row.history_id] = result
            history_evidence_artifacts[row.history_id] = artifact_digest
        elif row.operation_class == "SIGNAL_PROBE_RECEPTOR":
            case_runtime[row.case_id] = {
                "signal_receptor": result,
                "signal_receptor_artifact_digest": artifact_digest,
            }
        elif row.operation_class == "MASKED_SIGNAL_PROBE_PROJECT":
            case_runtime[row.case_id]["masked_receipt"] = result
        elif row.operation_class == "DUAL_PROBE_AND_ARM_INPUTS_BIND":
            case_runtime[row.case_id]["compact_dual"] = result
            case_runtime[row.case_id]["dual_artifact_digest"] = artifact_digest
        elif row.operation_class == "SIGNAL_INVOKE":
            case_runtime[row.case_id]["signal_receipt"] = result
            case_runtime[row.case_id]["signal_artifact_digest"] = artifact_digest
        elif row.operation_class == "BASELINE_INVOKE":
            case_runtime[row.case_id]["baseline_receipt"] = result
            case_runtime[row.case_id]["baseline_artifact_digest"] = artifact_digest
        elif row.operation_class == "DUAL_PROBE_CASE_OWNER_COMMIT":
            case_runtime[row.case_id]["owner_receipt"] = result
            case_runtime[row.case_id]["owner_artifact_digest"] = artifact_digest
        elif row.operation_class == "CASE_EVIDENCE_SEAL":
            case_evidence_artifacts[row.case_id] = artifact_digest

    if recorder.state != "COMPLETE" or recorder.event_count != 366:
        raise AssertionError("neutral S2-IU recording did not close")
    return recorder.run_directory


def _loaded_verifier_inputs(run_directory: Path) -> tuple[
    dict[str, dict[str, object]],
    dict[str, str],
    list[dict[str, object]],
    dict[str, dict[str, object]],
    dict[str, object],
]:
    rows = verifier._expected_rows()
    artifacts: dict[str, dict[str, object]] = {}
    artifact_digests: dict[str, str] = {}
    for row in rows:
        value, _, digest = verifier._load_artifact(run_directory / str(row["target"]))
        if value is None or digest is None:
            raise AssertionError(f"missing neutral artifact {row['operation_id']}")
        operation_id = str(row["operation_id"])
        artifacts[operation_id] = value
        artifact_digests[operation_id] = digest
    events = [
        json.loads(line)
        for line in (run_directory / "journal/operations.jsonl")
        .read_text(encoding="ascii")
        .splitlines()
    ]
    manifest = verifier._artifact_result(artifacts["ie-op-002"])
    if manifest is None or not isinstance(manifest.get("execution_plan"), dict):
        raise AssertionError("neutral manifest is incomplete")
    return (
        artifacts,
        artifact_digests,
        events,
        {str(row["operation_id"]): row for row in rows},
        manifest["execution_plan"],
    )


class S2IUSignalQualificationTests(s2id.S2IDPrivateTwoAreaConflictSignalTests):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory(prefix="s2iu-signal-")
        cls._case_root = Path(cls._temporary.name).resolve()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def setUp(self) -> None:
        self.output_directory = self._case_root / self._testMethodName
        self.output_directory.mkdir(parents=False, exist_ok=False)


class S2IUJointQualificationTests(s2ip.S2IPJointQualificationTests):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory(prefix="s2iu-joint-")
        cls._case_root = Path(cls._temporary.name).resolve()
        fixture_root = cls._case_root / "shared-neutral-fixture"
        fixture_root.mkdir()
        cls.valid_run = _complete_neutral_recording(
            fixture_root,
            "s2io-neutral-complete-01",
        )


class S2IUCompactReceiptQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory(prefix="s2iu-compact-")
        cls._case_root = Path(cls._temporary.name).resolve()
        fixture_root = cls._case_root / "shared-neutral-fixture"
        fixture_root.mkdir()
        cls.valid_run = _complete_neutral_recording(
            fixture_root,
            "s2iu-neutral-complete-01",
        )
        cls.loaded = _loaded_verifier_inputs(cls.valid_run)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def setUp(self) -> None:
        self.output_directory = self._case_root / self._testMethodName
        self.output_directory.mkdir(parents=False, exist_ok=False)

    def _validate_mutation(self, artifacts: dict[str, dict[str, object]]) -> list[str]:
        _, artifact_digests, events, rows, execution_plan = self.loaded
        errors: list[str] = []
        verifier._validate_s2it_compact_receipts(
            artifacts,
            artifact_digests,
            events,
            rows,
            execution_plan,
            errors,
        )
        return errors

    def test_35_all_runtime_and_operation_identifiers_are_valid_unique_and_complete(self) -> None:
        formation_values = {
            value
            for history in fixtures.HISTORIES
            for step in history.steps
            for value in (
                runner._formation_runtime_identifiers(history.history_id, step.ordinal).owner_id,
                runner._formation_runtime_identifiers(history.history_id, step.ordinal).authorization_id,
                runner._formation_runtime_identifiers(history.history_id, step.ordinal).consumption_id,
            )
        }
        case_values = {
            value
            for case in fixtures.FUNCTION_CASES
            for value in (
                runner._case_runtime_identifiers(case.case_id).signal_invocation_id,
                runner._case_runtime_identifiers(case.case_id).baseline_invocation_id,
                runner._case_runtime_identifiers(case.case_id).dual_owner_id,
                runner._case_runtime_identifiers(case.case_id).signal_owner_id,
                runner._case_runtime_identifiers(case.case_id).baseline_owner_id,
            )
        }
        operation_ids = tuple(row.operation_id for row in fixtures.REGISTRY.rows)
        self.assertEqual((114, 40, 154), (len(formation_values), len(case_values), len(formation_values | case_values)))
        self.assertTrue(formation_values.isdisjoint(case_values))
        self.assertEqual((183, 183), (len(operation_ids), len(set(operation_ids))))
        self.assertTrue(all(runner._STRICT_IDENTIFIER.fullmatch(value) for value in formation_values | case_values))
        self.assertTrue(all(runner._STRICT_IDENTIFIER.fullmatch(value) for value in operation_ids))

    def test_36_all_eight_arm_pairs_and_compact_projections_are_reached(self) -> None:
        for case in fixtures.FUNCTION_CASES:
            probe, bundle, signal_input, baseline_input, binding, _, identifiers = s2ir._case_fixture(case.case_id)
            dual_owner, signal_owner, baseline_owner = s2ir._owners(
                binding,
                signal_input,
                baseline_input,
                identifiers,
            )
            compact = runner.CompactDualProbeBindingReceiptV1.project(
                binding,
                dual_owner.prestate,
                signal_input,
                baseline_input,
            )
            signal_commit = conflict_signal.form_two_area_conflict_signal(
                probe,
                bundle,
                signal_input,
                signal_owner,
            )
            baseline_commit = direct_baseline.form_direct_two_area_conflict_baseline(
                probe,
                bundle,
                baseline_input,
                baseline_owner,
            )
            signal_receipt = runner.CompactSignalArmReceiptV1.project(signal_commit)
            baseline_receipt = runner.CompactSignalArmReceiptV1.project(baseline_commit)
            self.assertEqual(signal_commit.result.status, baseline_commit.result.status)
            self.assertEqual(binding.dual_probe_binding_digest, compact.dual_probe_binding_digest)
            for receipt in (signal_receipt, baseline_receipt):
                self.assertTrue(receipt.invocation_id)
                self.assertTrue(receipt.input_digest)
                self.assertTrue(receipt.owner_prestate_digest)

        artifacts, _, _, _, _ = self.loaded
        dual_indices = tuple(117 + 7 * index for index in range(8))
        signal_indices = tuple(118 + 7 * index for index in range(8))
        baseline_indices = tuple(119 + 7 * index for index in range(8))
        for index in dual_indices:
            artifact = artifacts[f"ie-op-{index:03d}"]
            self.assertLessEqual(len(recording.canonical_bytes(artifact)), 1_299)
        for index in (*signal_indices, *baseline_indices):
            artifact = artifacts[f"ie-op-{index:03d}"]
            receipt = verifier._artifact_result(artifact)
            self.assertIsNotNone(receipt)
            self.assertTrue({"invocation_id", "input_digest", "owner_prestate_digest"}.issubset(receipt))
            self.assertLessEqual(len(recording.canonical_bytes(artifact)), 1_999)

        sample = verifier._artifact_result(artifacts["ie-op-117"])
        self.assertIsNotNone(sample)
        worst = dict(sample)
        worst["dual_owner_id"] = MAX_IDENTIFIER
        envelope = {
            "schema": recording.RECORDER_SCHEMA,
            "operation_id": "ie-op-117",
            "owner_id": MAX_IDENTIFIER,
            "reservation_digest": _digest("max-reservation"),
            "start_event_digest": _digest("max-start"),
            "artifact": {"result": worst},
        }
        self.assertEqual(1_299, len(recording.canonical_bytes(envelope)))

    def test_37_valid_offline_reconstruction_and_complete_verification_pass(self) -> None:
        artifacts, _, _, _, _ = self.loaded
        self.assertEqual([], self._validate_mutation(artifacts))
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, self.valid_run)
        self.assertEqual("RECORDING_COMPLETE", finding.status, finding.errors)
        self.assertEqual((183, 366), (finding.operation_count, finding.event_count))

    def test_38_missing_reconstruction_field_fails_closed(self) -> None:
        artifacts = {key: dict(value) for key, value in self.loaded[0].items()}
        target = json.loads(json.dumps(artifacts["ie-op-117"]))
        del target["artifact"]["result"]["context_retrieval_probe_digest"]
        artifacts["ie-op-117"] = target
        errors = self._validate_mutation(artifacts)
        self.assertTrue(any("shape differs" in item for item in errors), errors)

    def test_39_swapped_reconstruction_fields_fail_closed(self) -> None:
        artifacts = {key: dict(value) for key, value in self.loaded[0].items()}
        target = json.loads(json.dumps(artifacts["ie-op-117"]))
        receipt = target["artifact"]["result"]
        receipt["signal_input_digest"], receipt["baseline_input_digest"] = (
            receipt["baseline_input_digest"],
            receipt["signal_input_digest"],
        )
        artifacts["ie-op-117"] = target
        errors = self._validate_mutation(artifacts)
        self.assertTrue(any("reconstruction differs" in item or "relation differs" in item for item in errors), errors)

    def test_40_foreign_reconstruction_source_fails_closed(self) -> None:
        artifacts = {key: dict(value) for key, value in self.loaded[0].items()}
        target = json.loads(json.dumps(artifacts["ie-op-117"]))
        target["artifact"]["result"]["context_retrieval_probe_digest"] = _digest("foreign-context-probe")
        artifacts["ie-op-117"] = target
        errors = self._validate_mutation(artifacts)
        self.assertTrue(any("source reconstruction differs" in item for item in errors), errors)

    def test_41_manipulated_arm_reconstruction_field_fails_closed(self) -> None:
        artifacts = {key: dict(value) for key, value in self.loaded[0].items()}
        target = json.loads(json.dumps(artifacts["ie-op-118"]))
        target["artifact"]["result"]["owner_prestate_digest"] = _digest("manipulated-owner-prestate")
        artifacts["ie-op-118"] = target
        errors = self._validate_mutation(artifacts)
        self.assertTrue(any("owner prestate differs" in item for item in errors), errors)

    def test_42_registry_budgets_gate_and_terminals_remain_bound(self) -> None:
        self.assertEqual((183, 366), (len(fixtures.REGISTRY.rows), fixtures.SUCCESS_EVENT_COUNT))
        self.assertEqual((1_037_466, 1_044_634), (fixtures.MAX_SUCCESS_PATH_BYTES, fixtures.MAX_FAILURE_PATH_BYTES))
        self.assertEqual((1_299, 1_999), (
            runner.COMPACT_DUAL_PROBE_BINDING_MAX_BYTES,
            runner.COMPACT_SIGNAL_ARM_MAX_BYTES,
        ))
        self.assertEqual((1_299, 1_999), (
            verifier.COMPACT_DUAL_PROBE_BINDING_MAX_BYTES,
            verifier.COMPACT_SIGNAL_ARM_MAX_BYTES,
        ))
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        self.assertTrue((self.valid_run / "terminal/complete/COMPLETE").is_file())
        self.assertFalse((self.valid_run / "terminal/failure/NOT_EVALUABLE").exists())


SIGNAL_TEST_METHODS = s2ip.SIGNAL_TEST_METHODS
JOINT_TEST_METHODS = s2ip.JOINT_TEST_METHODS
COMPACT_TEST_METHODS = tuple(
    f"test_{index:02d}_{suffix}"
    for index, suffix in (
        (35, "all_runtime_and_operation_identifiers_are_valid_unique_and_complete"),
        (36, "all_eight_arm_pairs_and_compact_projections_are_reached"),
        (37, "valid_offline_reconstruction_and_complete_verification_pass"),
        (38, "missing_reconstruction_field_fails_closed"),
        (39, "swapped_reconstruction_fields_fail_closed"),
        (40, "foreign_reconstruction_source_fails_closed"),
        (41, "manipulated_arm_reconstruction_field_fails_closed"),
        (42, "registry_budgets_gate_and_terminals_remain_bound"),
    )
)


def _active_ids(class_name: str, methods: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"{__name__}.{class_name}.{method}" for method in methods)


ACTIVE_TEST_IDS = (
    *_active_ids("S2IUSignalQualificationTests", SIGNAL_TEST_METHODS),
    *_active_ids("S2IUJointQualificationTests", JOINT_TEST_METHODS),
    *_active_ids("S2IUCompactReceiptQualificationTests", COMPACT_TEST_METHODS),
)
ACTIVE_OUTPUT_ROLES = tuple(
    f"case-output/{index:02d}-{method}"
    for index, method in enumerate(
        (*SIGNAL_TEST_METHODS, *JOINT_TEST_METHODS, *COMPACT_TEST_METHODS),
        1,
    )
)


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    signal_names = tuple(loader.getTestCaseNames(S2IUSignalQualificationTests))
    joint_names = tuple(loader.getTestCaseNames(S2IUJointQualificationTests))
    compact_names = tuple(loader.getTestCaseNames(S2IUCompactReceiptQualificationTests))
    discovered_ids = (
        *_active_ids("S2IUSignalQualificationTests", signal_names),
        *_active_ids("S2IUJointQualificationTests", joint_names),
        *_active_ids("S2IUCompactReceiptQualificationTests", compact_names),
    )
    if (
        signal_names != SIGNAL_TEST_METHODS
        or joint_names != JOINT_TEST_METHODS
        or compact_names != COMPACT_TEST_METHODS
    ):
        raise RuntimeError("S2-IU active test list differs from the static registration")
    if discovered_ids != ACTIVE_TEST_IDS or len(set(discovered_ids)) != len(discovered_ids):
        raise RuntimeError("S2-IU contains a duplicate or displaced test ID")
    if (
        len(ACTIVE_OUTPUT_ROLES) != len(ACTIVE_TEST_IDS)
        or len(set(ACTIVE_OUTPUT_ROLES)) != len(ACTIVE_OUTPUT_ROLES)
    ):
        raise RuntimeError("S2-IU contains a duplicate output role")
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(S2IUSignalQualificationTests))
    suite.addTests(loader.loadTestsFromTestCase(S2IUJointQualificationTests))
    suite.addTests(loader.loadTestsFromTestCase(S2IUCompactReceiptQualificationTests))
    return suite


if __name__ == "__main__":
    unittest.main()
