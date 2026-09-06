"""Read-only S2-NF verification: metadata and file bytes, never source generation."""

import json
import re

from tools import _s2nf_private_source_binding as binding


def check(condition, code):
    if not condition:
        raise ValueError(code)


def check_digest(value, key):
    check(type(value) is dict and value.get(key) == binding.digest(
        {k: v for k, v in value.items() if k != key}), "CANONICAL_DIGEST_INVALID")


def check_plans(execution, evaluation):
    check_digest(execution, "execution_digest")
    check_digest(evaluation, "evaluation_digest")
    check(execution["schema"] == "s2nf.source-execution-plan.v1"
          and evaluation["schema"] == "s2nf.retention-evaluation-plan.v1", "SCHEMA_INVALID")
    check(execution["contract_sha256"] == evaluation["contract_sha256"] == binding.CONTRACT_HASH,
          "DOCUMENT_BINDING_INVALID")
    check(evaluation["execution_digest"] == execution["execution_digest"], "ROOT_BINDING_INVALID")
    specs = binding.source_specs()
    sources = execution["sources"]
    check(type(sources) is list and len(sources) == 7, "SOURCE_COUNT_INVALID")
    for source, spec in zip(sources, specs, strict=True):
        check_digest(source, "source_digest")
        check(set(source) == set(spec.payload()) | {"pcm_sha256", "pcm_byte_count", "source_digest"},
              "SOURCE_FORM_INVALID")
        check(all(source[k] == v for k, v in spec.payload().items()), "SOURCE_METADATA_INVALID")
        check(source["pcm_byte_count"] == 19200 and type(source["pcm_sha256"]) is str
              and re.fullmatch(r"[0-9a-f]{64}", source["pcm_sha256"]), "PCM_BINDING_INVALID")
        check(spec.historical_pcm_sha256 is None or source["pcm_sha256"] == spec.historical_pcm_sha256,
              "HISTORICAL_PAYLOAD_INVALID")
    check(sources[0]["source_id"] != sources[2]["source_id"]
          and sources[0]["pcm_sha256"] == sources[2]["pcm_sha256"], "EXACT_SOURCE_IDENTITY_INVALID")
    check(execution["events"] == binding.events(), "EVENT_OR_TIME_BINDING_INVALID")
    check(execution["visual_sources"] == binding.visual_bindings(), "VISUAL_METADATA_INVALID")
    check(execution["receptor_profile"] == dict(binding.PROFILE)
          and execution["receptor_profile_digest"] == binding.digest(dict(binding.PROFILE)), "PROFILE_INVALID")
    check(execution["observed_bands"] == list(range(24))
          and execution["unobserved_bands"] == list(range(24, 48)), "BAND_PLAN_INVALID")
    check(execution["rules"] == [
        {"id": "HISTORICAL_SUM_L1_24", "arithmetic": "sum_in_band_order/24", "threshold": 0.2},
        {"id": "ALL_BANDS_24", "arithmetic": "max", "threshold": 0.2}]
        and execution["slow_rule"] == {"arithmetic": "sum_in_band_order/24", "threshold": 0.02}, "RULE_METADATA_INVALID")
    check(all(execution[k] is False for k in (
        "receptor_execution_authorized", "memory_execution_authorized", "rule_execution_authorized")), "EXECUTION_NOT_CLOSED")
    expected_budgets = dict(source_windows=7, source_samples=33600, source_pcm_bytes=134400,
        max_live_payloads=1, max_live_canonical_pcm_bytes=19200, formations=3, cues=10, events=13,
        future_audio_analyses=13, future_visual_analyses=3, future_receptor_values=1488,
        cases_per_rule=10, arm_records=40, slot_visits=800, expected_eligible_relationships=120,
        expected_band_differences=2880, max_band_differences=19200, max_equality_comparisons=1920,
        max_retrieval_comparisons=21120, max_verification_comparisons=21120,
        logical_retrieval_operations=560, max_live_rgb_bytes=6220800,
        formation_l1_limit=10656, max_state_bytes=44544, arm_bytes_exclusive=32768, max_output_bytes=4194304)
    check(execution["budgets"] == expected_budgets, "BUDGET_INVALID")
    cases = evaluation["cases"]
    check(len(cases) == 10, "CASE_COUNT_INVALID")
    subtypes = ("EXACT", "UNIFORM_GAIN", "FREQUENCY", "SPECTRAL_REWEIGHT", "LOCAL_PARTIAL_ADDITION")
    for i, case in enumerate(cases):
        first, ordinal = i < 5, i % 5
        expected = dict(case_id=f"c{i + 1:02d}", event_id=f"s2nf-h{1 if first else 2:02d}-e{ordinal + (3 if first else 2):02d}",
            source_id=f"nf-a{ordinal + 3:02d}", related_source_id="nf-a01", competitor_source_id="nf-a02",
            target_present=first, expected="UNIQUE_CORRECT_A" if first else "ABSTAIN",
            subtype=subtypes[ordinal], retention_eligible=first)
        check(case == expected, "EVALUATION_CASE_INVALID")
    check({k: evaluation[k] for k in ("positive_cases", "removal_controls", "exact_positive", "variant_positive",
          "retention_identity", "zero_denominator", "offset_losses_with_gains", "variation_axes")} == dict(
        positive_cases=5, removal_controls=5, exact_positive=1, variant_positive=4, retention_identity="D=R+L",
        zero_denominator="ERHALTUNG_NICHT_GEPRUEFT", offset_losses_with_gains=False,
        variation_axes=["pcm_bits", "receptor_48_bits", "observed_24_bits"]), "EVALUATION_BOUNDARY_INVALID")
    for root, keys in ((execution, {
        "schema", "contract_sha256", "sources", "visual_sources", "events", "generator_identity", "source_hashes",
        "receptor_profile", "receptor_profile_digest", "observed_bands", "unobserved_bands", "rules", "slow_rule",
        "budgets", "receptor_execution_authorized", "memory_execution_authorized", "rule_execution_authorized", "execution_digest"}),
        (evaluation, {"schema", "contract_sha256", "execution_digest", "cases", "positive_cases", "removal_controls",
        "exact_positive", "variant_positive", "retention_identity", "zero_denominator", "offset_losses_with_gains",
        "variation_axes", "evaluation_digest"})):
        check(set(root) == keys, "ROOT_FORM_INVALID")


def verify_once(out):
    with (out / "verification-reservation.json").open("x", encoding="ascii") as handle:
        handle.write('{"verification_calls":1,"pcm_generation_calls":0}')
    before = {}
    try:
        names = ("execution-plan.json", "evaluation-plan.json", "seal.json", "preregistration.json")
        check(all((out / n).stat().st_size <= binding.MAX_BYTES for n in names), "FILE_SIZE_INVALID")
        before = {n: binding.filehash(out / n) for n in names}
        execution, evaluation, seal, pre = [json.loads((out / n).read_bytes()) for n in names]
        check_plans(execution, evaluation)
        check_digest(seal, "seal_digest")
        check(seal["status"] == "S2NF_SOURCES_PRESEALED" and seal["schema"] == "s2nf.source-seal.v1", "SEAL_STATUS_INVALID")
        check(seal["run_id"] == pre["run_id"] == out.name, "RUN_ID_INVALID")
        check(seal["execution_file_sha256"] == before[names[0]]
              and seal["evaluation_file_sha256"] == before[names[1]]
              and seal["execution_digest"] == execution["execution_digest"]
              and seal["evaluation_digest"] == evaluation["evaluation_digest"], "SEAL_ROOTS_INVALID")
        check(seal["source_hashes_before"] == seal["source_hashes_after"] == execution["source_hashes"]
              == pre["source_hashes"] == binding.watched(), "SOURCE_FILES_CHANGED")
        check(execution["generator_identity"] == pre["generator_identity"] == binding.identity(), "GENERATOR_IDENTITY_INVALID")
        check(pre["source_specs"] == [s.payload() for s in binding.source_specs()]
              and pre["contract_sha256"] == binding.CONTRACT_HASH
              and pre["qualification_sha256"] == binding.filehash(binding.ROOT / binding.QUAL_DIR / "result.json"), "PREREGISTRATION_INVALID")
        check(pre["generation_calls_limit"] == 7 and pre["preseal_calls_limit"] == 1
              and pre["retry"] is False and pre["receptor_calls"] == 0, "CALL_BUDGET_INVALID")
        for key, expected in dict(completed_sources=7, attempted_sources=7, generated_pcm_bytes=134400,
            generated_samples=33600, max_live_payloads=1, max_live_canonical_pcm_bytes=19200,
            raw_payloads_persisted=0, receptor_calls=0, distance_calls=0, rule_calls=0,
            memory_calls=0, context_calls=0, field_calls=0, runtime_calls=0).items():
            check(type(seal[key]) is int and seal[key] == expected, "COUNTER_INVALID")
        check(seal["exact_pair"] == ["nf-a01", "nf-a03"]
              and seal["exact_payload_sha256"] == execution["sources"][0]["pcm_sha256"], "EXACT_PAIR_INVALID")
        after = {n: binding.filehash(out / n) for n in names}
        check(before == after, "ARTIFACTS_CHANGED")
        result = dict(status="S2NF_PRESEAL_BINDINGS_VERIFIED", run_id=out.name,
            execution_digest=execution["execution_digest"], evaluation_digest=evaluation["evaluation_digest"],
            seal_digest=seal["seal_digest"], sources=7, source_files_checked=len(execution["source_hashes"]),
            artifact_hashes_before=before, artifact_hashes_after=after, verification_calls=1,
            pcm_generation_calls=0, receptor_calls=0, distance_calls=0, rule_calls=0)
    except Exception as error:
        result = dict(status="NOT_EVALUABLE", run_id=out.name, phase="READ_ONLY_BINDING_VERIFICATION",
            error_class=type(error).__name__, code=str(error) if type(error) is ValueError else "BINDING_ERROR",
            artifact_hashes_before=before, verification_calls=1, pcm_generation_calls=0)
    binding.publish(out / "verification.json", binding.sealed(result, "verification_digest"))
    return result
