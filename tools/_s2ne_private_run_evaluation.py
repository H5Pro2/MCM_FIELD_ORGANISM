"""Post-verification S2-NE predictions; no expectations enter execution."""

import json
from pathlib import Path

from tools import _s2ne_private_run as run
from tools import _s2ne_private_run_verification as verifier


def summarize(rows):
    """Keep losses and false admissions explicit, including empty denominators."""
    groups = {}
    for row in rows:
        if row["retention_group"] is None:
            continue
        group = groups.setdefault(row["retention_group"], dict(N=0, D=0, R=0, L=0))
        group["N"] += 1
        if row["reference_correct_a"]:
            group["D"] += 1
            group["R" if row["alternative_correct_a"] else "L"] += 1
    for group in groups.values():
        run.require(group["D"] == group["R"] + group["L"], "RETENTION_COUNTS_INVALID")
        group["status"] = "ERHALTUNG_NICHT_GEPRUEFT" if group["D"] == 0 else "ERHALTUNG_GEPRUEFT"
    return dict(status="CONFIRMED" if all(r["prediction_matches"] for r in rows) else "FALSIFIED",
                rows=rows, retention=groups,
                reference_false_admissions=sum(r["reference_false_admission"] for r in rows),
                alternative_false_admissions=sum(r["alternative_false_admission"] for r in rows),
                reference_abstentions=sum(r["reference_abstains"] for r in rows),
                alternative_abstentions=sum(r["alternative_abstains"] for r in rows))


def _signature(arm):
    evidence = arm["evidence"]
    hypothesis = evidence["hypothesis"]
    return (evidence["decision"], None if hypothesis is None else hypothesis["area"],
            None if hypothesis is None else hypothesis["candidate_values_digest"])


def _inventory(record, catalog, config):
    checks = {}
    for h in range(1, 7):
        history = f"s2ne-h{h:02d}"
        events = [e for e in record["events"] if e["spec"]["history_id"] == history]
        formations = [e for e in events if e["kind"] == "FORMATION"]
        state = verifier.decode_state(record["states"][events[-1]["poststate"]], config)
        inputs = [tuple(catalog["audio"][e["spec"]["audio_source"]]["values"])
                  + tuple(e["source"]["visual"]["values"]) for e in formations]
        expected_b4 = [None] * 9
        for i, values in enumerate(inputs):
            expected_b4[i % 9] = values
        checks[history + ":b4"] = all((s.values if s.occupied else None) == expected
                                      for s, expected in zip(state.b4_state.entries, expected_b4, strict=True))
        # Final Fast placement follows the prebound history, not a new selection rule.
        positions = {1: (0,), 2: (0, 1), 3: (0,), 4: (12, 13, 11), 5: (1,), 6: ()}[h]
        expected_fast = [inputs[i] for i in positions]
        actual_fast = [s.auditory_values + s.visual_values for s in state.tspm_state.fast_state.slots if s.occupied]
        checks[history + ":fast"] = actual_fast == expected_fast
        expected_support = 3 if h == 4 else 1 if h == 5 else None
        for modality, start, stop in (("auditory", 0, 48), ("visual", 48, 336)):
            bank = getattr(state.tspm_state, modality + "_ppb1_state")
            occupied = [s for s in bank.slots if s.occupied]
            if expected_support is None:
                checks[history + ":" + modality] = occupied == [] and bank.accepted_step_count == 0
            else:
                original = inputs[0][start:stop]
                expected = original
                rate = getattr(config.profile.profile, modality + "_config").update_rate
                for _ in range(expected_support - 1):
                    expected = tuple((1.0 - rate) * p + rate * x for p, x in zip(expected, original, strict=True))
                checks[history + ":" + modality] = (len(occupied) == 1 and occupied[0].slot_id == bank.slots[0].slot_id
                    and occupied[0].support_count == expected_support and occupied[0].prototype_values == expected
                    and bank.accepted_step_count == expected_support)
    q10 = [e for e in record["events"] if e["kind"] == "CUE"][9]
    state = verifier.decode_state(record["states"][q10["prestate"]], config)
    original = tuple(catalog["audio"]["s001"]["values"])
    checks["q10:target_absent_from_a"] = (all(not s.occupied or s.values[:48] != original for s in state.b4_state.entries)
        and all(not s.occupied or s.auditory_values != original for s in state.tspm_state.fast_state.slots))
    return checks


def evaluate_main(record, verification, catalog, config):
    run.require(record["mode"] == "MAIN" and record["status"] == verification["status"] == "RECORDING_COMPLETE"
                and verification["record_digest"] == record["record_digest"]
                and verification["plan_digest"] == record["plan_digest"], "VERIFICATION_REQUIRED")
    verifier._check_digest(record, "record_digest")
    verifier._check_digest(verification, "verification_digest")
    run.require(record["plan"] == [run.asdict(e) for e in run.EVENTS] and run.digest(catalog) == record["catalog_digest"],
                "EVALUATION_BINDING_INVALID")
    t = tuple(catalog["audio"]["s001"]["values"])
    e = tuple(catalog["audio"]["s004"]["values"])
    stable = t
    rate = config.profile.profile.auditory_config.update_rate
    for _ in range(2):
        stable = tuple((1.0 - rate) * p + rate * x for p, x in zip(stable, t, strict=True))
    admit_a = ("ADMIT_SINGLE_CONTEXT", "A_RECENT", run.digest(list(t)))
    admit_e = ("ADMIT_SINGLE_CONTEXT", "A_RECENT", run.digest(list(e)))
    admit_b = ("ADMIT_SINGLE_CONTEXT", "B_STABLE_AUDITORY", run.digest(list(stable)))
    internal = ("ABSTAIN_INTERNAL_AMBIGUITY", None, None)
    public = ("ABSTAIN_AMBIGUOUS_CONTEXT", None, None)
    absent = ("ABSTAIN_NO_CONTEXT", None, None)
    incompatible = ("ABSTAIN_NO_APPLICABLE_CONTEXT", None, None)
    expected = ((admit_a, admit_a),) * 4 + ((internal, admit_a),) * 4 + (
        (admit_e, incompatible), (internal, admit_b), (internal, public), (internal, internal), (absent, absent))
    cues = [e for e in record["events"] if e["kind"] == "CUE"]
    run.require(len(cues) == len(expected) == 13 and len(verification["baseline_equality"]) == 13, "EVALUATION_COUNTS_INVALID")
    rows = []
    for i, (event, prediction, baseline) in enumerate(zip(cues, expected, verification["baseline_equality"], strict=True)):
        reference, alternative = _signature(event["arms"][0]), _signature(event["arms"][2])
        known = i < 8
        desired = admit_a if known else admit_b if i == 9 else None
        subtype = ("exact", "level", "frequency", "spectral")[i % 4] if known else None
        variation = tuple(catalog["audio"][event["spec"]["audio_source"]]["values"]) != t
        rows.append(dict(case_id=f"q{i + 1:02d}", reference=list(reference), alternative=list(alternative),
            expected_reference=list(prediction[0]), expected_alternative=list(prediction[1]),
            prediction_matches=(reference, alternative) == prediction and baseline["reference"] and baseline["alternative"],
            reference_correct_a=known and reference == admit_a, alternative_correct_a=known and alternative == admit_a,
            reference_false_admission=reference[0] == "ADMIT_SINGLE_CONTEXT" and reference != desired,
            alternative_false_admission=alternative[0] == "ADMIT_SINGLE_CONTEXT" and alternative != desired,
            reference_abstains=reference[0] != "ADMIT_SINGLE_CONTEXT", alternative_abstains=alternative[0] != "ADMIT_SINGLE_CONTEXT",
            retention_group=None if not known else f"{subtype}:{'competition' if i >= 4 else 'alone'}:{'varied' if variation else 'identical'}"))
    result = summarize(rows)
    inventories = _inventory(record, catalog, config)
    result["inventory_checks"] = inventories
    if not all(inventories.values()):
        result["status"] = "FALSIFIED"
    return run.sealed({**result, "run_id": record["run_id"], "record_digest": record["record_digest"],
                       "verification_digest": verification["verification_digest"]}, "evaluation_digest")


def evaluate_main_once(recording_path, verification_path):
    path, proof_path = Path(recording_path).resolve(strict=True), Path(verification_path).resolve(strict=True)
    run.require(path.name == "recording.json" and proof_path == path.with_name("verification.json")
                and path.parent.parent == (run.ROOT / "reports/s2ne").resolve(), "EVALUATION_PATH_INVALID")
    target = path.with_name("evaluation.json")
    run.require(not target.exists() and not target.with_name("evaluation.json.pending").exists(), "EVALUATION_ALREADY_EXISTS")
    record = json.loads(path.read_bytes())
    proof = json.loads(proof_path.read_bytes())
    verifier._check_digest(proof, "report_digest")
    run.require(proof["file_unchanged"] is True and proof["record_file_sha256"] == run.filehash(path), "VERIFIED_FILE_CHANGED")
    inner = {k: v for k, v in proof.items() if k not in ("record_file_sha256", "file_unchanged", "report_digest")}
    result = evaluate_main(record, inner, run.load_catalog(), run.make_config())
    run.atomic_write(target, result)
    return target


__all__ = ()
