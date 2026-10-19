"""Replay stored synthetic vectors only: python -m tools.s2uc_four_arm_check."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from collections.abc import Mapping

from tools import _s2uc_four_arm as four
from tools import _s2uc_record_codec as codec
from tools import _s2tu_retained_trace as tu

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports/s2uc/four-arm-20260930-01"
SOURCE = ROOT / "reports/s2uc/p2-supplier-correction-20260930-01/final/retained-success"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def normalized(value):
    if isinstance(value, tu.Frame):
        return (value.profile, value.segment, value.ordinal, tuple(x.hex() for x in value.values))
    if isinstance(value, dict):
        return {key: normalized(item) for key, item in value.items() if key != "owner"}
    if isinstance(value, (tuple, list)):
        return tuple(normalized(item) for item in value)
    return value


def reachable_frames(value, found, seen):
    if id(value) in seen:
        return
    seen.add(id(value))
    if isinstance(value, tu.Frame):
        found[id(value)] = value
    elif isinstance(value, Mapping):
        for item in value.values():
            reachable_frames(item, found, seen)
    elif isinstance(value, (tuple, list)):
        for item in value:
            reachable_frames(item, found, seen)
    elif isinstance(value, (tu.RetainedTrace, four.ub.CandidateTrace)):
        reachable_frames(value.frames, found, seen)
    elif type(value).__module__ in {four.__name__, four.ub.__name__, four.tw.__name__, tu.__name__}:
        reachable_frames(vars(value), found, seen)


class TemporaryObserver:
    """Line-boundary live Frame census; never stores frame references after callback."""
    def __init__(self, hint_ordinals):
        self.hint_ordinals = hint_ordinals
        self.peak_trace = self.peak_hint = self.peak_total = 0
        self.ns = 0
        self.samples = 0
        self.files = {str(Path(module.__file__).resolve()) for module in (four, four.ub, four.tw, tu)}

    def trace(self, frame, event, arg):
        if frame.f_code.co_filename not in self.files:
            return None
        start = time.perf_counter_ns()
        found, seen = {}, set()
        cursor = frame
        while cursor is not None:
            if cursor.f_code.co_filename in self.files:
                reachable_frames(cursor.f_locals, found, seen)
            cursor = cursor.f_back
        hints = sum(item.ordinal in self.hint_ordinals for item in found.values())
        self.peak_hint = max(self.peak_hint, hints)
        self.peak_trace = max(self.peak_trace, len(found) - hints)
        self.peak_total = max(self.peak_total, len(found))
        self.samples += 1
        self.ns += time.perf_counter_ns() - start
        return self.trace


def phase(function):
    before = tracemalloc.get_traced_memory()[0]
    tracemalloc.reset_peak()
    start = time.perf_counter_ns()
    result = function()
    elapsed = time.perf_counter_ns() - start
    current, peak = tracemalloc.get_traced_memory()
    return result, dict(elapsed_ns=elapsed, traced_net_bytes=current-before,
                        traced_incremental_peak_bytes=max(0, peak-before))


def lineage(arm):
    return [dict(generation=t.generation, formation=t.frames[0].segment,
                 ordinals=[f.ordinal for f in t.frames]) for t in four.retained(arm)]


def replay(record, prereg, provenance):
    results = {name: dict(hints=[], transitions=[], resources=[], reference_checks=0,
                          playback_ns=0, memory_call_ns=0, observation_ns=0)
               for name in four.ARMS}
    truth = {h['key']: h for h in provenance['hints']}
    for name, factory in four.ARMS.items():
        out = results[name]
        stream_hash = hashlib.sha256()
        hint_ordinals = {e['ordinal'] for s in record['stories'] for e in s['events'] if e['kind'] == 'HINT'}
        observer = TemporaryObserver(hint_ordinals)
        for story in record['stories']:
            profile = story['events'][0]['materialization']['projection_binding']['profile_digest']
            arm = factory(profile, f"four-arm/{story['story']}/{name}")
            reference = {'I2':'immediate', 'B1':'candidate'}.get(name)
            transitions = {t['ordinal']: t for t in story['transitions']}
            hints = {h['ordinal']: h for h in story['hints']}
            hint_before = None
            for event in story['events']:
                start = time.perf_counter_ns()
                ordinal = event['ordinal']
                kind = event['kind']
                segment = event['segment']
                if kind != 'CLOSE':
                    values = tuple(float.fromhex(v) for v in event['values_hex'])
                    frame = tu.Frame(values, profile, f"four-arm/{story['story']}/{name}", segment, ordinal)
                stream_hash.update(json.dumps([kind, ordinal, segment, event.get('values_hex')], separators=(',', ':')).encode())
                out['playback_ns'] += time.perf_counter_ns() - start
                start = time.perf_counter_ns()
                before = arm.evidence()
                if kind == 'HINT' and hint_before is None:
                    hint_before = before
                out['observation_ns'] += time.perf_counter_ns() - start
                start = time.perf_counter_ns()
                sys.settrace(observer.trace)
                try:
                    receipt = arm.close_segment(segment) if kind == 'CLOSE' else arm.form(frame) if kind == 'FORMATION' else arm.hint(frame)
                finally:
                    sys.settrace(None)
                out['memory_call_ns'] += time.perf_counter_ns() - start
                start = time.perf_counter_ns()
                resources = arm.resources()
                assert resources['trace_frames'] <= prereg['limits_trace_frames'][name]
                assert resources['hint_frames'] <= 2
                out['resources'].append(dict(story=story['story'], ordinal=ordinal, **resources))
                if reference:
                    expected = transitions[ordinal][reference] if kind == 'CLOSE' else event[reference]
                    assert normalized(receipt) == normalized(expected), (name, ordinal, 'receipt')
                    out['reference_checks'] += 1
                    if kind == 'CLOSE':
                        assert arm.inventory == transitions[ordinal][reference+'_inventory']
                        out['reference_checks'] += 1
                    if ordinal in hints:
                        assert normalized(hint_before) == normalized(hints[ordinal][reference+'_before'])
                        assert normalized(arm.evidence()) == normalized(hints[ordinal][reference+'_after'])
                        out['reference_checks'] += 2
                if kind == 'CLOSE':
                    out['transitions'].append(dict(story=story['story'], ordinal=ordinal, segment=segment,
                                                   receipt=receipt, retained=lineage(arm), candidate_generation=getattr(arm, 'candidate_generation', None)))
                if kind == 'HINT' and receipt is not None:
                    key = f"{story['story']}/{ordinal}"
                    stored = lineage(arm)
                    matches = [dict(**next(t for t in stored if t['generation'] == generation), offset=offset)
                               for generation, offset in receipt['matches']]
                    target = truth[key]['target']['formations']
                    correct = receipt['decision'] == 'TRACE_MATCH' and len(matches) == 1 and matches[0]['formation'] in target
                    expected = prereg['predicted_correct'][key][prereg['arms'].index(name)]
                    decision_expected = prereg['true_decision'] if expected else prereg['false_decision']
                    out['hints'].append(dict(key=key, receipt=receipt, matches=matches, retained=stored,
                                             correct_target=correct, expected_correct=expected,
                                             prediction='CONFIRMED' if correct == expected and receipt['decision'] == decision_expected else 'VIOLATED'))
                    hint_before = None
                out['observation_ns'] += time.perf_counter_ns() - start
                del before
            if reference:
                assert normalized(arm.evidence()) == normalized(story['before_close'][reference])
                out['reference_checks'] += 1
            arm.close_owner()
            assert all(v == 0 for v in arm.resources().values())
            if reference:
                assert normalized(arm.evidence()) == normalized(story['closed'][reference])
                out['reference_checks'] += 1
        out['input_sha256'] = stream_hash.hexdigest()
        out['temporary'] = dict(peak_live_trace_frames=observer.peak_trace, peak_live_hint_frames=observer.peak_hint,
                                peak_live_total_frames=observer.peak_total, samples=observer.samples, observer_ns=observer.ns)
        assert observer.peak_trace <= prereg['limits_trace_frames'][name]
        assert observer.peak_hint <= 2
    assert len({out['input_sha256'] for out in results.values()}) == 1
    return results


def main():
    prereg_bytes = (OUTPUT/'preregistration.json').read_bytes()
    prereg = json.loads(prereg_bytes)
    for name, sha in prereg['bindings'].items():
        assert digest((ROOT/name).read_bytes()) == sha, name
    tracemalloc.start()
    (record, provenance), loading = phase(lambda: (
        codec.loads((SOURCE/'product/record.json').read_bytes()),
        json.loads((SOURCE/'appendix/provenance.json').read_bytes())))
    results, replay_cost = phase(lambda: replay(record, prereg, provenance))
    report = dict(version='s2uc.four-arm.v1', scope='NEUTRAL_SYNTHETIC_DEVELOPMENT',
                  evaluated_utc=datetime.now(timezone.utc).isoformat(), preregistration_sha256=digest(prereg_bytes),
                  arms=results, loading=loading, replay_with_observation=replay_cost,
                  measurement_notes=['tracemalloc measures traced Python allocations, not process RAM.',
                    'Phase peaks are incremental above live allocations at phase start; not additive.',
                    'Temporary census samples unique Frame identities in active memory stack and arm state at Python trace boundaries.',
                    'Observer snapshots outside the arm are excluded from arm census, included in replay allocations.',
                    'memory_call_ns includes tracing; observer_ns is measured callback work, not total tracing overhead.',
                    'Numerical payload: 384 bytes per frame; aliases do not copy numerical payload.',
                    'Input and observer are only accessible by harness; arms receive single frames or segment close.',
                    'No process RAM measurement; interpreter/native allocations not fully represented.'],
                  bindings_unchanged=all(digest((ROOT/p).read_bytes()) == sha for p,sha in prereg['bindings'].items()))
    report['implementation_sha256'] = {p: digest((ROOT/p).read_bytes()) for p in
        ['tools/_s2uc_four_arm.py', 'tools/s2uc_four_arm_check.py', 'tests/test_s2uc_four_arm.py']}
    payload, serialization = phase(lambda: json.dumps(report, indent=2).encode())
    report['serialization_probe'] = dict(**serialization, serialized_probe_bytes=len(payload))
    # Exclusive output preserves any earlier evaluation.
    with (OUTPUT/'result.json').open('x', encoding='utf-8') as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')
    print(json.dumps({name: {'reference_checks': out['reference_checks'],
          'hints': [(h['key'], h['receipt']['decision'], h['prediction']) for h in out['hints']],
          'temporary': out['temporary']} for name,out in results.items()}, indent=2))


if __name__ == '__main__':
    main()
