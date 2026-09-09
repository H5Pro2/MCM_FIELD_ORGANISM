"""NW causal window controller; existing NV IO and receptor adapter unchanged."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from tools import _s2nw_private_learning_prediction as p
from tools import _s2nw_private_learning_verification as direct
from tools import _s2nv_private_prediction_run as nv

b = p.b
MAIN_GATE = False
OUT_ROOT = b.ROOT/"reports/s2nw"
SEAL_DIR = OUT_ROOT/b.RUN_ID
QUAL_ID = "s2nw-learning-qualification-20260909-01"
QUAL_DIR = OUT_ROOT/QUAL_ID
EXECUTION_DIGEST = "96b902af68ffb2662aaa6995756b1ca6c435b157012b17cb1065b18c7d5a4a7c"
SEAL_DIGEST = "9df2bc5147c6e85f51eb1a628bf2f0fffcf851e6037c74f52cfc2b5ef4fe4a65"
PREVERIFICATION_DIGEST = "5707a3147139c291fe4fb9816e718d47710288d9a07d52c225db9fc21a95075b"
OWN = ("tools/_s2nw_private_learning_prediction.py","tools/_s2nw_private_learning_verification.py",
    "tools/_s2nw_private_learning_run.py","tools/_s2nw_private_learning_evaluation.py",
    "tests/test_s2nw_private_learning.py","reports/s2nw/qualify_learning_once.py",
    "reports/s2nw/LERNQUALIFIKATIONSBINDUNG.md")


def atomic(path, value, limit):
    try:
        nv.atomic(path,value,limit)
    except nv.p.S2NVPredictionError as exc:
        raise p.S2NWLearningError(exc.code) from exc


def read(path, key):
    data = path.read_bytes()
    p.require(len(data) <= p.MAX_OUTPUT_BYTES,"INPUT_SIZE_EXCEEDED")
    value = json.loads(data)
    p.require(data == b.canonical(value),"CANONICAL_INPUT_INVALID")
    p.check_root(value,key)
    return value


def watched():
    paths = (*OWN,*nv.OWN[:4],"tools/_s2nv_private_source_binding.py","tests/test_s2nv_private_prediction.py",
        "tools/_s2nu_private_comparison_run.py","tools/_s2nu_private_comparison.py",
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
    p.require(plan["execution_digest"] == seal["execution_digest"] == proof["execution_digest"] == EXECUTION_DIGEST
        and seal["seal_digest"] == proof["seal_digest"] == SEAL_DIGEST
        and proof["verification_digest"] == PREVERIFICATION_DIGEST,"PRESEAL_BINDING_INVALID")
    p.require(seal["status"] == "S2NW_SOURCES_PRESEALED" and proof["status"] == "S2NW_PRESEAL_VERIFIED"
        and proof["verification_calls"] == 1,"PRESEAL_NOT_VALID")
    p.require(seal["execution_file_sha256"] == b.filehash(SEAL_DIR/"execution-plan.json")
        and seal["evaluation_file_sha256"] == b.filehash(SEAL_DIR/"evaluation-plan.json"),"PLAN_FILE_CHANGED")
    p.require(plan["source_hashes"] == seal["hashes_before"] == seal["hashes_after"] == b.watched()
        and plan["environment"] == b.environment() and plan["generator"] == b.generator_identity(),"SOURCE_CODE_ENVIRONMENT_CHANGED")
    b.qualification(plan["source_hashes"])
    p.require(len(plan["sources"]) == 26 and plan["profiles"] == b.profile_binding()
        and plan["prediction_contract"] == b.prediction_contract() and plan["forecast_sites"] == b.forecast_sites()
        and plan["learning_schedule"] == b.learning_schedule() and plan["budgets"] == b.budgets(),"PLAN_BINDING_INVALID")
    for spec,row in zip(b.specs(),plan["sources"],strict=True):
        p.require(row == b.bind_source(spec,row["pcm_sha256"]),"SOURCE_BINDING_INVALID")
    return plan


class AudioReader(nv.AudioReader):
    def __init__(self, profiles, generate):
        try:
            super().__init__(profiles,generate)
        except nv.p.S2NVPredictionError as exc:
            raise p.S2NWLearningError(exc.code) from exc

    def __call__(self, source, work):
        try:
            return super().__call__(source,work)
        except nv.p.S2NVPredictionError as exc:
            raise p.S2NWLearningError(exc.code) from exc


@dataclass(frozen=True, slots=True)
class PredictionBinding:
    data: bytes
    digest: str

    def __post_init__(self):
        p.require(type(self.data) is bytes and len(self.data) <= 65536
            and hashlib.sha256(self.data).hexdigest() == self.digest,"PREDICTION_BINDING_CHANGED")


class LearningPair:
    def __init__(self):
        self.primary,self.direct = p.initial(),direct.direct_initial()
        self._expected = self.payload_bytes()

    def payload_bytes(self):
        return b.canonical(dict(primary=self.primary.payload(),direct=self.direct.payload()))

    def check(self, phase):
        p.require(self.payload_bytes() == self._expected,"LEARNING_CHAIN_INVALID")
        p.require(self.primary.phase == self.direct.phase == phase,"LEARNING_PHASE_INVALID")

    def accept(self, primary, baseline):
        p.require(b.canonical(primary.payload()) == b.canonical(baseline.payload()),"DIRECT_LEARNER_DIFFERS")
        self.primary,self.direct = primary,baseline
        self._expected = self.payload_bytes()

    def change_phase(self, phase):
        self.check("TRAIN" if phase == "FROZEN" else "FROZEN")
        self.accept(p.transition(self.primary,phase),direct.direct_transition(self.direct,phase))
        return json.loads(self._expected)

    def release(self):
        self.primary,self.direct,self._expected = None,None,None


class PrefixStream:
    def __init__(self, sources, work, reader, pair, training):
        length = 6 if training else 5
        p.require(type(training) is bool and type(sources) is list and len(sources) == length
            and len({s["stream_id"] for s in sources}) == 1,"STREAM_INPUT_INVALID")
        pair.check("TRAIN" if training else "FROZEN")
        if training:
            p.require(pair.primary.n == 0,"TRAIN_RESTART_INVALID")
        self._sources = tuple(b.canonical(s) for s in sources)
        self._work,self._reader,self._pair,self._training = work,reader,pair,training
        self._offset = work.values["analyze_returns"]
        self._windows,self._sites = (),()
        self._pending,self._committed,self._observation = None,None,None
        self._closed = False

    def _check_pending(self):
        p.require(type(self._pending) is PredictionBinding and self._committed is not None,"PREDICTION_BINDING_MISSING")
        self._pending.__post_init__()
        p.require(self._pending.data == self._committed,"PREDICTION_BINDING_CHANGED")
        self._pair.check("TRAIN" if self._training else "FROZEN")
        bound = json.loads(self._committed)
        p.require(b.canonical(bound["learning_before"]) == self._pair.payload_bytes(),"LEARNING_CHAIN_INVALID")

    def bind_predictions(self):
        n = len(self._windows)
        p.require(not self._closed and 2 <= n < len(self._sources) and self._pending is None
            and self._observation is None,"BINDING_PHASE_INVALID")
        self._pair.check("TRAIN" if self._training else "FROZEN")
        p.require(self._work.values["analyze_returns"] == self._offset+n,"PREFIX_PROGRESS_INVALID")
        rows = [json.loads(x) for x in self._windows]
        previous,last = (tuple(row["projection"]["values"]) for row in rows[-2:])
        self._work.phase = "PREDICTION_BINDING"
        for arm in ("primary","direct"):
            for key,num in (("prediction_subtractions",96),("prediction_multiplications",48),("prediction_additions",96),("persist_copies",48)):
                self._work.add(arm+"_"+key,num)
        primary = p.predictions(p.LearnedInput(p.PROFILE,self._pair.primary.alpha,previous,last))
        baseline = direct.direct_predictions(p.LearnedInput(p.PROFILE,self._pair.direct.alpha,previous,last))
        p.require(b.canonical(primary) == b.canonical(baseline),"BASELINE_DIFFERS")
        value = b.sealed(dict(stream_id=json.loads(self._sources[0])["stream_id"],origin=n-1,target=n,
            phase="TRAIN" if self._training else "FROZEN",available_windows=n,
            completed_analyses_before=self._work.values["analyze_returns"],prefix_digests=[r["window_digest"] for r in rows],
            functional_prefix=dict(half_profile_digest=p.PROFILE,previous_values=list(previous),last_values=list(last)),
            learning_before=json.loads(self._pair.payload_bytes()),primary=primary,direct=baseline),"binding_digest")
        data = b.canonical(value)
        self._pending = PredictionBinding(data,hashlib.sha256(data).hexdigest())
        self._committed = data
        self._work.add("bound_sites")
        return self._pending

    def update_learning(self):
        p.require(self._training and not self._closed,"TEST_UPDATE_FORBIDDEN")
        p.require(self._observation is not None,"TARGET_NOT_OBSERVED")
        self._check_pending()
        observation,target = self._observation
        n = len(self._windows)
        p.require(self._work.values["analyze_returns"] == self._offset+n+1
            and self._pair.primary.n == n-2,"UPDATE_PROGRESS_INVALID")
        previous,last = (tuple(json.loads(row)["projection"]["values"]) for row in self._windows[-2:])
        self._work.phase = "LEARNING_UPDATE"
        results,markers = {},{}
        for arm,fn,state in (("primary",p.update,self._pair.primary),("direct",direct.direct_update,self._pair.direct)):
            for key in ("update_differences","update_products","update_additions"):
                self._work.add(arm+"_"+key,96)
            self._work.add(arm+"_updates")
            result,mark = fn(state,previous,last,target,observation)
            self._work.add(arm+"_update_divisions",int(mark["division_performed"]))
            results[arm],markers[arm] = result,mark
        p.require(markers["primary"] == markers["direct"],"DIRECT_LEARNER_DIFFERS")
        self._pair.accept(results["primary"],results["direct"])
        self._observation = None
        return dict(observation_digest=observation,states={arm:state.payload() for arm,state in results.items()},markers=markers)

    def read_next(self, ordinal):
        p.require(not self._closed and type(ordinal) is int and ordinal == len(self._windows)
            and ordinal < len(self._sources),"FUTURE_ACCESS_DENIED")
        self._pair.check("TRAIN" if self._training else "FROZEN")
        if ordinal >= 2:
            self._check_pending()
        else:
            p.require(self._pending is None,"BINDING_PHASE_INVALID")
        source = json.loads(self._sources[ordinal])
        row = self._reader(source,self._work)
        p.check_root(row,"window_digest")
        p.require(row["source_digest"] == source["source_digest"] and row["source_id"] == source["source_id"]
            and row["pcm_sha256"] == source["pcm_sha256"] and row["projection"]["profile_digest"] == p.PROFILE,"WINDOW_BINDING_INVALID")
        p.require(self._work.values["analyze_returns"] == self._offset+ordinal+1,"READER_PROGRESS_INVALID")
        target = tuple(row["projection"]["values"])
        p.vector(target)
        if ordinal >= 2:
            self._check_pending()
            binding = json.loads(self._committed)
            results = {}
            self._work.phase = "ERROR_CALCULATION"
            for arm,scorer in (("primary",p.score),("direct",direct.direct_score)):
                for key,num in (("error_terms",144),("mae_sums",3),("gains",2)):
                    self._work.add(arm+"_"+key,num)
                scores = {name:scorer(tuple(values),target) for name,values in binding[arm].items()}
                scores["gains"] = {name:scores[name]["mae"]-scores["LEARNED_DELTA"]["mae"] for name in p.BASELINES}
                results[arm] = scores
            p.require(b.canonical(results["primary"]) == b.canonical(results["direct"]),"BASELINE_DIFFERS")
            observation = b.digest(dict(binding_digest=binding["binding_digest"],target_window_digest=row["window_digest"],
                completed_analyses_after=self._work.values["analyze_returns"],primary_score_digest=b.digest(results["primary"]),
                direct_score_digest=b.digest(results["direct"])))
            learning_update = None
            if self._training:
                self._observation = (observation,target)
                learning_update = self.update_learning()
            site = b.sealed(dict(prediction_binding=binding,target_window_digest=row["window_digest"],
                completed_analyses_after=self._work.values["analyze_returns"],learning_update=learning_update,**results),"site_digest")
            self._sites += (b.canonical(site),)
            self._pending,self._committed = None,None
        self._windows += (b.canonical(row),)
        self._work.add("completed_windows")

    def close(self):
        p.require(not self._closed and len(self._windows) == len(self._sources)
            and len(self._sites) == len(self._sources)-2 and self._pending is None and self._observation is None,"CLOSE_INVALID")
        self._pair.check("TRAIN" if self._training else "FROZEN")
        self._closed = True
        return b.sealed(dict(stream_id=json.loads(self._sources[0])["stream_id"],windows=[json.loads(x) for x in self._windows],
            sites=[json.loads(x) for x in self._sites]),"stream_digest")

    def abort(self):
        self._pending,self._committed,self._observation = None,None,None
        self._windows,self._sites = (),()
        self._closed = True


def execute(plan, reader, run_id, work=None):
    work = p.Work() if work is None else work
    streams,active,failure,learning,pair = [],None,None,None,None
    try:
        p.check_root(plan,"execution_digest")
        p.require(len(plan["sources"]) == 26 and plan["profiles"] == b.profile_binding(),"PLAN_BINDING_INVALID")
        pair = LearningPair()
        learning = dict(initial=json.loads(pair.payload_bytes()))
        for s,(offset,length) in enumerate(((0,6),(6,5),(11,5),(16,5),(21,5))):
            active = PrefixStream(plan["sources"][offset:offset+length],work,reader,pair,s == 0)
            for k in range(length):
                if k >= 2:
                    active.bind_predictions()
                active.read_next(k)
            streams.append(active.close())
            active = None
            if s == 0:
                work.phase = "FREEZE"
                learning["frozen"] = pair.change_phase("FROZEN")
        work.phase = "LEARNER_CLOSE"
        learning["closed"] = pair.change_phase("CLOSED")
        work.phase,work.source_id = "FINAL_BINDINGS",None
        p.complete_counts(work.values,p.work_limits())
    except Exception as exc:
        failure = dict(phase=work.phase,source_id=work.source_id,code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),
            error_class=type(exc).__name__,work=dict(work.values))
        streams,learning = [],None
    finally:
        if active is not None:
            active.abort()
        if pair is not None:
            pair.release()
    result = dict(schema="s2nw.learned-prediction.v1",run_id=run_id,status="RECORDING_COMPLETE" if failure is None else "NOT_EVALUABLE",
        execution_digest=plan["execution_digest"],profiles=plan["profiles"],carriers=reader.carriers,streams=streams,learning=learning,
        work=dict(work.values),failure=failure,evaluation=None,main_gate_after=False,limits=p.work_limits(),verification_limits=p.verification_limits())
    if len(b.canonical(result))+128 > p.MAX_OUTPUT_BYTES:
        result.update(status="NOT_EVALUABLE",streams=[],learning=None,failure=dict(phase="RESULT_SIZE",source_id=None,
            code="OUTPUT_SIZE_EXCEEDED",error_class="S2NWLearningError",work=dict(work.values)))
    return b.sealed(result,"record_digest")


def make_reader(plan):
    def generate(source):
        n = source["ordinal"]-1
        spec = b.WindowSpec(0,n) if n < 6 else b.WindowSpec((n-6)//5+1,(n-6)%5)
        p.require(source == b.bind_source(spec,source["pcm_sha256"]),"SOURCE_BINDING_INVALID")
        return b.pcm_window(spec)
    reader = AudioReader(plan["profiles"],generate)
    loaded = reader.np
    p.require(loaded.__version__ == plan["environment"]["numpy"]["version"]
        and b.filehash(Path(loaded.__file__)) == plan["environment"]["numpy"]["files"].get(str(Path(loaded.__file__).resolve())),"NUMPY_BINDING_INVALID")
    return reader


def run_main_once(run_id):
    global MAIN_GATE
    out,phase,before,created = None,"QUALIFICATION_BINDING",{},False
    work = p.Work()
    try:
        p.require(MAIN_GATE is True and b.MAIN_GATE is False and nv.MAIN_GATE is False,"MAIN_GATE_CLOSED")
        p.require(type(run_id) is str and re.fullmatch(r"s2nw-learned-prediction-\d{8}-\d{2}",run_id),"RUN_ID_INVALID")
        out = OUT_ROOT/run_id
        out.mkdir(exist_ok=False)
        created = True
        before = watched()
        q = read(QUAL_DIR/"result.json","result_digest")
        p.require(q["run_id"]==QUAL_ID and q["status"]=="S2NW_LEARNING_QUALIFIED"
            and q["passed_tests"]==28 and q["unittest_calls"]==1 and q["exit_code"]==0
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
        result = b.sealed(dict(schema="s2nw.learned-prediction.v1",run_id=run_id,status="NOT_EVALUABLE",
            execution_digest=EXECUTION_DIGEST,seal_digest=SEAL_DIGEST,streams=[],learning=None,work=dict(work.values),
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
    from tools import _s2nw_private_learning_evaluation as evaluation
    with (out/"evaluation.claim").open("xb"):
        pass
    record = read(out/"result.json","record_digest")
    proof = read(out/"verification.json","verification_digest")
    plan = read(SEAL_DIR/"evaluation-plan.json","evaluation_digest")
    result = evaluation.evaluate(record,proof,plan)
    atomic(out/"evaluation.json",result,262144)
    return result
