"""External bounded evidence and resource accounting, never an input to policy."""
import json
import sys
import tracemalloc

from tools._s2uc_multi_error import CELL, HEAD, ENTRY, MultiErrorAdapter, POLICY
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_pair_context_adapter import PerceptionSample
from tools._s2uc_paired_error_ema import mae48, require
from tools._s2uc_signal_approx_adapter import SignalApproxAdapter
from tools._s2uc_continuation_adapter import consume_prediction
from tools._s2uc_origin_judge import GatedReplay
from tools.s2uc_continuous_comparison import state
from tools._s2uc_ema_stock_observer import digest
from tools._s2tu_retained_trace import Frame, RetainedTrace
from tools._s2ub_candidate_confirmation import CandidateTrace


def cells(a):
    return [dict(generation=r[0], ec=r[1], ep=r[2], role=r[3], offset=r[4], quality=r[5])
            for i in range(6) if (r := CELL.unpack_from(a.bank, i*32))[-1]]


def owned(a):
    seen = set()
    def size(v):
        if v is None or id(v) in seen: return 0
        seen.add(id(v))
        if isinstance(v, Frame): return 0
        n = sys.getsizeof(v)
        if isinstance(v, (list, tuple)): n += sum(size(x) for x in v)
        return n
    n = sys.getsizeof(a)+sys.getsizeof(vars(a))
    for key, value in vars(a).items():
        if key not in ('arm', 'pair', 'intervals', 'pending_prediction', '_checkpoint'):
            n += size(value)
    if a.pending_prediction:
        n += sys.getsizeof(a.pending_prediction)+size(a.pending_prediction.provenance_json)
    return n


class Meter:
    def __init__(self, a):
        self.a = a
        self.heap = self.frames = self.combined = self.slots = self.receipt = 0
        self.frame_bound = self.combined_bound = 0
        self.calls = []

    def measure(self, name, operation):
        a = self.a
        originals = list(a.pair)+list(a.arm._forming)+list(a.arm._hints)
        for _, _, fs in a._sources(): originals.extend(fs)
        originals.extend(x for x in a._frozen if x is not None)
        if a._pframe is not None: originals.append(a._pframe)
        # Only accept_perception creates one Frame; admission otherwise moves existing objects.
        bound = len({id(x) for x in originals})+int(name == 'perception')
        self.frame_bound = max(self.frame_bound, bound)
        self.combined_bound = max(self.combined_bound, bound+2)
        require(bound <= 18 and bound+2 <= 20, 'MULTI_FRAME_BOUND')
        del originals
        retained = owned(self.a)
        tracemalloc.start()
        base = tracemalloc.get_traced_memory()[0]
        try: return operation()
        finally:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            total = retained+max(0, peak-base)
            self.heap = max(self.heap, total)
            self.calls.append(dict(operation=name, retained=retained, transient=peak-base, total=total))
            require(total <= 16384, 'MULTI_PYTHON_BUDGET')

    def trace(self, frame, event, arg):
        # Separate qualification pass; never combined with heap measurement.
        # Traverse all active production locals, including containers/trace holders.
        if not frame.f_code.co_filename.replace('\\', '/').split('/')[-1].startswith('_s2'):
            return self.trace
        found, visited = set(), set()
        def collect(v):
            if id(v) in visited: return
            visited.add(id(v))
            if isinstance(v, Frame): found.add(id(v))
            elif isinstance(v, (RetainedTrace, CandidateTrace)): collect(v.frames)
            elif isinstance(v, (tuple, list)):
                for x in v: collect(x)
            elif isinstance(v, dict):
                for x in v.values(): collect(x)
        a = self.a
        for v in (a.pair, a.arm._forming, a.arm._hints, a.arm._retained_many,
                  a.arm._candidate, a._frozen, a._pframe): collect(v)
        cursor = frame
        while cursor:
            if cursor.f_code.co_filename.replace('\\', '/').split('/')[-1].startswith('_s2'):
                for v in tuple(cursor.f_locals.values()): collect(v)
            cursor = cursor.f_back
        n = len(found)
        slots = 0 if a.pending_prediction is None else 1+int(a.pending_prediction.context_values is not None)
        self.frames = max(self.frames, n)
        self.slots = max(self.slots, slots)
        self.combined = max(self.combined, n+slots)
        require(n <= 18 and slots <= 2 and n+slots <= 20, 'MULTI_FRAME_BUDGET')
        return self.trace

    def snapshot(self):
        return dict(additional_python_peak=self.heap, original_frames_peak=self.frames,
                    output_slots_peak=self.slots, combined_peak=self.combined,
                    original_frames_upper_bound=self.frame_bound, combined_upper_bound=self.combined_bound,
                    packed=416, receipt_bytes_peak=self.receipt,
                    utf8_upper=2*self.receipt, calls=self.calls)


def replay(values, profile, *, count, evidence=None):
    require(type(count) is int and 4 <= count <= 64 and count % 2 == 0, 'MULTI_REPLAY_BOUND')
    out = {} if evidence is None else evidence
    out.update(rows=[], forecasts=[], updates=[], states=[], admissions=[])
    a = MultiErrorAdapter(FactorRecencyArm(profile, 'owner'), 'stream', multi_policy=POLICY)
    ref = SignalApproxAdapter(FactorRecencyArm(profile, 'owner'), 'stream')
    source = GatedReplay(iter(values), profile)
    meter = Meter(a)
    try:
        for _ in range(count):
            s = source.take(a)
            if a.pending_prediction:
                p = a.pending_prediction
                out['rows'].append(dict(target=s.index, selected_mae=mae48(a.selected_values, s.values),
                    decision=p.status, choice=HEAD.unpack_from(a.bank, 192)[3],
                    persistence_mae=mae48(p.persistence_values, s.values)))
                old = cells(a)
                frozen = []
                expected = { (r['role'], r['generation'], r['offset']): dict(r) for r in old }
                for i in range(HEAD.unpack_from(a.bank, 192)[2]):
                    g, role, off, q, dest = ENTRY.unpack_from(a.bank, 208+16*i)
                    ec, ep = mae48(a._frozen[i].values, s.values), mae48(a._pframe.values, s.values)
                    live = a._generation_live(role, g)
                    frozen.append(dict(generation=g, role=role, offset=off, original_ordinal=a._frozen[i].ordinal,
                                       ec=ec, ep=ep, live=live))
                    if live:
                        prev = expected.get((role, g, off))
                        expected[role, g, off] = dict(generation=g, role=role, offset=off, quality=0,
                            ec=ec if prev is None else .5*prev['ec']+.5*ec,
                            ep=ep if prev is None else .5*prev['ep']+.5*ep)
                record = dict(target=s.index, before=old, hypotheses=frozen, status='STARTED')
                out['updates'].append(record)
                meter.measure('feedback', lambda: a.consume_feedback(s))
                key = lambda r: (r['role'], r['generation'], r['offset'])
                require(sorted(cells(a), key=key) == sorted(expected.values(), key=key), 'MULTI_OBSERVER_UPDATE')
                record.update(after=cells(a), status='COMPLETE')
                consume_prediction(ref, s)
            before = cells(a)
            admission = dict(index=s.index, before=before, status='STARTED')
            out['admissions'].append(admission)
            receipt = meter.measure('perception', lambda: a.accept_perception(s))
            ref.accept_perception(s)
            require(state(a.arm) == state(ref.arm), 'MULTI_MEMORY_CHANGED')
            admission.update(after=cells(a), status='COMPLETE')
            out['states'].append(digest(state(a.arm)))
            if receipt:
                meter.receipt = max(meter.receipt, len(receipt.json_text.encode()))
                out['forecasts'].append(json.loads(receipt.json_text))
        end = a.pending_prediction.target_index
        meter.measure('finish', a.finish_story)
        ref.release_prediction(); ref.finish_story()
        require(end == count+1 and not any(a.bank) and a._frozen == [None]*6, 'MULTI_RELEASE')
        out.update(arm='U', frames=count, censored_target=end, resources=meter.snapshot(),
                   slots_released=True, states_identical=True)
        return out
    finally:
        source.close()
        if not a.closed: a._terminate()
        if not ref.closed: ref._terminate()
