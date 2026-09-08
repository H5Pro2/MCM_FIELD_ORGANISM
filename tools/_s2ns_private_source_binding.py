"""Source-only NS specialization; historical sealers are never invoked."""
import hashlib
import json
import re

from tools import _s2nr_private_source_binding as common

ROOT = common.ROOT
CONTRACT = "docs/S2NS_STATISCHER_PLAN_AUDITIVE_ZWEI_SICHTEN_BESTAETIGUNG.md"
MAIN_GATE = False
QUAL_ID = "s2ns-source-binding-qualification-20260908-01"
QUAL_DIR = ROOT / "reports/s2ns" / QUAL_ID
MAX_METADATA_BYTES, MAX_OUTPUT_BYTES = 65536, 4194304
canonical, digest, filehash = common.canonical, common.digest, common.filehash
publish, sealed, SourceSpec = common.publish, common.sealed, common.SourceSpec
generators, environment, profiles = common.generators, common.environment, common.profiles
PINS = {**{p: h for p, h in common.PINS.items() if p != common.CONTRACT},
    CONTRACT: "a305a9588d164e90ffb19918fbefc561d745b643b768785d3cd057445e65153a",
    "tools/_s2nr_private_source_binding.py": "c0e748e2e6cdc24f3c084b3690eafe1fc6bbec036e61c663b9323595fe80c824"}
OWN = ("tools/_s2ns_private_source_binding.py", "tools/_s2ns_private_preseal_verification.py",
    "tests/test_s2ns_private_source_binding.py", "reports/s2ns/qualify_once.py",
    "reports/s2ns/preseal_once.py", "reports/s2ns/QUALIFIKATIONSBINDUNG.md")
AV, A = common.AV, common.A
VIEWS = (("LOWER_24", tuple(range(24))), ("UPPER_24", tuple(range(24, 48))))
# All tuples are neutral source bindings; evaluation roles live in evaluation_plan only.
ROWS = (
    ("h01", AV, 1, 1), ("h01", AV, 2, 2), ("h01", A, 3, None),
    ("h01", A, 4, None), ("h01", A, 5, None), ("h01", A, 6, None), ("h01", A, 7, None),
    ("h02", AV, 2, 2), ("h02", A, 3, None), ("h02", A, 4, None),
    ("h02", A, 5, None), ("h02", A, 6, None), ("h02", A, 7, None),
    ("h03", AV, 1, 1), ("h03", AV, 1, 1), ("h03", AV, 1, 1), ("h03", AV, 1, 1),
    ("h03", AV, 2, 3), ("h03", AV, 2, 4), ("h03", AV, 2, 5),
    ("h03", AV, 2, 6), ("h03", AV, 2, 7), ("h03", AV, 2, 8),
    ("h03", AV, 2, 9), ("h03", AV, 2, 10), ("h03", AV, 2, 11),
    ("h03", A, 3, None), ("h03", A, 4, None), ("h03", A, 5, None),
    ("h03", A, 6, None), ("h03", A, 7, None))
F1, F2 = (271000, 1084000, 6775000), (419000, 1676000, 10475000)
AMP = ((6, 20), (2, 20), (1, 20))
AUDIO = (
    ((F1, AMP, "s2ns-pcm-001"),), ((F2, AMP, "s2ns-pcm-002"),),
    ((F1, AMP, "s2ns-pcm-001"),),
    ((F1, ((9, 40), (3, 40), (3, 80)), "s2ns-pcm-001"),),
    (((279130, 1116520, 6978250), AMP, "s2ns-pcm-001"),),
    ((F1, ((6, 20), (2, 20), (0, 1)), "s2ns-pcm-001"),
     (F2, ((0, 1), (0, 1), (1, 20)), "s2ns-pcm-002")),
    (((593000, 2372000, 8302000), AMP, "s2ns-pcm-003"),))


class S2NSBindingError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NSBindingError(code)


def watched():
    require(all(filehash(ROOT / p) == h for p, h in PINS.items()), "PIN_CHANGED")
    return {p: filehash(ROOT / p) for p in sorted(set(PINS) | set(OWN) | set(common.CODE))}


def source_specs():
    result = []
    for i, groups in enumerate(AUDIO, 1):
        recipe = dict(sample_count=4800, sample_rate=48000, groups=[dict(seed=seed, partials=[
            dict(frequency_millihz=f, amplitude_ratio=list(a)) for f, a in zip(freq, amps, strict=True)])
            for freq, amps, seed in groups])
        result.append(SourceSpec(f"ns-a{i:02d}", "PCM", canonical(recipe).decode()))
    for i in range(1, 12):
        recipe = dict(algorithm="NH_SHA_GRID_RGB8_V1", seed=f"s2ns-independent-av-20260908-v1:visual:v{i:02d}",
            width=1920, height=1080, rows=8, columns=12, channels=3, format="RGB8",
            partial=False, visible_positions=None)
        result.append(SourceSpec(f"ns-v{i:02d}", "RGB", canonical(recipe).decode()))
    return tuple(result)


def events():
    result = []
    for n, (history, kind, a, v) in enumerate(ROWS, 1):
        end = n * 100000000
        audio = dict(source_id=f"ns-a{a:02d}", clock_id="audio.sample", start_tick=(n-1)*4800,
            end_tick=n*4800, endpoint_snapshot_index=n-1, common_window=[end-10000000, end])
        visual = None if v is None else dict(source_id=f"ns-v{v:02d}", clock_id="video.frame",
            start_tick=3*n-1, end_tick=3*n, common_window=[(3*n-1)*1000000000//30, end])
        result.append(dict(event_id=f"e{n:02d}", ordinal=n, history_id=history,
            starts_fresh_history=n in (1, 8, 14), event_type=kind,
            source_occurrence_id=f"s2ns-source-e{n:02d}", pairing_clock_id="s2ns-pairing-clock",
            auditory=audio, visual=visual))
    return result


def bind_source(spec, sha):
    require(type(spec) is SourceSpec and spec in source_specs(), "SOURCE_SPEC_INVALID")
    require(type(sha) is str and re.fullmatch(r"[0-9a-f]{64}", sha), "PAYLOAD_DIGEST_INVALID")
    occurrences = [dict(event_id=e["event_id"], ordinal=e["ordinal"], history_id=e["history_id"], **part)
        for e in events() for part in (e["auditory"], e["visual"])
        if part is not None and part["source_id"] == spec.source_id]
    return sealed({**spec.payload(), "payload_sha256": sha, "occurrences": occurrences}, "source_digest")


def budgets():
    return dict(pcm_sources=7, rgb_sources=11, events=31, histories=3, formations=16, auditory_cues=15,
        generated_pcm_bytes=134400, generated_rgb_bytes=68428800, max_live_pcm_payloads=1,
        max_live_rgb_payloads=1, max_pcm_bytes=19200, max_rgb_bytes=6220800,
        metadata_bytes=MAX_METADATA_BYTES, output_bytes=MAX_OUTPUT_BYTES,
        future_audio_analyses=31, future_nj=31, future_visual_analyses=16,
        future_scans=60, future_slot_rows=1200, future_band_differences=28800,
        future_decisions=90, future_equality_comparisons=4320,
        offline_scans=60, offline_slot_rows=1200, offline_band_differences=28800,
        offline_equality_comparisons=4320, formation_l1_terms=71040, offline_formations=16,
        max_state_bytes=98304, max_scan_bytes=32768, max_states=17)


def execution_plan(sources, env, hashes, gen):
    require(type(sources) is list and len(sources) == 18, "SOURCE_COUNT_INVALID")
    for spec, row in zip(source_specs(), sources, strict=True):
        require(type(row) is dict and row == bind_source(spec, row.get("payload_sha256")), "SOURCE_BINDING_INVALID")
    result = sealed(dict(schema="s2ns.source-execution-plan.v1", contract_sha256=PINS[CONTRACT],
        sources=sources, source_order=[s.source_id for s in source_specs()], events=events(),
        profiles=profiles(), views=[dict(view_id=name, indices=list(indices),
            complement=[i for i in range(48) if i not in indices]) for name, indices in VIEWS],
        comparison=dict(arms=["LOWER_24", "UPPER_24", "SAME_GENERATION_CONJUNCTION"],
            a_arithmetic="max", a_threshold=0.1, slow_arithmetic="historical sum in original index order / 24",
            slow_threshold=0.01, join="same history/profile/state/bank/slot/generation/current-slot-values",
            confirmation="both per-slot matches before public resolution", missing_view="ABSTAIN_INSUFFICIENT_EVIDENCE",
            full_mean_replacement=False, imputation=False),
        environment=env, generators=gen, source_hashes=hashes, budgets=budgets(),
        receptor_execution_authorized=False, nj_execution_authorized=False,
        comparison_execution_authorized=False, system_execution_authorized=False), "execution_digest")
    require(len(canonical(result)) <= MAX_METADATA_BYTES, "METADATA_SIZE_EXCEEDED")
    return result


def evaluation_plan(execution):
    cases = []
    for e in events():
        if e["event_type"] != A:
            continue
        cue = e["auditory"]["source_id"]
        subtype = {"ns-a03": "EXACT", "ns-a04": "LEVEL", "ns-a05": "FREQUENCY",
            "ns-a06": "MIXED_CONTROL", "ns-a07": "INDEPENDENT_CONTROL"}[cue]
        known = cue in ("ns-a03", "ns-a04", "ns-a05")
        prediction = "ABSTAIN" if not known or e["history_id"] == "h02" else (
            "A_RECENT" if e["history_id"] == "h01" else "B_STABLE_AUDITORY")
        cases.append(dict(event_id=e["event_id"], history_id=e["history_id"], cue_id=cue,
            target="ns-a01" if known else None, subtype=subtype, prediction=prediction))
    return sealed(dict(schema="s2ns.evaluation-plan.v1", execution_digest=execution["execution_digest"],
        contract_sha256=PINS[CONTRACT], target_source="ns-a01", competition_source="ns-a02", cases=cases,
        retention_identity="D=R+L", zero_denominator="ERHALTUNG_NICHT_GEPRUEFT",
        reference_arms_separate=True, relationship_and_public_denominators_separate=True,
        a_and_b_retention_separate=True, receptor_variation_reference="prior source-bound formation values on identical indices",
        missing_reference=None, slot_deviation_separate=True, offset_losses_with_gains=False,
        no_success_start_gate=True, no_replacement_source=True, mixed_disagreement_not_guaranteed=True,
        benefit_requires="gain or prevented false admission, no new false admission or relationship/public loss, positive varied D"),
        "evaluation_digest")


def preseal_once(run_id):
    require(type(run_id) is str and re.fullmatch(r"s2ns-source-preseal-\d{8}-\d{2}", run_id), "RUN_ID_INVALID")
    out = ROOT / "reports/s2ns" / run_id
    out.mkdir(exist_ok=False)
    before, rows, attempted = {}, [], 0
    phase, sid = "QUALIFICATION_BINDING", None
    try:
        q = json.loads((QUAL_DIR / "result.json").read_bytes())
        require(q["result_digest"] == digest({k:v for k,v in q.items() if k != "result_digest"})
            and q["status"] == "S2NS_SOURCE_BINDING_QUALIFIED" and q["passed_tests"] == 14
            and q["unittest_calls"] == 1 and q["exit_code"] == 0, "QUALIFICATION_REQUIRED")
        before = watched()
        require(before == q["hashes_before"] == q["hashes_after"] and MAIN_GATE is False, "QUALIFIED_SOURCES_CHANGED")
        phase = "ENVIRONMENT_BINDING"
        env = environment()
        pcm, rgb, gen = generators()
        publish(out / "preregistration.json", dict(run_id=run_id, hashes=before, environment=env, generators=gen,
            specs=[s.payload() for s in source_specs()], events=events(), profiles=profiles(), budgets=budgets(),
            qualification_sha256=filehash(QUAL_DIR / "result.json"), retry=False), MAX_METADATA_BYTES)
        for spec in source_specs():
            phase, sid = "PAYLOAD_GENERATION", spec.source_id
            attempted += 1
            payload = (pcm if spec.kind == "PCM" else rgb)(spec.recipe())
            try:
                phase = "PAYLOAD_BINDING"
                require((type(payload) is bytearray and len(payload) == 19200) if spec.kind == "PCM" else
                    (type(payload) is common.np.ndarray and payload.shape == (1080, 1920, 3)
                     and payload.dtype == common.np.uint8 and payload.flags.c_contiguous
                     and not payload.flags.writeable), "PAYLOAD_FORM_INVALID")
                view = memoryview(payload).cast("B")
                try:
                    require(view.nbytes == spec.payload()["byte_count"], "PAYLOAD_SIZE_INVALID")
                    sha = hashlib.sha256(view).hexdigest()
                finally:
                    view.release()
                    del view
            finally:
                del payload
            rows.append(bind_source(spec, sha))
        phase, sid = "PLAN_BINDING", None
        require(rows[0]["payload_sha256"] == rows[2]["payload_sha256"]
            and rows[0]["source_digest"] != rows[2]["source_digest"], "EXACT_COPY_DIFFERS")
        execution = execution_plan(rows, env, before, gen)
        evaluation = evaluation_plan(execution)
        after = watched()
        require(before == after and env == environment(), "BINDINGS_CHANGED")
        phase = "PUBLICATION"
        a = publish(out / "execution-plan.json", execution, MAX_METADATA_BYTES)
        b = publish(out / "evaluation-plan.json", evaluation, MAX_METADATA_BYTES)
        seal = sealed(dict(schema="s2ns.source-seal.v1", run_id=run_id, status="S2NS_SOURCES_PRESEALED",
            execution_digest=execution["execution_digest"], evaluation_digest=evaluation["evaluation_digest"],
            execution_file_sha256=a, evaluation_file_sha256=b, hashes_before=before, hashes_after=after,
            attempted_sources=attempted, completed_sources=len(rows), generated_pcm_sources=7, generated_rgb_sources=11,
            generated_pcm_bytes=134400, generated_rgb_bytes=68428800, max_live_pcm_payloads=1, max_live_rgb_payloads=1,
            raw_payloads_persisted=0, receptor_calls=0, nj_calls=0, distance_calls=0, memory_calls=0, context_calls=0,
            field_calls=0, runtime_calls=0, main_gate_after=MAIN_GATE,
            exact_pairs=[["ns-a01", "ns-a03"]], collisions=common.collisions(rows)), "seal_digest")
        publish(out / "seal.json", seal, MAX_METADATA_BYTES)
    except Exception as exc:
        publish(out / "failure.json", sealed(dict(run_id=run_id, status="NOT_EVALUABLE", phase=phase, source_id=sid,
            attempted_sources=attempted, completed_sources=len(rows), error_class=type(exc).__name__,
            code=exc.code if isinstance(exc, S2NSBindingError) else "TECHNICAL_EXECUTION_ERROR",
            hashes_before=before, main_gate_after=MAIN_GATE, retry=False), "failure_digest"), MAX_METADATA_BYTES)
    return out
