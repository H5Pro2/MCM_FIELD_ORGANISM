"""Neutral synthetic state/evidence qualification; no source or formation execution."""
from dataclasses import asdict, replace, FrozenInstanceError
from copy import deepcopy
import json
import math
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from tests import test_s2kz_private_auditory_partial_cue_retrieval_336 as fx
from tools import _s2ns_private_two_view as s
from tools import _s2ns_private_direct as direct
from tools import _s2ns_private_evaluation as evaluation

M = dict(execution_scans=0, execution_rows=0, execution_band_differences=0,
         verification_scans=0, verification_rows=0, verification_band_differences=0,
         execution_equality_comparisons=0, verification_equality_comparisons=0,
         verification_calls=0, historical_scans=0, max_scan_bytes=0, max_result_bytes=0,
         max_inventory_bytes=0, max_shared_bytes=0, max_evaluation_bytes=0,
         canonical_worst_record_bytes=0, formation_calls=0, receptor_calls=0, nj_calls=0, ns_payloads=0)
Z = (0.0,)*48


def inventory(config, state):
    bindings = []
    for b, slot in s.slot_items(state):
        values = s.slot_values(b, slot)
        h = s.slot_hash(b, slot)
        g = None if not slot.occupied else s.Generation("neutral-h", s.BANKS[b], slot.slot_id,
            "neutral-birth", 1, "CREATED", "1"*64, "2"*64, h, "3"*64)
        bindings.append(s.SlotBinding(s.BANKS[b], slot.slot_id, h,
            None if values is None else s.digest(list(values)), g))
    return s.Inventory("neutral-h", config.config_digest, s.profile.half.PROFILE_DIGEST,
        state.state_digest, "4"*64, tuple(bindings))


def views(config, values=Z):
    e = s.Endpoint("neutral-source", "1"*64, "2"*64, "3"*64, "4"*64,
        s.profile.half.PROFILE_DIGEST, config.config_digest, "audio.sample", 9600, 14400)
    return tuple(s.View(e, name, indices, tuple(values[i] for i in indices))
                 for name, indices in zip(s.VIEWS, s.INDICES, strict=True))


def expectation(*, target="target", originals=(Z,), area="A_RECENT", sources=None):
    origins = tuple(sources if sources is not None else (("target",),)+((),)*19)
    return evaluation.Expectation("neutral-case", target, area, "NEUTRAL", origins, originals,
        () if originals is None else ("e"*64,)*len(originals))


def tearDownModule():
    print("NS_TWO_VIEW_METRICS "+json.dumps(M, sort_keys=True))


class TwoViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = s.profile.build_config()
        cls.depth = 0
        original_primary, original_direct = s.scan_view, direct._scan
        def tracked(fn):
            def call(*args, **kwargs):
                r = fn(*args, **kwargs)
                kind = "verification" if cls.depth else "execution"
                M[kind+"_scans"] += 1
                M[kind+"_rows"] += len(r.rows)
                M[kind+"_band_differences"] += r.comparisons
                M["max_scan_bytes"] = max(M["max_scan_bytes"], len(s.canonical(asdict(r))))
                return r
            return call
        cls.guards = [patch.object(s, "scan_view", side_effect=tracked(original_primary)),
                      patch.object(direct, "_scan", side_effect=tracked(original_direct)),
                      patch.object(s.memory, "advance_s2jv_atomic", side_effect=AssertionError("FORMATION_FORBIDDEN")),
                      patch.object(s.profile.half, "project_auditory_half_v1", side_effect=AssertionError("NJ_FORBIDDEN"))]
        for g in cls.guards:
            g.start()
            cls.addClassCleanup(g.stop)

    def code(self, code, fn):
        with self.assertRaises(s.S2NSError) as caught:
            fn()
        self.assertEqual(code, caught.exception.code)

    def inputs(self, state=None, values=Z):
        state = fx._state(self.config) if state is None else state
        lower, upper = views(self.config, values)
        return dict(config=self.config, state=state, inventory=inventory(self.config, state), lower=lower, upper=upper)

    def arms(self, **kwargs):
        before = s.canonical(asdict(kwargs["state"]))
        p, b = s.retrieve(**kwargs), direct.direct(**kwargs)
        M["execution_equality_comparisons"] += p.equality_comparisons+b.equality_comparisons
        self.assertEqual(direct.semantics(p), direct.semantics(b))
        proof = self.verify(p,b,kwargs)
        M["verification_equality_comparisons"] += proof["verification_equality_comparisons"]
        M["max_result_bytes"] = max(M["max_result_bytes"], *(len(s.canonical(asdict(x))) for x in (p, b)))
        M["max_inventory_bytes"] = max(M["max_inventory_bytes"], len(s.canonical(asdict(kwargs["inventory"]))))
        shared = dict(inventory=asdict(kwargs["inventory"]), views=[None if v is None else asdict(v)
                     for v in (kwargs["lower"], kwargs["upper"])])
        M["max_shared_bytes"] = max(M["max_shared_bytes"], len(s.canonical(shared)))
        self.assertEqual(before, s.canonical(asdict(kwargs["state"])))
        return p, b, proof

    def verify(self,p,b,kwargs):
        type(self).depth += 1
        M["verification_calls"] += 1
        try:
            return direct.verify_pair(p,b,**kwargs)
        finally:
            type(self).depth -= 1

    def test_01_own_closed_immutable_views(self):
        lo, hi = views(self.config)
        self.assertEqual(tuple(range(48)), lo.indices+hi.indices)
        self.assertEqual(24, len(hi.values))
        with self.assertRaises(FrozenInstanceError):
            lo.name = "UPPER_24"
        self.code("VIEW_BINDING_INVALID", lambda: replace(hi, indices=lo.indices))
        self.code("VALUE_DOMAIN_INVALID", lambda: replace(lo, values=Z))
        for x in (float("inf"), float("nan"), -0.1, 1.1):
            with self.subTest(x=x):
                self.code("VALUE_DOMAIN_INVALID", lambda: replace(lo, values=(x,)*24))

    def test_02_binding_existing_projection_no_second_nj(self):
        h = s.profile.half
        values = tuple(float(i)/64 for i in range(48))
        payload = dict(profile_id=h.PROFILE_ID, profile_digest=h.PROFILE_DIGEST, geometry_id=h.GEOMETRY,
            source_profile_digest=h.RAW_PROFILE_DIGEST, source_state_digest="a"*64, source_values_digest="b"*64,
            snapshot_index=20, clock_id="audio.sample", window_start_tick=9600, window_end_tick=14400,
            carrier_ids=self.config.profile.profile.auditory_config.carrier_ids, values=values,
            subnormal_band_indices=(), underflow_band_indices=())
        p = h.HalfScaleAuditory48V1(**payload, projection_digest=h.digest(payload))
        lo, hi = s.bind_views(projection=p, config=self.config, source_id="neutral", source_digest="c"*64, pcm_digest="d"*64)
        self.assertEqual(values, lo.values+hi.values)
        self.assertEqual(lo.endpoint, hi.endpoint)
        self.assertEqual(p.source_state_digest, lo.endpoint.raw_state_digest)
        self.code("PROJECTION_BINDING_INVALID", lambda: s.bind_views(projection=lo, config=self.config,
            source_id="neutral", source_digest="c"*64, pcm_digest="d"*64))

    def test_03_missing_view_is_regular_abstention(self):
        for name in ("lower", "upper"):
            with self.subTest(name=name):
                kw = self.inputs()
                kw[name] = None
                p, _, _ = self.arms(**kw)
                self.assertEqual("ABSTAIN_INSUFFICIENT_EVIDENCE", p.admissions[-1].decision)
                self.assertEqual(1, len(p.scans))

    def test_04_foreign_endpoint_and_time(self):
        kw = self.inputs()
        for field, value, code in (("source_id", "other", "ENDPOINT_MISMATCH"),
                                   ("raw_state_digest", "f"*64, "ENDPOINT_MISMATCH"),
                                   ("pcm_digest", "f"*64, "ENDPOINT_MISMATCH")):
            with self.subTest(field=field):
                changed = {**kw, "upper": replace(kw["upper"], endpoint=replace(kw["upper"].endpoint, **{field:value}))}
                self.code(code, lambda: s.retrieve(**changed))
        self.code("CUE_TIME_INVALID", lambda: replace(kw["lower"].endpoint, end=14401))
        self.code("PROFILE_INVALID", lambda: replace(kw["lower"].endpoint, profile_digest="0"*64))
        late = self.inputs(fx._state(self.config, b4=(Z,), auditory_end_tick=12000))
        self.code("CUE_TIME_INVALID", lambda: s.retrieve(**late))

    def test_05_replaced_generation_same_slot_and_values(self):
        kw = self.inputs(fx._state(self.config, b4=(Z,)))
        lo = s.scan_view(config=self.config, state=kw["state"], inventory=kw["inventory"], view=kw["lower"])
        slots = list(kw["inventory"].slots)
        slots[0] = replace(slots[0], generation=replace(slots[0].generation, transition="REPLACED", event_id="new-birth"))
        changed = replace(kw["inventory"], slots=tuple(slots))
        hi = s.scan_view(config=self.config, state=kw["state"], inventory=changed, view=kw["upper"])
        self.assertEqual(kw["inventory"].slots[0].slot_digest, changed.slots[0].slot_digest)
        self.code("SCAN_BINDING_INVALID", lambda: s.combine(**kw, lower_scan=lo, upper_scan=hi))
        repaired_header = replace(hi, inventory_digest=kw["inventory"].inventory_digest)
        repaired_header = replace(repaired_header, scan_digest=s.digest(repaired_header.payload()))
        self.code("SCAN_GENERATION_INVALID", lambda: s.combine(**kw, lower_scan=lo, upper_scan=repaired_header))

    def test_06_generation_missing_or_wrong_birth(self):
        kw = self.inputs(fx._state(self.config, b4=(Z,)))
        slots = list(kw["inventory"].slots)
        slots[0] = replace(slots[0], generation=None)
        self.code("GENERATION_BINDING_INVALID", lambda: s.retrieve(**{**kw, "inventory":replace(kw["inventory"], slots=tuple(slots))}))
        self.code("GENERATION_BINDING_INVALID", lambda: replace(kw["inventory"].slots[0].generation, transition="MATCHED"))
        self.code("GENERATION_BINDING_INVALID", lambda: s.retrieve(**{**kw, "inventory":replace(kw["inventory"], history_id="foreign")}))

    def test_07_inclusive_a_boundary_and_adjacent(self):
        for v, match in ((0.1, True), (math.nextafter(0.1, math.inf), False)):
            with self.subTest(v=v):
                p, _, _ = self.arms(**self.inputs(fx._state(self.config, b4=((0.0,)*47+(v,),))))
                self.assertTrue(p.scans[0].rows[0].matched)
                self.assertEqual(match, p.scans[1].rows[0].matched)
                self.assertEqual(match, p.admissions[-1].area is not None)

    def test_08_two_slow_means_not_one_48_mean(self):
        v = (0.0,)*24+(0.015,)*24
        p, _, _ = self.arms(**self.inputs(fx._state(self.config, slow=(v,))))
        self.assertLess(sum(v)/48, 0.01)
        self.assertEqual(sum(v[24:])/24, p.scans[1].rows[12].statistic)
        self.assertFalse(p.scans[1].rows[12].matched)
        self.assertIsNone(p.admissions[-1].area)

    def test_09_slow_boundary_and_unstable(self):
        for v, support in ((0.24, 3), (math.nextafter(0.24, math.inf), 3), (0.0, 2)):
            with self.subTest(v=v, support=support):
                values = (v,)+(0.0,)*23+(v,)+(0.0,)*23
                p, _, _ = self.arms(**self.inputs(fx._state(self.config, slow=(values,), slow_supports=(support,))))
                self.assertEqual(support == 3, p.scans[0].rows[12].eligible)
                self.assertEqual(support == 3 and v/24 <= 0.01, p.scans[0].rows[12].matched)

    def test_10_disjoint_hits_do_not_vote(self):
        st = fx._state(self.config, b4=((0.0,)*24+(0.3,)*24, (0.3,)*24+(0.0,)*24))
        p, _, _ = self.arms(**self.inputs(st))
        self.assertEqual((0,), p.admissions[0].provenance)
        self.assertEqual((1,), p.admissions[1].provenance)
        self.assertEqual("ABSTAIN_NO_APPLICABLE_CONTEXT", p.admissions[2].decision)

    def test_11_shared_unique_despite_two_ambiguities(self):
        st = fx._state(self.config, b4=(Z, (0.0,)*24+(0.3,)*24, (0.3,)*24+(0.0,)*24))
        p, _, _ = self.arms(**self.inputs(st))
        self.assertEqual(["ABSTAIN_INTERNAL_AMBIGUITY"]*2, [x.decision for x in p.admissions[:2]])
        self.assertEqual((0,), p.admissions[2].provenance)

    def test_12_internal_equality_and_conflict_all_48(self):
        for right, status in ((Z, "ADMIT_SINGLE_CONTEXT"), ((0.0,)*47+(0.05,), "ABSTAIN_INTERNAL_CONFLICT")):
            with self.subTest(status=status):
                p, _, _ = self.arms(**self.inputs(fx._state(self.config, b4=(Z,), fast=(right,))))
                self.assertEqual(status, p.admissions[-1].decision)
                self.assertEqual(144, p.equality_comparisons)

    def test_13_every_bank_ambiguity_no_short_circuit(self):
        for kwargs in (dict(b4=(Z,Z)), dict(fast=(Z,Z)), dict(slow=(Z,Z))):
            with self.subTest(bank=next(iter(kwargs))):
                p, _, _ = self.arms(**self.inputs(fx._state(self.config, **kwargs)))
                self.assertEqual("ABSTAIN_INTERNAL_AMBIGUITY", p.admissions[-1].decision)
                self.assertTrue(all(tuple(r.index for r in x.rows) == tuple(range(20)) for x in p.scans))

    def test_14_public_ambiguity_and_null(self):
        for st, expected in ((fx._state(self.config, b4=(Z,), slow=(Z,)), "ABSTAIN_AMBIGUOUS_CONTEXT"),
                             (fx._state(self.config), "ABSTAIN_NO_CONTEXT")):
            with self.subTest(expected=expected):
                p, _, _ = self.arms(**self.inputs(st))
                self.assertEqual(expected, p.admissions[-1].decision)

    def test_15_lower_matches_historical_half_all_bands(self):
        st = fx._state(self.config, b4=(Z,), fast=(Z,))
        kw = self.inputs(st)
        p, _, _ = self.arms(**kw)
        oldcue = s.existing.Cue(s.existing.plan("CONTIGUOUS_24"), (0.0,)*24, self.config.config_digest,
            s.profile.half.PROFILE_DIGEST, "2"*64, "4"*64, "5"*64, "audio.sample", 9600, 14400)
        old = s.existing.retrieve(config=self.config, state=st, cue=oldcue)
        M["historical_scans"] += 1
        self.assertEqual((old.a_status,old.b_status,old.decision),
            (p.admissions[0].a_status,p.admissions[0].b_status,p.admissions[0].decision))
        self.assertEqual([(r.terms,r.statistic,r.matched) for r in old.rows],
                         [(r.terms,r.statistic,r.matched) for r in p.scans[0].rows])

    def test_16_unobserved_values_cannot_enter_view_scan(self):
        a, b = self.inputs(fx._state(self.config, b4=(Z,))), self.inputs(fx._state(self.config, b4=((0.0,)*24+(0.9,)*24,)))
        rows = [s.scan_view(config=self.config,state=x["state"],inventory=x["inventory"],view=x["lower"]).rows for x in (a,b)]
        self.assertEqual([r.terms for r in rows[0]], [r.terms for r in rows[1]])
        self.code("VIEW_BINDING_INVALID", lambda: s.scan_view(config=self.config, state=a["state"],
            inventory=a["inventory"], view=asdict(a["lower"])))

    def test_17_verification_accepts_unexpected_abstention(self):
        kw = self.inputs(fx._state(self.config, b4=(Z,Z)))
        p, _, proof = self.arms(**kw)
        e = self.evaluate(p, proof, kw, expectation())
        self.assertEqual("TECHNICALLY_VALID", proof["status"])
        self.assertTrue(all(x["public_retention"]["D"] == 0 for x in e["comparisons"]))
        self.assertTrue(all(x["public_retention"]["status"] == "ERHALTUNG_NICHT_GEPRUEFT" for x in e["comparisons"]))

    def evaluate(self, p, proof, kw, exp):
        e = evaluation.evaluate_case(p, proof, inventory=kw["inventory"],lower=kw["lower"],upper=kw["upper"],expectation=exp)
        M["max_evaluation_bytes"] = max(M["max_evaluation_bytes"],len(s.canonical(e)))
        return e

    def test_18_target_exclusion_can_create_false_admission(self):
        kw = self.inputs(fx._state(self.config, b4=((0.0,)*24+(0.2,)*24, (0.05,)*48)))
        p, _, proof = self.arms(**kw)
        e = self.evaluate(p, proof, kw, expectation(sources=(("target",),("other",))+((),)*18))
        low = e["comparisons"][0]
        self.assertEqual([0], low["lost_target_slots"])
        self.assertTrue(low["new_false_admission"])
        self.assertFalse(low["public_loss"])
        self.assertEqual(1, low["relationship_retention"]["L"])

    def test_19_public_loss_and_gain_never_netted(self):
        kw = self.inputs(fx._state(self.config, b4=((0.0,)*24+(0.2,)*24,)))
        p, _, proof = self.arms(**kw)
        e = self.evaluate(p,proof,kw,expectation())
        self.assertTrue(e["comparisons"][0]["public_loss"])
        self.assertEqual(dict(N=2,D=1,R=0,L=1,status="ASSESSED",gains=1),evaluation.retention([(True,False),(False,True)]))
        self.assertEqual(0,e["comparisons"][0]["public_by_area"]["B_STABLE_AUDITORY"]["D"])

    def test_20_original_variation_separate_from_ppb_drift(self):
        original = (0.1,)*48
        drift = (math.nextafter(0.1,math.inf),)*48
        kw = self.inputs(fx._state(self.config,slow=(drift,)),original)
        p, _, proof = self.arms(**kw)
        sources = ((),)*12+(("target",),)+((),)*7
        for originals, expected in (((original,), (False,False)), ((original,(0.2,)*48),(None,None)),
                                    (None,(None,None)), ((original[:24]+(0.2,)*24,), (False,True))):
            with self.subTest(expected=expected):
                e = self.evaluate(p,proof,kw,expectation(originals=originals,area="B_STABLE_AUDITORY",sources=sources))
                self.assertEqual(expected,tuple(x["receptor_variation"] for x in e["comparisons"]))
                self.assertTrue(all(x["cue_candidate_deviation"] for x in e["comparisons"]))

    def test_21_manipulated_scans_and_results(self):
        kw = self.inputs(fx._state(self.config,b4=(Z,)))
        p,b,proof = self.arms(**kw)
        self.code("RESULT_DIGEST_INVALID",lambda: self.verify(replace(p,result_digest="0"*64),b,kw))
        changed_scan = replace(p.scans[0],rows=p.scans[0].rows[:-1])
        changed_scan = replace(changed_scan,scan_digest=s.digest(changed_scan.payload()))
        changed = replace(p,scans=(changed_scan,p.scans[1]))
        changed = replace(changed,result_digest=s.digest(changed.payload()))
        self.code("SCAN_COMPLETENESS_INVALID",lambda: self.verify(changed,b,kw))
        row = replace(p.scans[0].rows[0],terms=(0.01,)+(0.0,)*23)
        tampered_scan = replace(p.scans[0],rows=(row,)+p.scans[0].rows[1:])
        tampered_scan = replace(tampered_scan,scan_digest=s.digest(tampered_scan.payload()))
        tampered = replace(p,scans=(tampered_scan,p.scans[1]))
        tampered = replace(tampered,result_digest=s.digest(tampered.payload()))
        self.code("RESULT_BINDING_INVALID",lambda: self.verify(tampered,b,kw))
        self.code("EVALUATION_REQUIRES_VERIFICATION",lambda: evaluation.evaluate_case(p,{**proof,"status":"BAD"},
            inventory=kw["inventory"],lower=kw["lower"],upper=kw["upper"],expectation=expectation()))

    def test_22_profile_state_and_mutability(self):
        kw = self.inputs()
        self.code("PROFILE_INVALID",lambda: s.retrieve(**{**kw,"config":fx._config()}))
        broken = replace(kw["state"],state_digest="f"*64)
        self.code("STATE_BINDING_INVALID",lambda: s.retrieve(**{**kw,"state":broken}))
        with self.assertRaises(FrozenInstanceError):
            kw["inventory"].state_digest = "0"*64
        self.assertFalse(s.MAIN_GATE)

    def test_23_canonical_full_capacity_and_total_envelope(self):
        values = (0.12345678901234566,)*48
        kw = self.inputs(fx._state(self.config,b4=(values,)*9,fast=(values,)*3,slow=(values,)*8))
        p,b,proof = self.arms(**kw)
        self.assertEqual(960,p.band_differences)
        self.assertLessEqual(M["max_scan_bytes"],32768)
        self.assertLessEqual(M["max_shared_bytes"],32768)
        # Worst admissible JSON subtree byte budgets plus concrete outer envelope.
        # ASCII padding substitutes bounded subtrees, not source or numeric data.
        def padded(size):
            return "x"*(size-2)
        record = dict(schema=s.SCHEMA,states=[padded(98304) for _ in range(17)],
            cases=[dict(shared=padded(32768),primary=padded(49152),baseline=padded(49152)) for _ in range(15)],
            source_metadata=padded(65536),evaluation_metadata=padded(65536),
            verification_metadata=padded(65536),record_digest="f"*64)
        M["canonical_worst_record_bytes"] = len(s.canonical(record))
        self.assertLess(M["canonical_worst_record_bytes"],4194304)
        self.assertGreater(len(s.canonical(dict(extra=record,overflow=padded(524288)))),4194304)
        path=Path(os.environ["S2NS_TWO_VIEW_QUAL_DIR"])/"neutral-full-capacity.json"
        data=s.canonical(dict(inventory=asdict(kw["inventory"]),views=[asdict(kw["lower"]),asdict(kw["upper"])],
            primary=asdict(p),baseline=asdict(b),verification=proof))
        with path.open("xb") as out:
            out.write(data)

    def test_24_budget_and_no_complement_values(self):
        self.assertLessEqual(M["execution_scans"],192)
        self.assertLessEqual(M["execution_band_differences"],28800)
        self.assertLessEqual(M["verification_scans"],96)
        self.assertLessEqual(M["verification_band_differences"],28800)
        self.assertLessEqual(M["execution_equality_comparisons"],4320)
        self.assertLessEqual(M["verification_equality_comparisons"],4320)
        self.assertNotIn("values",s.Admission.__dataclass_fields__)
        self.assertNotIn("hypothesis",s.Result.__dataclass_fields__)
        self.assertNotIn("runtime",s.__dict__)
