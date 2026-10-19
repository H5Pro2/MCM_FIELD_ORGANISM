import copy
import json
import unittest

from tools import _s2ts_temporal_trace_run as source
from tools import _s2tu_retained_trace as trace
from tools import _s2tu_run as run
from tools import _s2tu_source_schedule as schedule
from tools import _s2tu_verification as verification


def record():
    bound = schedule.binding()
    sources, _ = source.source_rows()
    values = dict(a=0.10, b=0.20, c=0.30, d=0.40)
    labels = {"nu-s02-w00": "a", "nu-s02-w01": "b", "nu-s02-w02": "c", "nu-s02-w03": "d"}
    store = trace.RetainedTraceStore(bound["profile"], "s2tu-owner-01")
    endpoints, transitions, decisions = [], [], []
    counts = dict(audio=0, nj=0, endpoints=0, formations=0, hints=0, segment_closes=0, owner_closes=0)
    for event in bound["events"]:
        if event["kind"] == "SEGMENT_CLOSE":
            transitions.append(store.close_segment(event["segment"]))
            counts["segment_closes"] += 1
            continue
        src = sources[event["source_id"]]
        value = values[labels[event["source_id"]]]
        encoded = [value.hex()] * 48
        endpoints.append(dict(ordinal=event["ordinal"], source_id=event["source_id"], pcm_sha256=src["pcm_sha256"],
                              payload_hash_checked=True, frame=dict(owner=event["owner"], segment=event["segment"],
                              ordinal=event["ordinal"], native_end=src["window_end_sample"], runtime_time=event["ordinal"]),
                              values=encoded, value_digest=run.digest(encoded)))
        frame = trace.Frame((value,) * 48, bound["profile"], event["owner"], event["segment"], event["ordinal"])
        result = store.form(frame) if event["kind"] == "FORMATION" else store.hint(frame)
        counts["audio"] += 1; counts["nj"] += 1; counts["endpoints"] += 1
        if event["kind"] == "FORMATION":
            counts["formations"] += 1
        else:
            counts["hints"] += 1
            if result is not None:
                decisions.append(dict(ordinal=event["ordinal"], result=result))
    retained = list(store.generations)
    store.close_owner(); counts["owner_closes"] += 1
    # The production boundary stores tuples as canonical JSON arrays.
    return json.loads(run.canonical(dict(status="RECORDING_COMPLETE", run_id=run.RUN_ID, binding=bound,
        binding_digest=run.digest(bound), counts=counts, endpoints=endpoints, transitions=transitions,
        decisions=decisions, retained_generations_before_owner_close=retained, owner_closed=True)))


class S2TUVerificationTests(unittest.TestCase):
    def test_neutral_full_chain_is_verified(self):
        result = verification.verify(record())
        self.assertEqual(result, dict(status="VERIFIED", read_only=True, decisions=4, transitions=3, retained_generations=[2, 3]))

    def test_source_and_value_manipulations_fail_closed(self):
        for field, value, code in (("source_id", "wrong", "SOURCE_BINDING_INVALID"), ("value_digest", "0" * 64, "VALUE_DIGEST_INVALID")):
            with self.subTest(field=field):
                item = copy.deepcopy(record()); item["endpoints"][0][field] = value
                with self.assertRaisesRegex(verification.S2TUVerificationError, code):
                    verification.verify(item)

    def test_transition_decision_and_owner_manipulations_fail_closed(self):
        cases = []
        item = copy.deepcopy(record()); item["transitions"][2]["evicted"] = None; cases.append((item, "TRANSITIONS_INVALID"))
        item = copy.deepcopy(record()); item["decisions"][3]["result"]["decision"] = "TRACE_MATCH"; cases.append((item, "DECISIONS_INVALID"))
        item = copy.deepcopy(record()); item["retained_generations_before_owner_close"] = [1, 2]; cases.append((item, "OWNER_CLOSE_INVALID"))
        for item, code in cases:
            with self.subTest(code=code):
                with self.assertRaisesRegex(verification.S2TUVerificationError, code):
                    verification.verify(item)
