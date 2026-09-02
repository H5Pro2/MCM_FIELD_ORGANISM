"""Pure post-recording evaluator for the private S2-KA hypothesis."""

from __future__ import annotations

import hashlib
import json

from tools._s2kb_withheld_variant_fixtures import CHECKPOINTS, FORMATION_SEQUENCE, HOLDOUT_ROLES


S2KB_EVIDENCE_SCHEMA = "s2kb.withheld-variant-evidence.v1"
CONFIRMED = "S2KA_WITHHELD_VARIANT_GENERALIZATION_CONFIRMED"
FALSIFIED = "S2KA_WITHHELD_VARIANT_GENERALIZATION_FALSIFIED"
NOT_EVALUABLE = "NOT_EVALUABLE"


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _selected(probe: dict[str, object], role: str) -> bool:
    return probe.get(role) is not None


def _baseline_match(probe: dict[str, object], role: str) -> bool | None:
    baseline = probe.get("baselines")
    if not isinstance(baseline, dict):
        return None
    value = baseline.get(role)
    if value is None:
        return None
    if not isinstance(value, dict) or not isinstance(value.get("match"), bool):
        return None
    return value["match"]


def evaluate_s2ka_evidence(evidence: object) -> dict[str, object]:
    issues: list[str] = []
    if not isinstance(evidence, dict) or evidence.get("schema") != S2KB_EVIDENCE_SCHEMA:
        issues.append("evidence schema differs")
        payload = {"status": NOT_EVALUABLE, "claims": {}, "issues": issues}
        return {**payload, "evaluation_digest": _digest(payload)}
    if evidence.get("formation_roles") != list(FORMATION_SEQUENCE):
        issues.append("formation sequence differs")
    if any(role in HOLDOUT_ROLES for role in evidence.get("formation_roles", [])):
        issues.append("holdout entered formation path")
    baseline_training = evidence.get("baseline_training_roles")
    if baseline_training != list(FORMATION_SEQUENCE) or any(role in HOLDOUT_ROLES for role in baseline_training or []):
        issues.append("holdout entered baseline training path")
    checkpoints = evidence.get("checkpoints")
    if not isinstance(checkpoints, list) or len(checkpoints) != 4:
        issues.append("checkpoint inventory differs")
        checkpoints = []
    by_id = {item.get("checkpoint_id"): item for item in checkpoints if isinstance(item, dict)}
    if set(by_id) != {item[0] for item in CHECKPOINTS}:
        issues.append("checkpoint identity differs")
    for checkpoint_id, formation_count in CHECKPOINTS:
        checkpoint = by_id.get(checkpoint_id)
        if not isinstance(checkpoint, dict) or checkpoint.get("formation_count") != formation_count:
            issues.append(f"checkpoint count differs: {checkpoint_id}")
            continue
        probes = checkpoint.get("probes")
        if not isinstance(probes, list) or [item.get("probe_role") for item in probes if isinstance(item, dict)] != list(HOLDOUT_ROLES):
            issues.append(f"probe inventory differs: {checkpoint_id}")
            continue
        for probe in probes:
            if not isinstance(probe, dict) or probe.get("prestate_digest") != probe.get("poststate_digest"):
                issues.append(f"read-only evidence differs: {checkpoint_id}")
            baseline = probe.get("baselines") if isinstance(probe, dict) else None
            if not isinstance(baseline, dict) or baseline.get("baseline_prestate_digest") != baseline.get("baseline_poststate_digest"):
                issues.append(f"baseline read-only evidence differs: {checkpoint_id}")
    if issues:
        payload = {"status": NOT_EVALUABLE, "claims": {}, "issues": issues}
        return {**payload, "evaluation_digest": _digest(payload)}

    probes = {
        (checkpoint_id, probe["probe_role"]): probe
        for checkpoint_id, _ in CHECKPOINTS
        for probe in by_id[checkpoint_id]["probes"]
    }
    h0, h1, h2, h3 = (probes[(checkpoint, "H1")] for checkpoint in ("C0", "C1", "C2", "C3"))
    negatives = [probes[(checkpoint, "N0")] for checkpoint, _ in CHECKPOINTS]
    claims = {
        "before_training_has_no_memory_match": not any(_selected(h0, role) for role in ("b4_selected", "fast_selected", "auditory_slow_selected", "visual_slow_selected")),
        "one_exposure_is_recent_only": _selected(h1, "b4_selected") and _selected(h1, "fast_selected") and not _selected(h1, "auditory_slow_selected") and not _selected(h1, "visual_slow_selected"),
        "varied_training_stabilizes_holdout": all(_selected(h2, role) for role in ("b4_selected", "fast_selected", "auditory_slow_selected", "visual_slow_selected")),
        "final_holdout_is_slow_only": not _selected(h3, "b4_selected") and not _selected(h3, "fast_selected") and _selected(h3, "auditory_slow_selected") and _selected(h3, "visual_slow_selected"),
        "negative_holdout_never_matches": all(not any(_selected(probe, role) for role in ("b4_selected", "fast_selected", "auditory_slow_selected", "visual_slow_selected")) for probe in negatives),
        "frozen_first_rejects_final_holdout": _baseline_match(h3, "frozen_first") is False,
        "nearest_exemplar_rejects_final_holdout": _baseline_match(h3, "replay_nearest") is False,
        "adaptive_baseline_accepts_final_holdout": _baseline_match(h3, "adaptive_prototype") is True,
        "all_baselines_reject_final_negative": all(_baseline_match(negatives[-1], role) is False for role in ("frozen_first", "replay_nearest", "adaptive_prototype")),
        "all_memory_and_baseline_probes_are_read_only": all(
            probe["prestate_digest"] == probe["poststate_digest"]
            and probe["baselines"]["baseline_prestate_digest"] == probe["baselines"]["baseline_poststate_digest"]
            for probe in probes.values()
        ),
    }
    status = CONFIRMED if all(claims.values()) else FALSIFIED
    payload = {"status": status, "claims": claims, "issues": []}
    return {**payload, "evaluation_digest": _digest(payload)}
