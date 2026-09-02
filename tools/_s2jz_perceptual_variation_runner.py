"""Private closed-gate runner for the finite S2-JZ variation experiment."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re

from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_read_only as read_only
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools._s2jz_perceptual_variation_fixtures import (
    FIXTURE_RECIPE_DIGEST,
    FIXTURE_ROLES,
    S2JZFixtureStream,
)
from tools._s2jz_perceptual_variation_measurement import (
    direct_l1_prototype_baseline,
    measure_receptor_distance,
    measure_transition,
    state_slot_projection,
    validate_variation_measurements,
)


S2JZ_RESULT_SCHEMA = "s2jz.perceptual-variation-result.v1"
MAIN_EXECUTION_ENABLED = False
AUTHORIZED_RUN_ID: str | None = None
HISTORIES = (
    ("g0", ("R0", "E0", "R0", "E0"), ("R0",)),
    ("g1", ("R0", "V1", "R0", "V1"), ("R0", "V1")),
    ("g2", ("R0", "A1", "R0", "A1"), ("R0", "A1")),
    ("g3", ("R0", "C1", "R0", "C1"), ("R0", "C1")),
    ("g4", ("R0", "Z1", "R0", "Z1"), ("R0", "Z1")),
)
FORMATION_COUNT = 20
PROBE_COUNT = 9
MEMORY_OPERATION_COUNT = 116
BASELINE_CALL_COUNT = 29
MEMORY_L1_LIMIT = 153_120
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")

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


class S2JZRunnerError(RuntimeError):
    """The closed-gate S2-JZ runner cannot publish a complete result."""


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)[:-1]).hexdigest()


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes(workspace_root: Path) -> dict[str, str]:
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        raise S2JZRunnerError("workspace_root must be one absolute Path")
    result = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        if not path.is_file():
            raise S2JZRunnerError(f"bound source missing: {relative}")
        result[relative] = _file_digest(path)
    return result


@dataclass(slots=True)
class _OperationChain:
    records: list[dict[str, object]]
    previous_digest: str | None = None

    def append(self, role: str, evidence: dict[str, object]) -> None:
        ordinal = len(self.records) + 1
        payload = {
            "schema": "s2jz.operation.v1",
            "operation_id": f"s2jz-op-{ordinal:03d}",
            "ordinal": ordinal,
            "role": role,
            "parent_operation_digest": self.previous_digest,
            "evidence": evidence,
        }
        record = {**payload, "operation_digest": _digest(payload)}
        self.records.append(record)
        self.previous_digest = record["operation_digest"]  # type: ignore[assignment]


def _selected(value: object | None, kind: str) -> dict[str, object] | None:
    if value is None:
        return None
    if kind == "b4":
        return {
            "slot_id": value.slot_id,  # type: ignore[attr-defined]
            "formation_index": value.formation_index,  # type: ignore[attr-defined]
            "auditory_distance": value.auditory_distance,  # type: ignore[attr-defined]
            "visual_distance": value.visual_distance,  # type: ignore[attr-defined]
            "mechanical_match": value.mechanical_match,  # type: ignore[attr-defined]
            "evidence_digest": value.entry_digest,  # type: ignore[attr-defined]
        }
    if kind == "fast":
        return {
            "slot_id": value.slot_id,  # type: ignore[attr-defined]
            "support": value.support,  # type: ignore[attr-defined]
            "auditory_distance": value.auditory_distance,  # type: ignore[attr-defined]
            "visual_distance": value.visual_distance,  # type: ignore[attr-defined]
            "mechanical_match": value.mechanical_match,  # type: ignore[attr-defined]
            "evidence_digest": value.slot_digest,  # type: ignore[attr-defined]
        }
    return {
        "slot_id": value.slot_id,  # type: ignore[attr-defined]
        "support": value.support,  # type: ignore[attr-defined]
        "stable": value.stable,  # type: ignore[attr-defined]
        "native_distance": value.native_distance,  # type: ignore[attr-defined]
        "mechanical_match": value.mechanical_match,  # type: ignore[attr-defined]
        "evidence_digest": value.slot_digest,  # type: ignore[attr-defined]
    }


def _probe_summary(role: str, finding: read_only.S2JVReadOnlyFindingV1) -> dict[str, object]:
    return {
        "evaluation_role": role,
        "probe_digest": finding.probe_digest,
        "finding_digest": finding.finding_digest,
        "prestate_digest": finding.prestate_digest,
        "poststate_digest": finding.poststate_digest,
        "b4_selected": _selected(finding.b4_selected, "b4"),
        "fast_selected": _selected(finding.fast_selected, "fast"),
        "auditory_slow_selected": _selected(finding.auditory_slow_selected, "slow"),
        "visual_slow_selected": _selected(finding.visual_slow_selected, "slow"),
        "native_tspm_finding_digest": finding.native_tspm_finding_digest,
        "ledger_digest": finding.ledger.ledger_digest,
    }


def _baseline_agrees(summary: dict[str, object], baseline: dict[str, object]) -> bool:
    fast_matches = [
        item for item in baseline["fast"]  # type: ignore[index]
        if item["auditory_distance"] <= baseline["fast_thresholds"][0]  # type: ignore[index]
        and item["visual_distance"] <= baseline["fast_thresholds"][1]  # type: ignore[index]
    ]
    auditory_matches = [
        item for item in baseline["auditory_slow"]  # type: ignore[index]
        if item["support"] >= 3 and item["distance"] <= baseline["slow_thresholds"][0]  # type: ignore[index]
    ]
    visual_matches = [
        item for item in baseline["visual_slow"]  # type: ignore[index]
        if item["support"] >= 3 and item["distance"] <= baseline["slow_thresholds"][1]  # type: ignore[index]
    ]
    return (
        (summary["fast_selected"] is not None) == bool(fast_matches)
        and (summary["auditory_slow_selected"] is not None) == bool(auditory_matches)
        and (summary["visual_slow_selected"] is not None) == bool(visual_matches)
    )


def evaluate_story_evidence(stories: list[dict[str, object]]) -> dict[str, object]:
    by_id = {item.get("story_id"): item for item in stories}
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
        claims[f"{story_id}_one_stable_pair"] = (
            len(slow_a) == 1
            and len(slow_v) == 1
            and slow_a[0][1] == 3
            and slow_v[0][1] == 3
        )
        claims[f"{story_id}_all_probes_match_shared_memory"] = (
            isinstance(probes, list)
            and bool(probes)
            and all(
                probe.get("fast_selected") is not None
                and probe.get("auditory_slow_selected") is not None
                and probe.get("visual_slow_selected") is not None
                and probe.get("baseline_agrees") is True
                for probe in probes
            )
        )
    g4 = by_id.get("g4", {})
    final = g4.get("final_state") if isinstance(g4, dict) else None
    probes = g4.get("probes") if isinstance(g4, dict) else None
    fast = final.get("fast", []) if isinstance(final, dict) else []
    slow_a = final.get("auditory_slow", []) if isinstance(final, dict) else []
    slow_v = final.get("visual_slow", []) if isinstance(final, dict) else []
    claims["g4_two_fast_and_two_unstable_slow_slots"] = (
        len(fast) == 2
        and len(slow_a) == 2
        and len(slow_v) == 2
        and all(slot[1] == 1 for slot in slow_a + slow_v)
    )
    claims["g4_probes_remain_separate_without_public_slow"] = (
        isinstance(probes, list)
        and len(probes) == 2
        and all(
            probe.get("fast_selected") is not None
            and probe.get("auditory_slow_selected") is None
            and probe.get("visual_slow_selected") is None
            and probe.get("baseline_agrees") is True
            for probe in probes
        )
        and len({probe["fast_selected"]["slot_id"] for probe in probes}) == 2
    )
    claims["all_probes_read_only"] = complete and all(
        probe.get("prestate_digest") == probe.get("poststate_digest")
        for story in stories
        for probe in story.get("probes", [])
    )
    confirmed = all(claims.values())
    return {
        "status": "S2JY_VARIATION_IDENTITY_CONFIRMED" if confirmed else "S2JY_VARIATION_IDENTITY_FALSIFIED",
        "claims": claims,
        "evaluation_digest": _digest(claims),
    }


def _atomic_write(path: Path, value: object) -> None:
    if path.exists():
        raise S2JZRunnerError("result path already exists")
    pending = path.with_name(f".{path.name}.pending")
    if pending.exists():
        raise S2JZRunnerError("pending path already exists")
    with pending.open("xb") as handle:
        handle.write(_json_bytes(value))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, path)


def _seal(payload: dict[str, object]) -> dict[str, object]:
    return {**payload, "record_digest": _digest(payload)}


def _materialize_preflight(profile) -> tuple[dict[str, object], ...]:
    stream = S2JZFixtureStream(profile, "s2jz-preflight-clock")
    fixtures = tuple(stream.materialize(role, index) for index, role in enumerate(FIXTURE_ROLES))
    reference = fixtures[0]
    measurements = validate_variation_measurements(
        tuple(measure_receptor_distance(reference, item) for item in fixtures)
    )
    return tuple(item.payload_without_digest() | {"measurement_digest": item.measurement_digest} for item in measurements)


def run_main_once(output_root: Path, workspace_root: Path, run_id: str) -> Path:
    if not MAIN_EXECUTION_ENABLED or AUTHORIZED_RUN_ID is None:
        raise S2JZRunnerError("S2-JZ main execution gate is closed")
    if run_id != AUTHORIZED_RUN_ID or _RUN_ID.fullmatch(run_id) is None:
        raise S2JZRunnerError("run_id is not authorized")
    if not isinstance(output_root, Path) or not output_root.is_absolute():
        raise S2JZRunnerError("output_root must be one absolute Path")
    output_root.mkdir(parents=True, exist_ok=True)
    directory = output_root / run_id
    directory.mkdir(exist_ok=False)
    result_path = directory / "result.json"
    hashes = source_hashes(workspace_root)
    operations = _OperationChain([])
    try:
        profile = build_s2jw_default_live_profile()
        limits = build_s2jv_ledger_limits(profile)
        config = coordinator.build_s2jv_coordinator_config(
            tspm_config=profile.tspm_config,
            b4_capacity=profile.b4_capacity,
            ledger_limits=limits,
        )
        preflight = _materialize_preflight(profile)
        stories: list[dict[str, object]] = []
        baseline_calls = 0
        for story_index, (story_id, formation_roles, probe_roles) in enumerate(HISTORIES):
            state = coordinator.initial_s2jv_composite_state(config)
            initial_digest = state.state_digest
            story_owner_id = f"s2jz-story-owner-{story_index}"
            if state.generation != 0:
                raise S2JZRunnerError("fresh story state generation differs")
            stream = S2JZFixtureStream(profile, f"s2jz-story-{story_index}-clock")
            formations = []
            block = 0
            for role in formation_roles:
                fixture = stream.materialize(role, block)
                operations.append("AV_PAIR", {"fixture_digest": fixture.fixture_digest, "pairing_digest": fixture.pairing_digest})
                baseline = direct_l1_prototype_baseline(config, state, fixture)
                baseline_calls += 1
                source = coordinator.bind_s2jv_coordinator_input(config=config, source=fixture.pair)
                owner = coordinator.S2JVFormationOwner(
                    f"s2jz-owner-{story_index}-{block}",
                    f"s2jz-authorization-{story_index}-{block}",
                    f"s2jz-consumption-{story_index}-{block}",
                    config.config_digest,
                    state.state_digest,
                    source.input_digest,
                )
                result = coordinator.advance_s2jv_atomic(config=config, prestate=state, source=source, owner=owner)
                transition = measure_transition(state, result)
                operations.append("B4_ARM", {"event": result.receipt.b4_event, "slot_id": result.receipt.b4_slot_id})
                operations.append("TSPM_ARM", {"result_digest": result.receipt.tspm_result_digest})
                state = result.poststate
                operations.append("COMPOSITE_VALIDATE", {"state_digest": state.state_digest, "receipt_digest": result.receipt.receipt_digest})
                formations.append({
                    "evaluation_role": role,
                    "fixture_digest": fixture.fixture_digest,
                    "baseline": baseline,
                    "transition": transition,
                })
                block += 1
            final_state = state_slot_projection(state)
            probes = []
            for role in probe_roles:
                fixture = stream.materialize(role, block)
                operations.append("AV_PAIR", {"fixture_digest": fixture.fixture_digest, "pairing_digest": fixture.pairing_digest})
                baseline = direct_l1_prototype_baseline(config, state, fixture)
                baseline_calls += 1
                probe = coordinator.bind_s2jv_probe(config=config, source=fixture.pair)
                finding = read_only.probe_s2jv_composite_read_only(config=config, state=state, probe=probe)
                summary = _probe_summary(role, finding)
                summary["baseline"] = baseline
                summary["baseline_agrees"] = _baseline_agrees(summary, baseline)
                operations.append("B4_READ", {"selected": summary["b4_selected"], "probe_digest": probe.probe_digest})
                operations.append("TSPM_READ", {"fast": summary["fast_selected"], "auditory_slow": summary["auditory_slow_selected"], "visual_slow": summary["visual_slow_selected"]})
                operations.append("READ_ONLY_VALIDATE", {"finding_digest": finding.finding_digest, "prestate_digest": finding.prestate_digest, "poststate_digest": finding.poststate_digest})
                probes.append(summary)
                block += 1
            stories.append({
                "story_id": story_id,
                "story_owner_id": story_owner_id,
                "initial_generation": 0,
                "initial_state_digest": initial_digest,
                "formations": formations,
                "final_state": final_state,
                "probes": probes,
            })
        if len(operations.records) != MEMORY_OPERATION_COUNT or baseline_calls != BASELINE_CALL_COUNT:
            raise S2JZRunnerError("bound operation count differs")
        evaluation = evaluate_story_evidence(stories)
        payload = {
            "schema": S2JZ_RESULT_SCHEMA,
            "run_id": run_id,
            "technical_status": "RECORDING_COMPLETE",
            "source_hashes": hashes,
            "fixture_recipe_digest": FIXTURE_RECIPE_DIGEST,
            "preflight_measurements": list(preflight),
            "plan": {
                "histories": [[sid, list(formations), list(probes)] for sid, formations, probes in HISTORIES],
                "formation_count": FORMATION_COUNT,
                "probe_count": PROBE_COUNT,
                "memory_operation_count": MEMORY_OPERATION_COUNT,
                "baseline_call_count": BASELINE_CALL_COUNT,
                "memory_l1_limit": MEMORY_L1_LIMIT,
                "raw_payload_retained": False,
                "field_read": False,
                "thresholds_changed": False,
            },
            "operations": operations.records,
            "stories": stories,
            "functional_evaluation": evaluation,
            "last_operation_digest": operations.previous_digest,
        }
        _atomic_write(result_path, _seal(payload))
        return result_path
    except Exception as exc:
        if not result_path.exists():
            _atomic_write(result_path, _seal({
                "schema": S2JZ_RESULT_SCHEMA,
                "run_id": run_id,
                "technical_status": "NOT_EVALUABLE",
                "error_type": type(exc).__name__,
                "completed_operation_count": len(operations.records),
                "source_hashes": hashes,
            }))
        raise
