"""Receptor-free NT metadata and one-shot preseal; no historical entry calls."""
import ast
from dataclasses import dataclass
import hashlib
import json
import math
import re
import struct

from tools import _s2np_private_source_binding as common

ROOT = common.ROOT
canonical, digest, filehash = common.canonical, common.digest, common.filehash
publish, sealed = common.publish, common.sealed
environment, profile_binding = common.environment, common.profile_binding
MAIN_GATE = False
CONTRACT = "docs/S2NT_STATISCHER_PRUEFPLAN_AUDIO_VARIANTEN_UND_MISCHUNGEN.md"
GENERATOR = "reports/s2nc/seal_inventory.py"
QUAL_ID = "s2nt-source-binding-qualification-20260908-01"
RUN_ID = "s2nt-source-preseal-20260908-01"
QUAL_DIR = ROOT / "reports/s2nt" / QUAL_ID
MAX_METADATA_BYTES = 65536
MAX_OUTPUT_BYTES = 2097152
PINS = {p: h for p, h in common.PINS.items() if p not in (common.CONTRACT, common.GENERATOR)}
PINS.update({CONTRACT: "917483459ad77f4f2bcba4a578cf4b813d78f6a1afaf9acb4cfaede5ef5a35ea",
    GENERATOR: "7709beaa1aede2393d27fa133cb67fa77d3200182d8e10ea7e125c6abd202618",
    "tools/_s2np_private_source_binding.py": "004ea7c8841e5f0b68fe9191604b0a0a7337ac568af2205dca900dd2ae874b12"})
OWN = ("tools/_s2nt_private_source_binding.py", "tools/_s2nt_private_preseal_verification.py",
       "tests/test_s2nt_private_source_binding.py", "reports/s2nt/qualify_once.py",
       "reports/s2nt/preseal_once.py", "reports/s2nt/QUALIFIKATIONSBINDUNG.md")
F = ((310000,1240000,5580000), "s2nt-pcm-001")
FS = ((319300,1277200,5747400), "s2nt-pcm-001")
G = ((470000,1880000,8460000), "s2nt-pcm-002")
GS = ((484100,1936400,8713800), "s2nt-pcm-002")
U = ((733000,2932000,11728000), "s2nt-pcm-003")
V = ((887000,3548000,14192000), "s2nt-pcm-004")
A, L = ((4,20),(2,20),(1,20)), ((3,20),(3,40),(3,80))
Z, H = ((4,20),(2,20),(0,1)), ((0,1),(0,1),(1,20))
ROWS = (((F,A),), ((G,A),), ((F,A),), ((F,L),), ((FS,A),),
        ((F,A),(G,H)), ((F,Z),(G,H)), ((G,A),), ((G,L),), ((GS,A),),
        ((G,A),(F,H)), ((G,Z),(F,H)), ((U,A),), ((V,A),))
PAIRS = ((3,1),(3,2),(4,1),(4,2),(5,1),(5,2),(6,1),(6,2),(7,1),(7,2),
         (8,1),(8,2),(9,1),(9,2),(10,1),(10,2),(11,1),(11,2),(12,1),(12,2),
         (13,1),(13,2),(14,1),(14,2),(1,2))


class S2NTBindingError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NTBindingError(code)


def native_index(start):
    require(type(start) is int and start >= 0 and start % 480 == 0, "NATIVE_WINDOW_INVALID")
    return start // 480


@dataclass(frozen=True, slots=True)
class SourceSpec:
    ordinal: int
    recipe_json: str

    def __post_init__(self):
        require(type(self.ordinal) is int and 1 <= self.ordinal <= 14, "SOURCE_ID_INVALID")
        value = json.loads(self.recipe_json)
        require(canonical(value).decode() == self.recipe_json, "RECIPE_CANONICAL_INVALID")
        require(value.keys() == {"sample_count","sample_rate","groups"}
                and value["sample_count"] == 4800 and value["sample_rate"] == 48000,
                "RECIPE_FORM_INVALID")
        require(type(value["groups"]) is list and 1 <= len(value["groups"]) <= 2, "GROUP_FORM_INVALID")
        for group in value["groups"]:
            require(group.keys() == {"seed","partials"} and re.fullmatch(r"[a-z0-9-]+", group["seed"])
                    and len(group["partials"]) == 3, "GROUP_FORM_INVALID")
            for p in group["partials"]:
                ratio = p["amplitude_ratio"]
                require(p.keys() == {"frequency_millihz","amplitude_ratio"}
                    and type(p["frequency_millihz"]) is int and 0 < p["frequency_millihz"] < 24000000
                    and type(ratio) is list and len(ratio) == 2
                    and all(type(x) is int for x in ratio) and ratio[0] >= 0 and ratio[1] > 0,
                    "PARTIAL_FORM_INVALID")

    def recipe(self):
        return json.loads(self.recipe_json)

    def payload(self):
        start = (self.ordinal-1)*4800
        recipe = self.recipe()
        return dict(source_id=f"nt-a{self.ordinal:02d}", ordinal=self.ordinal, format="PCM_F32LE",
            channels=1, recipe=recipe, recipe_digest=digest(recipe), clock_id="audio.sample",
            window_start_sample=start, window_end_sample=start+4800,
            nj_snapshot_index=native_index(start), pcm_byte_count=19200)


def source_specs():
    return tuple(SourceSpec(n, canonical(dict(sample_count=4800, sample_rate=48000, groups=[
        dict(seed=group[1], partials=[dict(frequency_millihz=f, amplitude_ratio=list(a))
            for f,a in zip(group[0], amps, strict=True)]) for group, amps in row])).decode())
        for n,row in enumerate(ROWS,1))


def bind_source(spec, sha):
    require(type(spec) is SourceSpec and spec in source_specs(), "SOURCE_SPEC_INVALID")
    require(type(sha) is str and re.fullmatch(r"[0-9a-f]{64}", sha), "PAYLOAD_DIGEST_INVALID")
    return sealed({**spec.payload(), "pcm_sha256":sha}, "source_digest")


def watched():
    require(all(filehash(ROOT/p) == h for p,h in PINS.items()), "PIN_CHANGED")
    return {p:filehash(ROOT/p) for p in sorted(set(PINS) | set(OWN))}


def pure_generator():
    require(filehash(ROOT/GENERATOR) == PINS[GENERATOR], "GENERATOR_CHANGED")
    tree = ast.parse((ROOT/GENERATOR).read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == "pcm_bytes"]
    require(len(nodes) == 1, "GENERATOR_SELECTION_INVALID")
    namespace = dict(hashlib=hashlib, math=math, struct=struct)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(ROOT/GENERATOR),"exec"),namespace)
    return namespace["pcm_bytes"], dict(path=GENERATOR, file_sha256=PINS[GENERATOR],function="pcm_bytes",
        ast_digest=digest(ast.dump(nodes[0],include_attributes=False)), historical_entry_executed=False)


def budgets():
    return dict(pcm_sources=14, generated_pcm_bytes=268800, max_live_payloads=1, max_live_payload_bytes=19200,
        future_analyses=14, future_nj=14, future_values_per_scale=672, pairs_per_implementation=25,
        primary_differences=1200, both_differences=2400, order_checks=24, equality_checks=2400,
        offline_halving_checks=672, offline_term_checks=2400, offline_equality_checks=2400,
        offline_sums=50, offline_order_checks=24, max_metadata_bytes=MAX_METADATA_BYTES,
        max_output_bytes=MAX_OUTPUT_BYTES, max_verification_bytes=262144)


def execution_plan(sources, env, hashes, generator):
    require(type(sources) is list and len(sources) == 14, "SOURCE_COUNT_INVALID")
    for spec,row in zip(source_specs(),sources,strict=True):
        require(type(row) is dict and row == bind_source(spec,row.get("pcm_sha256")), "SOURCE_BINDING_INVALID")
    result = sealed(dict(schema="s2nt.source-execution-plan.v1", contract_sha256=PINS[CONTRACT],
        sources=sources, source_order=[s.payload()["source_id"] for s in source_specs()],
        pairs=[dict(pair_id=f"d{q:02d}-{r:02d}",source_id=f"nt-a{q:02d}",reference_id=f"nt-a{r:02d}") for q,r in PAIRS],
        diagnostic=dict(indices=list(range(48)), arithmetic="historical sum in original index order / 48",
            threshold=None, direct_baseline=True, raw_and_half_equality_separate=True),
        environment=env, generator=generator, profiles=profile_binding(), source_hashes=hashes, budgets=budgets(),
        receptor_execution_authorized=False, nj_execution_authorized=False,
        comparison_execution_authorized=False, system_execution_authorized=False),"execution_digest")
    require(len(canonical(result)) <= MAX_METADATA_BYTES, "METADATA_SIZE_EXCEEDED")
    return result


def evaluation_plan(execution):
    # Every predicate is literal and refers only to planned distance rows.
    primary = (("d04-01","d06-01"),("d04-01","d07-01"),("d05-01","d06-01"),("d05-01","d07-01"),
        ("d09-02","d11-02"),("d09-02","d12-02"),("d10-02","d11-02"),("d10-02","d12-02"))
    attribution = (("d04-01","d04-02"),("d05-01","d05-02"),("d09-02","d09-01"),("d10-02","d10-01"))
    controls = (("d04-01","d13-01"),("d04-01","d14-01"),("d04-01","d01-02"),
        ("d05-01","d13-01"),("d05-01","d14-01"),("d05-01","d01-02"),
        ("d09-02","d13-02"),("d09-02","d14-02"),("d09-02","d01-02"),
        ("d10-02","d13-02"),("d10-02","d14-02"),("d10-02","d01-02"))
    return sealed(dict(schema="s2nt.evaluation-plan.v1", execution_digest=execution["execution_digest"],
        contract_sha256=PINS[CONTRACT], families=[
            dict(reference="nt-a01",exact="nt-a03",level="nt-a04",frequency="nt-a05",addition="nt-a06",replacement="nt-a07"),
            dict(reference="nt-a02",exact="nt-a08",level="nt-a09",frequency="nt-a10",addition="nt-a11",replacement="nt-a12")],
        independent_controls=["nt-a13","nt-a14"],
        order_checks=[dict(check_id=f"o{i:02d}",group=kind,left=l,operator="LT",right=r)
            for i,(kind,l,r) in enumerate([(kind,l,r) for kind,items in
                (("PRIMARY",primary),("ATTRIBUTION",attribution),("CONTROL",controls)) for l,r in items],1)],
        ties_separate=True, exact_not_variation=True, nominal_variation_requires_changed_values=True,
        no_semantic_identity=True, components_are_generator_provenance_only=True,
        operational_admission=None, no_threshold_fitting=True, no_success_start_gate=True,
        no_replacement_source=True, negative_l1_not_universal_representation_failure=True),"evaluation_digest")


def preseal_once(run_id):
    require(run_id == RUN_ID and MAIN_GATE is False, "RUN_BINDING_INVALID")
    out = ROOT/"reports/s2nt"/run_id
    out.mkdir(exist_ok=False)
    phase, sid, attempted, rows, before = "QUALIFICATION_BINDING",None,0,[],{}
    try:
        q = json.loads((QUAL_DIR/"result.json").read_bytes())
        require(q["result_digest"] == digest({k:v for k,v in q.items() if k != "result_digest"})
            and q["status"] == "S2NT_SOURCE_BINDING_QUALIFIED" and q["passed_tests"] == 16
            and q["unittest_calls"] == 1 and q["exit_code"] == 0, "QUALIFICATION_REQUIRED")
        before = watched()
        require(before == q["hashes_before"] == q["hashes_after"], "QUALIFIED_SOURCES_CHANGED")
        phase = "ENVIRONMENT_BINDING"
        env = environment()
        pcm, gen = pure_generator()
        publish(out/"preregistration.json",dict(run_id=run_id,hashes=before,environment=env,generator=gen,
            specs=[s.payload() for s in source_specs()],profiles=profile_binding(),budgets=budgets(),
            evaluation_template=evaluation_plan(dict(execution_digest="0"*64)),
            pairs=list(PAIRS),qualification_sha256=filehash(QUAL_DIR/"result.json"),retry=False),MAX_METADATA_BYTES)
        for spec in source_specs():
            phase,sid = "PAYLOAD_GENERATION",spec.payload()["source_id"]
            attempted += 1
            payload = pcm(spec.recipe())
            try:
                phase = "PAYLOAD_BINDING"
                require(type(payload) is bytearray and len(payload) == 19200,"PAYLOAD_FORM_INVALID")
                sha = hashlib.sha256(payload).hexdigest()
            finally:
                del payload
            rows.append(bind_source(spec,sha))
        phase,sid = "PLAN_BINDING",None
        for a,b in ((0,2),(1,7)):
            require(rows[a]["pcm_sha256"] == rows[b]["pcm_sha256"]
                and rows[a]["source_digest"] != rows[b]["source_digest"],"EXACT_COPY_DIFFERS")
        execution = execution_plan(rows,env,before,gen)
        evaluation = evaluation_plan(execution)
        after = watched()
        require(before == after and env == environment(),"BINDINGS_CHANGED")
        phase = "PUBLICATION"
        ef = publish(out/"execution-plan.json",execution,MAX_METADATA_BYTES)
        vf = publish(out/"evaluation-plan.json",evaluation,MAX_METADATA_BYTES)
        seal = sealed(dict(schema="s2nt.source-seal.v1",run_id=run_id,status="S2NT_SOURCES_PRESEALED",
            execution_digest=execution["execution_digest"],evaluation_digest=evaluation["evaluation_digest"],
            execution_file_sha256=ef,evaluation_file_sha256=vf,hashes_before=before,hashes_after=after,
            qualification_file_sha256=filehash(QUAL_DIR/"result.json"),attempted_sources=attempted,completed_sources=len(rows),
            generated_pcm_bytes=268800,max_live_payloads=1,raw_payloads_persisted=0,
            receptor_calls=0,nj_calls=0,distance_calls=0,memory_calls=0,field_calls=0,context_calls=0,runtime_calls=0,
            main_gate_after=MAIN_GATE,exact_pairs=[["nt-a01","nt-a03"],["nt-a02","nt-a08"]],
            collisions=common.collision_groups(rows)),"seal_digest")
        publish(out/"seal.json",seal,MAX_METADATA_BYTES)
    except Exception as exc:
        publish(out/"failure.json",sealed(dict(run_id=run_id,status="NOT_EVALUABLE",phase=phase,source_id=sid,
            attempted_sources=attempted,completed_sources=len(rows),error_class=type(exc).__name__,
            code=exc.code if isinstance(exc,S2NTBindingError) else "TECHNICAL_EXECUTION_ERROR",
            hashes_before=before,main_gate_after=MAIN_GATE,retry=False),"failure_digest"),MAX_METADATA_BYTES)
    return out
