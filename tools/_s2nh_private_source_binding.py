"""S2-NH source-only binding; no perception or memory execution imports."""

import ast
from dataclasses import dataclass, asdict
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys

import numpy as np
from reports.s2nd import seal_inventory as utility
from tools import _s2mt_private_presealed_transfer_sources as pure

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "docs/S2NH_UNABHAENGIGER_AV_RUNTIME_TRANSFERPLAN.md"
MASTER = "s2nh-independent-av-20260906-v1"
QUAL_ID = "s2nh-source-binding-qualification-20260906-01"
RUN_ID = "s2nh-source-preseal-20260906-01"
MAIN_GATE = False
MAX_BYTES = 4_194_304
canonical, digest, filehash, f32 = utility.canonical, utility.digest, utility.filehash, pure._f32
AV, A, V = "COMPLETE_AV_PERCEPTION", "PARTIAL_AUDITORY_CUE", "PARTIAL_VISUAL_CUE"
ROWS = ((AV,"p00"),(AV,"p01"),(A,"p00"),(V,"p00"),
        (AV,"p02"),(AV,"p00"),(AV,"p01"),(AV,"p02"),(AV,"p00"),(AV,"p01"),
        (AV,"p02"),(AV,"p00"),(AV,"p01"),(AV,"p03"),(AV,"p04"),(AV,"p05"),
        (AV,"p06"),(AV,"p07"),(AV,"p08"),(AV,"p09"),(AV,"p10"),(AV,"p11"),
        (A,"p13"),(V,"p13"),(A,"p14"),(V,"p14"),(A,"p12"),(V,"p12"))
QUAL_REFERENCE = "reports/s2ng/s2ng-private-runtime-composition-qualification-20260906-02/result.json"
NG_RECORD = "reports/s2ng/s2ng-real-runtime-comparison-20260906-01/recording.json"
OWN = (CONTRACT, ".gitattributes", "tools/_s2nh_private_source_binding.py",
       "tools/_s2nh_private_preseal_verification.py", "tests/test_s2nh_private_source_binding.py",
       "reports/s2nh/qualify_once.py", "reports/s2nh/preseal_once.py",
       "reports/s2nd/seal_inventory.py", "tools/_s2mt_private_presealed_transfer_sources.py",
       QUAL_REFERENCE, NG_RECORD)


class S2NHError(ValueError):
    pass


def require(ok, code):
    if not ok:
        raise S2NHError(code)


def sealed(value, key):
    return {**value, key: digest(value)}


def watched():
    old = json.loads((ROOT / QUAL_REFERENCE).read_bytes())
    pins = old["hashes_after"]
    require(old["status"] == "S2NG_COMPOSITION_QUALIFIED"
            and all(filehash(ROOT / p) == h for p,h in pins.items()), "HISTORICAL_BINDING_CHANGED")
    return {p: filehash(ROOT / p) for p in sorted(set(pins) | set(OWN))}


@dataclass(frozen=True, slots=True)
class SourceSpec:
    source_id: str
    kind: str
    recipe_json: str

    def __post_init__(self):
        require(type(self.source_id) is str and re.fullmatch(r"[a-z][a-z0-9-]{1,95}", self.source_id), "SOURCE_ID_INVALID")
        require(self.kind in ("PCM", "RGB", "RGB_CUE"), "SOURCE_KIND_INVALID")
        require(type(self.recipe_json) is str and canonical(json.loads(self.recipe_json)).decode("ascii") == self.recipe_json,
                "RECIPE_FORM_INVALID")

    def payload(self):
        return dict(source_id=self.source_id, kind=self.kind, recipe=json.loads(self.recipe_json),
                    recipe_digest=digest(json.loads(self.recipe_json)))


def audio_recipe(master, index):
    require(type(master) is str and master.isascii() and type(index) is int and 0 <= index < 15, "RECIPE_ID_INVALID")
    parent = 0 if index == 13 else 1 if index == 14 else index
    word = hashlib.sha256(f"{master}:audio:p{parent:02d}".encode("ascii")).digest()
    frequency = 60 + int.from_bytes(word[:4], "big") % 2741
    phase = (2.0 * math.pi * int.from_bytes(word[4:8], "big")) / 2**32
    return dict(algorithm="NH_SINE_F32_V1", seed=f"{master}:audio:p{parent:02d}",
                frequency_hz=frequency + (7 if index == 14 else 0), phase=phase,
                amplitude=f32(0.8500000238418579), input_scale=f32(0.989912331104279),
                post_gain=f32(0.9) if index == 13 else None,
                sample_rate=48000, sample_count=4800, format="PCM_F32LE", channels=1)


def rgb_recipe(seed, partial):
    return dict(algorithm="NH_SHA_GRID_RGB8_V1", seed=seed, width=1920, height=1080,
                rows=8, columns=12, channels=3, format="RGB8", partial=partial,
                visible_positions=list(range(32)) if partial else None)


def source_specs():
    result = [SourceSpec(f"nh-a{i:02d}", "PCM", canonical(audio_recipe(MASTER, i)).decode("ascii")) for i in range(15)]
    result += [SourceSpec(f"nh-v{i:02d}", "RGB", canonical(rgb_recipe(f"{MASTER}:visual:p{i:02d}", False)).decode("ascii")) for i in range(13)]
    for ordinal, parent in ((4,0),(24,0),(26,1),(28,12)):
        result.append(SourceSpec(f"nh-vcue-e{ordinal:02d}", "RGB_CUE",
                                 canonical(rgb_recipe(f"{MASTER}:visual:p{parent:02d}", True)).decode("ascii")))
    return tuple(result)


def pcm_payload(recipe):
    require(recipe["algorithm"] == "NH_SINE_F32_V1" and recipe["sample_rate"] == 48000
            and recipe["sample_count"] == 4800 and recipe["format"] == "PCM_F32LE" and recipe["channels"] == 1,
            "PCM_FORM_INVALID")
    require(all(type(recipe[k]) in (int, float) and math.isfinite(recipe[k]) for k in
                ("frequency_hz", "phase", "amplitude", "input_scale"))
            and (recipe["post_gain"] is None or type(recipe["post_gain"]) is float and math.isfinite(recipe["post_gain"])), "PCM_PARAMETERS_INVALID")
    payload = bytearray(19200)
    for j in range(4800):
        theta = ((2.0 * math.pi * recipe["frequency_hz"] * j) / 48000) + recipe["phase"]
        value = f32(f32(recipe["amplitude"] * math.sin(theta)) * recipe["input_scale"])
        if recipe["post_gain"] is not None:
            value = f32(value * recipe["post_gain"])
        require(math.isfinite(value) and -1 <= value <= 1, "PCM_NORMALFORM_INVALID")
        struct.pack_into("<f", payload, 4*j, value)
    return payload


def rgb_payload(recipe):
    require(recipe == rgb_recipe(recipe["seed"], recipe["partial"])
            and type(recipe["partial"]) is bool, "RGB_FORM_INVALID")
    bits, block = [], 0
    while len(bits) < 288:
        word = hashlib.sha256(f"{recipe['seed']}:{block:03d}".encode("ascii")).digest()
        for byte in word:
            bits.extend(255 if byte & (1 << shift) else 0 for shift in range(8))
        block += 1
    grid = np.asarray(bits[:288], dtype=np.uint8).reshape(8,12,3)
    if recipe["partial"]:
        grid.reshape(-1)[32:] = 0
    # Broadcast directly into one full frame; no full-frame expansion intermediates.
    frame = np.empty((1080,1920,3), dtype=np.uint8)
    frame.reshape(8,135,12,160,3)[:] = grid[:,None,:,None,:]
    frame.setflags(write=False)
    return frame


def bind_source(spec, sha, byte_count):
    require(type(spec) is SourceSpec and type(sha) is str and re.fullmatch(r"[0-9a-f]{64}", sha), "PAYLOAD_ID_INVALID")
    require(type(byte_count) is int and byte_count == (19200 if spec.kind == "PCM" else 6220800), "PAYLOAD_SIZE_INVALID")
    return sealed({**spec.payload(), "payload_sha256":sha, "byte_count":byte_count}, "source_digest")


def events():
    result, audio_count = [], 0
    for k, (kind, recipe) in enumerate(ROWS, 1):
        end, audio, visual = k*100000000, None, None
        if kind != V:
            audio = dict(source_id=f"nh-a{int(recipe[1:]):02d}", clock_id="audio.sample",
                start_tick=audio_count*4800, end_tick=(audio_count+1)*4800,
                hop_start=audio_count*10, hop_end=(audio_count+1)*10,
                endpoint_snapshot_index=audio_count*10, common_window=[end-10000000,end])
            audio_count += 1
        if kind != A:
            frame = (k-1)*3+2
            visual = dict(source_id=f"nh-vcue-e{k:02d}" if kind == V else f"nh-v{int(recipe[1:]):02d}",
                clock_id="video.frame", start_tick=frame, end_tick=frame+1,
                common_window=[frame*1000000000//30,end])
        result.append(dict(event_id=f"e{k:02d}", ordinal=k, event_type=kind, recipe_id=recipe,
            source_occurrence_id=f"s2nh-source-e{k:02d}", field_clock_id="s2nh-transfer-field-clock",
            common_end_tick=end, auditory=audio, visual=visual))
    return result


def profile_binding():
    path = ROOT / "tools/_s2jw_default_live_profile.py"
    constants = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id.startswith("EXPECTED_"):
                constants[node.targets[0].id] = ast.literal_eval(node.value)
    record = json.loads((ROOT / NG_RECORD).read_bytes())
    require(filehash(ROOT / NG_RECORD) == "927013f5fd313d3e319d376561be18ba5aa04cadef66af17c7bf1000f0c1acb1", "PROFILE_REFERENCE_CHANGED")
    return dict(profile_id="default-live", auditory=dict(utility.PROFILE),
        visual=dict(source_width=1920,source_height=1080,grid_columns=12,grid_rows=8,frames_per_second=30.0,
                    carrier_order="grid_row-grid_column-rgb_channel"),
        existing_digest_constants=constants, coordinator_config_digest=record["comparison"]["config_digest"],
        configuration_reference_file=NG_RECORD, configuration_reference_sha256=filehash(ROOT / NG_RECORD),
        derivation="READ_ONLY_LITERAL_CONSTANTS_AND_EXISTING_CONFIG_BINDING")


def identity():
    return dict(python_version=sys.version, python_build=list(__import__('platform').python_build()),
        executable=sys.executable, executable_sha256=filehash(Path(sys.executable)),
        implementation=sys.implementation.name, pointer_bits=struct.calcsize("P")*8,
        math=utility.math_identity(math, sys.builtin_module_names), numpy_version=np.__version__,
        numpy_binary=dict(path=np._core._multiarray_umath.__file__, sha256=filehash(Path(np._core._multiarray_umath.__file__))),
        f32_generator=dict(path="tools/_s2mt_private_presealed_transfer_sources.py", function="_f32", entry_called=False),
        identity_helper=dict(path="reports/s2nd/seal_inventory.py", function="math_identity", entry_called=False))


def budgets():
    return dict(pcm_recipes=15, full_rgb=13, visual_cues=4, events=28,
        generated_samples=72000, generated_pcm_bytes=288000, generated_rgb_bytes=105753600,
        max_live_pcm_payloads=1, max_live_rgb_payloads=1, max_pcm_bytes=19200, max_rgb_bytes=6220800,
        max_output_bytes=MAX_BYTES, runtime_events_per_arm=28, formations_per_arm=20,
        field_contacts_total=16128, scan_receipts=32, slot_visits=576,
        auditory_differences=7680, visual_comparisons=8192, equality_comparisons=5376,
        scan_comparisons=21248, verification_comparisons=21248, logical_scan_operations=416,
        formation_l1_limit=142080, state_bytes=98304, input_bytes=16384, pair_bytes=16384,
        scan_bytes_exclusive=32768, metadata_bytes=65536, serialization_bound=4096000)


def execution_plan(sources, hashes, generator):
    require(type(sources) is list and len(sources) == 32, "SOURCE_INVENTORY_INVALID")
    for s, spec in zip(sources, source_specs(), strict=True):
        require(s == bind_source(spec, s["payload_sha256"], s["byte_count"]), "SOURCE_BINDING_INVALID")
    return sealed(dict(schema="s2nh.execution.v1", masterseed=MASTER, sources=sources, events=events(),
        source_hashes=hashes, generator_identity=generator, contract_sha256=filehash(ROOT / CONTRACT),
        profile=profile_binding(), rules=["HISTORICAL_SUM_L1_24", "ALL_BANDS_24"],
        observed_audio_bands=list(range(24)), visible_visual_positions=list(range(32)),
        budgets=budgets(), main_gate=False, receptor_execution_authorized=False), "execution_digest")


def evaluation_plan(execution):
    cases = []
    for k, target, variant in ((3,"p00","EXACT"),(4,"p00","EXACT"),(23,"p00","GAIN"),(24,"p00","EXACT"),
                               (25,"p01","FREQUENCY"),(26,"p01","EXACT"),(27,None,"UNKNOWN"),(28,None,"UNKNOWN")):
        cases.append(dict(ordinal=k, target_recipe=target, variant=variant, expected_context=target is not None,
                          phase="EARLY_COMPETITION" if k < 5 else "AFTER_PRESSURE"))
    return sealed(dict(schema="s2nh.evaluation.v1", execution_digest=execution["execution_digest"], cases=cases,
        formation_roles={"p00":"A","p01":"B","p02":"C"}, pressure_recipes=[f"p{i:02d}" for i in range(3,12)],
        expected_support={"p00":3,"p01":3,"p02":2}, expected_recent_eviction=["p00","p01","p02"],
        retention_identity="D=R+L", zero_denominator="ERHALTUNG_NICHT_GEPRUEFT", offset_losses=False,
        separate_axes=["modality","phase","variant","observed_competition","pcm_bits","receptor_bits","observed_bits"],
        excluded_target_candidates_separate=True, geometry_success_gate=False), "evaluation_digest")


def publish(path, value):
    data = canonical(value)
    require(len(data) <= MAX_BYTES, "OUTPUT_LIMIT_EXCEEDED")
    with path.open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    return hashlib.sha256(data).hexdigest()


def collisions(sources):
    groups = {}
    for s in sources:
        groups.setdefault((s["kind"] == "PCM", s["payload_sha256"]), []).append(s["source_id"])
    return [v for v in groups.values() if len(v)>1]


def preseal_once():
    out = ROOT / "reports/s2nh" / RUN_ID
    out.mkdir(exist_ok=False)
    phase, sid, attempted, sources = "QUALIFICATION_BINDING", None, 0, []
    try:
        qpath = ROOT / "reports/s2nh" / QUAL_ID / "result.json"
        q = json.loads(qpath.read_bytes())
        require(q["status"] == "S2NH_SOURCE_BINDING_QUALIFIED" and q["exit_code"] == 0
                and q["unittest_calls"] == 1 and q["hashes_after"] == watched(), "QUALIFICATION_REQUIRED")
        before, generator, specs = watched(), identity(), source_specs()
        publish(out / "preregistration.json", dict(run_id=RUN_ID, hashes=before, generator=generator,
            specifications=[s.payload() for s in specs], events=events(), budgets=budgets(),
            qualification_sha256=filehash(qpath), preseal_calls=1, retry=False))
        for spec in specs:
            phase, sid = "PAYLOAD_GENERATION", spec.source_id
            attempted += 1
            payload = pcm_payload(json.loads(spec.recipe_json)) if spec.kind == "PCM" else rgb_payload(json.loads(spec.recipe_json))
            try:
                phase = "PAYLOAD_BINDING"
                view = memoryview(payload).cast("B")
                try:
                    sources.append(bind_source(spec, hashlib.sha256(view).hexdigest(), view.nbytes))
                finally:
                    view.release()
                    del view
            finally:
                del payload
        phase, sid = "PLAN_PUBLICATION", None
        require(before == watched() and not MAIN_GATE, "SOURCES_CHANGED")
        execution = execution_plan(sources, before, generator)
        evaluation = evaluation_plan(execution)
        ah = publish(out / "execution-plan.json", execution)
        bh = publish(out / "evaluation-plan.json", evaluation)
        publish(out / "seal.json", sealed(dict(run_id=RUN_ID, status="S2NH_SOURCES_PRESEALED",
            execution_digest=execution["execution_digest"], evaluation_digest=evaluation["evaluation_digest"],
            execution_file_sha256=ah, evaluation_file_sha256=bh, hashes_before=before, hashes_after=watched(),
            attempted_sources=attempted, completed_sources=len(sources), collisions=collisions(sources),
            counters=dict(pcm=15,rgb=13,visual_cues=4,events=28,receptor=0,memory=0,field=0,context=0,runtime=0,
                          distances=0,rule_comparisons=0,raw_payloads_saved=0), main_gate=False), "seal_digest"))
    except Exception as error:
        publish(out / "failure.json", dict(run_id=RUN_ID, status="NOT_EVALUABLE", phase=phase, source_id=sid,
            attempted_sources=attempted, completed_sources=len(sources), error_class=type(error).__name__,
            code=str(error) if isinstance(error, S2NHError) else "SOURCE_BINDING_OR_EXECUTION_ERROR", main_gate=False))
    return out
