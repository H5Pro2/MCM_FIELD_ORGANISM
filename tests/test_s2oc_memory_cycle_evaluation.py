"""Synthetic verified-record interface fixtures, not simulated memory histories."""
from copy import deepcopy
import unittest
from tools import _s2oc_memory_cycle_evaluation as e


def seal(x, key):
    x.pop(key, None)
    x[key] = e.digest(x)
    return x


def fixture():
    events, rows, states, scans, transitions = [], [], {}, [], []
    origins = ("a", "cue", "a", "a", "a", "b", "b", "b", "b", "c", "c", "c", "c", "d", "cue", "d", "d", "d", "e", "e", "cue")
    slots = [dict(slot_id=f"slot-{i}", occupied=False, support_count=0) for i in range(24)]
    births = [None] * 24
    for n, source in enumerate(origins, 1):
        events.append(dict(event_id=f"neutral-{n}", rgb=dict(path="neutral/" + source)))
        actions = ["UNCHANGED" if s["occupied"] else "FREE" for s in slots]
        updates = {}
        if n in (1, 3, 4, 5):
            updates[n-1] = (1, "CREATED")
            updates[9] = (min(n, 2), "CREATED" if n == 1 else "MATCHED")
            if n > 1:
                updates.update({12: (min(n-2, 3), "CREATED" if n == 3 else "MATCHED"),
                                20: (min(n-2, 3), "CREATED" if n == 3 else "MATCHED")})
        if n == 13:
            updates.update({i: (0, "CLEARED") for i in (0, 2, 3, 9)})
        if n == 14:
            updates[4] = (0, "CLEARED")
        if n == 16:
            updates[10] = (1, "CREATED")
            updates.update({i: (1, "CREATED") for i in (21, 22, 23)})
        if n == 20:
            updates.update({10: (1, "REPLACED"), 20: (1, "REPLACED")})
        for i, (support, action) in updates.items():
            slots[i].update(occupied=bool(support), support_count=support)
            actions[i] = action
            if action in ("CREATED", "REPLACED", "CLEARED"):
                births[i] = n if support else None
        g = None if source == "cue" else dict(actions=actions)
        if g:
            transitions.append(dict(event=n, fast_selected="slot-10" if n >= 16 else "slot-9"))
        key = f"state-{n}"
        states[key] = dict(body=dict(b4_state=dict(entries=deepcopy(slots[:9])), tspm_state={
            name: dict(slots=deepcopy(slots[a:b])) for name, a, b in
            (("fast_state", 9, 12), ("auditory_ppb1_state", 12, 20), ("visual_ppb1_state", 20, 24))}))
        h = None
        if n in (2, 15):
            h = dict(area="A_RECENT" if n == 2 else "B_STABLE", provenance_slot_digests=["candidate"])
        if source == "cue":
            scans.append(dict(ordinal=n, role="PRIMARY", value=dict(bank_scans=[dict(records=[
                dict(slot_id="slot-0" if n == 2 else "slot-20", slot_digest="candidate")])])))
        rows.append(dict(memory=key, generations=g, current_births=list(births),
                         step=dict(hypothesis=h, context_status="ABSTAIN_NO_CONTEXT")))
    record = dict(status="RECORDING_COMPLETE", manifest=dict(events=events, manifest_digest="neutral-manifest"),
                  execution=dict(rows=rows, states=states, scans=scans))
    plan = seal(dict(manifest_digest="neutral-manifest", roles=dict(A="a"), decisions=[
        dict(event=f"neutral-{n}", status=s, area=a) for n, s, a in
        ((2, "ADMIT_SINGLE_CONTEXT", "A_RECENT"), (15, "ADMIT_SINGLE_CONTEXT", "B_STABLE"),
         (21, "ABSTAIN_NO_CONTEXT", None))]), "evaluation_digest")
    proof = dict(read_only=True, evaluation_allowed=True, core=dict(evaluation_allowed=True,
        core=dict(transitions=transitions)))
    bind(record, proof)
    return record, proof, plan


def bind(record, proof):
    seal(record, "record_digest")
    proof["core"]["record_digest"] = record["record_digest"]
    seal(proof["core"], "verification_digest")
    seal(proof, "verification_digest")


class AssessmentTests(unittest.TestCase):
    def test_01_eight_findings_and_immutability(self):
        args = fixture(); before = deepcopy(args)
        out = e.evaluate(*args)
        self.assertEqual(out["status"], "CONFIRMED")
        self.assertEqual((len(out["decisions"]), len(out["checkpoints"])), (3, 5))
        self.assertEqual(args, before)

    def test_02_no_verification(self):
        r, p, plan = fixture(); p["evaluation_allowed"] = False; seal(p, "verification_digest")
        with self.assertRaises(e.EvaluationError) as ex: e.evaluate(r, p, plan)
        self.assertEqual(ex.exception.code, "NOT_VERIFIED")

    def test_03_foreign_proof(self):
        r, p, plan = fixture(); p["core"]["record_digest"] = "foreign"
        seal(p["core"], "verification_digest"); seal(p, "verification_digest")
        with self.assertRaises(e.EvaluationError) as ex: e.evaluate(r, p, plan)
        self.assertEqual(ex.exception.code, "NOT_VERIFIED")

    def test_04_changed_record(self):
        r, p, plan = fixture(); r["status"] = "NOT_EVALUABLE"
        with self.assertRaises(e.EvaluationError) as ex: e.evaluate(r, p, plan)
        self.assertEqual(ex.exception.code, "DIGEST_INVALID")

    def test_05_valid_unexpected_abstention(self):
        r, p, plan = fixture(); r["execution"]["rows"][14]["step"]["hypothesis"] = None; bind(r, p)
        out = e.evaluate(r, p, plan)
        self.assertEqual(out["status"], "FALSIFIED")
        self.assertFalse(out["decisions"][1]["confirmed"])

    def test_06_wrong_target(self):
        r, p, plan = fixture(); r["execution"]["scans"][1]["value"]["bank_scans"][0]["records"][0]["slot_id"] = "slot-12"; bind(r, p)
        # Auditory lineage alone cannot establish a visual B provenance.
        out = e.evaluate(r, p, plan)
        self.assertFalse(out["decisions"][1]["confirmed"])

    def test_07_support_saturation(self):
        r, p, plan = fixture()
        r["execution"]["states"]["state-5"]["body"]["tspm_state"]["fast_state"]["slots"][0]["support_count"] = 4
        bind(r, p); out = e.evaluate(r, p, plan)
        self.assertFalse(out["checkpoints"][0]["confirmed"])

    def test_08_a_still_in_b4(self):
        r, p, plan = fixture(); row = r["execution"]["rows"][13]
        row["generations"]["actions"][4] = "UNCHANGED"
        r["execution"]["states"]["state-14"]["body"]["b4_state"]["entries"][4]["occupied"] = True
        bind(r, p); self.assertFalse(e.evaluate(r, p, plan)["checkpoints"][2]["confirmed"])

    def test_09_a_fast_not_expired(self):
        r, p, plan = fixture(); r["execution"]["rows"][12]["generations"]["actions"][9] = "UNCHANGED"
        r["execution"]["states"]["state-13"]["body"]["tspm_state"]["fast_state"]["slots"][0]["occupied"] = True
        bind(r, p); self.assertFalse(e.evaluate(r, p, plan)["checkpoints"][1]["confirmed"])

    def test_10_four_slow_slots(self):
        r, p, plan = fixture()
        r["execution"]["states"]["state-16"]["body"]["tspm_state"]["visual_ppb1_state"]["slots"][3]["occupied"] = False
        bind(r, p); self.assertFalse(e.evaluate(r, p, plan)["checkpoints"][3]["confirmed"])

    def test_11_old_birth_same_id(self):
        r, p, plan = fixture(); r["execution"]["rows"][19]["current_births"][20] = 3
        bind(r, p); self.assertFalse(e.evaluate(r, p, plan)["checkpoints"][4]["confirmed"])

    def test_12_old_receipt_not_current(self):
        r, p, plan = fixture()
        r["execution"]["rows"][20]["step"] = deepcopy(r["execution"]["rows"][14]["step"])
        bind(r, p); out = e.evaluate(r, p, plan)
        self.assertFalse(out["decisions"][2]["target"])
        self.assertFalse(out["decisions"][2]["confirmed"])

    def test_13_plan_mismatch(self):
        r, p, plan = fixture(); plan["manifest_digest"] = "foreign"; seal(plan, "evaluation_digest")
        with self.assertRaises(e.EvaluationError) as ex: e.evaluate(r, p, plan)
        self.assertEqual(ex.exception.code, "PLAN_INVALID")

    def test_14_failure_not_evaluated(self):
        r, p, plan = fixture(); r["status"] = "NOT_EVALUABLE"; bind(r, p)
        with self.assertRaises(e.EvaluationError) as ex: e.evaluate(r, p, plan)
        self.assertEqual(ex.exception.code, "NOT_VERIFIED")

    def test_15_bounded_output(self):
        out = e.evaluate(*fixture())
        self.assertLessEqual(len(e.canonical(out)), 3000)
        self.assertTrue(all(x["confirmed"] for x in out["checkpoints"]))
