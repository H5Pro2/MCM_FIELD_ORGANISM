import unittest
from copy import deepcopy
import json
from tools import _s2ts_temporal_trace as ts
from tools import _s2ts_temporal_trace_run as run
from tools import _s2ts_temporal_trace_verification as verify

P = "a" * 64


class TraceRunTests(unittest.TestCase):
    def test_bound_sequence_has_20_events_and_neutral_results(self):
        events = run.schedule()
        frames = {}
        values = {"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0}
        for event in events:
            if event["source_id"]:
                frames[event["ordinal"]] = ts.Frame((values[event["label"]],) * 48, P, event["session"], event["ordinal"], 1, event["runtime_time"])
        result = run.execute_frames(events, frames)
        self.assertEqual(len(events), 20)
        self.assertEqual([x["result"]["decision"] for x in result["decisions"]], ["TRACE_MATCH", "ABSTAIN_ORDER_MISMATCH", "ABSTAIN_ORDER_MISMATCH", "ABSTAIN_NO_TRACE", "ABSTAIN_AMBIGUOUS_OFFSET"])

    def test_source_binding_and_independent_verification_reject_tampering(self):
        bound = run.binding(); events = tuple(bound["events"]); frames = {}; rows = []
        values = {"a": 0.1, "b": 0.2, "c": 0.3, "d": 0.4}; source_rows, _ = run.source_rows()
        for event in events:
            if event["source_id"] is None:
                continue
            value = values[event["label"]]; ordinal = event["ordinal"]
            frame = ts.Frame((value,) * 48, P, event["session"], ordinal, source_rows[event["source_id"]]["window_end_sample"], event["runtime_time"])
            frames[ordinal] = frame
            rows.append(dict(ordinal=ordinal, source_id=event["source_id"], pcm_sha256=source_rows[event["source_id"]]["pcm_sha256"], payload_hash_checked=True,
                             half_values_hex=[x.hex() for x in frame.values], frame=dict(native_end=frame.native_end, runtime_time=frame.runtime_time, value_digest=frame.value_digest)))
        record = dict(status="RECORDING_COMPLETE", binding=bound, endpoints=rows, trace=run.canonical_trace(run.execute_frames(events, frames)),
                      counts=dict(audio=18, nj=18, endpoints=18, formations=8, hints=10, closes=2))
        record = json.loads(run.canonical(record))
        self.assertEqual(verify.verify(record)["status"], "VERIFIED")
        for field, value, code in (("source_id", "nu-s99-w99", "SOURCE_RECEIPT_INVALID"), ("half_values_hex", ["0x1.0000000000000p+1"] * 48, "VALUE_DOMAIN_INVALID")):
            changed = deepcopy(record); changed["endpoints"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(verify.S2TSVerificationError, code):
                verify.verify(changed)
        incomplete = deepcopy(record); incomplete["endpoints"].pop()
        with self.assertRaisesRegex(verify.S2TSVerificationError, "ENDPOINT_COUNT_INVALID"):
            verify.verify(incomplete)
        equivalent = deepcopy(record); equivalent["trace"]["decisions"][0]["result"]["offsets"] = list(equivalent["trace"]["decisions"][0]["result"]["offsets"])
        self.assertEqual(verify.verify(equivalent)["status"], "VERIFIED")
        for offsets, code in (([0], "TRACE_DECISIONS_INVALID"), ([], "TRACE_DECISIONS_INVALID"), ([0, 1], "TRACE_DECISIONS_INVALID"), (["0"], "OFFSET_FORM_INVALID")):
            changed = deepcopy(record); changed["trace"]["decisions"][0]["result"]["offsets"] = offsets
            with self.subTest(offsets=offsets), self.assertRaisesRegex(verify.S2TSVerificationError, code):
                verify.verify(changed)
        changed = deepcopy(record); changed["trace"]["baselines"][0]["single"]["present"] = [False, True]
        with self.assertRaisesRegex(verify.S2TSVerificationError, "BASELINES_INVALID"):
            verify.verify(changed)
        changed = deepcopy(record); changed["trace"]["baselines"][0].pop("trace_digest")
        with self.assertRaisesRegex(verify.S2TSVerificationError, "BASELINES_INVALID"):
            verify.verify(changed)

    def test_development_canonical_trace_converts_internal_tuples_once(self):
        events = run.schedule(); frames = {}
        for event in events:
            if event["source_id"] is not None:
                frames[event["ordinal"]] = ts.Frame((0.1,) * 48, P, event["session"], event["ordinal"], 1, event["runtime_time"])
        trace = run.canonical_trace(run.execute_frames(events, frames))
        self.assertIsInstance(trace["decisions"][0]["result"]["offsets"], list)
        self.assertIsInstance(trace["baselines"][0]["single"]["present"], list)
