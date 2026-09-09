"""Prefix-gated NV execution; no standalone future materialization entry."""
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import re
import sys

from tools import _s2nv_private_prediction as p
from tools import _s2nv_private_prediction_verification as direct
from tools import _s2nu_private_comparison_run as old_io

b = p.b
MAIN_GATE = False
OUT_ROOT = b.ROOT/"reports/s2nv"
SEAL_DIR = OUT_ROOT/b.RUN_ID
QUAL_ID = "s2nv-prediction-qualification-20260909-01"
QUAL_DIR = OUT_ROOT/QUAL_ID
EXECUTION_DIGEST = "37a6a114860f868bda9d7bfbb437ad6f3e8e22820fedc60d49a1622ae209499e"
SEAL_DIGEST = "c927527b71f016e5f359fc2e439c8b58a23672fcb22f8cb959760313ade8507a"
PREVERIFICATION_DIGEST = "5c2bcbd6c0ee9079a170f9c6e9b107453755e262338f3c859ec1152e88731eb7"
OWN = ("tools/_s2nv_private_prediction.py","tools/_s2nv_private_prediction_verification.py",
    "tools/_s2nv_private_prediction_run.py","tools/_s2nv_private_prediction_evaluation.py",
    "tests/test_s2nv_private_prediction.py","reports/s2nv/qualify_prediction_once.py",
    "reports/s2nv/PROGNOSEQUALIFIKATIONSBINDUNG.md")


def atomic(path, value, limit):
    try:
        old_io.atomic(path,value,limit)
    except old_io.c.S2NUComparisonError as exc:
        raise p.S2NVPredictionError(exc.code) from exc


def read(path, key):
    data = path.read_bytes()
    p.require(len(data)<=p.MAX_OUTPUT_BYTES,"INPUT_SIZE_EXCEEDED")
    value = json.loads(data)
    p.require(data==b.canonical(value),"CANONICAL_INPUT_INVALID")
    p.check_root(value,key)
    return value


def watched():
    paths = (*OWN,"tools/_s2nu_private_comparison_run.py","tools/_s2nu_private_comparison.py",
        "tools/_s2nu_private_comparison_verification.py","tools/_s2nu_private_order_evaluation.py",
        "mcm_field_organism/broadband_hearing_path.py")
    result = {**b.watched(),**{path:b.filehash(b.ROOT/path) for path in paths}}
    for name in ("execution-plan.json","evaluation-plan.json","seal.json","verification.json"):
        result[(SEAL_DIR/name).relative_to(b.ROOT).as_posix()] = b.filehash(SEAL_DIR/name)
    return result


def load_presealed():
    plan = read(SEAL_DIR/"execution-plan.json","execution_digest")
    seal = read(SEAL_DIR/"seal.json","seal_digest")
    proof = read(SEAL_DIR/"verification.json","verification_digest")
    p.require(plan["execution_digest"]==seal["execution_digest"]==proof["execution_digest"]==EXECUTION_DIGEST
        and seal["seal_digest"]==proof["seal_digest"]==SEAL_DIGEST
        and proof["verification_digest"]==PREVERIFICATION_DIGEST,"PRESEAL_BINDING_INVALID")
    p.require(seal["status"]=="S2NV_SOURCES_PRESEALED" and proof["status"]=="S2NV_PRESEAL_VERIFIED"
        and proof["verification_calls"]==1,"PRESEAL_NOT_VALID")
    p.require(seal["execution_file_sha256"]==b.filehash(SEAL_DIR/"execution-plan.json")
        and seal["evaluation_file_sha256"]==b.filehash(SEAL_DIR/"evaluation-plan.json"),"PLAN_FILE_CHANGED")
    p.require(plan["source_hashes"]==seal["hashes_before"]==seal["hashes_after"]==b.watched()
        and plan["environment"]==b.environment() and plan["generator"]==b.generator_identity(),"SOURCE_CODE_ENVIRONMENT_CHANGED")
    b.qualification(plan["source_hashes"])
    p.require(len(plan["sources"])==20 and plan["profiles"]==b.profile_binding()
        and plan["prediction_contract"]==b.prediction_contract() and plan["forecast_sites"]==b.forecast_sites()
        and plan["budgets"]==b.budgets(),"PLAN_BINDING_INVALID")
    for spec,row in zip(b.specs(),plan["sources"],strict=True):
        p.require(row==b.bind_source(spec,row["pcm_sha256"]),"SOURCE_BINDING_INVALID")
    return plan


def window_record(source, state, projection):
    raw,half = state.energy,projection.values
    return b.sealed(dict(source_id=source["source_id"],source_digest=source["source_digest"],pcm_sha256=source["pcm_sha256"],
        payload_checked_before_analysis=True,raw_state=state.canonical_payload(),raw_state_digest=state.digest(),
        projection=asdict(projection),raw_hex=[x.hex() for x in raw],half_hex=[x.hex() for x in half],
        raw_f64le_sha256=hashlib.sha256(p.bits(raw)).hexdigest(),half_f64le_sha256=hashlib.sha256(p.bits(half)).hexdigest(),
        raw_subnormal_indices=[i for i,x in enumerate(raw) if 0<x<sys.float_info.min]),"window_digest")


class AudioReader:
    """One-window adapter, invoked only by the prefix controller in the run."""
    def __init__(self, profiles, generate):
        import numpy as np
        from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
        from tools import _s2nj_private_auditory_output_projection as nj
        p.require(profiles==b.profile_binding() and profiles["raw"]==nj.raw_profile_payload()
            and profiles["half"]==nj.profile_payload(),"PROFILE_INVALID")
        self.np,self.nj,self.generate = np,nj,generate
        self.config = LogSpectralConfig(**profiles["raw"]["config"])
        self.receptor = LogSpectralReceptor(self.config)
        self.carriers = list(self.receptor.channel_ids)

    def __call__(self, source, work):
        from mcm_field_organism.broadband_hearing_path import AuditoryReceptorContact, AuditoryReceptorState
        start,end,index = source["window_start_sample"],source["window_end_sample"],source["nj_snapshot_index"]
        work.source_id,work.phase = source["source_id"],"NATIVE_TIME_BINDING"
        p.require(all(type(x) is int for x in (start,end,index)) and start>=0 and start%480==0
            and index==start//480 and end==start+4800 and source["clock_id"]=="audio.sample","SOURCE_TIME_INVALID")
        work.phase = "PCM_GENERATION"
        work.add("generation_attempts")
        payload = self.generate(source)
        try:
            work.phase = "PCM_HASH"
            p.require(type(payload) is bytearray and len(payload)==19200
                and hashlib.sha256(payload).hexdigest()==source["pcm_sha256"],"PCM_HASH_INVALID")
            samples = self.np.frombuffer(payload,dtype="<f4")
            try:
                p.require(samples.shape==(4800,) and self.np.all(self.np.isfinite(samples))
                    and self.np.all(self.np.abs(samples)<=1.0),"PCM_FORM_INVALID")
                work.add("payloads_checked")
                work.phase = "RECEPTOR_ANALYZE"
                work.add("analyze_attempts")
                raw = self.receptor.analyze(samples)
                work.add("analyze_returns")
            finally:
                del samples
        finally:
            del payload
        work.phase = "RAW_STATE_BINDING"
        p.require(type(raw) is tuple and len(raw)==48 and all(type(x) is float and math.isfinite(x) and x>=0 for x in raw),"RAW_VALUES_INVALID")
        activity = AuditoryReceptorContact.ACTIVE_ENERGY if any(x!=0 for x in raw) else AuditoryReceptorContact.ACTIVE_ZERO
        state = AuditoryReceptorState("auditory",self.nj.RAW_GEOMETRY,index,start,end,self.receptor.channel_ids,raw,activity)
        raw_digest = state.digest()
        work.phase = "NJ_PROJECTION"
        work.add("nj_attempts")
        projection = self.nj.project_auditory_half_v1(state,config=self.config,source_profile_digest=self.nj.RAW_PROFILE_DIGEST)
        work.add("nj_returns")
        p.require(state.digest()==raw_digest,"RAW_MUTATED")
        return window_record(source,state,projection)


@dataclass(frozen=True, slots=True)
class PredictionBinding:
    data: bytes
    digest: str

    def __post_init__(self):
        p.require(type(self.data) is bytes and len(self.data)<=65536
            and hashlib.sha256(self.data).hexdigest()==self.digest,"PREDICTION_BINDING_CHANGED")


class PrefixStream:
    def __init__(self, sources, work, reader):
        p.require(type(sources) is list and len(sources)==5 and len({s["stream_id"] for s in sources})==1,"STREAM_INPUT_INVALID")
        self._sources = tuple(b.canonical(s) for s in sources)
        self._work,self._reader = work,reader
        self._offset = work.values["analyze_returns"]
        self._windows,self._sites = (),()
        self._pending,self._committed = None,None
        self._closed = False

    def _check_pending(self):
        p.require(type(self._pending) is PredictionBinding and self._committed is not None,"PREDICTION_BINDING_MISSING")
        self._pending.__post_init__()
        p.require(self._pending.data==self._committed,"PREDICTION_BINDING_CHANGED")

    def bind_predictions(self):
        n = len(self._windows)
        p.require(not self._closed and 2<=n<=4 and self._pending is None,"BINDING_PHASE_INVALID")
        p.require(self._work.values["analyze_returns"]==self._offset+n,"PREFIX_PROGRESS_INVALID")
        rows = [json.loads(x) for x in self._windows]
        previous,last = (tuple(row["projection"]["values"]) for row in rows[-2:])
        li,pi = p.LinearInput(p.PROFILE,previous,last),p.PersistInput(p.PROFILE,last)
        self._work.phase = "PREDICTION_BINDING"
        for arm in ("primary","direct"):
            self._work.add(arm+"_prediction_subtractions",48)
            self._work.add(arm+"_prediction_additions",48)
            self._work.add(arm+"_persist_copies",48)
        primary = dict(LINEAR_TWO_STATE=list(p.linear(li)),PERSIST_LAST=list(p.persist(pi)))
        baseline = direct.direct_predictions(li,pi)
        p.require(b.canonical(primary)==b.canonical(baseline),"BASELINE_DIFFERS")
        value = b.sealed(dict(stream_id=json.loads(self._sources[0])["stream_id"],origin=n-1,target=n,
            available_windows=n,completed_analyses_before=self._work.values["analyze_returns"],
            prefix_digests=[r["window_digest"] for r in rows],half_profile_digest=p.PROFILE,
            functional_prefix=dict(half_profile_digest=p.PROFILE,previous_values=list(previous),last_values=list(last)),
            primary=primary,direct=baseline),"binding_digest")
        data = b.canonical(value)
        self._pending = PredictionBinding(data,hashlib.sha256(data).hexdigest())
        self._committed = data
        self._work.add("bound_sites")
        return self._pending

    def read_next(self, ordinal):
        p.require(not self._closed and type(ordinal) is int and ordinal==len(self._windows) and ordinal<5,"FUTURE_ACCESS_DENIED")
        if ordinal>=2:
            self._check_pending()
        else:
            p.require(self._pending is None,"BINDING_PHASE_INVALID")
        # This is the only reader invocation in the production execution path.
        source = json.loads(self._sources[ordinal])
        row = self._reader(source,self._work)
        p.check_root(row,"window_digest")
        p.require(row["source_digest"]==source["source_digest"] and row["source_id"]==source["source_id"]
            and row["pcm_sha256"]==source["pcm_sha256"] and row["projection"]["profile_digest"]==p.PROFILE,
            "WINDOW_BINDING_INVALID")
        p.require(self._work.values["analyze_returns"]==self._offset+ordinal+1,"READER_PROGRESS_INVALID")
        target = tuple(row["projection"]["values"])
        p.vector(target)
        if ordinal>=2:
            self._check_pending()
            binding = json.loads(self._committed)
            results = {}
            self._work.phase = "ERROR_CALCULATION"
            for arm in ("primary","direct"):
                self._work.add(arm+"_error_terms",96)
                self._work.add(arm+"_mae_sums",2)
                self._work.add(arm+"_gains")
                scorer = p.score if arm=="primary" else direct.direct_score
                scores = {name:scorer(tuple(values),target) for name,values in binding[arm].items()}
                scores["gain"] = scores["PERSIST_LAST"]["mae"]-scores["LINEAR_TWO_STATE"]["mae"]
                results[arm] = scores
            p.require(b.canonical(results["primary"])==b.canonical(results["direct"]),"BASELINE_DIFFERS")
            site = b.sealed(dict(prediction_binding=binding,target_window_digest=row["window_digest"],
                completed_analyses_after=self._work.values["analyze_returns"],**results),"site_digest")
            self._sites += (b.canonical(site),)
            self._pending,self._committed = None,None
        self._windows += (b.canonical(row),)
        self._work.add("completed_windows")

    def close(self):
        p.require(not self._closed and len(self._windows)==5 and len(self._sites)==3 and self._pending is None,"CLOSE_INVALID")
        self._closed = True
        return b.sealed(dict(stream_id=json.loads(self._sources[0])["stream_id"],
            windows=[json.loads(x) for x in self._windows],sites=[json.loads(x) for x in self._sites]),"stream_digest")

    def abort(self):
        self._pending,self._committed = None,None
        self._windows,self._sites = (),()
        self._closed = True


def execute(plan, reader, run_id, work=None):
    work = p.Work() if work is None else work
    streams,active,failure = [],None,None
    try:
        p.check_root(plan,"execution_digest")
        p.require(len(plan["sources"])==20 and plan["profiles"]==b.profile_binding(),"PLAN_BINDING_INVALID")
        for offset in (0,5,10,15):
            active = PrefixStream(plan["sources"][offset:offset+5],work,reader)
            for k in range(5):
                if k>=2:
                    active.bind_predictions()
                active.read_next(k)
            streams.append(active.close())
            active = None
        work.phase,work.source_id = "FINAL_BINDINGS",None
        p.require(work.values==p.work_limits(),"COUNTERS_INVALID")
    except Exception as exc:
        failure = dict(phase=work.phase,source_id=work.source_id,code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),
            error_class=type(exc).__name__,work=dict(work.values))
        streams = []
    finally:
        if active is not None:
            active.abort()
    result = dict(schema="s2nv.prospective-prediction.v1",run_id=run_id,
        status="RECORDING_COMPLETE" if failure is None else "NOT_EVALUABLE",execution_digest=plan["execution_digest"],
        profiles=plan["profiles"],carriers=reader.carriers,streams=streams,work=dict(work.values),failure=failure,
        evaluation=None,main_gate_after=False,limits=p.work_limits(),verification_limits=p.verification_limits())
    if len(b.canonical(result))+128>p.MAX_OUTPUT_BYTES:
        result.update(status="NOT_EVALUABLE",streams=[],failure=dict(phase="RESULT_SIZE",source_id=None,
            code="OUTPUT_SIZE_EXCEEDED",error_class="S2NVPredictionError",work=dict(work.values)))
    return b.sealed(result,"record_digest")


def make_reader(plan):
    def generate(source):
        n = source["ordinal"]-1
        spec = b.WindowSpec(n//5+1,n%5)
        p.require(source==b.bind_source(spec,source["pcm_sha256"]),"SOURCE_BINDING_INVALID")
        return b.pcm_window(spec)
    reader = AudioReader(plan["profiles"],generate)
    loaded = reader.np
    p.require(loaded.__version__==plan["environment"]["numpy"]["version"] and
        b.filehash(Path(loaded.__file__))==plan["environment"]["numpy"]["files"].get(str(Path(loaded.__file__).resolve())),"NUMPY_BINDING_INVALID")
    return reader


def run_main_once(run_id):
    global MAIN_GATE
    out,phase,before,created = None,"QUALIFICATION_BINDING",{},False
    work = p.Work()
    try:
        p.require(MAIN_GATE is True and b.MAIN_GATE is False,"MAIN_GATE_CLOSED")
        p.require(type(run_id) is str and re.fullmatch(r"s2nv-prospective-prediction-\d{8}-\d{2}",run_id),"RUN_ID_INVALID")
        out = OUT_ROOT/run_id
        out.mkdir(exist_ok=False)
        created = True
        before = watched()
        q = read(QUAL_DIR/"result.json","result_digest")
        p.require(q["run_id"]==QUAL_ID and q["status"]=="S2NV_PREDICTION_QUALIFIED"
            and q["passed_tests"]==20 and q["unittest_calls"]==1 and q["exit_code"]==0
            and q["hashes_before"]==q["hashes_after"]==before,"QUALIFICATION_INVALID")
        phase = "SOURCE_BINDING"
        plan = load_presealed()
        atomic(out/"preregistration.json",dict(run_id=run_id,execution_digest=plan["execution_digest"],seal_digest=SEAL_DIGEST,
            hashes=before,limits=p.work_limits(),verification_limits=p.verification_limits(),retry=False),65536)
        phase = "RECEPTOR_INIT"
        reader = make_reader(plan)
        result = execute(plan,reader,run_id,work)
        phase = "FINAL_CODE_BINDING"
        p.require(watched()==before,"CODE_CHANGED")
        result.pop("record_digest")
        result.update(code_hashes_before=before,code_hashes_after=before,seal_digest=SEAL_DIGEST)
        result = b.sealed(result,"record_digest")
        p.require(len(b.canonical(result))<=p.MAX_OUTPUT_BYTES,"OUTPUT_SIZE_EXCEEDED")
    except Exception as exc:
        if not created or (out/"result.json").exists():
            raise
        result = b.sealed(dict(schema="s2nv.prospective-prediction.v1",run_id=run_id,status="NOT_EVALUABLE",
            execution_digest=EXECUTION_DIGEST,seal_digest=SEAL_DIGEST,streams=[],work=dict(work.values),
            failure=dict(phase=phase,source_id=work.source_id,code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),
                error_class=type(exc).__name__,work=dict(work.values)),evaluation=None,main_gate_after=False,
            limits=p.work_limits(),verification_limits=p.verification_limits(),code_hashes_before=before,
            code_hashes_after={path:b.filehash(b.ROOT/path) for path in before}),"record_digest")
    finally:
        MAIN_GATE = False
    atomic(out/"result.json",result,p.MAX_OUTPUT_BYTES)
    return out


def verify_file_once(out):
    with (out/"verification.claim").open("xb"):
        pass
    before = b.filehash(out/"result.json")
    try:
        record = read(out/"result.json","record_digest")
        p.require(record["run_id"]==out.name and record["seal_digest"]==SEAL_DIGEST,"RUN_BINDING_INVALID")
        p.require(record["code_hashes_before"]==record["code_hashes_after"]==watched(),"CODE_CHANGED")
        plan = load_presealed()
        report = direct.verify_record(record,plan)
        report.pop("verification_digest")
        p.require(before==b.filehash(out/"result.json") and MAIN_GATE is False,"READ_ONLY_INVALID")
        report.update(file_sha256_before=before,file_sha256_after=before,verification_calls=1)
    except Exception as exc:
        report = dict(status="NOT_EVALUABLE",phase="VERIFICATION",code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),
            evaluation_allowed=False,verification_calls=1)
    report = b.sealed(report,"verification_digest")
    atomic(out/"verification.json",report,p.MAX_VERIFICATION_BYTES)
    return report


def evaluate_file_once(out):
    from tools import _s2nv_private_prediction_evaluation as evaluation
    with (out/"evaluation.claim").open("xb"):
        pass
    record = read(out/"result.json","record_digest")
    proof = read(out/"verification.json","verification_digest")
    plan = read(SEAL_DIR/"evaluation-plan.json","evaluation_digest")
    result = evaluation.evaluate(record,proof,plan)
    atomic(out/"evaluation.json",result,262144)
    return result
