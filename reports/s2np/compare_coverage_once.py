"""One authorized NP comparison from frozen evidence; no source/receptor execution."""

from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

from tools import _s2np_private_source_binding as b
from tools import _s2np_private_preseal_verification as plans
from tools import _s2np_private_coverage_comparison as c
from tools import _s2np_private_coverage_evaluation as evaluation

RUN_ID = "s2np-coverage-corpus-comparison-20260907-01"
PRESEAL = b.ROOT / "reports/s2np/s2np-source-preseal-20260907-01"
MATERIAL = b.ROOT / "reports/s2np/s2np-receptor-nj-materialization-20260907-01"
QUAL = b.ROOT / "reports/s2np/s2np-coverage-comparison-qualification-20260907-02"
MATERIAL_FILE_HASH = "59796211f0203216a9c71c5b1e93a0326ebcc6d947e7c7ad7d4910d97307f430"
MATERIAL_ROOT = "f548fa82983390465854b1c1b4824c2a32f5b73669cb85c01dc0de853151b9f7"
MATERIAL_VERIFICATION = "c2dc1ce3ebf7d2124d315adb090c140b0593b13e40c503f93773a0bbb0860be2"
QUAL_ROOT = "6c104e8afb5456cda6f8c20cdd181c33ff94c0c8bbacac01f02e3f70a9367f9d"
EXECUTION_ROOT = "bae2b0ef565a5117c28984d40753da39cc1ca82b576e59864c72d57212254664"
EVALUATION_ROOT = "0d2849710a4d321cc63ae42b024f46e0ead3579f0d4dfce9dd4139243e4cd96d"
SEAL_ROOT = "a72aa07c9dc153f29a187470bce76fb918ce8cbbaeb4f2666c700fb719bf307b"


def root(value, key, expected=None):
    c.require(type(value) is dict and value.get(key) == b.digest({k: v for k, v in value.items() if k != key}),
              "ROOT_DIGEST_INVALID")
    c.require(expected is None or value[key] == expected, "ROOT_BINDING_INVALID")
    return value


def read(path, key, expected=None):
    data = path.read_bytes()
    c.require(len(data) <= c.MAX_OUTPUT_BYTES, "INPUT_SIZE_EXCEEDED")
    value = json.loads(data)
    c.require(data == b.canonical(value), "CANONICAL_INPUT_INVALID")
    return root(value, key, expected)


def check_hashes(hashes):
    c.require(all(b.filehash(b.ROOT / path) == sha for path, sha in hashes.items()), "BOUND_FILE_CHANGED")


def bind_inputs():
    q = read(QUAL / "result.json", "result_digest", QUAL_ROOT)
    c.require(q["status"] == "S2NP_COVERAGE_COMPARISON_QUALIFIED" and q["passed_tests"] == 22
              and q["exit_code"] == 0 and q["unittest_calls"] == 1
              and q["hashes_before"] == q["hashes_after"], "QUALIFICATION_INVALID")
    check_hashes(q["hashes_after"])
    execution = read(PRESEAL / "execution-plan.json", "execution_digest", EXECUTION_ROOT)
    expected = read(PRESEAL / "evaluation-plan.json", "evaluation_digest", EVALUATION_ROOT)
    seal = read(PRESEAL / "seal.json", "seal_digest", SEAL_ROOT)
    plans.check_plans(execution, expected)
    c.require(seal["status"] == "S2NP_SOURCES_PRESEALED" and seal["execution_digest"] == EXECUTION_ROOT
              and seal["evaluation_digest"] == EVALUATION_ROOT
              and seal["execution_file_sha256"] == b.filehash(PRESEAL / "execution-plan.json")
              and seal["evaluation_file_sha256"] == b.filehash(PRESEAL / "evaluation-plan.json"), "SEAL_INVALID")
    c.require(execution["environment"] == b.environment(), "INTERPRETER_ENVIRONMENT_CHANGED")
    c.require(seal["hashes_before"] == seal["hashes_after"] == execution["source_hashes"] == b.watched(),
              "SOURCE_CODE_BINDING_INVALID")
    material = read(MATERIAL / "result.json", "record_digest", MATERIAL_ROOT)
    prior_check = read(MATERIAL / "verification.json", "verification_digest", MATERIAL_VERIFICATION)
    c.require(b.filehash(MATERIAL / "result.json") == MATERIAL_FILE_HASH
              == prior_check["file_sha256_before"] == prior_check["file_sha256_after"]
              and prior_check["record_digest"] == MATERIAL_ROOT
              and prior_check["status"] == "S2NP_MATERIALIZATION_VALID"
              and prior_check["half_values_checked"] == 576 and prior_check["materialized_sources"] == 12,
              "VERIFIED_MATERIALIZATION_INVALID")
    c.require(material["status"] == "RECEPTOR_NJ_MATERIALIZATION_COMPLETE" and material["failure"] is None
              and material["execution_digest"] == EXECUTION_ROOT and material["seal_digest"] == SEAL_ROOT
              and material["counts"]["completed_sources"] == len(material["states"]) == 12
              and material["source_hashes_before"] == material["source_hashes_after"], "MATERIALIZATION_INVALID")
    check_hashes(material["source_hashes_before"])
    profile = root(material["profile"], "profile_digest")
    c.require(profile["bound_profiles"] == execution["profiles"] == b.profile_binding()
              and profile["config"] == execution["profiles"]["raw"]["config"], "PROFILE_BINDING_INVALID")
    for source, row in zip(execution["sources"], material["states"], strict=True):
        root(row, "materialized_state_digest")
        c.require(all(row[k] == source[k] for k in (
            "source_id", "source_digest", "recipe_digest", "pcm_sha256", "ordinal", "clock_id")), "SOURCE_INVALID")
        projection = root(row["projection"], "projection_digest")
        c.require(projection["profile_digest"] == c.PROFILE
                  and projection["source_profile_digest"] == execution["profiles"]["raw_profile_digest"]
                  and projection["source_state_digest"] == row["raw_state_digest"] == b.digest(row["raw_state"])
                  and projection["source_values_digest"] == row["raw_values_digest"]
                  and projection["clock_id"] == source["clock_id"]
                  and projection["window_start_tick"] == source["window_start_sample"]
                  and projection["window_end_tick"] == source["window_end_sample"]
                  and projection["snapshot_index"] == source["snapshot_index"]
                  and projection["carrier_ids"] == profile["carriers"], "PROJECTION_SOURCE_INVALID")
        c.values_check(tuple(projection["values"]), 48)
        c.require([x.hex() for x in projection["values"]] == row["half_values_hex"], "VALUE_BINDING_INVALID")
    watched = {**q["hashes_after"], **material["source_hashes_before"]}
    for path in (Path(__file__), QUAL / "result.json", QUAL / "preregistration.json",
                 MATERIAL / "result.json", MATERIAL / "verification.json"):
        watched[path.relative_to(b.ROOT).as_posix()] = b.filehash(path)
    return execution, expected, material, prior_check, watched


def catalog_from(material):
    return tuple(c.project_values(source_id=row["source_id"], source_digest=row["source_digest"],
        payload_digest=row["pcm_sha256"], projection_digest=row["projection"]["projection_digest"],
        profile_digest=row["projection"]["profile_digest"],
        start_tick=row["projection"]["window_start_tick"], end_tick=row["projection"]["window_end_tick"],
        snapshot_index=row["projection"]["snapshot_index"], values=tuple(row["projection"]["values"]), view_id=view)
        for view, _ in c.VIEWS for row in material["states"])


def atomic(out, name, value):
    data = c.bounded_payload(value)
    c.require(sum(p.stat().st_size for p in out.glob("*.json")) + len(data) <= c.MAX_OUTPUT_BYTES,
              "TOTAL_EVIDENCE_SIZE_EXCEEDED")
    pending = out / (name + ".pending")
    c.require(not (out / name).exists(), "OUTPUT_ALREADY_EXISTS")
    b.publish(pending, value)
    os.rename(pending, out / name)
    return b.filehash(out / name)


def restore_panel(row):
    relations = tuple(c.Relation(reference_id=r["reference_id"], reference_digest=r["reference_digest"],
        differences=tuple(c.BandDifference(**d) for d in r["differences"]), mean=r["mean"],
        maximum=r["maximum"], applicable=tuple(r["applicable"])) for r in row["relations"])
    findings = tuple(c.Finding(f["condition_id"], f["threshold"], tuple(f["hits"]), f["status"]) for f in row["findings"])
    return c.PanelResult(**{**row, "relations": relations, "findings": findings})


def verify_recording_once(out, expected_hash, watched):
    """Read the recorded bytes, not the live results; no source differences."""
    c.require(not (out / "verification.json").exists(), "VERIFICATION_ALREADY_EXISTS")
    c.require(b.filehash(out / "recording.json") == expected_hash, "RECORDING_FILE_CHANGED")
    recorded = read(out / "recording.json", "record_digest")
    c.require(recorded["run_id"] == RUN_ID and recorded["status"] == "RECORDING_COMPLETE"
              and recorded["source_hashes"] == watched and recorded["execution_digest"] == EXECUTION_ROOT
              and recorded["evaluation_plan_digest"] == EVALUATION_ROOT, "RECORDING_BINDING_INVALID")
    root(recorded["materialization"], "record_digest", MATERIAL_ROOT)
    root(recorded["materialization_verification"], "verification_digest", MATERIAL_VERIFICATION)
    c.require(recorded["counts"] == dict(primary_findings=360, direct_findings=360,
              primary_relationship_rows=360, direct_relationship_rows=360,
              primary_band_differences=3840, direct_band_differences=3840), "COUNT_BINDING_INVALID")
    catalog = tuple(c.ViewValues(**{**v, "values": tuple(v["values"]), "indices": tuple(v["indices"])})
                    for v in recorded["catalog"])
    c.require(b.canonical([asdict(v) for v in catalog]) ==
              b.canonical([asdict(v) for v in catalog_from(recorded["materialization"])]), "CATALOG_SOURCE_INVALID")
    primary = tuple(restore_panel(r) for r in recorded["primary"])
    direct = tuple(restore_panel(r) for r in recorded["direct"])
    verification = c.verify_fixed(catalog, primary, direct)
    check_hashes(watched)
    c.require(b.filehash(out / "recording.json") == expected_hash and not c.MAIN_GATE and not b.MAIN_GATE,
              "READ_ONLY_BINDING_INVALID")
    evidence = b.sealed(dict(run_id=RUN_ID, recording_sha256_before=expected_hash,
        recording_sha256_after=b.filehash(out / "recording.json"), record_digest=recorded["record_digest"],
        verification_calls=1, read_only=True, evidence=verification,
        new_band_differences=0, parent_half_multiplications_repeated=0,
        primary_direct_bitwise_equal=True, main_gate_after=False), "verification_digest")
    atomic(out, "verification.json", evidence)
    return catalog, primary, verification


def main():
    out = b.ROOT / "reports/s2np" / RUN_ID
    out.mkdir(exist_ok=False)
    phase, watched, counts = "INPUT_BINDINGS", {}, {}
    attempts = dict(primary=0, direct=0, verification=0, evaluation=0)
    try:
        execution, expected, material, prior_check, watched = bind_inputs()
        prereg = dict(run_id=RUN_ID, command=[sys.executable, "-m", "reports.s2np.compare_coverage_once"],
            source_hashes=watched, execution_digest=EXECUTION_ROOT, evaluation_digest=EVALUATION_ROOT,
            materialization_digest=MATERIAL_ROOT, prior_verification_digest=MATERIAL_VERIFICATION,
            qualification_digest=QUAL_ROOT, environment=execution["environment"],
            limits=dict(panel_findings_per_implementation=360, relationship_rows_per_implementation=360,
                        band_differences_per_implementation=3840, both_band_differences=7680,
                        total_evidence_bytes=2097152, verification_calls=1, evaluation_calls=1),
            payload_generations=0, receptor_calls=0, nj_calls=0, system_calls=0, retry=False, main_gate=False)
        c.require(len(b.canonical(prereg)) <= b.MAX_METADATA_BYTES, "METADATA_SIZE_EXCEEDED")
        atomic(out, "preregistration.json", prereg)
        phase = "VIEW_BINDING"
        catalog = catalog_from(material)
        before = b.digest([asdict(v) for v in catalog])
        phase, attempts["primary"] = "PRIMARY_COMPARISON", 1
        primary = c.compare_fixed(catalog, "PRIMARY")
        counts.update(primary_findings=360, primary_relationship_rows=360, primary_band_differences=3840)
        phase, attempts["direct"] = "DIRECT_COMPARISON", 1
        direct = c.compare_fixed(catalog, "DIRECT")
        counts.update(direct_findings=360, direct_relationship_rows=360, direct_band_differences=3840)
        c.require(before == b.digest([asdict(v) for v in catalog]), "INPUT_MUTATION")
        check_hashes(watched)
        phase = "RECORDING"
        record = b.sealed(dict(run_id=RUN_ID, status="RECORDING_COMPLETE", execution_digest=EXECUTION_ROOT,
            evaluation_plan_digest=EVALUATION_ROOT, source_hashes=watched, counts=counts,
            materialization=material, materialization_verification=prior_check,
            catalog=[asdict(v) for v in catalog], primary=[asdict(r) for r in primary], direct=[asdict(r) for r in direct],
            main_gate_after=False), "record_digest")
        record_hash = atomic(out, "recording.json", record)
        del primary, direct, record
        phase, attempts["verification"] = "READ_ONLY_VERIFICATION", 1
        checked_catalog, checked_primary, verification = verify_recording_once(out, record_hash, watched)
        phase, attempts["evaluation"] = "POST_VERIFICATION_EVALUATION", 1
        assessed = evaluation.evaluate(checked_catalog, checked_primary, verification, expected, EXECUTION_ROOT,
            tuple((s["source_id"], s["pcm_sha256"]) for s in execution["sources"]))
        atomic(out, "evaluation.json", assessed)
        phase = "FINAL_BINDINGS"
        check_hashes(watched)
        c.require(not c.MAIN_GATE and not b.MAIN_GATE, "GATE_INVALID")
        files = {p.name: dict(sha256=b.filehash(p), bytes=p.stat().st_size) for p in sorted(out.glob("*.json"))}
        summary = b.sealed(dict(run_id=RUN_ID, status="RECORDING_COMPLETE", technical_status="TECHNICALLY_VALID",
            evaluation_completed=True, attempts=attempts, counts=counts, files=files,
            source_hashes_before=watched, source_hashes_after=watched, main_gate_after=False,
            payload_generations=0, receptor_calls=0, nj_calls=0, memory_calls=0, field_calls=0,
            context_calls=0, runtime_calls=0, qualification_calls=0), "result_digest")
        atomic(out, "result.json", summary)
        print(json.dumps(dict(run_id=RUN_ID, status=summary["status"], result_digest=summary["result_digest"],
            evidence_bytes=sum(p.stat().st_size for p in out.glob("*.json")), attempts=attempts)))
        return 0
    except Exception as exc:
        failure = b.sealed(dict(run_id=RUN_ID, status="NOT_EVALUABLE", phase=phase, attempts=attempts,
            completed_counts=counts, partial_attempt_counts_not_inferred=True,
            error_class=type(exc).__name__, code=str(exc) if isinstance(exc, (c.S2NPCoverageError, b.S2NPBindingError))
            else "TECHNICAL_EXECUTION_ERROR", source_hashes=watched, main_gate_after=False), "result_digest")
        atomic(out, "failure.json", failure)
        print(json.dumps(failure))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
