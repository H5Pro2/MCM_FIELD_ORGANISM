import copy
import json
import unittest

from tools import _s2ts_temporal_trace_run as source
from tools import _s2tu_retained_trace as tu
from tools import _s2tw_exact_confirmation as confirmation
from tools import _s2tw_run as run
from tools import _s2tw_source_schedule as schedule
from tools import _s2tw_verification as verification


def record():
    bound = schedule.binding(); sources, _ = source.source_rows()
    values = {"nu-s02-w00": .1, "nu-s02-w01": .2, "nu-s02-w02": .3, "nu-s02-w03": .4, "nu-s02-w04": .5}
    baseline = tu.RetainedTraceStore(bound["profile"], "s2tw-baseline")
    candidate = confirmation.ExactConfirmationStore(bound["profile"], "s2tw-confirm")
    endpoints=[]; transitions=[]; decisions=[]; counts=dict(audio=0,nj=0,endpoints=0,formations=0,hints=0,segment_closes=0,owner_closes=0)
    for event in bound["events"]:
        if event["kind"] == "SEGMENT_CLOSE":
            base=baseline.close_segment(event["segment"]); confirm=candidate.close_segment(event["segment"])
            transitions.append(dict(ordinal=event["ordinal"],baseline=base,confirmation=confirm,baseline_inventory=list(baseline.generations),confirmation_inventory=list(candidate.inventory)))
            counts["segment_closes"] += 1; continue
        value=values[event["source_id"]]; encoded=[value.hex()]*48; item=sources[event["source_id"]]
        endpoints.append(dict(ordinal=event["ordinal"],source_id=event["source_id"],pcm_sha256=item["pcm_sha256"],payload_hash_checked=True,values=encoded,value_digest=run.digest(encoded)))
        b=tu.Frame((value,)*48,bound["profile"],"s2tw-baseline",event["segment"],event["ordinal"])
        c=tu.Frame((value,)*48,bound["profile"],"s2tw-confirm",event["segment"],event["ordinal"])
        base=baseline.form(b) if event["kind"]=="FORMATION" else baseline.hint(b)
        confirm=candidate.form(c) if event["kind"]=="FORMATION" else candidate.hint(c)
        counts["audio"] += 1; counts["nj"] += 1; counts["endpoints"] += 1
        if event["kind"] == "FORMATION": counts["formations"] += 1
        else:
            counts["hints"] += 1
            if base is not None: decisions.append(dict(ordinal=event["ordinal"],baseline=base,confirmation=confirm))
    before=dict(baseline=list(baseline.generations),confirmation=list(candidate.inventory)); baseline.close_owner(); candidate.close_owner(); counts["owner_closes"]=2
    return json.loads(run.canonical(dict(status="RECORDING_COMPLETE",run_id=run.RUN_ID,binding=bound,binding_digest=run.digest(bound),counts=counts,endpoints=endpoints,transitions=transitions,decisions=decisions,inventories_before_owner_close=before,owner_closed=True)))


class VerificationTests(unittest.TestCase):
    def test_full_neutral_chain_is_verified(self):
        self.assertEqual(verification.verify(record())["status"], "VERIFIED")

    def test_manipulated_source_transition_and_decision_fail_closed(self):
        cases=[]
        item=copy.deepcopy(record()); item["endpoints"][0]["source_id"]="wrong"; cases.append((item,"SOURCE_BINDING_INVALID"))
        item=copy.deepcopy(record()); item["transitions"][1]["confirmation"]["action"]="TRACE_RETAINED"; cases.append((item,"TRANSITIONS_INVALID"))
        item=copy.deepcopy(record()); item["decisions"][0]["confirmation"]["result"]="wrong"; cases.append((item,"DECISIONS_INVALID"))
        for item, code in cases:
            with self.subTest(code=code):
                with self.assertRaisesRegex(verification.S2TWVerificationError, code): verification.verify(item)
