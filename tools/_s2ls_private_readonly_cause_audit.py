"""Read-only post-run cause audit for the completed S2-LS corpus result."""

from __future__ import annotations

from itertools import combinations, product
import hashlib
import json
import math
import os
from pathlib import Path
from threading import Lock

import numpy as np

from tools import _s2ls_private_presealed_av_corpus_plan as corpus_source


SCHEMA = "s2ls.readonly-cause-audit.v1"
AUDIT_ID = "s2ls-readonly-cause-audit-20260904-03"
EXPECTED_RESULT_SHA256 = "2be76afc69f7d587cd1098895915c905d8d5349bb6795e3dde903f71744d4fc1"
EXPECTED_RECORD_DIGEST = "c939b15dae96b8a6c17be2f09936f70043e56d055624159ece6d862c976fface"
EXPECTED_PLAN_DIGEST = "1ad42964295cce44b87f6c3d02479983878ca7c403eee21440783fe3326e661a"
EXPECTED_EVIDENCE_DIGEST = "0840c261f91f824cd913fb1bc5ccdd9ba21b75d6680e61948561a986e2443f9b"
RESULT_RELATIVE_PATH = "reports/s2ls/s2ls-real-presealed-av-corpus-20260904-01/result.json"
PLAN_RELATIVE_PATH = "reports/s2ls/s2ls-presealed-av-corpus-plan-20260904-01/presealed-corpus-plan.json"
EVIDENCE_RELATIVE_PATH = "reports/s2ls/s2ls-corpus-receptor-materialization-20260904-01/receptor-materialization.json"
VISUAL_VISIBLE = tuple(range(32))
AUDITORY_OBSERVED = tuple(range(24))
FAST_THRESHOLD = 0.2
FAST_UPDATE_FACTOR = 0.5
AUDITORY_SLOW_THRESHOLD = 0.02
VISUAL_SLOW_THRESHOLD = 0.01
MAX_AUDIT_BYTES = 1_048_576
AUDIT_ENABLED = False

_LOCK = Lock()
_USED = False


class S2LSCauseAuditError(RuntimeError):
    """The completed evidence cannot support a read-only cause statement."""


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LSCauseAuditError(message)


def _load(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    value = json.loads(data.decode("ascii"))
    _require(type(value) is dict and data == _canonical_bytes(value, newline=True), "input is not canonical")
    return value


def _mean_l1(left: tuple[float, ...], right: tuple[float, ...], positions: tuple[int, ...] | None = None) -> float:
    _require(len(left) == len(right), "distance dimensions differ")
    indexes = tuple(range(len(left))) if positions is None else positions
    return math.fsum(abs(left[index] - right[index]) for index in indexes) / len(indexes)


def _frozen_inputs(workspace_root: Path) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    result_path = workspace_root / RESULT_RELATIVE_PATH
    _require(hashlib.sha256(result_path.read_bytes()).hexdigest() == EXPECTED_RESULT_SHA256, "completed result changed")
    result = _load(result_path)
    plan = _load(workspace_root / PLAN_RELATIVE_PATH)
    evidence = _load(workspace_root / EVIDENCE_RELATIVE_PATH)
    _require(result.get("record_digest") == EXPECTED_RECORD_DIGEST, "record digest differs")
    _require(result.get("technical_status") == "RECORDING_COMPLETE", "result is incomplete")
    _require(plan.get("plan_digest") == EXPECTED_PLAN_DIGEST, "plan digest differs")
    _require(evidence.get("evidence_digest") == EXPECTED_EVIDENCE_DIGEST, "receptor evidence digest differs")
    return result, plan, evidence


def _transition_trace(result: dict[str, object], plan: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    events = result["execution"]["events"][:17]
    families = {
        str(family["family_id"]): set(str(item) for item in family["training_content_ids"])
        for family in plan["evaluation_root"]["families"]
    }
    lineages: dict[str, dict[str, list[str]]] = {"AUDITORY": {}, "VISUAL": {}}
    trace = []
    pressure_updates = []
    for event in events:
        transition = event["formation_transition"]
        fast = transition["fast"]
        if not fast["pre_slot"]["occupied"]:
            effective_fast_event = "CREATED"
        elif fast["auditory_source_distance"] <= FAST_THRESHOLD and fast["visual_source_distance"] <= FAST_THRESHOLD:
            effective_fast_event = "MATCHED"
        else:
            effective_fast_event = "REPLACED"
        fast_projection = {
            **fast,
            "recorded_projection_event": fast["event"],
            "effective_event": effective_fast_event,
        }
        ppb_projections = {}
        for role in ("auditory_ppb", "visual_ppb"):
            item = transition[role]
            if item["slot_id"] is None:
                effective_event = "NO_UPDATE"
            elif not item["pre_slot"]["occupied"]:
                effective_event = "CREATED"
            elif item["source_distance"] <= item["match_threshold"]:
                effective_event = "MATCHED"
            else:
                effective_event = "REPLACED"
            ppb_projections[role] = {
                **item,
                "recorded_projection_event": item["event"],
                "effective_event": effective_event,
            }
        row = {
            "formation_index": transition["formation_index"],
            "event_id": event["frozen_event_id"],
            "content_id": event["content_id"],
            "fast": fast_projection,
            "auditory_ppb": ppb_projections["auditory_ppb"],
            "visual_ppb": ppb_projections["visual_ppb"],
        }
        trace.append({**row, "trace_row_digest": _digest(row)})
        for modality, role in (("AUDITORY", "auditory_ppb"), ("VISUAL", "visual_ppb")):
            item = ppb_projections[role]
            slot_id = item["slot_id"]
            if slot_id is None:
                continue
            prior = list(lineages[modality].get(slot_id, ()))
            touched = sorted(name for name, members in families.items() if members.intersection(prior))
            if (
                str(event["content_id"]) in set(plan["evaluation_root"]["pressure_content_ids"])
                and touched
                and item["effective_event"] in {"MATCHED", "REPLACED"}
            ):
                payload = {
                    "formation_index": transition["formation_index"],
                    "event_id": event["frozen_event_id"],
                    "pressure_content_id": event["content_id"],
                    "modality": modality,
                    "slot_id": slot_id,
                    "recorded_projection_event": item["recorded_projection_event"],
                    "effective_transition_event": item["effective_event"],
                    "prior_content_lineage": prior,
                    "prior_family_ids": touched,
                    "source_distance": item["source_distance"],
                    "post_prototype_digest": item["post_slot"]["prototype_digest"],
                }
                pressure_updates.append({**payload, "update_digest": _digest(payload)})
            if item["effective_event"] in {"CREATED", "REPLACED"}:
                lineages[modality][slot_id] = [event["content_id"]]
            elif item["effective_event"] == "MATCHED":
                lineages[modality].setdefault(slot_id, []).append(event["content_id"])
    return trace, pressure_updates


def _replay_fast_values(
    formations: list[dict[str, object]],
) -> dict[str, tuple[tuple[float, ...], tuple[float, ...]]]:
    slots: dict[str, tuple[tuple[float, ...], tuple[float, ...]]] = {}
    for event in formations:
        transition = event["formation_transition"]["fast"]
        slot_id = str(transition["selected_slot_id"])
        source = event["memory_observation"]["formation_values"]
        auditory_source = tuple(source["auditory"])
        visual_source = tuple(source["visual"])
        pre_slot = transition["pre_slot"]
        if not pre_slot["occupied"]:
            auditory_post = auditory_source
            visual_post = visual_source
        else:
            _require(slot_id in slots, "Fast replay lacks the recorded predecessor")
            auditory_pre, visual_pre = slots[slot_id]
            auditory_distance = _mean_l1(auditory_pre, auditory_source)
            visual_distance = _mean_l1(visual_pre, visual_source)
            _require(auditory_distance == transition["auditory_source_distance"], "Fast auditory distance replay differs")
            _require(visual_distance == transition["visual_source_distance"], "Fast visual distance replay differs")
            if auditory_distance <= FAST_THRESHOLD and visual_distance <= FAST_THRESHOLD:
                auditory_post = tuple(
                    (1.0 - FAST_UPDATE_FACTOR) * previous + FAST_UPDATE_FACTOR * current
                    for previous, current in zip(auditory_pre, auditory_source, strict=True)
                )
                visual_post = tuple(
                    (1.0 - FAST_UPDATE_FACTOR) * previous + FAST_UPDATE_FACTOR * current
                    for previous, current in zip(visual_pre, visual_source, strict=True)
                )
            else:
                auditory_post = auditory_source
                visual_post = visual_source
        post_slot = transition["post_slot"]
        _require(_digest(list(auditory_post)) == post_slot["auditory_values_digest"], "Fast auditory value replay differs")
        _require(_digest(list(visual_post)) == post_slot["visual_values_digest"], "Fast visual value replay differs")
        slots[slot_id] = (auditory_post, visual_post)
    return slots


def _final_candidates(result: dict[str, object]) -> dict[str, dict[str, tuple[tuple[str, tuple[float, ...]], ...]]]:
    formations = [event for event in result["execution"]["events"] if event["event_type"] == "COMPLETE_AV_PERCEPTION"]
    final = formations[-1]["memory_observation"]
    by_index = {event["memory_observation"]["generation"]: event for event in formations}
    fast_values = _replay_fast_values(formations)
    candidates: dict[str, dict[str, tuple[tuple[str, tuple[float, ...]], ...]]] = {"AUDITORY": {}, "VISUAL": {}}
    for modality, offset in (("AUDITORY", 0), ("VISUAL", 48)):
        length = 48 if modality == "AUDITORY" else 288
        b4 = []
        for slot in final["b4"]:
            source = by_index[slot["formation_index"]]["memory_observation"]["formation_values"]
            values = tuple(source["auditory"] if modality == "AUDITORY" else source["visual"])
            _require(_digest(list(tuple(source["auditory"]) + tuple(source["visual"]))) == slot["values_digest"], "B4 source reconstruction differs")
            b4.append((slot["slot_id"], values))
        fast = []
        for slot in final["fast"]:
            _require(slot["slot_id"] in fast_values, "final Fast slot lacks a replayed value")
            pair = fast_values[slot["slot_id"]]
            values = pair[0] if modality == "AUDITORY" else pair[1]
            key = slot["auditory_values_digest"] if modality == "AUDITORY" else slot["visual_values_digest"]
            _require(_digest(list(values)) == key, "final Fast slot differs from transition replay")
            fast.append((slot["slot_id"], values))
        bank = final["auditory_slow"] if modality == "AUDITORY" else final["visual_slow"]
        slow = tuple(
            (slot["slot_id"], tuple(slot["prototype_values"]))
            for slot in bank
            if slot["support_count"] >= 3 and len(slot["prototype_values"]) == length
        )
        candidates[modality] = {"B4_RECENT": tuple(b4), "TSPM_FAST": tuple(fast), "B_STABLE": slow}
    return candidates


def _cue_hit_audit(
    result: dict[str, object],
    evidence: dict[str, object],
    candidates: dict[str, dict[str, tuple[tuple[str, tuple[float, ...]], ...]]],
) -> list[dict[str, object]]:
    content = {str(item["content_id"]): item for item in evidence["content_receptor_states"]}
    visual_cues = {str(item["content_id"]): item for item in evidence["visual_cue_receptor_states"]}
    recorded = {event["frozen_event_id"]: event for event in result["execution"]["events"][17:]}
    rows = []
    for frozen in evidence["event_receptor_bindings"][17:]:
        modality = "VISUAL" if frozen["event_kind"] == "VISUAL_PARTIAL_CUE" else "AUDITORY"
        content_id = str(frozen["content_id"])
        cue_values = tuple(
            visual_cues[content_id]["state"]["values"]
            if modality == "VISUAL"
            else content[content_id]["auditory"]["values"]
        )
        target_values = tuple(content[content_id]["visual" if modality == "VISUAL" else "auditory"]["values"])
        positions = VISUAL_VISIBLE if modality == "VISUAL" else AUDITORY_OBSERVED
        bank_rows = []
        for bank_role in ("B4_RECENT", "TSPM_FAST", "B_STABLE"):
            threshold = None if modality == "VISUAL" else (AUDITORY_SLOW_THRESHOLD if bank_role == "B_STABLE" else FAST_THRESHOLD)
            candidate_rows = []
            hits = []
            for candidate_id, values in candidates[modality][bank_role]:
                full_l1 = _mean_l1(target_values, values)
                observed_l1 = _mean_l1(cue_values, values, positions)
                matched = (
                    all(values[index] == cue_values[index] for index in positions)
                    if modality == "VISUAL"
                    else observed_l1 <= threshold
                )
                payload = {
                    "candidate_id": candidate_id,
                    "candidate_values_digest": _digest(list(values)),
                    "full_vector_mean_l1_to_target": full_l1,
                    "observed_mean_l1_to_cue": observed_l1,
                    "scan_rule": "EXACT_VISIBLE_POSITION_EQUALITY" if modality == "VISUAL" else "OBSERVED_MEAN_L1_LE_THRESHOLD",
                    "threshold": threshold,
                    "matched": matched,
                }
                candidate_rows.append({**payload, "candidate_relation_digest": _digest(payload)})
                if matched:
                    hits.append(candidate_id)
            bank_rows.append({"bank_role": bank_role, "hit_ids": hits, "candidates": candidate_rows})
        event = recorded[frozen["event_id"]]
        payload = {
            "event_id": frozen["event_id"],
            "content_id": content_id,
            "modality": modality,
            "recorded_primary_decision": event["primary_scan"]["decision"],
            "recorded_baseline_decision": event["baseline_scan"]["decision"],
            "banks": bank_rows,
        }
        rows.append({**payload, "cue_audit_digest": _digest(payload)})
    return rows


def _visual_payload(plan: dict[str, object], content_id: str) -> np.ndarray:
    recipes = {str(item["content_id"]): item for item in plan["generation_root"]["content_recipes"]}
    inventory = {str(item["content_id"]): item for item in plan["generation_root"]["content_inventory"]}
    payload = corpus_source._visual_bytes(recipes[content_id]["recipe"])
    _require(hashlib.sha256(payload).hexdigest() == inventory[content_id]["visual_payload_sha256"], "regenerated visual source digest differs")
    return np.frombuffer(payload, dtype=np.uint8).reshape(1080, 1920, 3)


def _raw_pair_metric(plan: dict[str, object], evidence_content: dict[str, object], left_id: str, right_id: str) -> dict[str, object]:
    left = _visual_payload(plan, left_id)
    right = _visual_payload(plan, right_id)
    raw_l1 = float(np.mean(np.abs(left.astype(np.int16) - right.astype(np.int16)), dtype=np.float64) / 255.0)
    reduced_left = tuple(evidence_content[left_id]["visual"]["values"])
    reduced_right = tuple(evidence_content[right_id]["visual"]["values"])
    reduced_l1 = _mean_l1(reduced_left, reduced_right)
    del left, right
    return {
        "left_content_id": left_id,
        "right_content_id": right_id,
        "raw_rgb_normalized_mean_l1": raw_l1,
        "reduced_288_mean_l1": reduced_l1,
        "retained_distance_ratio": reduced_l1 / raw_l1 if raw_l1 else 1.0,
    }


def _aggregate(values: list[float]) -> dict[str, float]:
    return {"count": len(values), "minimum": min(values), "maximum": max(values), "mean": math.fsum(values) / len(values)}


def _visual_structure_loss(plan: dict[str, object], evidence: dict[str, object]) -> dict[str, object]:
    content = {str(item["content_id"]): item for item in evidence["content_receptor_states"]}
    families = [tuple(str(item) for item in family["training_content_ids"]) for family in plan["evaluation_root"]["families"]]
    holdouts = [tuple(str(item) for item in family["holdout_content_ids"]) for family in plan["evaluation_root"]["families"]]
    pressure = tuple(str(item) for item in plan["evaluation_root"]["pressure_content_ids"])
    categories = {
        "within_family_training": tuple(pair for family in families for pair in combinations(family, 2)),
        "cross_family_training": tuple(product(families[0], families[1])),
        "holdout_to_own_training": tuple(pair for index in range(2) for pair in product(holdouts[index], families[index])),
        "pressure_to_training": tuple(product(pressure, families[0] + families[1])),
    }
    category_rows = {}
    for name, pairs in categories.items():
        metrics = [_raw_pair_metric(plan, content, left, right) for left, right in pairs]
        category_rows[name] = {
            "pair_count": len(metrics),
            "raw_rgb_normalized_mean_l1": _aggregate([item["raw_rgb_normalized_mean_l1"] for item in metrics]),
            "reduced_288_mean_l1": _aggregate([item["reduced_288_mean_l1"] for item in metrics]),
            "retained_distance_ratio": _aggregate([item["retained_distance_ratio"] for item in metrics]),
            "pair_metrics_digest": _digest(metrics),
        }
    per_source = []
    for content_id in sorted(content):
        image = _visual_payload(plan, content_id).astype(np.float64)
        reshaped = image.reshape(8, 135, 12, 160, 3).transpose(0, 2, 1, 3, 4)
        means = reshaped.mean(axis=(2, 3))
        residual = float(np.mean(np.abs(reshaped - means[:, :, None, None, :])) / 255.0)
        stddev = float(np.mean(np.std(reshaped, axis=(2, 3), dtype=np.float64)) / 255.0)
        frozen = np.asarray(content[content_id]["visual"]["values"], dtype=np.float64).reshape(8, 12, 3)
        _require(np.array_equal(means / 255.0, frozen), "block mean differs from frozen receptor values")
        payload = {"content_id": content_id, "within_block_mean_absolute_residual": residual, "within_block_mean_standard_deviation": stddev}
        per_source.append({**payload, "structure_digest": _digest(payload)})
        del image, reshaped, means, frozen
    return {
        "method": "TRANSIENT_RGB8_PAIRWISE_L1_AND_WITHIN_BLOCK_RESIDUAL",
        "raw_payload_retained": False,
        "category_metrics": category_rows,
        "within_block_structure": {
            "mean_absolute_residual": _aggregate([item["within_block_mean_absolute_residual"] for item in per_source]),
            "mean_standard_deviation": _aggregate([item["within_block_mean_standard_deviation"] for item in per_source]),
            "per_source_digest": _digest(per_source),
        },
    }


def build_readonly_audit(workspace_root: Path) -> dict[str, object]:
    result, plan, evidence = _frozen_inputs(workspace_root)
    trace, pressure_updates = _transition_trace(result, plan)
    candidates = _final_candidates(result)
    cue_audit = _cue_hit_audit(result, evidence, candidates)
    visual_loss = _visual_structure_loss(plan, evidence)
    payload = {
        "schema": SCHEMA,
        "audit_id": AUDIT_ID,
        "status": "S2LS_READONLY_CAUSE_AUDIT_COMPLETE",
        "source_bindings": {
            "result_sha256": EXPECTED_RESULT_SHA256,
            "record_digest": EXPECTED_RECORD_DIGEST,
            "plan_digest": EXPECTED_PLAN_DIGEST,
            "evidence_digest": EXPECTED_EVIDENCE_DIGEST,
        },
        "prior_attempts": [
            {
                "audit_id": "s2ls-readonly-cause-audit-20260904-01",
                "status": "AUDIT_FAILED_RECONSTRUCTION_ASSUMPTION",
                "artifact_created": False,
                "functional_execution": False,
            },
            {
                "audit_id": "s2ls-readonly-cause-audit-20260904-02",
                "status": "AUDIT_SUPERSEDED_SUPPORT_SATURATION_CLASSIFICATION",
                "artifact_created": True,
                "functional_execution": False,
            },
        ],
        "formation_transition_trace": trace,
        "pressure_family_prototype_updates": pressure_updates,
        "partial_cue_hit_sets": cue_audit,
        "visual_structure_loss": visual_loss,
        "calls": {"memory": 0, "receptor": 0, "context": 0, "field": 0},
        "thresholds_changed": False,
        "raw_payload_retained": False,
    }
    return {**payload, "audit_digest": _digest(payload)}


def materialize_audit_once(*, workspace_root: Path, output_root: Path, audit_id: str) -> Path:
    global AUDIT_ENABLED, _USED
    _require(AUDIT_ENABLED is True and audit_id == AUDIT_ID, "audit is not authorized")
    _require(not _USED and _LOCK.acquire(blocking=False), "audit is already consumed")
    _USED = True
    try:
        record = build_readonly_audit(workspace_root)
        run_dir = output_root / audit_id
        run_dir.mkdir(parents=True, exist_ok=False)
        target = run_dir / "cause-audit.json"
        temporary = run_dir / ".cause-audit.json.tmp"
        data = _canonical_bytes(record, newline=True)
        _require(len(data) <= MAX_AUDIT_BYTES, "audit exceeds bounded envelope")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, target)
        except Exception:
            if temporary.exists():
                temporary.unlink()
            raise
        return target
    finally:
        AUDIT_ENABLED = False
        _LOCK.release()


__all__: tuple[str, ...] = ()
