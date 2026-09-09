"""Closed causal NY composition over existing NW reader and atomic IO."""
import json
import re
from pathlib import Path
from tools import _s2ny_private_prediction as p
from tools import _s2ny_private_prediction_verification as direct
from tools import _s2nw_private_learning_run as nw

b=p.b
MAIN_GATE=False
OUT_ROOT=b.ROOT/"reports/s2ny"
SEAL_DIR=OUT_ROOT/b.RUN_ID
QUAL_ID="s2ny-prediction-qualification-20260909-01"
QUAL_DIR=OUT_ROOT/QUAL_ID
EXECUTION_DIGEST="17ecbda94c20fdc30cf49007fef12d326cbe628e3d78cb49d8dc5c7d341e43da"
SEAL_DIGEST="7c3fc3c302d1be1fec16e688c7c8d5c53956132ec939aeac56f7b41706e36cc3"
PREVERIFICATION_DIGEST="4a387ba5ae260d099859e4c174ba8e355cf21d9efd949beaf34802752cdb43b6"
OWN=("tools/_s2ny_private_prediction.py","tools/_s2ny_private_prediction_run.py",
    "tools/_s2ny_private_prediction_verification.py","tools/_s2ny_private_prediction_evaluation.py",
    "tests/test_s2ny_private_prediction.py","reports/s2ny/qualify_prediction_once.py",
    "reports/s2ny/PROGNOSEQUALIFIKATIONSBINDUNG.md")


def atomic(path,value,limit):
    try:
        nw.atomic(path,value,limit)
    except p.nw.S2NWLearningError as exc:
        raise p.S2NYPredictionError(exc.code) from exc


def read(path,key):
    value=b.read_canonical(path,2097152)
    p.check(value,key)
    return value


def watched():
    paths=(*OWN,*nw.OWN[:4],*nw.nv.OWN[:4],"tools/_s2nv_private_source_binding.py",
        "tools/_s2nu_private_comparison_run.py","tools/_s2nu_private_comparison.py",
        "tools/_s2nu_private_comparison_verification.py","tools/_s2nu_private_order_evaluation.py",
        "mcm_field_organism/broadband_hearing_path.py","tests/test_s2nv_private_prediction.py",
        "tests/test_s2ny_private_source_binding.py")
    hashes={**b.watched(),**{path:b.filehash(b.ROOT/path) for path in paths}}
    for name in ("execution-plan.json","evaluation-plan.json","seal.json","verification.json"):
        hashes[(SEAL_DIR/name).relative_to(b.ROOT).as_posix()]=b.filehash(SEAL_DIR/name)
    return hashes


def load_presealed():
    ex=read(SEAL_DIR/"execution-plan.json","execution_digest")
    se=read(SEAL_DIR/"seal.json","seal_digest")
    proof=read(SEAL_DIR/"verification.json","verification_digest")
    p.require(ex["execution_digest"]==se["execution_digest"]==proof["execution_digest"]==EXECUTION_DIGEST
        and se["seal_digest"]==proof["seal_digest"]==SEAL_DIGEST and proof["verification_digest"]==PREVERIFICATION_DIGEST,"PRESEAL_BINDING_INVALID")
    p.require(proof["status"]=="S2NY_PRESEAL_VERIFIED" and proof["verification_calls"]==1
        and ex["source_hashes"]==se["hashes_before"]==se["hashes_after"]==b.watched(),"PRESEAL_BINDING_INVALID")
    p.require(se["execution_file_sha256"]==b.filehash(SEAL_DIR/"execution-plan.json")
        and se["evaluation_file_sha256"]==b.filehash(SEAL_DIR/"evaluation-plan.json"),"PLAN_FILE_CHANGED")
    p.require(ex["environment"]==b.environment() and ex["generator"]==b.generator_identity()
        and ex["freeze_import"]==b.load_freezes() and ex["prediction_contract"]==b.prediction_contract()
        and ex["forecast_sites"]==b.forecast_sites() and ex["budgets"]==b.budgets(),"PLAN_BINDING_INVALID")
    b.qualification(ex["source_hashes"])
    for spec,row in zip(b.specs(),ex["sources"],strict=True):
        p.require(row==b.bind_source(spec,row["pcm_sha256"]),"SOURCE_BINDING_INVALID")
    return ex


class FrozenInputs:
    def __init__(self,payload):
        p.check(payload,"freeze_import_digest")
        p.require(payload["profiles"]==b.profile_binding() and len(payload["histories"])==2,"FREEZE_FORM_INVALID")
        for history,row in zip(("H1","H2"),payload["histories"],strict=True):
            state=row["frozen_payload"]
            p.check(state,"state_digest")
            p.require(row["history_id"]==history and row["binding"]["history"]==history
                and state["phase"]=="FROZEN" and state["n"]==4 and state["profile_digest"]==p.PROFILE
                and row["alpha_binary64_hex"]==state["alpha"].hex() and len(b.canonical(state))<=4096,"FREEZE_FORM_INVALID")
        self.data=b.canonical(payload)
        self._bound=self.data
        self.closed=False

    def snapshot(self):
        p.require(not self.closed and self.data==self._bound,"FREEZE_BINDING_CHANGED")
        return json.loads(self.data)

    def coefficients(self):
        return tuple(h["frozen_payload"]["alpha"] for h in self.snapshot()["histories"])

    def release(self):
        self.closed=True
        self.data=self._bound=None


def evidence_for(site,arm,states,stream_id):
    return [dict(history=h,state_digest=states[j],stream_id=stream_id,target=site["prediction_binding"]["target"],
        site_digest=site["site_digest"],target_window_digest=site["target_window_digest"],
        score_digest=b.digest(site[arm]["scores"][h]),mae=site[arm]["scores"][h]["mae"])
        for j,h in enumerate(("H1","H2"))]


class PrefixStream:
    def __init__(self,sources,work,reader,frozen):
        p.require(type(sources) is list and len(sources)==5 and len({x["stream_id"] for x in sources})==1,"STREAM_INPUT_INVALID")
        for k,row in enumerate(sources):
            p.check(row,"source_digest")
            p.require(row["window_ordinal"]==k,"SOURCE_ORDER_INVALID")
        frozen.snapshot()
        self._sources=tuple(b.canonical(x) for x in sources)
        self.work,self.reader,self.frozen=work,reader,frozen
        self._offset=work.values["analyze_returns"]
        self._windows,self._sites=(),()
        self._pending,self._committed,self._previous=None,None,None
        self.error_evidence=None
        self.closed=False

    def _check_pending(self):
        p.require(self._pending is not None and self._committed is not None,"PREDICTION_BINDING_MISSING")
        p.require(self._pending==self._committed,"PREDICTION_BINDING_CHANGED")
        payload=json.loads(self._committed)
        p.check(payload,"binding_digest")
        p.require(payload["freeze_import_digest"]==self.frozen.snapshot()["freeze_import_digest"],"FREEZE_BINDING_CHANGED")

    def _errors(self,n):
        if n==2:
            p.require(self._previous is None and self.error_evidence is None,"ERROR_PROVENANCE_INVALID")
            return dict(primary=None,direct=None)
        p.require(type(self._previous) is bytes and self._sites and self._previous==self._sites[-1],"ERROR_PROVENANCE_INVALID")
        previous=json.loads(self._previous)
        p.check(previous,"site_digest")
        sid=json.loads(self._sources[0])["stream_id"]
        p.require(previous["prediction_binding"]["target"]==n-1
            and previous["prediction_binding"]["stream_id"]==sid
            and previous["target_window_digest"]==json.loads(self._windows[-1])["window_digest"],"ERROR_PROVENANCE_INVALID")
        states=[h["frozen_payload"]["state_digest"] for h in self.frozen.snapshot()["histories"]]
        expected={a:evidence_for(previous,a,states,sid) for a in ("primary","direct")}
        p.require(type(self.error_evidence) is bytes and self.error_evidence==b.canonical(expected),"ERROR_PROVENANCE_INVALID")
        return expected

    def bind_predictions(self):
        n=len(self._windows)
        p.require(not self.closed and 2<=n<5 and self._pending is None,"BINDING_PHASE_INVALID")
        p.require(self.work.values["analyze_returns"]==self._offset+n,"PREFIX_PROGRESS_INVALID")
        frozen=self.frozen.snapshot()
        self.work.phase="PAST_ERROR_BINDING"
        evidence=self._errors(n)
        prefix=tuple(tuple(json.loads(row)["projection"]["values"]) for row in self._windows[-3:])
        self.work.phase="PREDICTION_BINDING"
        outputs={}
        for arm,fn in (("primary",p.predict),("direct",direct.direct_predict)):
            errors=None if evidence[arm] is None else tuple(x["mae"] for x in evidence[arm])
            outputs[arm]=fn(self.frozen.coefficients(),prefix,errors)
            for key,num in p.step_work(outputs[arm]).items():
                if key not in ("error_terms","mae_sums","gains"):
                    self.work.add(arm+"_"+key,num)
        p.require(b.canonical(outputs["primary"])==b.canonical(outputs["direct"]),"BASELINE_DIFFERS")
        binding=b.sealed(dict(stream_id=json.loads(self._sources[0])["stream_id"],target=n,origin=n-1,
            completed_analyses_before=self.work.values["analyze_returns"],
            prefix_digests=[json.loads(row)["window_digest"] for row in self._windows],
            freeze_import_digest=frozen["freeze_import_digest"],error_evidence=evidence,**outputs),"binding_digest")
        data=b.canonical(binding)
        p.require(len(data)<=65536,"BINDING_SIZE_EXCEEDED")
        self._pending=self._committed=data
        self.work.add("bound_sites")
        return data

    def read_next(self,k):
        p.require(not self.closed and type(k) is int and k==len(self._windows) and k<5,"FUTURE_ACCESS_DENIED")
        self.frozen.snapshot()
        if k>=2:
            self._check_pending()
        source=json.loads(self._sources[k])
        self.work.source_id=source["source_id"]
        self.work.phase="SOURCE_PROCESSING"
        row=self.reader(source,self.work)
        p.check(row,"window_digest")
        p.require(row["source_id"]==source["source_id"] and row["source_digest"]==source["source_digest"]
            and row["pcm_sha256"]==source["pcm_sha256"] and row["projection"]["profile_digest"]==p.PROFILE,"WINDOW_BINDING_INVALID")
        p.require(self.work.values["analyze_returns"]==self._offset+k+1,"READER_PROGRESS_INVALID")
        target=tuple(row["projection"]["values"])
        p.vector(target)
        self.frozen.snapshot()
        if k>=2:
            self._check_pending()
            binding=json.loads(self._committed)
            scores={}
            self.work.phase="ERROR_CALCULATION"
            for arm,fn in (("primary",p.score),("direct",direct.direct_score)):
                scores[arm]=fn(binding[arm],target)
                for key in ("error_terms","mae_sums","gains"):
                    self.work.add(arm+"_"+key,p.step_work(binding[arm])[key])
            p.require(b.canonical(scores["primary"])==b.canonical(scores["direct"]),"BASELINE_DIFFERS")
            site=b.sealed(dict(prediction_binding=binding,target_window_digest=row["window_digest"],
                completed_analyses_after=self.work.values["analyze_returns"],**scores),"site_digest")
            self._previous=b.canonical(site)
            self._sites+=(self._previous,)
            states=[h["frozen_payload"]["state_digest"] for h in self.frozen.snapshot()["histories"]]
            self.error_evidence=b.canonical({a:evidence_for(site,a,states,source["stream_id"]) for a in ("primary","direct")})
            self._pending=self._committed=None
        self._windows+=(b.canonical(row),)
        self.work.add("completed_windows")

    def close(self):
        p.require(not self.closed and len(self._windows)==5 and len(self._sites)==3 and self._pending is None,"CLOSE_INVALID")
        self.frozen.snapshot()
        result=b.sealed(dict(stream_id=json.loads(self._sources[0])["stream_id"],windows=[json.loads(x) for x in self._windows],
            sites=[json.loads(x) for x in self._sites],closed=True),"stream_digest")
        self.abort()
        return result

    def abort(self):
        self.closed=True
        self._windows,self._sites,self._sources=(),(),()
        self.error_evidence=self._previous=self._pending=self._committed=None


def execute(plan,reader,run_id,work=None):
    work=p.Work() if work is None else work
    streams,active,frozen,failure=[],None,None,None
    try:
        p.check(plan,"execution_digest")
        p.require(len(plan["sources"])==30 and plan["profiles"]==b.profile_binding(),"PLAN_BINDING_INVALID")
        frozen=FrozenInputs(plan["freeze_import"])
        for s in range(6):
            active=PrefixStream(plan["sources"][s*5:s*5+5],work,reader,frozen)
            for k in range(5):
                if k>=2:
                    active.bind_predictions()
                active.read_next(k)
            streams.append(active.close())
            active=None
        frozen.snapshot()
        p.count_form(work.values,p.limits())
    except Exception as exc:
        failure=dict(phase=work.phase,source_id=work.source_id,code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),
            error_class=type(exc).__name__,work=dict(work.values))
        streams=[]
    finally:
        if active is not None:
            active.abort()
        if frozen is not None:
            frozen.release()
    result=dict(schema="s2ny.prefix-recommendation.v1",run_id=run_id,status="RECORDING_COMPLETE" if failure is None else "NOT_EVALUABLE",
        execution_digest=plan["execution_digest"],profiles=plan["profiles"],sources=plan["sources"],freeze_import=plan["freeze_import"],
        carriers=reader.carriers,streams=streams,closed=True,work=dict(work.values),failure=failure,evaluation=None,
        main_gate_after=False,limits=p.limits(),verification_limits=p.verification_limits())
    if len(b.canonical(result))+128>p.MAX_OUTPUT_BYTES:
        result.update(status="NOT_EVALUABLE",streams=[],failure=dict(phase="RESULT_SIZE",source_id=None,
            code="OUTPUT_SIZE_EXCEEDED",error_class="S2NYPredictionError",work=dict(work.values)))
    return b.sealed(result,"record_digest")


def make_reader(plan):
    def generate(source):
        n=source["ordinal"]-1
        p.require(type(n) is int and 0<=n<30,"SOURCE_BINDING_INVALID")
        spec=b.specs()[n]
        p.require(source==b.bind_source(spec,source["pcm_sha256"]),"SOURCE_BINDING_INVALID")
        return b.pcm_window(spec)
    reader=nw.AudioReader(plan["profiles"],generate)
    p.require(reader.np.__version__==plan["environment"]["numpy"]["version"]
        and b.filehash(Path(reader.np.__file__))==plan["environment"]["numpy"]["files"].get(str(Path(reader.np.__file__).resolve())),"NUMPY_BINDING_INVALID")
    return reader


def run_main_once(run_id):
    global MAIN_GATE
    created=False
    work=p.Work()
    before={}
    phase="QUALIFICATION_BINDING"
    try:
        p.require(MAIN_GATE is True and b.MAIN_GATE is False and nw.MAIN_GATE is False and nw.nv.MAIN_GATE is False,"MAIN_GATE_CLOSED")
        p.require(type(run_id) is str and re.fullmatch(r"s2ny-prefix-recommendation-\d{8}-\d{2}",run_id),"RUN_ID_INVALID")
        out=OUT_ROOT/run_id
        out.mkdir(exist_ok=False)
        created=True
        before=watched()
        q=read(QUAL_DIR/"result.json","result_digest")
        p.require(q["status"]=="S2NY_PREDICTION_QUALIFIED" and q["run_id"]==QUAL_ID and q["passed_tests"]==30
            and q["unittest_calls"]==1 and q["exit_code"]==0 and q["hashes_before"]==q["hashes_after"]==before,"QUALIFICATION_INVALID")
        phase="SOURCE_BINDING"
        plan=load_presealed()
        atomic(out/"preregistration.json",dict(run_id=run_id,execution_digest=EXECUTION_DIGEST,seal_digest=SEAL_DIGEST,
            hashes=before,limits=p.limits(),verification_limits=p.verification_limits(),retry=False),65536)
        phase="RECEPTOR_INIT"
        result=execute(plan,make_reader(plan),run_id,work)
        phase="FINAL_CODE_BINDING"
        p.require(watched()==before,"CODE_CHANGED")
        result.pop("record_digest")
        result.update(code_hashes_before=before,code_hashes_after=before,seal_digest=SEAL_DIGEST)
        result=b.sealed(result,"record_digest")
        p.require(len(b.canonical(result))<=p.MAX_OUTPUT_BYTES,"OUTPUT_SIZE_EXCEEDED")
    except Exception as exc:
        if not created:
            raise
        result=b.sealed(dict(schema="s2ny.prefix-recommendation.v1",run_id=run_id,status="NOT_EVALUABLE",
            execution_digest=EXECUTION_DIGEST,seal_digest=SEAL_DIGEST,streams=[],work=dict(work.values),failure=dict(
                phase=phase,source_id=work.source_id,code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),error_class=type(exc).__name__,work=dict(work.values)),
            evaluation=None,main_gate_after=False,limits=p.limits(),verification_limits=p.verification_limits(),
            code_hashes_before=before,code_hashes_after={path:b.filehash(b.ROOT/path) for path in before}),"record_digest")
    finally:
        MAIN_GATE=False
    atomic(out/"result.json",result,p.MAX_OUTPUT_BYTES)
    return out


def verify_file_once(out):
    with (out/"verification.claim").open("xb"):
        pass
    before=b.filehash(out/"result.json")
    try:
        record=read(out/"result.json","record_digest")
        p.require(record["run_id"]==out.name and record["seal_digest"]==SEAL_DIGEST
            and record["code_hashes_before"]==record["code_hashes_after"]==watched(),"RUN_BINDING_INVALID")
        report=direct.verify_record(record,load_presealed())
        report.pop("verification_digest")
        p.require(before==b.filehash(out/"result.json") and MAIN_GATE is False,"READ_ONLY_INVALID")
        report.update(file_sha256_before=before,file_sha256_after=before,verification_calls=1)
    except Exception as exc:
        report=dict(status="NOT_EVALUABLE",phase="VERIFICATION",code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),evaluation_allowed=False,verification_calls=1)
    report=b.sealed(report,"verification_digest")
    atomic(out/"verification.json",report,p.MAX_VERIFICATION_BYTES)
    return report


def evaluate_file_once(out):
    from tools import _s2ny_private_prediction_evaluation as evaluation
    with (out/"evaluation.claim").open("xb"):
        pass
    result=evaluation.evaluate(read(out/"result.json","record_digest"),read(out/"verification.json","verification_digest"),
        read(SEAL_DIR/"evaluation-plan.json","evaluation_digest"))
    atomic(out/"evaluation.json",result,262144)
    return result
