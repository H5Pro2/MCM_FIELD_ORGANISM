"""One bound, neutral S2-TY overall qualification; never opens NU/TW payloads."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import ast

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy

from tools import _s2nj_private_auditory_output_projection as nj
from tools import _s2ty_resource_ledger as ledger
from tools import _s2ty_source_time_binding as binding


QUALIFICATION_ID = "s2ty-neutral-overall-qualification-20260920-03"
RESULT_DIR = ROOT / "reports" / "s2ty" / QUALIFICATION_ID
TEST_MODULES = (
    "tests.test_s2ty_event_control",
    "tests.test_s2ty_record_verification",
    "tests.test_s2ty_resource_ledger",
    "tests.test_s2ty_failure_verification",
    "tests.test_s2ty_source_time_binding",
    "tests.test_s2ty_run_envelope",
)
TEST_IDS = (
    "tests.test_s2ty_event_control.Tests.test_complete",
    "tests.test_s2ty_event_control.Tests.test_primary_error",
    "tests.test_s2ty_event_control.Tests.test_owner_close_failure_without_primary_error_closes_direct_owner",
    "tests.test_s2ty_event_control.Tests.test_owner_close_failure_preserves_primary_error_and_closes_direct_owner",
    "tests.test_s2ty_record_verification.Tests.test_full_flow",
    "tests.test_s2ty_record_verification.Tests.test_manipulated_receipts_and_inventory_fail",
    "tests.test_s2ty_record_verification.Tests.test_order_and_status_fail",
    "tests.test_s2ty_record_verification.Tests.test_inner_success_status_mismatch_is_rejected",
    "tests.test_s2ty_record_verification.Tests.test_exact_confirmation_keeps_generation_and_fifo_position",
    "tests.test_s2ty_record_verification.Tests.test_direct_hint_decision_before_eviction_is_verified",
    "tests.test_s2ty_record_verification.Tests.test_eviction_manipulation_fails",
    "tests.test_s2ty_record_verification.Tests.test_duplicate_owner_arm_is_rejected",
    "tests.test_s2ty_record_verification.Tests.test_missing_owner_arm_is_rejected",
    "tests.test_s2ty_record_verification.Tests.test_unknown_owner_arm_is_rejected",
    "tests.test_s2ty_resource_ledger.Tests.test_planned_shape_has_bounded_dual_arm_native_peak",
    "tests.test_s2ty_resource_ledger.Tests.test_fft_workspace_and_python_administration_are_explicitly_separate",
    "tests.test_s2ty_resource_ledger.Tests.test_success_and_failure_records_are_alternative_envelopes",
    "tests.test_s2ty_resource_ledger.Tests.test_source_binding_is_required_before_a_run_budget_can_pass",
    "tests.test_s2ty_resource_ledger.Tests.test_boundary_and_overflow_report_full_failure_contributions",
    "tests.test_s2ty_resource_ledger.Tests.test_global_limit_is_enforced_when_local_classes_fit",
    "tests.test_s2ty_failure_verification.Tests.test_error_before_first_formation_is_verified",
    "tests.test_s2ty_failure_verification.Tests.test_error_after_completed_progress_is_verified",
    "tests.test_s2ty_failure_verification.Tests.test_error_between_arms_records_changed_direct_state",
    "tests.test_s2ty_failure_verification.Tests.test_owner_close_error_preserves_primary_error",
    "tests.test_s2ty_failure_verification.Tests.test_owner_close_error_after_complete_input_is_verified",
    "tests.test_s2ty_failure_verification.Tests.test_manipulated_progress_arm_and_close_are_rejected",
    "tests.test_s2ty_failure_verification.Tests.test_mismatched_attempted_and_completed_counters_are_rejected",
    "tests.test_s2ty_failure_verification.Tests.test_owner_close_failure_requires_a_failed_close_receipt",
    "tests.test_s2ty_failure_verification.Tests.test_complete_neutral_failure_envelopes_fit_the_failure_ledger_branch",
    "tests.test_s2ty_source_time_binding.Tests.test_s2tw_shape_reuse_and_native_time_are_bound",
    "tests.test_s2ty_source_time_binding.Tests.test_logical_clock_is_complete_and_separate_from_native_time",
    "tests.test_s2ty_source_time_binding.Tests.test_missing_duplicate_reverse_and_manipulated_runtime_times_fail_closed",
    "tests.test_s2ty_source_time_binding.Tests.test_payload_profile_time_and_endpoint_failures_are_typed",
    "tests.test_s2ty_source_time_binding.Tests.test_once_created_half_values_are_shared_by_both_arms",
    "tests.test_s2ty_source_time_binding.Tests.test_source_binding_artifact_is_counted_by_ledger",
    "tests.test_s2ty_run_envelope.Tests.test_complete_neutral_chain_has_distinct_owners_and_independent_verification",
    "tests.test_s2ty_run_envelope.Tests.test_source_failure_stops_before_event_control_with_endpoint_progress",
    "tests.test_s2ty_run_envelope.Tests.test_swapped_endpoint_and_invented_source_failure_are_rejected",
    "tests.test_s2ty_run_envelope.Tests.test_time_failure_stops_before_event_control",
    "tests.test_s2ty_run_envelope.Tests.test_code_binding_and_distinct_owners_are_required",
    "tests.test_s2ty_run_envelope.Tests.test_envelope_manipulation_is_rejected",
    "tests.test_s2ty_run_envelope.Tests.test_control_failure_after_direct_arm_progress_uses_failure_verifier",
    "tests.test_s2ty_run_envelope.Tests.test_materialized_neutral_chain_records_hash_receptor_and_nj_calls",
    "tests.test_s2ty_run_envelope.Tests.test_materialized_hash_receptor_and_nj_failures_stop_before_memory",
    "tests.test_s2ty_run_envelope.Tests.test_materialization_failure_counts_follow_direct_call_steps_not_phase",
    "tests.test_s2ty_run_envelope.Tests.test_materialized_source_failure_keeps_prior_receipts_and_direct_counts",
    "tests.test_s2ty_run_envelope.Tests.test_materialized_manifest_failure_is_verified_without_revalidation_escape",
    "tests.test_s2ty_run_envelope.Tests.test_materialized_control_failure_uses_record_failure_verifier",
    "tests.test_s2ty_run_envelope.Tests.test_materialization_receipt_digest_bindings_reject_manipulation",
)
CODE_PATHS = (
    "tools/_s2ty_event_control.py",
    "tools/_s2ty_audio_materialization.py",
    "tools/_s2ty_perception_trace_adapter.py",
    "tools/_s2ty_record.py",
    "tools/_s2ty_record_verification.py",
    "tools/_s2ty_failure_verification.py",
    "tools/_s2ty_resource_ledger.py",
    "tools/_s2ty_source_time_binding.py",
    "tools/_s2tu_retained_trace.py",
    "tools/_s2tw_exact_confirmation.py",
    "tools/_s2tw_source_schedule.py",
    "tools/_s2ts_temporal_trace_run.py",
    "tools/_s2ts_temporal_trace.py",
    "tools/_s2nj_private_auditory_output_projection.py",
    "mcm_field_organism/log_spectral_receptor.py",
    "mcm_field_organism/broadband_hearing_path.py",
    "tools/_s2ty_run_envelope.py",
    "reports/s2ty/qualify_s2ty_neutral_once.py",
)
TEST_PATHS = tuple(module.replace(".", "/") + ".py" for module in TEST_MODULES)
STARTER_PRECHECK_PATH = "tests/test_s2ty_formal_qualification_starter.py"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def file_hashes(paths):
    return {path: digest_bytes((ROOT / path).read_bytes()) for path in paths}


def write_json(path, value):
    path.write_bytes(canonical(value))


def discovered_test_ids():
    identifiers = []
    for path in TEST_PATHS:
        tree = ast.parse((ROOT / path).read_text(encoding="utf-8"), filename=path)
        module_name = path[:-3].replace("/", ".")
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name.startswith("test_"):
                        identifiers.append(f"{module_name}.{node.name}.{member.name}")
    return tuple(identifiers)


def executed_test_entries(output):
    pattern = re.compile(r"^(test_[A-Za-z0-9_]+) \(([^)]+)\) \.\.\. (ok|FAIL|ERROR|skipped.*)$", re.MULTILINE)
    return tuple((match.group(2), match.group(1), match.group(3)) for match in pattern.finditer(output))


def qualification_outcome(*, exit_code, output, observation, before, after):
    entries = executed_test_entries(output)
    actual_ids = tuple(identifier for identifier, _, _ in entries)
    reported = int(match.group(1)) if (match := re.search(r"Ran (\d+) tests", output)) else None
    observation_valid = (
        type(observation) is dict
        and observation.get("counts") == {"pcm_hashes": 22, "audio_analyses": 22, "nj_projections": 22}
        and observation.get("success_branch", {}).get("contributions", {}).get("record", 1) <= observation.get("record_reserve_bytes", 0)
    )
    exact_ids = (
        len(actual_ids) == len(TEST_IDS)
        and len(set(actual_ids)) == len(actual_ids)
        and set(actual_ids) == set(TEST_IDS)
        and all(identifier.rsplit(".", 1)[1] == method for identifier, method, _ in entries)
    )
    all_successful = len(entries) == len(TEST_IDS) and all(status == "ok" for _, _, status in entries)
    reasons = []
    if exit_code != 0:
        reasons.append("UNITTEST_EXIT_NONZERO")
    if reported != len(TEST_IDS):
        reasons.append("TEST_COUNT_INVALID")
    if not exact_ids:
        reasons.append("TEST_IDS_INVALID")
    if not all_successful:
        reasons.append("TEST_RESULTS_INVALID")
    if before != after:
        reasons.append("HASHES_CHANGED")
    if not observation_valid:
        reasons.append("MATERIALIZATION_OBSERVATION_INVALID")
    return {
        "qualified": not reasons,
        "reasons": reasons,
        "tests_reported": reported,
        "tests_executed": actual_ids,
        "test_ids_exact": exact_ids,
        "test_results_all_ok": all_successful,
        "observation_valid": observation_valid,
        "hashes_unchanged": before == after,
    }


def environment_and_profiles():
    manifest = binding.source_manifest()
    return {
        "python": sys.version,
        "python_implementation": platform.python_implementation(),
        "numpy": numpy.__version__,
        "profiles": {
            "raw_profile_digest": nj.RAW_PROFILE_DIGEST,
            "half_profile_digest": nj.PROFILE_DIGEST,
            "manifest_profile": manifest["profile"],
            "raw_geometry": nj.RAW_GEOMETRY,
            "half_geometry": nj.GEOMETRY,
        },
        "limits": ledger.LIMITS,
    }


def main():
    if RESULT_DIR.exists():
        raise SystemExit("qualification result directory already exists")
    RESULT_DIR.mkdir(parents=True)
    all_paths = CODE_PATHS + TEST_PATHS + (STARTER_PRECHECK_PATH,)
    before = file_hashes(all_paths)
    environment = environment_and_profiles()
    discovered = discovered_test_ids()
    plan = {
        "schema": "s2ty.neutral-overall-qualification.v1",
        "qualification_id": QUALIFICATION_ID,
        "command": [sys.executable, "-B", "-m", "unittest", *TEST_MODULES, "-v"],
        "unittest_invocations": 1,
        "expected_test_count": len(TEST_IDS),
        "test_ids": TEST_IDS,
        "discovered_test_ids": discovered,
        "code_hashes_before": {path: before[path] for path in CODE_PATHS},
        "test_hashes_before": {path: before[path] for path in TEST_PATHS},
        "starter_precheck_hash_before": before[STARTER_PRECHECK_PATH],
        "environment": environment,
        "neutral_source_scope": "Only in-memory zero PCM with resealed neutral manifest; no NU/TW payload access.",
        "process_memory_scope": "NOT_STATICALLY_BOUNDED: Python administration and NumPy implementation temporaries are not a process-peak proof.",
    }
    write_json(RESULT_DIR / "qualification-plan.json", plan)
    if len(discovered) != len(TEST_IDS) or set(discovered) != set(TEST_IDS):
        result = {
            "schema": "s2ty.neutral-overall-qualification-result.v1",
            "qualification_id": QUALIFICATION_ID,
            "status": "NOT_QUALIFIED_PRESTART",
            "qualification_reasons": ["STATIC_TEST_INVENTORY_INVALID"],
            "tests_expected": len(TEST_IDS),
            "tests_discovered": discovered,
            "formal_main_run_authorized": False,
        }
        write_json(RESULT_DIR / "qualification-result.json", result)
        return 1
    observation = RESULT_DIR / "materialized-observation.json"
    environment_for_test = {**os.environ, "S2TY_FORMAL_OBSERVATION_PATH": str(observation)}
    completed = subprocess.run(plan["command"], cwd=ROOT, env=environment_for_test, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    output = completed.stdout
    (RESULT_DIR / "unittest-output.txt").write_text(output, encoding="utf-8")
    after = file_hashes(all_paths)
    write_json(RESULT_DIR / "hashes-before.json", before)
    write_json(RESULT_DIR / "hashes-after.json", after)
    observation_value = json.loads(observation.read_text(encoding="ascii")) if observation.exists() else None
    outcome = qualification_outcome(
        exit_code=completed.returncode,
        output=output,
        observation=observation_value,
        before=before,
        after=after,
    )
    result = {
        "schema": "s2ty.neutral-overall-qualification-result.v1",
        "qualification_id": QUALIFICATION_ID,
        "status": "QUALIFIED" if outcome["qualified"] else "NOT_QUALIFIED",
        "exit_code": completed.returncode,
        "tests_expected": len(TEST_IDS),
        "tests_reported": outcome["tests_reported"],
        "tests_executed": outcome["tests_executed"],
        "test_ids_exact": outcome["test_ids_exact"],
        "test_results_all_ok": outcome["test_results_all_ok"],
        "qualification_reasons": outcome["reasons"],
        "hashes_unchanged": outcome["hashes_unchanged"],
        "test_output_sha256": digest_bytes(output.encode("utf-8")),
        "observation": observation_value,
        "environment_before": environment,
        "environment_after": environment_and_profiles(),
        "artifact_bytes_excluding_result": None,
        "process_memory_statement": plan["process_memory_scope"],
        "real_sources_processed": False,
        "formal_main_run_authorized": False,
    }
    report = (
        "# S2-TY-neutrale Gesamtqualifikation\n\n"
        f"ID: `{QUALIFICATION_ID}`. Status: `{result['status']}`. "
        f"Tests: `{result['tests_reported']}/{result['tests_expected']}`; Exit-Code: `{result['exit_code']}`.\n\n"
        "Der Lauf verwendet nur neutrale In-Memory-PCM-Fenster. Die beobachtete erfolgreiche "
        "Materialisierung umfasst 22 Hashpruefungen, 22 Rezeptoranalysen und 22 NJ-Projektionen. "
        "Simulierte Fehlerfaelle sind davon getrennte Testfaelle.\n\n"
        f"Die beobachtete Erfolgshuelle benoetigt `{observation_value['success_branch']['contributions']['record'] if observation_value else 'unavailable'}` Byte "
        f"bei `{observation_value['record_reserve_bytes'] if observation_value else 'unavailable'}` Byte Recordreserve. "
        "Die begrenzte MCM-Nutzlast und die bekannte FFT-Untergrenze stehen im Ergebnis. "
        "Python- und NumPy-Prozessspitzen bleiben nicht statisch begrenzt; daraus folgt keine reale Laufzulassung.\n"
    )
    (RESULT_DIR / "REPORT.md").write_text(report, encoding="utf-8")
    result["artifact_bytes_excluding_result"] = {
        path.name: path.stat().st_size for path in RESULT_DIR.iterdir() if path.is_file()
    }
    write_json(RESULT_DIR / "qualification-result.json", result)
    return 0 if outcome["qualified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
