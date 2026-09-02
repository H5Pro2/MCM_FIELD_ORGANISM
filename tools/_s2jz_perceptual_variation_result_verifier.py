"""Independent read-only verifier for the private S2-JZ result."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re

from tools._s2jz_perceptual_variation_fixtures import (
    FIXTURE_RECIPE_DIGEST as EXPECTED_FIXTURE_RECIPE_DIGEST,
)


S2JZ_RESULT_SCHEMA = "s2jz.perceptual-variation-result.v1"
FIXTURE_ROLES = ("R0", "E0", "V1", "A1", "C1", "Z1")
HISTORIES = (
    ("g0", ("R0", "E0", "R0", "E0"), ("R0",)),
    ("g1", ("R0", "V1", "R0", "V1"), ("R0", "V1")),
    ("g2", ("R0", "A1", "R0", "A1"), ("R0", "A1")),
    ("g3", ("R0", "C1", "R0", "C1"), ("R0", "C1")),
    ("g4", ("R0", "Z1", "R0", "Z1"), ("R0", "Z1")),
)
EXPECTED_ROLES = tuple(
    role
    for _, formations, probes in HISTORIES
    for role in (
        *(("AV_PAIR", "B4_ARM", "TSPM_ARM", "COMPOSITE_VALIDATE") * len(formations)),
        *(("AV_PAIR", "B4_READ", "TSPM_READ", "READ_ONLY_VALIDATE") * len(probes)),
    )
)
SOURCE_PATHS = (
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
    "mcm_field_organism/_tspm1_s2dr_private_comparison.py",
    "tools/_s2jw_default_live_profile.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_ledger.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2jw_profiled_memory_read_only.py",
    "tools/_s2jz_perceptual_variation_fixtures.py",
    "tools/_s2jz_perceptual_variation_measurement.py",
    "tools/_s2jz_perceptual_variation_runner.py",
    "tools/_s2jz_perceptual_variation_result_verifier.py",
)
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")


@dataclass(frozen=True, slots=True)
class S2JZVerificationFinding:
    status: str
    run_id: str | None
    operation_count: int
    functional_status: str | None
    issues: tuple[str, ...]
    finding_digest: str


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finding(status: str, run_id: str | None, count: int, functional: str | None, issues: list[str]) -> S2JZVerificationFinding:
    payload = {
        "status": status,
        "run_id": run_id,
        "operation_count": count,
        "functional_status": functional,
        "issues": issues,
    }
    return S2JZVerificationFinding(status, run_id, count, functional, tuple(issues), _digest(payload))


def _contains_raw(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            key in {"pixel_bytes", "pcm_bytes", "raw_bytes", "raw_payload"}
            or _contains_raw(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_raw(item) for item in value)
    return False


def _baseline_agrees(probe: dict[str, object]) -> bool:
    baseline = probe.get("baseline")
    if not isinstance(baseline, dict):
        return False
    try:
        fast = any(
            item["auditory_distance"] <= baseline["fast_thresholds"][0]
            and item["visual_distance"] <= baseline["fast_thresholds"][1]
            for item in baseline["fast"]
        )
        auditory = any(
            item["support"] >= 3
            and item["distance"] <= baseline["slow_thresholds"][0]
            for item in baseline["auditory_slow"]
        )
        visual = any(
            item["support"] >= 3
            and item["distance"] <= baseline["slow_thresholds"][1]
            for item in baseline["visual_slow"]
        )
    except (KeyError, TypeError, IndexError):
        return False
    return (
        (probe.get("fast_selected") is not None) == fast
        and (probe.get("auditory_slow_selected") is not None) == auditory
        and (probe.get("visual_slow_selected") is not None) == visual
    )


def _evaluate(stories: object) -> dict[str, object] | None:
    if not isinstance(stories, list) or len(stories) != 5:
        return None
    by_id = {item.get("story_id"): item for item in stories if isinstance(item, dict)}
    claims: dict[str, bool] = {}
    complete = set(by_id) == {"g0", "g1", "g2", "g3", "g4"}
    claims["five_fresh_histories"] = (
        complete
        and len({item.get("story_owner_id") for item in stories}) == 5
        and all(item.get("initial_generation") == 0 for item in stories)
    )
    for story_id in ("g0", "g1", "g2", "g3"):
        item = by_id.get(story_id, {})
        final = item.get("final_state") if isinstance(item, dict) else None
        probes = item.get("probes") if isinstance(item, dict) else None
        slow_a = final.get("auditory_slow", []) if isinstance(final, dict) else []
        slow_v = final.get("visual_slow", []) if isinstance(final, dict) else []
        claims[f"{story_id}_one_stable_pair"] = len(slow_a) == 1 and len(slow_v) == 1 and slow_a[0][1] == 3 and slow_v[0][1] == 3
        claims[f"{story_id}_all_probes_match_shared_memory"] = isinstance(probes, list) and bool(probes) and all(
            probe.get("fast_selected") is not None
            and probe.get("auditory_slow_selected") is not None
            and probe.get("visual_slow_selected") is not None
            and probe.get("baseline_agrees") is True
            and _baseline_agrees(probe)
            for probe in probes
        )
    g4 = by_id.get("g4", {})
    final = g4.get("final_state") if isinstance(g4, dict) else None
    probes = g4.get("probes") if isinstance(g4, dict) else None
    fast = final.get("fast", []) if isinstance(final, dict) else []
    slow_a = final.get("auditory_slow", []) if isinstance(final, dict) else []
    slow_v = final.get("visual_slow", []) if isinstance(final, dict) else []
    claims["g4_two_fast_and_two_unstable_slow_slots"] = len(fast) == 2 and len(slow_a) == 2 and len(slow_v) == 2 and all(slot[1] == 1 for slot in slow_a + slow_v)
    claims["g4_probes_remain_separate_without_public_slow"] = (
        isinstance(probes, list)
        and len(probes) == 2
        and all(
            probe.get("fast_selected") is not None
            and probe.get("auditory_slow_selected") is None
            and probe.get("visual_slow_selected") is None
            and probe.get("baseline_agrees") is True
            and _baseline_agrees(probe)
            for probe in probes
        )
        and len({probe["fast_selected"]["slot_id"] for probe in probes}) == 2
    )
    claims["all_probes_read_only"] = complete and all(
        probe.get("prestate_digest") == probe.get("poststate_digest")
        for story in stories
        for probe in story.get("probes", [])
    )
    return {
        "status": "S2JY_VARIATION_IDENTITY_CONFIRMED" if all(claims.values()) else "S2JY_VARIATION_IDENTITY_FALSIFIED",
        "claims": claims,
        "evaluation_digest": _digest(claims),
    }


def _preflight_valid(items: object) -> bool:
    if not isinstance(items, list) or len(items) != 6:
        return False
    by_role = {item.get("candidate_role"): item for item in items if isinstance(item, dict)}
    if set(by_role) != set(FIXTURE_ROLES):
        return False
    for item in items:
        if not isinstance(item, dict):
            return False
        payload = dict(item)
        measurement_digest = payload.pop("measurement_digest", None)
        if measurement_digest != _digest(payload):
            return False
    try:
        r0, e0, v1, a1, c1, z1 = (by_role[key] for key in FIXTURE_ROLES)
        close = lambda left, right: math.isclose(left, right, rel_tol=0.0, abs_tol=1e-15)
        return (
            close(r0["auditory_distance"], 0.0)
            and close(r0["visual_distance"], 0.0)
            and close(e0["auditory_distance"], 0.0)
            and close(e0["visual_distance"], 0.0)
            and close(v1["auditory_distance"], 0.0)
            and close(v1["visual_distance"], 2.0 / 255.0)
            and close(a1["visual_distance"], 0.0)
            and 0.0 < a1["auditory_distance"] < 0.01
            and close(c1["auditory_distance"], a1["auditory_distance"])
            and close(c1["visual_distance"], v1["visual_distance"])
            and z1["auditory_distance"] > 0.02
            and z1["visual_distance"] > 0.2
        )
    except (KeyError, TypeError):
        return False


def verify_s2jz_result(directory: Path, workspace_root: Path) -> S2JZVerificationFinding:
    if not isinstance(directory, Path) or not directory.is_absolute():
        return _finding("NOT_EVALUABLE", None, 0, None, ["directory must be one absolute Path"])
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        return _finding("NOT_EVALUABLE", None, 0, None, ["workspace_root must be one absolute Path"])
    path = directory / "result.json"
    if not directory.is_dir() or not path.is_file():
        return _finding("NOT_EVALUABLE", None, 0, None, ["atomic result is missing"])
    issues: list[str] = []
    if {item.name for item in directory.iterdir()} != {"result.json"}:
        issues.append("unregistered result artifact")
    try:
        record = json.loads(path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _finding("NOT_EVALUABLE", None, 0, None, ["result is unreadable"])
    if not isinstance(record, dict):
        return _finding("NOT_EVALUABLE", None, 0, None, ["result root differs"])
    run_id = record.get("run_id") if isinstance(record.get("run_id"), str) else None
    if run_id is None or _RUN_ID.fullmatch(run_id) is None or directory.name != run_id:
        issues.append("run identity differs")
    payload = dict(record)
    stored = payload.pop("record_digest", None)
    if stored != _digest(payload):
        issues.append("record digest differs")
    if record.get("schema") != S2JZ_RESULT_SCHEMA or _contains_raw(record):
        issues.append("schema or raw-payload boundary differs")
    if record.get("technical_status") == "NOT_EVALUABLE":
        return _finding("NOT_EVALUABLE", run_id, 0, None, issues or ["run recorded technical failure"])
    if record.get("technical_status") != "RECORDING_COMPLETE":
        issues.append("technical status differs")

    expected_plan = {
        "histories": [[sid, list(formations), list(probes)] for sid, formations, probes in HISTORIES],
        "formation_count": 20,
        "probe_count": 9,
        "memory_operation_count": 116,
        "baseline_call_count": 29,
        "memory_l1_limit": 153_120,
        "raw_payload_retained": False,
        "field_read": False,
        "thresholds_changed": False,
    }
    if (
        record.get("plan") != expected_plan
        or record.get("fixture_recipe_digest") != EXPECTED_FIXTURE_RECIPE_DIGEST
        or not _preflight_valid(record.get("preflight_measurements"))
    ):
        issues.append("plan or measured fixture preflight differs")

    hashes = record.get("source_hashes")
    if not isinstance(hashes, dict) or set(hashes) != set(SOURCE_PATHS):
        issues.append("source inventory differs")
    else:
        for relative in SOURCE_PATHS:
            path_source = workspace_root / relative
            if not path_source.is_file() or hashes.get(relative) != _file_digest(path_source):
                issues.append(f"source digest differs: {relative}")

    operations = record.get("operations")
    previous = None
    count = 0
    if not isinstance(operations, list) or len(operations) != 116:
        issues.append("operation count differs")
    else:
        count = len(operations)
        for index, (item, role) in enumerate(zip(operations, EXPECTED_ROLES, strict=True), 1):
            if not isinstance(item, dict):
                issues.append(f"operation {index} differs")
                continue
            item_payload = dict(item)
            item_digest = item_payload.pop("operation_digest", None)
            if (
                item.get("operation_id") != f"s2jz-op-{index:03d}"
                or item.get("ordinal") != index
                or item.get("role") != role
                or item.get("parent_operation_digest") != previous
                or item_digest != _digest(item_payload)
            ):
                issues.append(f"operation chain differs at {index}")
            previous = item_digest
        if record.get("last_operation_digest") != previous:
            issues.append("last operation digest differs")

    stories = record.get("stories")
    if isinstance(stories, list):
        for item, expected in zip(stories, HISTORIES, strict=False):
            if (
                not isinstance(item, dict)
                or item.get("story_id") != expected[0]
                or [entry.get("evaluation_role") for entry in item.get("formations", [])] != list(expected[1])
                or [entry.get("evaluation_role") for entry in item.get("probes", [])] != list(expected[2])
            ):
                issues.append("story role sequence differs")
    recomputed = _evaluate(stories)
    functional = record.get("functional_evaluation")
    functional_status = None
    if recomputed is None or recomputed != functional:
        issues.append("functional evaluation differs")
    elif isinstance(functional, dict) and isinstance(functional.get("status"), str):
        functional_status = functional["status"]
    return _finding("RECORDING_COMPLETE" if not issues else "NOT_EVALUABLE", run_id, count, functional_status, issues)
