"""Closed NT comparison file binding. Gate stays false until separate approval."""
import json
import os
import re

from tools import _s2nt_private_comparison as c
from tools import _s2nt_private_comparison_verification as direct
from tools import _s2nt_private_order_evaluation as evaluation

b = c.b
MAIN_GATE = False
QUAL_ID = "s2nt-comparison-qualification-20260908-01"
QUAL_DIR = b.ROOT/"reports/s2nt"/QUAL_ID
SEAL_DIR = b.ROOT/"reports/s2nt/s2nt-source-preseal-20260908-01"
MATERIAL_DIR = b.ROOT/"reports/s2nt/s2nt-receptor-nj-materialization-20260908-01"
ANCHORS = c.Anchors("512cab06237f98ca0481f6b16764e30bdd99bb18841f0fb204c5e4700ae8673d",
    "48a75e2957b1c2e65bc6e63f1a24200b3538fb779406d9abb9f2f2638704647f",
    "8fe9e748a841a2b0a63e8e4536cdbc92151e6ff828c60310652926b02afeee59")
OWN = ("tools/_s2nt_private_comparison.py","tools/_s2nt_private_comparison_verification.py",
    "tools/_s2nt_private_order_evaluation.py","tools/_s2nt_private_comparison_run.py",
    "tests/test_s2nt_private_comparison.py","reports/s2nt/qualify_comparison_once.py",
    "reports/s2nt/VERGLEICHSQUALIFIKATIONSBINDUNG.md")


def watched():
    return {**b.watched(),**{p:b.filehash(b.ROOT/p) for p in OWN}}


def read(path,key):
    data = path.read_bytes()
    c.require(len(data) <= 2097152,"INPUT_SIZE_EXCEEDED")
    value = json.loads(data)
    c.require(data == c.canonical(value),"CANONICAL_INPUT_INVALID")
    c.check_root(value,key)
    return value


def load_verified_nt():
    c.require(MAIN_GATE is True,"MAIN_GATE_CLOSED")
    plan = read(SEAL_DIR/"execution-plan.json","execution_digest")
    seal = read(SEAL_DIR/"seal.json","seal_digest")
    c.require(seal["seal_digest"] == "ab2f64627d3385592281b6b0b312968bd4ff6397dcc46ec72fafd5779dad676a"
        and seal["execution_digest"] == ANCHORS.execution_digest
        and seal["execution_file_sha256"] == b.filehash(SEAL_DIR/"execution-plan.json")
        and seal["evaluation_file_sha256"] == b.filehash(SEAL_DIR/"evaluation-plan.json"),"SEAL_BINDING_INVALID")
    material = read(MATERIAL_DIR/"result.json","record_digest")
    proof = read(MATERIAL_DIR/"verification.json","verification_digest")
    c.require(b.environment() == plan["environment"],"ENVIRONMENT_CHANGED")
    c.require(all(b.filehash(b.ROOT/p) == h for p,h in material["source_hashes_before"].items()),"MATERIALIZATION_CODE_CHANGED")
    c.bind_inputs(plan,material,proof,ANCHORS)
    return plan,material,proof


def atomic(path,value,limit):
    data = c.canonical(value)
    c.require(len(data) <= limit,"OUTPUT_SIZE_EXCEEDED")
    c.require(not path.exists(),"WRITE_CONFLICT")
    temporary = path.with_suffix(path.suffix+".pending")
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.rename(temporary,path)


def run_main_once(run_id):
    global MAIN_GATE
    c.require(MAIN_GATE is True,"MAIN_GATE_CLOSED")
    c.require(type(run_id) is str and re.fullmatch(r"s2nt-diagnostic-comparison-\d{8}-\d{2}",run_id),"RUN_ID_INVALID")
    out = b.ROOT/"reports/s2nt"/run_id
    out.mkdir(exist_ok=False)
    phase,before = "QUALIFICATION_BINDING",{}
    try:
        before = watched()
        q = read(QUAL_DIR/"result.json","result_digest")
        c.require(q["status"] == "S2NT_COMPARISON_QUALIFIED" and q["passed_tests"] == 18 and q["unittest_calls"] == 1
            and q["hashes_before"] == q["hashes_after"] == before,"QUALIFICATION_INVALID")
        atomic(out/"preregistration.json",dict(run_id=run_id,code_hashes=before,limits=c.LIMITS,retry=False,
            anchors=dict(execution_digest=ANCHORS.execution_digest,materialization_digest=ANCHORS.materialization_digest,
                verification_digest=ANCHORS.verification_digest)),65536)
        phase = "MATERIALIZATION_BINDING"
        plan,material,proof = load_verified_nt()
        phase = "PAIR_COMPARISON"
        result = c.compare_all(plan,material,proof,ANCHORS)
        phase = "FINAL_BINDINGS"
        c.require(watched() == before,"CODE_CHANGED")
        result.pop("comparison_digest")
        result.update(run_id=run_id,code_hashes_before=before,code_hashes_after=watched(),main_gate_after=False)
        result = c.sealed(result,"comparison_digest")
        c.require(len(c.canonical(result)) <= c.MAX_OUTPUT_BYTES,"OUTPUT_SIZE_EXCEEDED")
    except Exception as exc:
        result = c.sealed(dict(run_id=run_id,status="NOT_EVALUABLE",phase=phase,error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),code_hashes_before=before,
            evaluation=None,retry=False,main_gate_after=False),"comparison_digest")
    finally:
        MAIN_GATE = False
    atomic(out/"result.json",result,c.MAX_OUTPUT_BYTES)
    return out


def verify_file_once(out):
    with (out/"verification.claim").open("xb"):
        pass
    before = b.filehash(out/"result.json")
    try:
        result = read(out/"result.json","comparison_digest")
        c.require(result["run_id"] == out.name,"RUN_ID_INVALID")
        if result["status"] == "NOT_EVALUABLE":
            c.require(type(result["phase"]) is str and result["evaluation"] is None,"FAILURE_FORM_INVALID")
            report = dict(status="TECHNICAL_FAILURE_RECORDED",comparison_digest=result["comparison_digest"],evaluation_allowed=False)
        else:
            c.require(result["code_hashes_before"] == result["code_hashes_after"] == watched(),"CODE_CHANGED")
            report = direct.verify_comparison(result,ANCHORS)
            report.pop("verification_digest")
        c.require(before == b.filehash(out/"result.json") and MAIN_GATE is False,"READ_ONLY_BINDING_INVALID")
        report.update(file_sha256_before=before,file_sha256_after=before,verification_calls=1)
    except Exception as exc:
        report = dict(status="NOT_EVALUABLE",phase="VERIFICATION",code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),evaluation_allowed=False)
    report = c.sealed(report,"verification_digest")
    atomic(out/"verification.json",report,c.MAX_VERIFICATION_BYTES)
    return report


def evaluate_file_once(out):
    with (out/"evaluation.claim").open("xb"):
        pass
    record = read(out/"result.json","comparison_digest")
    proof = read(out/"verification.json","verification_digest")
    plan = read(SEAL_DIR/"evaluation-plan.json","evaluation_digest")
    result = evaluation.evaluate(record,proof,plan)
    atomic(out/"evaluation.json",result,262144)
    return result
