"""NX composition of unchanged NW scalar arithmetic and fixed controls."""
from tools import _s2nw_private_learning_prediction as nw
from tools import _s2nx_private_source_binding as b

PROFILE = nw.PROFILE
MAX_OUTPUT_BYTES = 2097152
MAX_VERIFICATION_BYTES = 262144
BASELINES = ("PERSIST", "LINEAR", "FIXED_HALF")
HISTORIES = ("H1", "H2")
vector, bits, check_root = nw.vector, nw.bits, nw.check_root


class S2NXLearningError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NXLearningError(code)


def predict(coefficients, previous, last):
    require(type(coefficients) is tuple and len(coefficients) in (1, 2), "COEFFICIENT_FORM_INVALID")
    learned = [list(nw.learned(nw.LearnedInput(PROFILE, a, previous, last))) for a in coefficients]
    return learned, dict(
        FIXED_HALF=list(nw.learned(nw.LearnedInput(PROFILE, 0.5, previous, last))),
        LINEAR=list(nw.historical.linear(nw.historical.LinearInput(PROFILE, previous, last))),
        PERSIST=list(nw.historical.persist(nw.historical.PersistInput(PROFILE, last))))


def scores(predictions, target, histories):
    result = {name: nw.score(tuple(values), target) for name, values in predictions.items()}
    gains = {}
    for history in histories:
        gains[history] = {}
        for baseline in BASELINES:
            gains[history][baseline] = result[baseline]["mae"]-result[history]["mae"]
    result["gains"] = gains
    result["cross_gain"] = None if len(histories) == 1 else result["H2"]["mae"]-result["H1"]["mae"]
    return result


def work_limits():
    result = dict(generation_attempts=32, payloads_checked=32, analyze_attempts=32, analyze_returns=32,
        nj_attempts=32, nj_returns=32, completed_windows=32, bound_sites=20,
        raw_payloads_persisted=0, rolling_hops=0, memory_calls=0, field_calls=0, context_calls=0, runtime_calls=0)
    for arm in ("primary", "direct"):
        result.update({arm+"_"+key: value for key, value in dict(
            prediction_subtractions=3456, prediction_multiplications=2496, prediction_additions=3456,
            persist_copies=960, update_differences=768, update_products=768, update_additions=768,
            updates=8, update_divisions=8, error_terms=4416, mae_sums=92, gains=108).items()})
    return result


def verification_limits():
    return dict(halvings=1536, prediction_subtractions=6912, prediction_multiplications=4992,
        prediction_additions=6912, persist_copies=1920, update_differences=1536, update_products=1536,
        update_additions=1536, updates=16, update_divisions=16, error_terms=8832, mae_sums=184,
        gains=216, windows=32, sites=20)


def step_work(training):
    h = 1 if training else 2
    return dict(prediction_subtractions=(h+2)*48, prediction_multiplications=(h+1)*48,
        prediction_additions=(h+2)*48, persist_copies=48, error_terms=(h+3)*48,
        mae_sums=h+3, gains=3 if training else 7)


class Work:
    def __init__(self):
        self.values = dict.fromkeys(work_limits(), 0)
        self.phase, self.source_id = "INITIALIZATION", None

    def add(self, key, n=1):
        require(type(n) is int and n >= 0 and key in self.values and self.values[key]+n <= work_limits()[key], "WORK_LIMIT_EXCEEDED")
        self.values[key] += n


def count_form(counts, limits, complete=False):
    require(set(counts) == set(limits) and all(type(x) is int and 0 <= x <= limits[k] for k, x in counts.items()), "COUNTERS_INVALID")
    if complete:
        require(all(counts[k] == v for k, v in limits.items() if not k.endswith("update_divisions")), "COMPLETE_COUNTERS_INVALID")
