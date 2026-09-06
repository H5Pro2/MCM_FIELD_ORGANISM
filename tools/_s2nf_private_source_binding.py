"""S2-NF source-only binding. No receptor, memory, field or rule imports."""

import ast
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys

from reports.s2nd import seal_inventory as harmonic

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "docs/S2NF_PROSPEKTIVER_ERHALTUNGS_UND_VERLUSTPLAN_UNTER_KONKURRENZ.md"
CONTRACT_HASH = "d652db5fb9b0ad07ae09ae572235d563d38a37caa99184ee0c4ed05b31f0e16b"
ND_PLAN = "reports/s2nd/s2nd-source-panel-preseal-20260906-02/execution-plan.json"
LB_PLAN = "docs/S2LB_D_FAR_PCM_MATERIALISIERUNGSPLAN.json"
LB_CODE = "tools/_s2lb_d_far_pcm_materialization.py"
LB_RESULT = "reports/s2kx/s2lb-d-far-pcm-materialization-20260904-01/materialization.json"
QUAL_DIR = "reports/s2nf/s2nf-source-binding-qualification-20260906-01"
PROFILE = (("sample_rate", 48000), ("window_size", 4800), ("hop_size", 480),
           ("min_frequency", 50.0), ("max_frequency", 18000.0), ("band_count", 48))
EVENT_ROWS = (
    (1, "nf-a01", "nf-v01"), (1, "nf-a02", "nf-v02"),
    (1, "nf-a03", None), (1, "nf-a04", None), (1, "nf-a05", None),
    (1, "nf-a06", None), (1, "nf-a07", None),
    (2, "nf-a02", "nf-v02"), (2, "nf-a03", None), (2, "nf-a04", None),
    (2, "nf-a05", None), (2, "nf-a06", None), (2, "nf-a07", None),
)
MAX_BYTES = 4194304
canonical, digest, filehash = harmonic.canonical, harmonic.digest, harmonic.filehash


def require(ok, code):
    if not ok:
        raise ValueError(code)


def sealed(value, key):
    return {**value, key: digest(value)}


def historical_bindings():
    require(filehash(ROOT / CONTRACT) == CONTRACT_HASH, "CONTRACT_CHANGED")
    text = (ROOT / CONTRACT).read_text(encoding="utf-8")
    pins = dict(re.findall(r"\| ([^|\n]+?) \| ([0-9a-f]{64}) \|", text))
    require(len(pins) == 9, "HISTORICAL_INVENTORY_INVALID")
    require(all(filehash(ROOT / p) == h for p, h in pins.items()), "HISTORICAL_SOURCE_CHANGED")
    old = json.loads((ROOT / "reports/s2ne/s2ne-run-completion-qualification-20260906-01/result.json").read_bytes())
    require(all(filehash(ROOT / p) == h for p, h in old["hashes_after"].items()), "QUALIFIED_SOURCE_CHANGED")
    return {**pins, **old["hashes_after"], CONTRACT: CONTRACT_HASH}


def watched():
    paths = set(historical_bindings()) | {
        "tools/_s2nf_private_source_binding.py", "tools/_s2nf_private_preseal_verification.py",
        "tests/test_s2nf_private_source_binding.py", "reports/s2nf/qualify_once.py",
        "reports/s2nf/preseal_once.py"}
    return {p: filehash(ROOT / p) for p in sorted(paths)}


@dataclass(frozen=True, slots=True)
class SourceSpec:
    source_id: str
    ordinal: int
    kind: str
    recipe_json: str
    historical_pcm_sha256: str | None

    def __post_init__(self):
        require(type(self.ordinal) is int and 1 <= self.ordinal <= 7
                and self.source_id == f"nf-a{self.ordinal:02d}", "SOURCE_ID_INVALID")
        require(self.kind in ("HARMONIC", "SQUARE_CHIRP"), "SOURCE_KIND_INVALID")
        require(type(self.recipe_json) is str
                and canonical(json.loads(self.recipe_json)).decode("ascii") == self.recipe_json, "RECIPE_FORM_INVALID")
        require(self.historical_pcm_sha256 is None or re.fullmatch(r"[0-9a-f]{64}", self.historical_pcm_sha256),
                "PAYLOAD_DIGEST_INVALID")

    def payload(self):
        return dict(source_id=self.source_id, ordinal=self.ordinal, kind=self.kind,
                    recipe=json.loads(self.recipe_json), recipe_digest=digest(json.loads(self.recipe_json)),
                    format="PCM_F32LE", channels=1, sample_rate=48000, sample_count=4800,
                    clock_id="s2nf-source-sample-clock", window_start_sample=(self.ordinal - 1) * 4800,
                    window_end_sample=self.ordinal * 4800, historical_pcm_sha256=self.historical_pcm_sha256)


def source_specs():
    historical_bindings()
    nd = json.loads((ROOT / ND_PLAN).read_bytes())
    source_map = {s["source_id"]: s for s in nd["sources"]}
    lb = json.loads((ROOT / LB_PLAN).read_bytes())["recipe"]
    specs = []
    for ordinal, parent in enumerate(("s001", None, "s007", "s008", "s009", "s010", "s001"), 1):
        if parent is None:
            recipe, kind = lb, "SQUARE_CHIRP"
            old_hash = "97a11dfcb89615b257d430ab718505b2ec207b8b8684c012ec5bdc6adcea4f5b"
        else:
            s = source_map[parent]
            recipe = {k: s[k] for k in ("algorithm", "seed", "partials")}
            old_hash, kind = s["pcm_sha256"], "HARMONIC"
            if ordinal == 7:
                recipe = {**recipe, "partials": recipe["partials"] + [
                    dict(frequency_millihz=120000, amplitude_ratio=[3, 10])]}
                old_hash = None
        specs.append(SourceSpec(f"nf-a{ordinal:02d}", ordinal, kind, canonical(recipe).decode("ascii"), old_hash))
    return tuple(specs)


def validate_specs(specs):
    require(type(specs) is tuple and specs == source_specs(), "SOURCE_PLAN_CHANGED")
    return specs


def events():
    counts, result = {}, []
    for history, audio, visual in EVENT_ROWS:
        j = counts.get(history, 0)
        h = f"s2nf-h{history:02d}"
        result.append(dict(event_id=f"{h}-e{j + 1:02d}", history_id=h, ordinal=j,
            kind="FORMATION" if visual else "PARTIAL_AUDITORY_CUE", audio_source_id=audio, visual_source_id=visual,
            audio_clock_id=h + "-audio-sample", audio_start_tick=9600 * j, audio_end_tick=9600 * j + 4800,
            visual_clock_id=None if visual is None else "video.frame",
            visual_start_tick=None if visual is None else 6 * j + 2,
            visual_end_tick=None if visual is None else 6 * j + 3,
            pair_clock_id=None if visual is None else h + "-pair-clock",
            audio_common_window=None if visual is None else [200000000 * j, 200000000 * j + 100000000],
            visual_common_window=None if visual is None else [(6 * j + 2) * 1000000000 // 30, 200000000 * j + 100000000]))
        counts[history] = j + 1
    return result


def visual_bindings():
    path = ROOT / "tools/_s2jx_default_live_memory_fixtures.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "_ROWS" for t in n.targets)]
    require(len(nodes) == 1, "VISUAL_LITERAL_INVALID")
    rows = ast.literal_eval(nodes[0].value)
    return [dict(source_id=sid, ordinal=o, pcm_or_pixel_generation_performed=False,
                 format="RGB8", width=1920, height=1080, columns=12, rows=8, channels=3,
                 payload_sha256=rows[o][3], receptor_values_digest=rows[o][5],
                 generator_file_sha256=filehash(path)) for sid, o in (("nf-v01", 0), ("nf-v02", 2))]


def chirp_functions():
    """Select unchanged pure definitions, never import the receptor-bearing module."""
    historical_bindings()
    names = ("S2LBMaterializationError", "_f32", "_materialize_pcm")
    tree = ast.parse((ROOT / LB_CODE).read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names]
    require(tuple(n.name for n in nodes) == names, "PURE_GENERATOR_SELECTION_INVALID")
    namespace = {"math": math, "struct": struct, "Any": object}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(ROOT / LB_CODE), "exec"), namespace)
    return namespace["_materialize_pcm"], dict(path=LB_CODE, file_sha256=filehash(ROOT / LB_CODE),
        selected_definitions=list(names), definitions_digest=digest([ast.dump(n, include_attributes=False) for n in nodes]),
        module_entry_executed=False, function_bodies_modified=False)


def identity():
    _, chirp = chirp_functions()
    return dict(python_version=sys.version, python_executable=sys.executable,
        python_executable_sha256=filehash(Path(sys.executable)), implementation=sys.implementation.name,
        pointer_bits=struct.calcsize("P") * 8, math_module=harmonic.math_identity(math, sys.builtin_module_names),
        harmonic_generator=dict(path="reports/s2nd/seal_inventory.py", function="pcm_payload",
            sha256=filehash(ROOT / "reports/s2nd/seal_inventory.py"), entry_executed=False),
        chirp_generator=chirp, binding_sha256=filehash(Path(__file__)))


def generate_digest(spec):
    """One complete source at a time; the chirp has only scalar packed fragments."""
    if spec.kind == "HARMONIC":
        payload = harmonic.pcm_payload(json.loads(spec.recipe_json))
        try:
            require(len(payload) == 19200, "PCM_SIZE_INVALID")
            return hashlib.sha256(payload).hexdigest()
        finally:
            del payload
    function, _ = chirp_functions()
    samples = function({"recipe": json.loads(spec.recipe_json)})
    try:
        require(len(samples) == 4800, "PCM_SIZE_INVALID")
        sha = hashlib.sha256()
        for value in samples:
            require(type(value) is float and math.isfinite(value) and -1.0 <= value <= 1.0, "PCM_VALUE_INVALID")
            sha.update(struct.pack("<f", value))
        return sha.hexdigest()
    finally:
        del samples


def bind_payload(spec, pcm_sha256, byte_count=19200):
    require(type(spec) is SourceSpec and type(byte_count) is int and byte_count == 19200, "PAYLOAD_BINDING_INVALID")
    require(type(pcm_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", pcm_sha256), "PAYLOAD_DIGEST_INVALID")
    require(spec.historical_pcm_sha256 is None or spec.historical_pcm_sha256 == pcm_sha256, "HISTORICAL_PAYLOAD_DIFFERS")
    return sealed({**spec.payload(), "pcm_sha256": pcm_sha256, "pcm_byte_count": byte_count}, "source_digest")


def execution_plan(sources, generator_identity, hashes):
    return sealed(dict(schema="s2nf.source-execution-plan.v1", contract_sha256=CONTRACT_HASH,
        sources=sources, visual_sources=visual_bindings(), events=events(), generator_identity=generator_identity,
        source_hashes=hashes, receptor_profile=dict(PROFILE), receptor_profile_digest=digest(dict(PROFILE)),
        observed_bands=list(range(24)), unobserved_bands=list(range(24, 48)),
        rules=[dict(id="HISTORICAL_SUM_L1_24", arithmetic="sum_in_band_order/24", threshold=0.2),
               dict(id="ALL_BANDS_24", arithmetic="max", threshold=0.2)],
        slow_rule=dict(arithmetic="sum_in_band_order/24", threshold=0.02),
        budgets=dict(source_windows=7, source_samples=33600, source_pcm_bytes=134400,
            max_live_payloads=1, max_live_canonical_pcm_bytes=19200, formations=3, cues=10, events=13,
            future_audio_analyses=13, future_visual_analyses=3, future_receptor_values=1488,
            cases_per_rule=10, arm_records=40, slot_visits=800, expected_eligible_relationships=120,
            expected_band_differences=2880, max_band_differences=19200, max_equality_comparisons=1920,
            max_retrieval_comparisons=21120, max_verification_comparisons=21120,
            logical_retrieval_operations=560, max_live_rgb_bytes=6220800,
            formation_l1_limit=10656, max_state_bytes=44544, arm_bytes_exclusive=32768, max_output_bytes=MAX_BYTES),
        receptor_execution_authorized=False, memory_execution_authorized=False, rule_execution_authorized=False), "execution_digest")


def evaluation_plan(execution):
    cases = []
    subtypes = ("EXACT", "UNIFORM_GAIN", "FREQUENCY", "SPECTRAL_REWEIGHT", "LOCAL_PARTIAL_ADDITION")
    for event in execution["events"]:
        if event["kind"] == "FORMATION":
            continue
        present = event["history_id"] == "s2nf-h01"
        cases.append(dict(case_id=f"c{len(cases) + 1:02d}", event_id=event["event_id"],
            source_id=event["audio_source_id"], related_source_id="nf-a01", competitor_source_id="nf-a02",
            target_present=present, expected="UNIQUE_CORRECT_A" if present else "ABSTAIN",
            subtype=subtypes[int(event["audio_source_id"][-2:]) - 3], retention_eligible=present))
    return sealed(dict(schema="s2nf.retention-evaluation-plan.v1", execution_digest=execution["execution_digest"],
        contract_sha256=CONTRACT_HASH, cases=cases, positive_cases=5, removal_controls=5,
        exact_positive=1, variant_positive=4, retention_identity="D=R+L",
        zero_denominator="ERHALTUNG_NICHT_GEPRUEFT", offset_losses_with_gains=False,
        variation_axes=["pcm_bits", "receptor_48_bits", "observed_24_bits"]), "evaluation_digest")


def publish(path, value):
    data = canonical(value)
    require(len(data) <= MAX_BYTES, "OUTPUT_SIZE_EXCEEDED")
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    return hashlib.sha256(data).hexdigest()


def preseal_once(run_id, output_root):
    require(re.fullmatch(r"s2nf-source-preseal-[0-9]{8}-[0-9]{2}", run_id), "RUN_ID_INVALID")
    require(Path(output_root).resolve(strict=True) == (ROOT / "reports/s2nf").resolve(), "OUTPUT_ROOT_INVALID")
    out = Path(output_root).resolve(strict=True) / run_id
    out.mkdir(exist_ok=False)
    phase, sid, attempted, sources, before = "QUALIFICATION", None, 0, [], {}
    try:
        q = json.loads((ROOT / QUAL_DIR / "result.json").read_bytes())
        require(q["status"] == "S2NF_SOURCE_BINDING_QUALIFIED" and q["exit_code"] == 0
                and q["unittest_calls"] == 1, "QUALIFICATION_REQUIRED")
        require(all(filehash(ROOT / p) == h for p, h in q["hashes_after"].items()), "QUALIFIED_SOURCES_CHANGED")
        phase = "SOURCE_BINDINGS"
        before = watched()
        specs = validate_specs(source_specs())
        generator_identity = identity()
        publish(out / "preregistration.json", dict(run_id=run_id, source_hashes=before,
            source_specs=[s.payload() for s in specs], generator_identity=generator_identity,
            contract_sha256=CONTRACT_HASH, qualification_sha256=filehash(ROOT / QUAL_DIR / "result.json"),
            generation_calls_limit=7, preseal_calls_limit=1, retry=False, receptor_calls=0))
        for spec in specs:
            phase, sid = "PCM_GENERATION", spec.source_id
            attempted += 1
            pcm_sha = generate_digest(spec)
            phase = "PAYLOAD_BINDING"
            sources.append(bind_payload(spec, pcm_sha))
        phase, sid = "PLAN_BINDING", None
        require(sources[0]["pcm_sha256"] == sources[2]["pcm_sha256"], "EXACT_COPY_DIFFERS")
        after = watched()
        require(before == after, "SOURCES_CHANGED")
        execution = execution_plan(sources, generator_identity, before)
        evaluation = evaluation_plan(execution)
        phase = "PUBLICATION"
        a = publish(out / "execution-plan.json", execution)
        b = publish(out / "evaluation-plan.json", evaluation)
        seal = sealed(dict(schema="s2nf.source-seal.v1", run_id=run_id, status="S2NF_SOURCES_PRESEALED",
            execution_digest=execution["execution_digest"], evaluation_digest=evaluation["evaluation_digest"],
            execution_file_sha256=a, evaluation_file_sha256=b, source_hashes_before=before, source_hashes_after=after,
            completed_sources=len(sources), attempted_sources=attempted, generated_pcm_bytes=134400,
            generated_samples=33600, max_live_payloads=1, max_live_canonical_pcm_bytes=19200,
            raw_payloads_persisted=0, receptor_calls=0, distance_calls=0, rule_calls=0,
            memory_calls=0, context_calls=0, field_calls=0, runtime_calls=0,
            exact_pair=["nf-a01", "nf-a03"], exact_payload_sha256=sources[0]["pcm_sha256"]), "seal_digest")
        publish(out / "seal.json", seal)
        return out
    except Exception as error:
        publish(out / "failure.json", dict(run_id=run_id, status="NOT_EVALUABLE", phase=phase,
            source_id=sid, attempted_sources=attempted, completed_sources=len(sources),
            error_class=type(error).__name__, code=str(error) if type(error) is ValueError else "SOURCE_BINDING_OR_EXECUTION_ERROR",
            source_hashes_before=before))
        return out


__all__ = ()
