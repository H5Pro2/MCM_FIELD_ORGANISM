"""Single authorized NG call over the sealed MT plan; no historical main call."""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

from tools import _s2ng_private_runtime_comparison as run
from tools import _s2ng_private_comparison_verification as verify
from tools import _s2ng_private_comparison_evaluation as evaluate
from tools import _s2mt_private_transfer_runtime_runner as mt

ROOT = run.ROOT
ID = "s2ng-real-runtime-comparison-20260906-01"
OUT = ROOT/"reports/s2ng"/ID
SOURCE = "reports/s2mt/s2mt-presealed-transfer-runtime-20260906-05/result.json"
SOURCE_SHA = "2de06dfc17728fd1c9aa7793e616e5a530cbf716306431117ce9dce4325d886f"
PLAN_DIGEST = "3b749837273f9cfb1af4ac50659881c48a4a113384d65999dc90e922b46fd26c"
QUALIFICATION = "reports/s2ng/s2ng-private-runtime-composition-qualification-20260906-02/result.json"
CALLER = "reports/s2ng/run_runtime_comparison_once.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_plan():
    run.require(sha(ROOT/SOURCE) == SOURCE_SHA, "SOURCE_FILE_INVALID")
    historical = json.loads((ROOT/SOURCE).read_bytes())
    verify.check(historical, "record_digest")
    p = historical["presealed_source_plan"]
    values = {k: v for k, v in p.items() if k != "recipe_digests"}
    values["recipes"] = tuple(mt.raw_source.S2MTScaledRawRecipeV2(**x) for x in p["recipes"])
    values["formation_sequence"] = tuple(p["formation_sequence"])
    values["cue_sequence"] = tuple(tuple(x) for x in p["cue_sequence"])
    plan = mt.raw_source._validated_plan(mt.raw_source.PresealedAVCorpusPlanV2(**values))
    run.require(plan.plan_digest == PLAN_DIGEST and plan.formation_sequence == mt.raw_source.FORMATION_SEQUENCE
                and plan.cue_sequence == mt.raw_source.CUE_SEQUENCE
                and p["recipe_digests"] == [x.recipe_digest for x in plan.recipes], "PLAN_INVALID")
    run.require(all(sha(ROOT/p) == h for p, h in historical["source_hashes"].items()), "HISTORICAL_COMPONENT_CHANGED")
    return plan


def failure(error, phase, ordinal):
    return dict(phase=phase, event_ordinal=ordinal, error_class=type(error).__name__,
                code=getattr(error, "code", "S2NG_EXECUTION_ERROR"))


def verify_once(path, config):
    """One independent read of the atomic envelope, without runtime replay."""
    before = sha(path)
    proof = None
    try:
        data = path.read_bytes()
        run.require(len(data) <= run.MAX_BYTES, "RECORD_SIZE_EXCEEDED")
        record = json.loads(data)
        verify.check(record, "result_digest")
        run.require(run.canonical(record) == data and record["run_id"] == ID
            and record["plan_digest"] == PLAN_DIGEST and record["main_calls"] == 1
            and record["gate_after"] is False and record["source_hashes_before"] == record["source_hashes_after"]
            and all(sha(ROOT/p) == h for p, h in record["source_hashes_after"].items()), "RUN_BINDING_INVALID")
        for s in record["closed_snapshots"]:
            verify.check(s, "snapshot_digest")
            run.require(s["status"] == "CLOSED" and 0 <= s["processed_event_count"] <= 28, "CLOSE_INVALID")
        if record["comparison"] is not None:
            proof = verify.verify_record(record["comparison"], config=config)
            run.require(record["materialized_events"] == 28 and record["materialization_calls"] == 1
                and len(record["closed_snapshots"]) == 2 and record["closed_snapshots"] == record["comparison"]["final"], "LIFECYCLE_INVALID")
            if proof["status"] == "RECORDING_COMPLETE":
                run.require(proof["completed_events"] == 28 and proof["field_contacts"] == 16128
                    and proof["scan_receipts"] == 32 and record["failure"] is None
                    and all(s["memory_formation_attempt_count"] == 20 for s in record["closed_snapshots"]), "COUNTS_INVALID")
        else:
            run.require(record["status"] == "NOT_EVALUABLE" and record["failure"] is not None
                and record["failure"]["phase"] in ("BINDINGS", "MATERIALIZATION", "RUNTIME_INIT", "EVENT_PROCESSING", "RUNTIME_CLOSE", "SERIALIZATION"), "FAILURE_INVALID")
        run.require(record["close_errors"] == [] and sha(path) == before, "READ_ONLY_OR_CLOSE_INVALID")
        report = dict(status=record["status"], evidence_valid=True, comparison_verification=proof, error=None)
    except Exception as error:
        report = dict(status="NOT_EVALUABLE", evidence_valid=False, comparison_verification=None,
                      error=failure(error, "VERIFICATION", None))
    report = run.sealed({**report, "run_id": ID, "result_file_sha256": before,
                        "file_unchanged": sha(path) == before, "verification_calls": 1}, "verification_digest")
    run.ne.atomic_write(OUT/"verification.json", report)
    return report


def evaluate_once(record, proof):
    """Targets and generation provenance are used only after verification."""
    generations = {m: {} for m in ("auditory", "visual")}
    original = {}
    for n, recipe in enumerate(mt.raw_source.FORMATION_SEQUENCE):
        pair = record["pairs"][n]["arms"][0]
        pre = record["states"][pair["pre"]["memory_state_digest"]]
        post = record["states"][pair["memory"]]
        for timed in record["inputs"][n]["field"]["timed_frames"]:
            original.setdefault((recipe, timed["frame"]["modality_id"]), run.digest(timed["frame"]["values"]))
        for modality in generations:
            bank = modality + "_ppb1_state"
            for a, b in zip(pre["tspm_state"][bank]["slots"], post["tspm_state"][bank]["slots"], strict=True):
                if a != b:
                    key = b["slot_id"]
                    if not a["occupied"] or b["support_count"] == 1:
                        generations[modality][key] = []
                    generations[modality][key].append(recipe)
    final = record["states"][record["pairs"][19]["arms"][0]["memory"]]
    inventories, targets = {}, {}
    for modality in generations:
        inventories[modality] = []
        for s in final["tspm_state"][modality+"_ppb1_state"]["slots"]:
            if not s["occupied"]:
                continue
            lineage = generations[modality].get(s["slot_id"], [])
            d = run.digest(s["prototype_values"])
            inventories[modality].append(dict(slot_id=s["slot_id"], support=s["support_count"],
                values_digest=d, formation_recipes=lineage))
            if lineage and len(set(lineage)) == 1:
                targets.setdefault((lineage[0], modality), []).append(d)
    expectations = []
    for ordinal, (recipe, modality_label) in enumerate(mt.raw_source.CUE_SEQUENCE, 21):
        modality = modality_label.lower()
        ds = tuple(dict.fromkeys(([original[recipe, modality]] if (recipe, modality) in original else [])
                                 + targets.get((recipe, modality), [])))
        expectations.append(evaluate.ExpectationV1(ordinal, modality, ds, recipe in ("n00", "n01"),
            "EXACT_SOURCE_REUSE" if recipe != "n12" else "UNKNOWN", "REAL_PRESSURE_INVENTORY"))
    result = evaluate.evaluate(record, proof, tuple(expectations))
    return run.sealed(dict(comparison=result, final_slow_inventory=inventories,
        final_b4_inventory=final["b4_state"], final_fast_inventory=final["tspm_state"]["fast_state"],
        target_assignment="Own PPB generation lineage plus original source digest; evaluator only"), "evaluation_digest")


def main():
    run.require(Path.cwd().resolve() == ROOT and not run.MAIN_GATE, "WORKSPACE_OR_GATE_INVALID")
    OUT.mkdir(exist_ok=False)
    qualification = json.loads((ROOT/QUALIFICATION).read_bytes())
    run.require(qualification["status"] == "S2NG_COMPOSITION_QUALIFIED"
        and all(sha(ROOT/p) == h for p, h in qualification["hashes_after"].items()), "QUALIFIED_SOURCE_CHANGED")
    watched = set(qualification["hashes_after"]) | set(mt.SOURCE_PATHS) | {SOURCE, QUALIFICATION, CALLER}
    before = {p: sha(ROOT/p) for p in sorted(watched)}
    run.ne.atomic_write(OUT/"preregistration.json", dict(run_id=ID, source_file=SOURCE, source_file_sha256=SOURCE_SHA,
        plan_digest=PLAN_DIGEST, source_hashes_before=before, python=sys.version, interpreter_sha256=sha(Path(sys.executable)),
        main_call_limit=1, materialization_call_limit=1, verification_call_limit=1, evaluation_call_limit=1,
        retry=False, limits=run.budget(tuple(s.event_type for s in mt.EVENT_SPECS)),
        event_specs=[asdict(s) for s in mt.EVENT_SPECS], main_gate_before=False))
    phase, ordinal, error_record = "BINDINGS", None, None
    composition, comparison, config = None, None, None
    materialization_calls, materialized_events = 0, None
    closed, close_errors = [], []
    run.MAIN_GATE = True
    try:
        plan = load_plan()
        config = mt.field_source._build_config()
        phase = "MATERIALIZATION"
        materialization_calls += 1
        materialized = mt._materialize_events(plan, config)
        materialized_events = len(materialized)
        events = tuple(mt._build_event(e) for e in materialized)
        del materialized
        phase = "RUNTIME_INIT"
        # Keep the partial object reachable so any created runtimes can be closed on failure.
        composition = run.RuntimeComparison.__new__(run.RuntimeComparison)
        composition.__init__(config=config, events=events, field_clock_id=mt.FIELD_CLOCK_ID, comparison_id=ID, mode="MAIN")
        phase = "EVENT_PROCESSING"
        for ordinal in range(1, 29):
            composition.process_next()
            if composition.failed:
                break
        phase = "RUNTIME_CLOSE"
        comparison = composition.finish()
        phase = "SERIALIZATION"
    except Exception as error:
        error_record = failure(error, phase, ordinal)
        comparison = None
    finally:
        run.MAIN_GATE = False
        for subject in getattr(composition, "subjects", ()):
            try:
                closed.append(asdict(subject.close() if subject.snapshot().status == "OPEN" else subject.snapshot()))
            except Exception as error:
                close_errors.append(failure(error, "RUNTIME_CLOSE", ordinal))
    after = {p: sha(ROOT/p) for p in sorted(watched)}
    envelope = dict(run_id=ID, plan_digest=PLAN_DIGEST, source_hashes_before=before, source_hashes_after=after,
        status="RECORDING_COMPLETE" if comparison is not None and comparison["status"] == "RECORDING_COMPLETE" and before == after and not close_errors else "NOT_EVALUABLE",
        comparison=comparison, failure=error_record, close_errors=close_errors, closed_snapshots=closed,
        main_calls=1, materialization_calls=materialization_calls, materialized_events=materialized_events, gate_after=run.MAIN_GATE)
    record = run.sealed(envelope, "result_digest")
    if len(run.canonical(record)) > run.MAX_BYTES:
        envelope.update(status="NOT_EVALUABLE", comparison=None,
            failure=dict(phase="SERIALIZATION", event_ordinal=ordinal, error_class="S2NGError", code="RECORD_SIZE_EXCEEDED"))
        record = run.sealed(envelope, "result_digest")
    run.ne.atomic_write(OUT/"recording.json", record)
    proof = verify_once(OUT/"recording.json", config)
    functional = None
    if proof["status"] == "RECORDING_COMPLETE" and proof["evidence_valid"]:
        try:
            functional = evaluate_once(json.loads((OUT/"recording.json").read_bytes())["comparison"], proof["comparison_verification"])
            run.ne.atomic_write(OUT/"evaluation.json", functional)
        except Exception as error:
            run.ne.atomic_write(OUT/"evaluation-error.json", failure(error, "EVALUATION", None))
    print(json.dumps(dict(run_id=ID, execution_status=record["status"], verification_status=proof["status"],
        verification_valid=proof["evidence_valid"], failure=record["failure"], gate_after=run.MAIN_GATE,
        closed_snapshots=closed, result_digest=record["result_digest"],
        evaluation=None if functional is None else functional["comparison"]["groups"])))
    return 0 if functional is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
