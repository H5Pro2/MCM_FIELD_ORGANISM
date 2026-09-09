"""NZ binding around the unchanged NY causal composition, not its main entry."""
import re
from pathlib import Path
from tools import _s2nz_private_source_binding as b
from tools import _s2ny_private_prediction_run as ny

p=ny.p
atomic,read=ny.atomic,ny.read
MAIN_GATE=False
OUT_ROOT=b.ROOT/"reports/s2nz"
SEAL_DIR=OUT_ROOT/b.RUN_ID
QUAL_ID="s2nz-diagnostic-qualification-20260909-01"
QUAL_DIR=OUT_ROOT/QUAL_ID
TEST_COUNT=24
EXECUTION_DIGEST="7f424a6dbc694b4f8cb20160ce8a294e0d4923137b9f0fcdf83aeb5a48e0d113"
SEAL_DIGEST="4341121eb545faa00b5158ded2ca148b8cf153e5295a6565f0e02d9c5521da41"
PREVERIFICATION_DIGEST="a127825ce2e6ecb5d0e8b27bd28a66516f925df2a8b0753b816a2ac49214de9c"
OWN=("tools/_s2nz_private_diagnostic_run.py","tools/_s2nz_private_diagnostic_evaluation.py",
    "tests/test_s2nz_private_diagnostic.py","reports/s2nz/qualify_diagnostic_once.py",
    "reports/s2nz/DIAGNOSEQUALIFIKATIONSBINDUNG.md")


def watched():
    hashes={**ny.watched(),**b.watched(),**{s:b.filehash(b.ROOT/s) for s in OWN}}
    for name in ("execution-plan.json","evaluation-plan.json","seal.json","verification.json"):
        hashes[(SEAL_DIR/name).relative_to(b.ROOT).as_posix()]=b.filehash(SEAL_DIR/name)
    return hashes


def boundary():
    return dict(schema="s2nz.observed-target-boundary.v1",prediction_contract=b.prediction_contract(),
        noise_contract=b.noise_contract(),clean_counterpart_input=False,clean_reconstruction_target=False,
        historical_core_schema="s2ny.prefix-recommendation.v1",diagnostic_only=True)


def validate_plan(plan):
    p.check(plan,"execution_digest")
    p.require(plan.get("schema")=="s2nz.source-execution-plan.v1" and
        plan.get("contract_sha256")==b.PINS[b.CONTRACT] and plan.get("profiles")==b.profile_binding()
        and plan.get("budgets")==b.budgets(),"PLAN_BINDING_INVALID")
    p.require(plan.get("prediction_contract")==b.prediction_contract()
        and plan.get("noise_contract")==b.noise_contract(),"CONTROL_BOUNDARY_INVALID")
    sources=plan.get("sources")
    p.require(type(sources) is list and len(sources)==30 and len({s["source_id"] for s in sources})==30
        and plan.get("source_order")==[s["source_id"] for s in sources],"SOURCE_ORDER_INVALID")
    for n,s in enumerate(sources):
        p.check(s,"source_digest")
        p.require(s["stream_id"]==f"s{n//5+1:02d}" and s["window_ordinal"]==n%5
            and s["ordinal"]==n+1 and s["clock_id"]=="audio.sample"
            and s["window_start_sample"]==n*4800 and s["window_end_sample"]==(n+1)*4800
            and s["nj_snapshot_index"]==n*10,"SOURCE_TIME_INVALID")
    p.require(plan.get("authorizations")=={key:False for key in b.FORBIDDEN_CALLS},"AUTHORIZATION_INVALID")


def load_presealed():
    ex=read(SEAL_DIR/"execution-plan.json","execution_digest")
    se=read(SEAL_DIR/"seal.json","seal_digest")
    proof=read(SEAL_DIR/"verification.json","verification_digest")
    validate_plan(ex)
    p.require(ex["execution_digest"]==se["execution_digest"]==proof["execution_digest"]==EXECUTION_DIGEST
        and se["seal_digest"]==proof["seal_digest"]==SEAL_DIGEST
        and proof["verification_digest"]==PREVERIFICATION_DIGEST
        and proof["status"]=="S2NZ_PRESEAL_VERIFIED" and proof["verification_calls"]==1,"PRESEAL_BINDING_INVALID")
    p.require(ex["source_hashes"]==se["hashes_before"]==se["hashes_after"]==b.watched()
        and ex["environment"]==b.environment() and ex["generator"]==b.generator_identity()
        and ex["freeze_import"]==b.load_freezes() and ex["forecast_sites"]==b.forecast_sites(),"SOURCE_BINDING_INVALID")
    for name,key in (("execution-plan.json","execution_file_sha256"),("evaluation-plan.json","evaluation_file_sha256")):
        p.require(b.filehash(SEAL_DIR/name)==se[key],"PLAN_FILE_CHANGED")
    p.require(read(SEAL_DIR/"evaluation-plan.json","evaluation_digest")==b.evaluation_plan(ex),"EVALUATION_BINDING_INVALID")
    b.qualification(ex["source_hashes"])
    for spec,row in zip(b.specs(),ex["sources"],strict=True):
        p.require(row==b.bind_source(spec,row["pcm_sha256"]),"SOURCE_BINDING_INVALID")
    return ex


def generate(source):
    p.require(type(source) is dict and type(source.get("ordinal")) is int and 1<=source["ordinal"]<=30,"SOURCE_BINDING_INVALID")
    spec=b.specs()[source["ordinal"]-1]
    p.require(source==b.bind_source(spec,source.get("pcm_sha256")),"SOURCE_BINDING_INVALID")
    return b.pcm_window(spec)


def make_reader(plan):
    reader=ny.nw.AudioReader(plan["profiles"],generate)
    p.require(reader.np.__version__==plan["environment"]["numpy"]["version"] and
        b.filehash(Path(reader.np.__file__))==plan["environment"]["numpy"]["files"].get(str(Path(reader.np.__file__).resolve())),"NUMPY_BINDING_INVALID")
    return reader


def failure_record(plan,run_id,work,phase,exc):
    return b.sealed(dict(schema="s2nz.diagnostic-run.v1",run_id=run_id,status="NOT_EVALUABLE",
        execution_digest=plan["execution_digest"],boundary=boundary(),core=None,work=dict(work.values),
        failure=dict(phase=phase,source_id=work.source_id,code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),
            error_class=type(exc).__name__,work=dict(work.values)),evaluation=None,closed=True,main_gate_after=False),"record_digest")


def execute(plan,reader,run_id,work=None):
    work=p.Work() if work is None else work
    try:
        validate_plan(plan)
        # Keep the original NY schema/digest as an explicit nested reusable core.
        core=ny.execute(plan,reader,run_id,work)
        result=dict(schema="s2nz.diagnostic-run.v1",run_id=run_id,status=core["status"],
            execution_digest=plan["execution_digest"],boundary=boundary(),core=core,work=dict(work.values),
            failure=core["failure"],evaluation=None,closed=core["closed"],main_gate_after=False)
        p.require(len(b.canonical(result))+128<=p.MAX_OUTPUT_BYTES,"OUTPUT_SIZE_EXCEEDED")
        return b.sealed(result,"record_digest")
    except Exception as exc:
        return failure_record(plan,run_id,work,"NZ_COMPOSITION",exc)


def verify_record(record,plan):
    p.require(len(b.canonical(record))<=p.MAX_OUTPUT_BYTES,"OUTPUT_SIZE_EXCEEDED")
    p.check(record,"record_digest")
    validate_plan(plan)
    p.require(record["schema"]=="s2nz.diagnostic-run.v1" and record["execution_digest"]==plan["execution_digest"]
        and record["boundary"]==boundary() and record["evaluation"] is None and record["closed"] is True
        and record["main_gate_after"] is False,"RECORD_BINDING_INVALID")
    p.count_form(record["work"],p.limits())
    if record["core"] is None:
        p.require(record["status"]=="NOT_EVALUABLE" and type(record["failure"]) is dict
            and type(record["failure"].get("phase")) is str and type(record["failure"].get("code")) is str
            and record["failure"]["work"]==record["work"],"FAILURE_BINDING_INVALID")
        core_proof=None
        allowed=False
    else:
        core=record["core"]
        p.require(core["run_id"]==record["run_id"] and core["status"]==record["status"]
            and core["work"]==record["work"] and core["failure"]==record["failure"],"CORE_BINDING_INVALID")
        core_proof=ny.direct.verify_record(core,plan)
        allowed=core_proof["evaluation_allowed"]
    return b.sealed(dict(status="S2NZ_DIAGNOSTIC_VERIFIED" if allowed else "TECHNICAL_FAILURE_RECORDED",
        record_digest=record["record_digest"],execution_digest=plan["execution_digest"],core_proof=core_proof,
        evaluation_allowed=allowed,read_only=True,baseline_equal=allowed,payload_regenerations=0,
        chronology_independently_proven=False),"verification_digest")


def run_main_once(run_id):
    global MAIN_GATE
    created=False
    before={}
    plan=dict(execution_digest=EXECUTION_DIGEST)
    work=p.Work()
    phase="QUALIFICATION_BINDING"
    try:
        p.require(MAIN_GATE is True and not any((b.MAIN_GATE,ny.MAIN_GATE,ny.nw.MAIN_GATE,ny.nw.nv.MAIN_GATE)),"MAIN_GATE_CLOSED")
        p.require(type(run_id) is str and re.fullmatch(r"s2nz-diagnostic-disturbance-\d{8}-\d{2}",run_id),"RUN_ID_INVALID")
        out=OUT_ROOT/run_id
        out.mkdir(exist_ok=False)
        created=True
        before=watched()
        q=read(QUAL_DIR/"result.json","result_digest")
        p.require(q["status"]=="S2NZ_DIAGNOSTIC_QUALIFIED" and q["run_id"]==QUAL_ID and q["passed_tests"]==TEST_COUNT
            and q["unittest_calls"]==1 and q["exit_code"]==0 and q["hashes_before"]==q["hashes_after"]==before,"QUALIFICATION_INVALID")
        phase="SOURCE_BINDING"
        plan=load_presealed()
        atomic(out/"preregistration.json",dict(run_id=run_id,execution_digest=EXECUTION_DIGEST,
            seal_digest=SEAL_DIGEST,hashes=before,boundary=boundary(),limits=p.limits(),
            verification_limits=p.verification_limits(),retry=False),65536)
        phase="RECEPTOR_INIT"
        result=execute(plan,make_reader(plan),run_id,work)
        phase="FINAL_CODE_BINDING"
        p.require(watched()==before,"CODE_CHANGED")
    except Exception as exc:
        if not created:
            raise
        result=failure_record(plan,run_id,work,phase,exc)
    finally:
        MAIN_GATE=False
    result.pop("record_digest")
    result.update(code_hashes_before=before,code_hashes_after={s:b.filehash(b.ROOT/s) for s in before},seal_digest=SEAL_DIGEST)
    if len(b.canonical(result))+128>p.MAX_OUTPUT_BYTES:
        result.update(status="NOT_EVALUABLE",core=None,failure=dict(phase="RESULT_SIZE",source_id=None,
            code="OUTPUT_SIZE_EXCEEDED",error_class="S2NYPredictionError",work=dict(work.values)))
    atomic(out/"result.json",b.sealed(result,"record_digest"),p.MAX_OUTPUT_BYTES)
    return out


def verify_file_once(out):
    with (out/"verification.claim").open("xb"):
        pass
    before=b.filehash(out/"result.json")
    try:
        record=read(out/"result.json","record_digest")
        p.require(record["run_id"]==out.name and record["seal_digest"]==SEAL_DIGEST
            and record["code_hashes_before"]==record["code_hashes_after"]==watched(),"RUN_BINDING_INVALID")
        report=verify_record(record,load_presealed())
        report.pop("verification_digest")
        p.require(before==b.filehash(out/"result.json") and MAIN_GATE is False,"READ_ONLY_INVALID")
        report.update(file_sha256_before=before,file_sha256_after=before,verification_calls=1)
    except Exception as exc:
        report=dict(status="NOT_EVALUABLE",phase="VERIFICATION",code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),
            evaluation_allowed=False,verification_calls=1)
    report=b.sealed(report,"verification_digest")
    atomic(out/"verification.json",report,p.MAX_VERIFICATION_BYTES)
    return report


def evaluate_file_once(out):
    from tools import _s2nz_private_diagnostic_evaluation as evaluation
    with (out/"evaluation.claim").open("xb"):
        pass
    result=evaluation.evaluate(read(out/"result.json","record_digest"),read(out/"verification.json","verification_digest"),
        read(SEAL_DIR/"evaluation-plan.json","evaluation_digest"))
    atomic(out/"evaluation.json",result,262144)
    return result
