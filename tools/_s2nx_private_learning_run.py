"""Private causal two-history controller. No historical entry is repurposed."""
import hashlib
import json
import re
from pathlib import Path
from tools import _s2nx_private_learning_prediction as p
from tools import _s2nw_private_learning_run as nw
from tools import _s2nw_private_learning_verification as direct

b = p.b
MAIN_GATE = False
OUT_ROOT = b.ROOT/"reports/s2nx"
SEAL_DIR = OUT_ROOT/b.RUN_ID
QUAL_ID = "s2nx-learning-qualification-20260909-01"
QUAL_DIR = OUT_ROOT/QUAL_ID
EXECUTION_DIGEST = "f52992815d49889334b11f64a13e00879984ce4cabecd3670a0fcf2d7441b80c"
SEAL_DIGEST = "2c6d26ccacfb55341b513d9f240973335d076e69c5a4bd134092c06471953f42"
PREVERIFICATION_DIGEST = "3ce0b1d01818e228ca18b6e1786aaa9e6062ed3442d262e0366e296056a8a93e"
OWN = ("tools/_s2nx_private_learning_prediction.py", "tools/_s2nx_private_learning_run.py",
    "tools/_s2nx_private_learning_verification.py", "tools/_s2nx_private_learning_evaluation.py",
    "tests/test_s2nx_private_learning.py", "reports/s2nx/qualify_learning_once.py",
    "reports/s2nx/LERNQUALIFIKATIONSBINDUNG.md")
LAYOUT = ((0, 6), (6, 6), (12, 5), (17, 5), (22, 5), (27, 5))
read = nw.read
AudioReader = nw.AudioReader


def atomic(path, value, limit):
    try:
        nw.atomic(path, value, limit)
    except p.nw.S2NWLearningError as exc:
        raise p.S2NXLearningError(exc.code) from exc


def watched():
    paths = (*OWN, *nw.OWN[:4], *nw.nv.OWN[:4], "tools/_s2nv_private_source_binding.py",
        "tools/_s2nu_private_comparison_run.py", "tools/_s2nu_private_comparison.py",
        "tools/_s2nu_private_comparison_verification.py", "tools/_s2nu_private_order_evaluation.py",
        "mcm_field_organism/broadband_hearing_path.py", "tests/test_s2nv_private_prediction.py")
    result = {**b.watched(), **{path: b.filehash(b.ROOT/path) for path in paths}}
    for name in ("execution-plan.json", "evaluation-plan.json", "seal.json", "verification.json"):
        result[(SEAL_DIR/name).relative_to(b.ROOT).as_posix()] = b.filehash(SEAL_DIR/name)
    return result


def load_presealed():
    plan = read(SEAL_DIR/"execution-plan.json", "execution_digest")
    seal = read(SEAL_DIR/"seal.json", "seal_digest")
    proof = read(SEAL_DIR/"verification.json", "verification_digest")
    p.require(plan["execution_digest"] == seal["execution_digest"] == proof["execution_digest"] == EXECUTION_DIGEST
        and seal["seal_digest"] == proof["seal_digest"] == SEAL_DIGEST
        and proof["verification_digest"] == PREVERIFICATION_DIGEST, "PRESEAL_BINDING_INVALID")
    p.require(seal["status"] == "S2NX_SOURCES_PRESEALED" and proof["status"] == "S2NX_PRESEAL_VERIFIED"
        and proof["verification_calls"] == 1, "PRESEAL_NOT_VALID")
    p.require(seal["execution_file_sha256"] == b.filehash(SEAL_DIR/"execution-plan.json")
        and seal["evaluation_file_sha256"] == b.filehash(SEAL_DIR/"evaluation-plan.json"), "PLAN_FILE_CHANGED")
    p.require(plan["source_hashes"] == seal["hashes_before"] == seal["hashes_after"] == b.watched()
        and plan["environment"] == b.environment() and plan["generator"] == b.generator_identity(), "SOURCE_CODE_ENVIRONMENT_CHANGED")
    b.qualification(plan["source_hashes"])
    p.require(plan["profiles"] == b.profile_binding() and plan["prediction_contract"] == b.prediction_contract()
        and plan["learning_schedule"] == b.learning_schedule() and plan["forecast_sites"] == b.forecast_sites()
        and plan["budgets"] == b.budgets() and len(plan["sources"]) == 32, "PLAN_BINDING_INVALID")
    for spec, row in zip(b.specs(), plan["sources"], strict=True):
        p.require(row == b.bind_source(spec, row["pcm_sha256"]), "SOURCE_BINDING_INVALID")
    return plan


def history_binding(history, sources):
    return b.sealed(dict(history=history, source_digests=[s["source_digest"] for s in sources]), "history_digest")


class LearningPair(nw.LearningPair):
    def __init__(self, history, sources):
        p.require(history in p.HISTORIES and len(sources) == 6, "HISTORY_BINDING_INVALID")
        self.binding = b.canonical(history_binding(history, sources))
        self._bound = self.binding
        super().__init__()

    def check(self, phase):
        p.require(self.binding == self._bound, "HISTORY_BINDING_INVALID")
        try:
            super().check(phase)
        except p.nw.S2NWLearningError as exc:
            raise p.S2NXLearningError(exc.code) from exc

    def bound_payload(self):
        return dict(binding=json.loads(self.binding), states=json.loads(self.payload_bytes()))


class Histories:
    def __init__(self, sources):
        self.pairs = {h: LearningPair(h, sources[i*6:i*6+6]) for i, h in enumerate(p.HISTORIES)}
        self._owners = dict(self.pairs)
        self._bindings = {h: pair.binding for h, pair in self.pairs.items()}
        self.freezes = {}
        self._frozen_bytes = None

    def check(self, training=None):
        p.require(set(self.pairs) == set(p.HISTORIES) and all(self.pairs[h] is self._owners[h]
            and self.pairs[h].binding == self._bindings[h] for h in p.HISTORIES), "HISTORY_BINDING_INVALID")
        if training is not None:
            p.require(training in p.HISTORIES, "HISTORY_BINDING_INVALID")
            self.pairs[training].check("TRAIN")
            if training == "H2":
                p.require("H1" in self.freezes, "FREEZE_BINDING_MISSING")
                self.pairs["H1"].check("FROZEN")
        else:
            p.require(set(self.freezes) == set(p.HISTORIES) and self._frozen_bytes == b.canonical(self.freezes), "FREEZE_BINDING_MISSING")
            for h in p.HISTORIES:
                self.pairs[h].check("FROZEN")
                p.require(b.canonical(self.pairs[h].bound_payload()) == b.canonical(self.freezes[h]), "FREEZE_BINDING_INVALID")

    def snapshot(self, training=None):
        self.check(training)
        return {h: self.pairs[h].bound_payload() for h in ((training,) if training else p.HISTORIES)}

    def freeze(self, history):
        self.check(history)
        p.require(history not in self.freezes, "FREEZE_BINDING_INVALID")
        self.pairs[history].change_phase("FROZEN")
        self.freezes[history] = self.pairs[history].bound_payload()
        if len(self.freezes) == 2:
            self._frozen_bytes = b.canonical(self.freezes)

    def close(self):
        self.check()
        result = {}
        for h in p.HISTORIES:
            self.pairs[h].change_phase("CLOSED")
            result[h] = self.pairs[h].bound_payload()
        return result

    def release(self):
        for pair in self._owners.values():
            pair.release()
        self.pairs.clear()
        self.freezes.clear()
        self._owners.clear()
        self._bindings.clear()
        self._frozen_bytes = None


class PrefixStream:
    def __init__(self, sources, work, reader, histories, training=None):
        histories.check(training)
        p.require(type(sources) is list and len(sources) == (6 if training else 5)
            and len({s["stream_id"] for s in sources}) == 1, "STREAM_INPUT_INVALID")
        if training:
            pair = histories.pairs[training]
            p.require(pair.primary.n == 0 and pair.binding == b.canonical(history_binding(training, sources)), "HISTORY_BINDING_INVALID")
        for k, source in enumerate(sources):
            p.check_root(source, "source_digest")
            p.require(source["window_ordinal"] == k, "SOURCE_ORDER_INVALID")
        self._sources = tuple(b.canonical(s) for s in sources)
        self._work, self._reader, self._histories, self._training = work, reader, histories, training
        self._offset = work.values["analyze_returns"]
        self._windows, self._sites = (), ()
        self._pending, self._committed, self._observation = None, None, None
        self._closed = False

    def _check_pending(self):
        p.require(type(self._pending) is nw.PredictionBinding and self._committed is not None, "PREDICTION_BINDING_MISSING")
        try:
            self._pending.__post_init__()
        except p.nw.S2NWLearningError as exc:
            raise p.S2NXLearningError(exc.code) from exc
        p.require(self._pending.data == self._committed, "PREDICTION_BINDING_CHANGED")
        p.require(b.canonical(json.loads(self._committed)["learning_before"])
            == b.canonical(self._histories.snapshot(self._training)), "LEARNING_CHAIN_INVALID")

    def bind_predictions(self):
        from tools import _s2nx_private_learning_verification as verification
        n = len(self._windows)
        p.require(not self._closed and 2 <= n < len(self._sources) and self._pending is None
            and self._observation is None, "BINDING_PHASE_INVALID")
        learning = self._histories.snapshot(self._training)
        p.require(self._work.values["analyze_returns"] == self._offset+n, "PREFIX_PROGRESS_INVALID")
        previous, last = (tuple(json.loads(r)["projection"]["values"]) for r in self._windows[-2:])
        self._work.phase = "PREDICTION_BINDING"
        predictions = {}
        for arm, fn in (("primary", p.predict), ("direct", verification.direct_predict)):
            for key, num in p.step_work(bool(self._training)).items():
                if key.startswith("prediction_") or key == "persist_copies":
                    self._work.add(arm+"_"+key, num)
            coefficients = tuple(self._histories.pairs[h].primary.alpha if arm == "primary"
                else self._histories.pairs[h].direct.alpha for h in learning)
            learned, controls = fn(coefficients, previous, last)
            predictions[arm] = {**dict(zip(learning, learned, strict=True)), **controls}
        p.require(b.canonical(predictions["primary"]) == b.canonical(predictions["direct"]), "BASELINE_DIFFERS")
        value = b.sealed(dict(stream_id=json.loads(self._sources[0])["stream_id"], origin=n-1, target=n,
            phase="TRAIN" if self._training else "FROZEN", active_histories=list(learning), available_windows=n,
            completed_analyses_before=self._work.values["analyze_returns"], prefix_digests=[json.loads(r)["window_digest"] for r in self._windows],
            functional_prefix=dict(half_profile_digest=p.PROFILE, previous_values=list(previous), last_values=list(last)),
            learning_before=learning, **predictions), "binding_digest")
        data = b.canonical(value)
        self._pending = nw.PredictionBinding(data, hashlib.sha256(data).hexdigest())
        self._committed = data
        self._work.add("bound_sites")
        return self._pending

    def update_learning(self):
        p.require(self._training is not None and not self._closed, "TEST_UPDATE_FORBIDDEN")
        p.require(self._observation is not None, "TARGET_NOT_OBSERVED")
        self._check_pending()
        observation, target = self._observation
        pair = self._histories.pairs[self._training]
        n = len(self._windows)
        p.require(self._work.values["analyze_returns"] == self._offset+n+1 and pair.primary.n == n-2, "UPDATE_PROGRESS_INVALID")
        previous, last = (tuple(json.loads(r)["projection"]["values"]) for r in self._windows[-2:])
        self._work.phase = "LEARNING_UPDATE"
        results, markers = {}, {}
        for arm, fn, state in (("primary", p.nw.update, pair.primary), ("direct", direct.direct_update, pair.direct)):
            for key in ("update_differences", "update_products", "update_additions"):
                self._work.add(arm+"_"+key, 96)
            self._work.add(arm+"_updates")
            results[arm], markers[arm] = fn(state, previous, last, target, observation)
            self._work.add(arm+"_update_divisions", int(markers[arm]["division_performed"]))
        p.require(markers["primary"] == markers["direct"], "DIRECT_LEARNER_DIFFERS")
        pair.accept(results["primary"], results["direct"])
        self._observation = None
        return dict(history=self._training, observation_digest=observation, states={a: s.payload() for a, s in results.items()}, markers=markers)

    def read_next(self, ordinal):
        from tools import _s2nx_private_learning_verification as verification
        p.require(not self._closed and type(ordinal) is int and ordinal == len(self._windows)
            and ordinal < len(self._sources), "FUTURE_ACCESS_DENIED")
        self._histories.check(self._training)
        if ordinal >= 2:
            self._check_pending()
        source = json.loads(self._sources[ordinal])
        row = self._reader(source, self._work)
        p.check_root(row, "window_digest")
        p.require(row["source_digest"] == source["source_digest"] and row["source_id"] == source["source_id"]
            and row["pcm_sha256"] == source["pcm_sha256"] and row["projection"]["profile_digest"] == p.PROFILE, "WINDOW_BINDING_INVALID")
        p.require(self._work.values["analyze_returns"] == self._offset+ordinal+1, "READER_PROGRESS_INVALID")
        target = tuple(row["projection"]["values"])
        p.vector(target)
        if ordinal >= 2:
            self._check_pending()
            binding = json.loads(self._committed)
            results = {}
            self._work.phase = "ERROR_CALCULATION"
            for arm, scorer in (("primary", p.nw.score), ("direct", direct.direct_score)):
                for key in ("error_terms", "mae_sums", "gains"):
                    self._work.add(arm+"_"+key, p.step_work(bool(self._training))[key])
                results[arm] = p.scores(binding[arm], target, binding["active_histories"]) if arm == "primary" else verification.scores(
                    binding[arm], target, binding["active_histories"], scorer)
            p.require(b.canonical(results["primary"]) == b.canonical(results["direct"]), "BASELINE_DIFFERS")
            observation = b.digest(dict(binding_digest=binding["binding_digest"], target_window_digest=row["window_digest"],
                completed_analyses_after=self._work.values["analyze_returns"], primary_score_digest=b.digest(results["primary"]),
                direct_score_digest=b.digest(results["direct"])))
            learning_update = None
            if self._training:
                self._observation = (observation, target)
                learning_update = self.update_learning()
            site = b.sealed(dict(prediction_binding=binding, target_window_digest=row["window_digest"],
                completed_analyses_after=self._work.values["analyze_returns"], learning_update=learning_update, **results), "site_digest")
            self._sites += (b.canonical(site),)
            self._pending, self._committed = None, None
        self._windows += (b.canonical(row),)
        self._work.add("completed_windows")

    def close(self):
        p.require(not self._closed and len(self._windows) == len(self._sources)
            and len(self._sites) == len(self._sources)-2 and self._pending is None and self._observation is None, "CLOSE_INVALID")
        self._histories.check(self._training)
        self._closed = True
        return b.sealed(dict(stream_id=json.loads(self._sources[0])["stream_id"], windows=[json.loads(x) for x in self._windows],
            sites=[json.loads(x) for x in self._sites]), "stream_digest")

    def abort(self):
        self._pending, self._committed, self._observation = None, None, None
        self._windows, self._sites = (), ()
        self._closed = True


def execute(plan, reader, run_id, work=None):
    work = p.Work() if work is None else work
    streams, active, failure, learning, histories = [], None, None, None, None
    try:
        p.check_root(plan, "execution_digest")
        p.require(len(plan["sources"]) == 32 and plan["profiles"] == b.profile_binding(), "PLAN_BINDING_INVALID")
        histories = Histories(plan["sources"])
        learning = dict(initial={h: pair.bound_payload() for h, pair in histories.pairs.items()})
        for s, (offset, length) in enumerate(LAYOUT):
            history = p.HISTORIES[s] if s < 2 else None
            active = PrefixStream(plan["sources"][offset:offset+length], work, reader, histories, history)
            for k in range(length):
                if k >= 2:
                    active.bind_predictions()
                active.read_next(k)
            streams.append(active.close())
            active = None
            if history:
                work.phase = "FREEZE"
                histories.freeze(history)
            if s == 1:
                learning["frozen"] = json.loads(b.canonical(histories.freezes))
        work.phase = "LEARNER_CLOSE"
        learning["closed"] = histories.close()
        work.phase, work.source_id = "FINAL_BINDINGS", None
        p.count_form(work.values, p.work_limits(), True)
    except Exception as exc:
        failure = dict(phase=work.phase, source_id=work.source_id, code=getattr(exc, "code", "TECHNICAL_EXECUTION_ERROR"),
            error_class=type(exc).__name__, work=dict(work.values))
        streams, learning = [], None
    finally:
        if active is not None:
            active.abort()
        if histories is not None:
            histories.release()
    result = dict(schema="s2nx.crossed-learning.v1", run_id=run_id, status="RECORDING_COMPLETE" if failure is None else "NOT_EVALUABLE",
        execution_digest=plan["execution_digest"], profiles=plan["profiles"], carriers=reader.carriers, streams=streams, learning=learning,
        work=dict(work.values), failure=failure, evaluation=None, main_gate_after=False, limits=p.work_limits(), verification_limits=p.verification_limits())
    if len(b.canonical(result))+128 > p.MAX_OUTPUT_BYTES:
        result.update(status="NOT_EVALUABLE", streams=[], learning=None, failure=dict(phase="RESULT_SIZE", source_id=None,
            code="OUTPUT_SIZE_EXCEEDED", error_class="S2NXLearningError", work=dict(work.values)))
    return b.sealed(result, "record_digest")


def make_reader(plan):
    def generate(source):
        n = source["ordinal"]-1
        p.require(type(n) is int and 0 <= n < 32, "SOURCE_BINDING_INVALID")
        spec = b.specs()[n]
        p.require(source == b.bind_source(spec, source["pcm_sha256"]), "SOURCE_BINDING_INVALID")
        return b.pcm_window(spec)
    reader = AudioReader(plan["profiles"], generate)
    loaded = reader.np
    p.require(loaded.__version__ == plan["environment"]["numpy"]["version"]
        and b.filehash(Path(loaded.__file__)) == plan["environment"]["numpy"]["files"].get(str(Path(loaded.__file__).resolve())), "NUMPY_BINDING_INVALID")
    return reader


def run_main_once(run_id):
    global MAIN_GATE
    out, phase, before, created = None, "QUALIFICATION_BINDING", {}, False
    work = p.Work()
    try:
        p.require(MAIN_GATE is True and b.MAIN_GATE is False and nw.MAIN_GATE is False and nw.nv.MAIN_GATE is False, "MAIN_GATE_CLOSED")
        p.require(type(run_id) is str and re.fullmatch(r"s2nx-crossed-learning-\d{8}-\d{2}", run_id), "RUN_ID_INVALID")
        out = OUT_ROOT/run_id
        out.mkdir(exist_ok=False)
        created = True
        before = watched()
        q = read(QUAL_DIR/"result.json", "result_digest")
        p.require(q["run_id"] == QUAL_ID and q["status"] == "S2NX_LEARNING_QUALIFIED" and q["passed_tests"] == 32
            and q["unittest_calls"] == 1 and q["exit_code"] == 0 and q["hashes_before"] == q["hashes_after"] == before, "QUALIFICATION_INVALID")
        phase = "SOURCE_BINDING"
        plan = load_presealed()
        atomic(out/"preregistration.json", dict(run_id=run_id, execution_digest=plan["execution_digest"], seal_digest=SEAL_DIGEST,
            hashes=before, limits=p.work_limits(), verification_limits=p.verification_limits(), retry=False), 65536)
        phase = "RECEPTOR_INIT"
        result = execute(plan, make_reader(plan), run_id, work)
        phase = "FINAL_CODE_BINDING"
        p.require(watched() == before, "CODE_CHANGED")
        result.pop("record_digest")
        result.update(code_hashes_before=before, code_hashes_after=before, seal_digest=SEAL_DIGEST)
        result = b.sealed(result, "record_digest")
        p.require(len(b.canonical(result)) <= p.MAX_OUTPUT_BYTES, "OUTPUT_SIZE_EXCEEDED")
    except Exception as exc:
        if not created or (out/"result.json").exists():
            raise
        result = b.sealed(dict(schema="s2nx.crossed-learning.v1", run_id=run_id, status="NOT_EVALUABLE",
            execution_digest=EXECUTION_DIGEST, seal_digest=SEAL_DIGEST, streams=[], learning=None, work=dict(work.values),
            failure=dict(phase=phase, source_id=work.source_id, code=getattr(exc, "code", "TECHNICAL_EXECUTION_ERROR"),
                error_class=type(exc).__name__, work=dict(work.values)), evaluation=None, main_gate_after=False,
            limits=p.work_limits(), verification_limits=p.verification_limits(), code_hashes_before=before,
            code_hashes_after={path: b.filehash(b.ROOT/path) for path in before}), "record_digest")
    finally:
        MAIN_GATE = False
    atomic(out/"result.json", result, p.MAX_OUTPUT_BYTES)
    return out


def verify_file_once(out):
    from tools import _s2nx_private_learning_verification as verification
    with (out/"verification.claim").open("xb"):
        pass
    before = b.filehash(out/"result.json")
    try:
        record = read(out/"result.json", "record_digest")
        p.require(record["run_id"] == out.name and record["seal_digest"] == SEAL_DIGEST, "RUN_BINDING_INVALID")
        p.require(record["code_hashes_before"] == record["code_hashes_after"] == watched(), "CODE_CHANGED")
        report = verification.verify_record(record, load_presealed())
        report.pop("verification_digest")
        p.require(before == b.filehash(out/"result.json") and MAIN_GATE is False, "READ_ONLY_INVALID")
        report.update(file_sha256_before=before, file_sha256_after=before, verification_calls=1)
    except Exception as exc:
        report = dict(status="NOT_EVALUABLE", phase="VERIFICATION", code=getattr(exc, "code", "TECHNICAL_BINDING_ERROR"),
            evaluation_allowed=False, verification_calls=1)
    report = b.sealed(report, "verification_digest")
    atomic(out/"verification.json", report, p.MAX_VERIFICATION_BYTES)
    return report


def evaluate_file_once(out):
    from tools import _s2nx_private_learning_evaluation as evaluation
    with (out/"evaluation.claim").open("xb"):
        pass
    result = evaluation.evaluate(read(out/"result.json", "record_digest"), read(out/"verification.json", "verification_digest"),
        read(SEAL_DIR/"evaluation-plan.json", "evaluation_digest"))
    atomic(out/"evaluation.json", result, 262144)
    return result
