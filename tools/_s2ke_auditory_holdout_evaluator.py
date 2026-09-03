"""Pure evaluator for prospective S2-KC auditory holdout evidence."""

from __future__ import annotations

import hashlib
import json

from tools._s2ke_auditory_holdout_fixtures import CHECKPOINTS, FORMATION_SEQUENCE, HOLDOUT_ROLES


S2KE_EVIDENCE_SCHEMA = "s2ke.auditory-holdout-evidence.v1"
CONFIRMED = "S2KC_AUDITORY_HOLDOUT_GENERALIZATION_CONFIRMED"
FALSIFIED = "S2KC_AUDITORY_HOLDOUT_GENERALIZATION_FALSIFIED"
NOT_EVALUABLE = "NOT_EVALUABLE"


def _digest(value: object) -> str:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def _match(probe: dict[str, object], role: str) -> bool:
    value = probe.get(role)
    return isinstance(value, dict) and value.get("mechanical_match") is True


def _baseline_match(probe: dict[str, object], role: str) -> bool | None:
    baselines = probe.get("baselines")
    value = baselines.get(role) if isinstance(baselines, dict) else None
    return value.get("match") if isinstance(value, dict) and type(value.get("match")) is bool else None


def evaluate_s2kc_evidence(evidence: object) -> dict[str, object]:
    issues: list[str] = []
    if not isinstance(evidence, dict) or evidence.get("schema") != S2KE_EVIDENCE_SCHEMA:
        issues.append("evidence schema differs")
    elif evidence.get("formation_roles") != list(FORMATION_SEQUENCE):
        issues.append("formation sequence differs")
    elif evidence.get("baseline_training_roles") != list(FORMATION_SEQUENCE):
        issues.append("baseline training sequence differs")
    elif any(role in HOLDOUT_ROLES for role in evidence.get("formation_roles", [])):
        issues.append("holdout entered training")
    checkpoints = evidence.get("checkpoints") if isinstance(evidence, dict) else None
    if not isinstance(checkpoints, list) or len(checkpoints) != len(CHECKPOINTS):
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
            baselines = probe.get("baselines") if isinstance(probe, dict) else None
            if not isinstance(probe, dict) or probe.get("prestate_digest") != probe.get("poststate_digest"):
                issues.append(f"memory read-only evidence differs: {checkpoint_id}")
            if not isinstance(baselines, dict) or baselines.get("prestate_digest") != baselines.get("poststate_digest"):
                issues.append(f"baseline read-only evidence differs: {checkpoint_id}")
    if issues:
        payload = {"status": NOT_EVALUABLE, "claims": {}, "issues": issues}
        return {**payload, "evaluation_digest": _digest(payload)}

    probes = {
        (checkpoint_id, probe["probe_role"]): probe
        for checkpoint_id, _ in CHECKPOINTS
        for probe in by_id[checkpoint_id]["probes"]
    }
    h0, h1, h2, h3 = (probes[(checkpoint, "H_AUDIO")] for checkpoint in ("C0", "C1", "C2", "C3"))
    negatives = [probes[(checkpoint, "N_AUDIO")] for checkpoint, _ in CHECKPOINTS]
    visual_h = h3.get("visual_slow_selected")
    visual_n = negatives[-1].get("visual_slow_selected")
    claims = {
        "before_training_has_no_match": not any(_match(h0, role) for role in ("b4_selected", "fast_selected", "auditory_slow_selected")),
        "one_exposure_has_no_slow_match": not _match(h1, "auditory_slow_selected"),
        "varied_training_stabilizes_auditory_holdout": _match(h2, "auditory_slow_selected") and h2["auditory_slow_selected"].get("support") == 3,
        "final_holdout_is_auditory_slow_only": not _match(h3, "b4_selected") and not _match(h3, "fast_selected") and _match(h3, "auditory_slow_selected") and h3["auditory_slow_selected"].get("support") == 3,
        "negative_has_no_auditory_match": all(not any(_match(probe, role) for role in ("b4_selected", "fast_selected", "auditory_slow_selected")) for probe in negatives),
        "visual_control_is_non_discriminating": isinstance(visual_h, dict) and isinstance(visual_n, dict) and visual_h.get("evidence_digest") == visual_n.get("evidence_digest"),
        "frozen_rejects_final_holdout": _baseline_match(h3, "frozen") is False,
        "replay_rejects_final_holdout": _baseline_match(h3, "nearest") is False,
        "adaptive_accepts_final_holdout": _baseline_match(h3, "adaptive") is True,
        "all_baselines_reject_final_negative": all(_baseline_match(negatives[-1], role) is False for role in ("frozen", "nearest", "adaptive")),
        "all_probes_are_read_only": all(
            probe["prestate_digest"] == probe["poststate_digest"]
            and probe["baselines"]["prestate_digest"] == probe["baselines"]["poststate_digest"]
            for probe in probes.values()
        ),
    }
    payload = {"status": CONFIRMED if all(claims.values()) else FALSIFIED, "claims": claims, "issues": []}
    return {**payload, "evaluation_digest": _digest(payload)}
