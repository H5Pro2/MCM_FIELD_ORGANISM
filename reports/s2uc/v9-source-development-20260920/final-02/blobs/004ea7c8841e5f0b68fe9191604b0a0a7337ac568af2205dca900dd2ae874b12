"""Source-only S2-NP binding; no receptor, NJ, scan or system imports."""

import ast
from dataclasses import dataclass
import hashlib
from importlib import metadata
import json
import math
import os
from pathlib import Path
import re
import struct
import sys

from reports.s2nd import seal_inventory as common

ROOT = Path(__file__).resolve().parents[1]
MAIN_GATE = False
CONTRACT = "docs/S2NP_STATISCHER_AUDITIVER_ABDECKUNGSVERGLEICH.md"
GENERATOR = "tools/_s2nc_private_receptor_materialization.py"
NJ = "tools/_s2nj_private_auditory_output_projection.py"
PINS = {
    CONTRACT: "484f592257fa9cfb245e84aff72ab3c9d2fff92501be0576353dfeaff9d26953",
    GENERATOR: "8a2898d9e6bf6a3d0ca5da527008bb8fe361f37fba892631857b34185e491d14",
    NJ: "e052cc76cf4c9678e11673d95390dea21634bba8082187567a760faaaf4904e5",
    "reports/s2nd/seal_inventory.py": "9f72d2a9fc9676235cf69b23ea690d25f0a782222c54393ecf5b44107f0ce91c",
    "mcm_field_organism/log_spectral_receptor.py": "26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0",
}
QUAL_ID = "s2np-source-binding-qualification-20260907-01"
MAX_METADATA_BYTES = 65536
MAX_OUTPUT_BYTES = 2097152
QUAL_DIR = ROOT / "reports/s2np" / QUAL_ID
canonical, digest, filehash = common.canonical, common.digest, common.filehash
A0, A1, A2 = ((8, 20), (2, 20), (1, 20)), ((6, 20), (3, 40), (3, 80)), ((6, 20), (4, 20), (1, 20))
ROWS = (
    ((310000, 620000, 930000), A0, "s2np-pcm-001"),
    ((2710000, 5420000, 8130000), A0, "s2np-pcm-002"),
    ((310000, 620000, 930000), A0, "s2np-pcm-001"),
    ((310000, 620000, 930000), A1, "s2np-pcm-001"),
    ((319300, 638600, 957900), A0, "s2np-pcm-001"),
    ((310000, 620000, 930000), A2, "s2np-pcm-001"),
    ((2710000, 5420000, 8130000), A0, "s2np-pcm-002"),
    ((2710000, 5420000, 8130000), A1, "s2np-pcm-002"),
    ((2791300, 5582600, 8373900), A0, "s2np-pcm-002"),
    ((2710000, 5420000, 8130000), A2, "s2np-pcm-002"),
    ((415000, 1127000, 2761000), A0, "s2np-pcm-003"),
    ((2471000, 5323000, 11537000), A0, "s2np-pcm-004"),
)
VIEWS = (
    ("CONTIGUOUS_24", tuple(range(24))),
    ("DISTRIBUTED_24", (0, 3, 4, 7, 8, 11, 12, 15, 16, 19, 20, 23,
                        24, 27, 28, 31, 32, 35, 36, 39, 40, 43, 44, 47)),
    ("FULL_48_DIAGNOSTIC", tuple(range(48))),
)
PANELS = (("p01", ("np-a01", "np-a02")), ("p02", ("np-a01",)),
          ("p03", ("np-a02",)), ("p04", ()))
CUES = tuple(f"np-a{i:02d}" for i in range(3, 13))


class S2NPBindingError(ValueError):
    pass


def require(ok, code):
    if not ok:
        raise S2NPBindingError(code)


def sealed(value, key):
    return {**value, key: digest(value)}


def check_digest(value):
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value), "DIGEST_INVALID")


def watched():
    for path, expected in PINS.items():
        require(filehash(ROOT / path) == expected, "PIN_CHANGED")
    own = ("tools/_s2np_private_source_binding.py", "tools/_s2np_private_preseal_verification.py",
           "tests/test_s2np_private_source_binding.py", "reports/s2np/qualify_once.py",
           "reports/s2np/preseal_once.py")
    return {p: filehash(ROOT / p) for p in sorted(set(PINS) | set(own))}


@dataclass(frozen=True, slots=True)
class SourceSpec:
    ordinal: int
    frequencies: tuple[int, ...]
    amplitudes: tuple[tuple[int, int], ...]
    seed: str

    def __post_init__(self):
        require(type(self.ordinal) is int and 1 <= self.ordinal <= 12, "SOURCE_ID_INVALID")
        require(type(self.frequencies) is tuple and len(self.frequencies) == 3
                and all(type(f) is int and 0 < f < 24000000 for f in self.frequencies), "RECIPE_INVALID")
        require(type(self.amplitudes) is tuple and len(self.amplitudes) == 3
                and all(type(a) is tuple and len(a) == 2 and all(type(x) is int and x > 0 for x in a)
                        for a in self.amplitudes), "RECIPE_INVALID")
        require(type(self.seed) is str and re.fullmatch(r"[a-z0-9-]+", self.seed), "SEED_INVALID")

    @property
    def source_id(self):
        return f"np-a{self.ordinal:02d}"

    def recipe(self):
        return dict(sample_count=4800, sample_rate=48000, groups=[dict(seed=self.seed, partials=[
            dict(frequency_millihz=f, amplitude_ratio=list(a))
            for f, a in zip(self.frequencies, self.amplitudes, strict=True)])])

    def payload(self):
        return dict(source_id=self.source_id, ordinal=self.ordinal, format="PCM_F32LE", channels=1,
                    recipe=self.recipe(), recipe_digest=digest(self.recipe()), clock_id="audio.sample",
                    window_start_sample=(self.ordinal - 1) * 4800, window_end_sample=self.ordinal * 4800,
                    snapshot_index=10 * (self.ordinal - 1), pcm_byte_count=19200)


def source_specs():
    return tuple(SourceSpec(n, *row) for n, row in enumerate(ROWS, 1))


def validate_specs(specs):
    require(type(specs) is tuple and specs == source_specs(), "SOURCE_PLAN_CHANGED")


def profile_binding():
    # Literal metadata only: never import or execute the receptor or NJ.
    raw = dict(schema="s2nj.bound-unscaled-auditory-profile.v1", geometry_id="auditory.log48.50-18000.w4800.h480.v1",
        config=dict(sample_rate=48000, window_size=4800, hop_size=480, min_frequency=50.0,
                    max_frequency=18000.0, band_count=48), window="numpy.hanning.symmetric",
        fft="numpy.fft.rfft.norm-none", reduction="sqrt-sum-square-weighted-amplitude",
        receptor_sha256=PINS["mcm_field_organism/log_spectral_receptor.py"])
    half = dict(profile_id="s2nj.auditory.hann48.output-half.v1",
        geometry_id="auditory.log48.50-18000.w4800.h480.half.v1", raw_profile_digest=digest(raw),
        factor_hex="0x1.0000000000000p-1", operation="binary64-multiply-once-after-raw-reduction",
        output_domain="finite-0-through-1-inclusive", rounding="qualified-binary64-nearest-even",
        subnormal_policy="preserve-native-rounded-result-report-underflow-no-flush-or-clamp",
        max_output_bytes=16384)
    return dict(raw=raw, raw_profile_digest=digest(raw), half=half, half_profile_digest=digest(half),
                nj_source_sha256=PINS[NJ], projection_executed=False)


def pure_generator():
    require(filehash(ROOT / GENERATOR) == PINS[GENERATOR], "GENERATOR_CHANGED")
    tree = ast.parse((ROOT / GENERATOR).read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "pcm_bytes"]
    require(len(nodes) == 1, "GENERATOR_SELECTION_INVALID")
    namespace = dict(hashlib=hashlib, math=math, struct=struct)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(ROOT / GENERATOR), "exec"), namespace)
    return namespace["pcm_bytes"], dict(path=GENERATOR, file_sha256=PINS[GENERATOR], function="pcm_bytes",
        ast_digest=digest(ast.dump(nodes[0], include_attributes=False)), historical_entry_executed=False)


def environment():
    dist = metadata.distribution("numpy")
    package = Path(dist.locate_file("numpy")).resolve(strict=True)
    binaries = sorted(package.rglob("*.pyd"))
    require(bool(binaries), "NUMPY_BINARY_BINDING_MISSING")
    libraries = package.parent / "numpy.libs"
    paths = [package / "__init__.py", *binaries, *sorted(libraries.glob("*.dll"))]
    return dict(python_version=sys.version, implementation=sys.implementation.name,
        executable=sys.executable, executable_sha256=filehash(Path(sys.executable)),
        python_dlls={str(p): filehash(p) for p in sorted(Path(sys.executable).parent.glob("python*.dll"))},
        pointer_bits=struct.calcsize("P") * 8, byteorder=sys.byteorder,
        binary64=dict(radix=sys.float_info.radix, mant_dig=sys.float_info.mant_dig, rounds=sys.float_info.rounds),
        math_module=common.math_identity(math, sys.builtin_module_names),
        numpy=dict(version=dist.version, package_path=str(package), files={str(p): filehash(p) for p in paths}),
        numpy_imported=False)


def bind_source(spec, sha):
    check_digest(sha)
    require(type(spec) is SourceSpec, "SOURCE_TYPE_INVALID")
    return sealed({**spec.payload(), "pcm_sha256": sha}, "source_digest")


def execution_plan(sources, identity, hashes, generator):
    require(type(sources) is list and len(sources) == 12, "SOURCE_COUNT_INVALID")
    for spec, source in zip(source_specs(), sources, strict=True):
        require(source == bind_source(spec, source.get("pcm_sha256")), "SOURCE_BINDING_INVALID")
    plan = dict(schema="s2np.source-execution-plan.v1", contract_sha256=PINS[CONTRACT], sources=sources,
        source_order=[s.source_id for s in source_specs()], profiles=profile_binding(), environment=identity,
        generator=generator, source_hashes=hashes,
        views=[dict(view_id=n, indices=list(i), diagnostic_only=n == "FULL_48_DIAGNOSTIC") for n, i in VIEWS],
        panels=[dict(panel_id=p, reference_ids=list(refs), cue_ids=list(CUES)) for p, refs in PANELS],
        cases=[dict(case_id=f"c{10*j+k+1:02d}", panel_id=p, cue_id=c)
               for j, (p, _) in enumerate(PANELS) for k, c in enumerate(CUES)],
        conditions=[dict(condition_id=n, arithmetic=a, threshold=t) for n, a, t in (
            ("A_HISTORICAL_SUM", "sum_in_index_order/len(indices)", 0.1),
            ("A_ALL_BANDS", "max", 0.1), ("SLOW_HISTORICAL_SUM", "sum_in_index_order/len(indices)", 0.01))],
        budgets=dict(source_count=12, generated_samples=57600, generated_pcm_bytes=230400,
            max_live_payloads=1, max_live_payload_bytes=19200, cases_per_view_condition=40,
            primary_panel_findings=360, primary_relationship_rows=360, primary_band_differences=3840,
            both_panel_findings=720, both_relationship_rows=720, both_band_differences=7680,
            future_analyses=12, future_nj_projections=12, future_values_per_scale=576,
            max_metadata_bytes=MAX_METADATA_BYTES, max_output_bytes=MAX_OUTPUT_BYTES),
        receptor_execution_authorized=False, nj_execution_authorized=False, comparison_execution_authorized=False,
        system_execution_authorized=False)
    require(len(canonical(plan)) <= MAX_METADATA_BYTES, "METADATA_SIZE_EXCEEDED")
    return sealed(plan, "execution_digest")


def evaluation_plan(execution):
    subtypes = ("EXACT", "LEVEL", "FREQUENCY", "SPECTRAL")
    rows = []
    for n, cue in enumerate(CUES):
        target = "np-a01" if n < 4 else "np-a02" if n < 8 else None
        rows.append(dict(cue_id=cue, target_source_id=target, subtype=subtypes[n % 4] if n < 8 else "INDEPENDENT_CONTROL"))
    return sealed(dict(schema="s2np.evaluation-plan.v1", execution_digest=execution["execution_digest"],
        contract_sha256=PINS[CONTRACT], relations=rows,
        removal_pairs=[["p01", "p02"], ["p01", "p03"], ["p02", "p04"], ["p03", "p04"]],
        retention_identity="D=R+L", zero_denominator="ERHALTUNG_NICHT_GEPRUEFT",
        relation_and_unique_retention_separate=True, offset_losses_with_gains=False,
        variation_axes=["payload", "rounded_values_by_view"], no_distance_success_gate=True), "evaluation_digest")


def collision_groups(sources):
    groups = {}
    for s in sources:
        groups.setdefault(s["pcm_sha256"], []).append(s["source_id"])
    return [dict(pcm_sha256=h, source_ids=ids) for h, ids in sorted(groups.items()) if len(ids) > 1]


def publish(path, value, limit=MAX_OUTPUT_BYTES):
    data = canonical(value)
    require(len(data) <= limit, "OUTPUT_SIZE_EXCEEDED")
    with Path(path).open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    return hashlib.sha256(data).hexdigest()


def preseal_once(run_id):
    require(re.fullmatch(r"s2np-source-preseal-\d{8}-\d{2}", run_id), "RUN_ID_INVALID")
    out = ROOT / "reports/s2np" / run_id
    out.mkdir(exist_ok=False)
    phase, sid, attempted, sources, before = "QUALIFICATION_BINDING", None, 0, [], {}
    try:
        q = json.loads((QUAL_DIR / "result.json").read_bytes())
        require(q["status"] == "S2NP_SOURCE_BINDING_QUALIFIED" and q["passed_tests"] == 16
                and q["unittest_calls"] == 1 and q["exit_code"] == 0, "QUALIFICATION_REQUIRED")
        before = watched()
        require(before == q["hashes_after"], "QUALIFIED_SOURCES_CHANGED")
        specs = source_specs()
        validate_specs(specs)
        phase = "ENVIRONMENT_BINDING"
        identity = environment()
        generate, generator = pure_generator()
        publish(out / "preregistration.json", dict(run_id=run_id, hashes=before, sources=[s.payload() for s in specs],
            environment=identity, generator=generator, profiles=profile_binding(),
            qualification_sha256=filehash(QUAL_DIR / "result.json"), generation_limit=12, retry=False), MAX_METADATA_BYTES)
        for spec in specs:
            phase, sid = "PCM_GENERATION", spec.source_id
            attempted += 1
            payload = generate(spec.recipe())
            try:
                require(type(payload) is bytearray and len(payload) == 19200, "PCM_FORM_INVALID")
                sha = hashlib.sha256(payload).hexdigest()
            finally:
                del payload
            phase = "SOURCE_BINDING"
            sources.append(bind_source(spec, sha))
        phase, sid = "PLAN_BINDING", None
        require(sources[0]["pcm_sha256"] == sources[2]["pcm_sha256"]
                and sources[1]["pcm_sha256"] == sources[6]["pcm_sha256"], "EXACT_COPY_DIFFERS")
        execution = execution_plan(sources, identity, before, generator)
        evaluation = evaluation_plan(execution)
        after = watched()
        require(before == after and identity == environment(), "BINDINGS_CHANGED")
        phase = "PUBLICATION"
        a = publish(out / "execution-plan.json", execution, MAX_METADATA_BYTES)
        b = publish(out / "evaluation-plan.json", evaluation, MAX_METADATA_BYTES)
        seal = sealed(dict(schema="s2np.source-seal.v1", run_id=run_id, status="S2NP_SOURCES_PRESEALED",
            execution_digest=execution["execution_digest"], evaluation_digest=evaluation["evaluation_digest"],
            execution_file_sha256=a, evaluation_file_sha256=b, hashes_before=before, hashes_after=after,
            attempted_sources=attempted, completed_sources=len(sources), generated_samples=57600,
            generated_pcm_bytes=230400, max_live_payloads=1, max_live_payload_bytes=19200,
            raw_payloads_persisted=0, receptor_calls=0, nj_calls=0, distance_calls=0, comparison_calls=0,
            memory_calls=0, context_calls=0, field_calls=0, runtime_calls=0, main_gate_after=False,
            exact_pairs=[["np-a01", "np-a03"], ["np-a02", "np-a07"]],
            collisions=collision_groups(sources)), "seal_digest")
        publish(out / "seal.json", seal, MAX_METADATA_BYTES)
    except Exception as exc:
        publish(out / "failure.json", dict(run_id=run_id, status="NOT_EVALUABLE", phase=phase,
            source_id=sid, attempted_sources=attempted, completed_sources=len(sources),
            error_class=type(exc).__name__, code=str(exc) if isinstance(exc, S2NPBindingError) else "TECHNICAL_EXECUTION_ERROR",
            hashes_before=before, main_gate_after=False))
    return out


__all__ = ()
