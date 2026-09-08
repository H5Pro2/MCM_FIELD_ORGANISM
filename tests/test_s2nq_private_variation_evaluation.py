"""Synthetic evaluator inputs only: no scans, receptors, NJ projection or memory."""
from copy import deepcopy
from dataclasses import asdict
import json
import unittest

from tools import _s2nq_private_evaluation as subject

s=subject.s
ORIGINAL=(0.7,)*48
DRIFT=(float.fromhex("0x1.6666666666665p-1"),)*48
METRICS=dict(evaluations=0,maximum_output_bytes=0)


def seal(value,key):
    return {**value,key:s.digest(value)}


def projection(values,n,carriers):
    half=s.profile.half
    payload=dict(profile_id=half.PROFILE_ID,profile_digest=half.PROFILE_DIGEST,geometry_id=half.GEOMETRY,
        source_profile_digest=half.RAW_PROFILE_DIGEST,source_state_digest=s.digest(dict(neutral_state=n)),
        source_values_digest=s.digest([2.0*x for x in values]),snapshot_index=20*n,clock_id="audio.sample",
        window_start_tick=9600*n,window_end_tick=9600*n+4800,carrier_ids=carriers,values=values,
        subnormal_band_indices=(),underflow_band_indices=())
    return half.HalfScaleAuditory48V1(**payload,projection_digest=s.digest(payload))


def fixture(cue_values=ORIGINAL,references=None,decisions=((True,True),),source="neutral-original"):
    """Minimal synthetic evaluation shape, not a claimed memory or verification run."""
    references=(ORIGINAL,)*4 if references is None else references
    config=s.profile.build_config()
    carriers=config.profile.profile.auditory_config.carrier_ids
    empty=dict(b4_state=dict(entries=[]),tspm_state=dict(fast_state=dict(slots=[]),
        auditory_ppb1_state=dict(slots=[dict(slot_id="neutral-slot",occupied=False)])))
    states={"initial":empty}
    events=[]
    previous="initial"
    for n,values in enumerate(references):
        spec=dict(history="neutral-history",event_id=f"neutral-formation-{n}",ordinal=n,audio_source=source,visual_ordinal=0)
        p=projection(values,n,carriers)
        src=seal(dict(event=spec,source_root="1"*64,source_digest="2"*64,pcm_digest="3"*64,
                      projection=asdict(p)),"binding_digest")
        key=f"state-{n}"
        states[key]=deepcopy(empty)
        states[key]["tspm_state"]["auditory_ppb1_state"]["slots"]=[dict(slot_id="neutral-slot",occupied=True,
            support_count=min(n+1,3),last_selected_step=n+1,prototype_values=DRIFT)]
        events.append(seal(dict(kind="FORMATION",spec=spec,source=src,prestate=previous,poststate=key,
                               formation=dict(synthetic_evaluator_fixture=True)),"event_digest"))
        previous=key
    for k,dec in enumerate(decisions):
        n=len(references)+k
        cues,arms=[],[]
        for view,admitted in zip(s.VIEWS,dec,strict=True):
            bp=s.plan(view)
            c=s.Cue(bp,tuple(cue_values[i] for i in bp.observed),config.config_digest,s.profile.half.PROFILE_DIGEST,
                "4"*64,"5"*64,"6"*64,"audio.sample",9600*n,9600*n+4800)
            cues.append(asdict(c))
            row=dict(bank=s.ROLES[2],slot_id="neutral-slot",slot_digest="7"*64,eligible=True,
                     matched=admitted,terms=[abs(DRIFT[i]-cue_values[i]) for i in bp.observed])
            h=None if not admitted else dict(area="B_STABLE_AUDITORY",provenance=["7"*64],
                indices=bp.complement,values=tuple(DRIFT[i] for i in bp.complement))
            arm=dict(cue_digest=c.cue_digest,rows=[row],hypothesis=h,
                     decision="ADMIT_SINGLE_CONTEXT" if admitted else "ABSTAIN_NO_APPLICABLE_CONTEXT")
            arms.extend((arm,deepcopy(arm)))
        events.append(seal(dict(kind="CUE",spec=dict(history="neutral-history",event_id=f"neutral-cue-{k}",
            ordinal=n,audio_source="neutral-cue",visual_ordinal=None),prestate=previous,poststate=previous,
            cues=cues,arms=arms),"event_digest"))
    return dict(status="RECORDING_COMPLETE",states=states,events=events,synthetic_evaluator_fixture=True)


def evaluate(record,subtype="EXACT"):
    # A synthetic digest-bound shape isolates this unit; no technical verifier is invoked.
    r=json.loads(s.canonical(seal(record,"record_digest")))
    proof=seal(dict(status="RECORDING_COMPLETE",record_digest=r["record_digest"],synthetic_evaluator_fixture=True),"verification_digest")
    before=s.digest(r)
    result=subject.evaluate(r,proof,{"neutral-cue":("neutral-original",subtype)})
    assert before==s.digest(r)
    METRICS["evaluations"]+=1
    METRICS["maximum_output_bytes"]=max(METRICS["maximum_output_bytes"],len(s.canonical(result)))
    return result


def break_reference(record,change):
    for e in record["events"]:
        if e["kind"]=="FORMATION":
            change(e)
            e["source"]=seal({k:v for k,v in e["source"].items() if k!="binding_digest"},"binding_digest")
            updated=seal({k:v for k,v in e.items() if k!="event_digest"},"event_digest")
            e.clear()
            e.update(updated)


def tearDownModule():
    print("NQ_VARIATION_METRICS "+json.dumps(METRICS,sort_keys=True))


class VariationTests(unittest.TestCase):
    def test_01_exact_cue_despite_prototype_drift(self):
        self.assertNotEqual(ORIGINAL,DRIFT)
        result=evaluate(fixture())
        o=result["observations"][0]
        self.assertEqual([False,False],o["receptor_variation"])
        self.assertEqual([True,True],o["cue_candidate_deviation"])
        self.assertEqual(["DETERMINED"]*2,o["receptor_variation_status"])
        self.assertEqual((False,False),result["groups"][0]["receptor_variation"])
        self.assertEqual(4,len(o["formation_references"]))

    def test_02_visible_variation_not_inferred_from_label(self):
        values=(0.6,)+ORIGINAL[1:]
        result=evaluate(fixture(values),subtype="EXACT")
        self.assertEqual([True,True],result["observations"][0]["receptor_variation"])
        unchanged=evaluate(fixture(),subtype="FREQUENCY")
        self.assertEqual([False,False],unchanged["observations"][0]["receptor_variation"])

    def test_03_outside_the_respective_view(self):
        for index,expected in ((1,[True,False]),(47,[False,True])):
            with self.subTest(index=index):
                values=list(ORIGINAL)
                values[index]=0.6
                result=evaluate(fixture(tuple(values)))
                self.assertEqual(expected,result["observations"][0]["receptor_variation"])

    def test_04_missing_bound_values_are_not_false(self):
        record=fixture()
        break_reference(record,lambda e:e["source"]["projection"].pop("values"))
        o=evaluate(record)["observations"][0]
        self.assertEqual([None,None],o["receptor_variation"])
        self.assertEqual(["INVALID_REFERENCE_BINDING"]*2,o["receptor_variation_status"])
        self.assertEqual([True,True],o["cue_candidate_deviation"])
        self.assertEqual([],o["formation_references"])

    def test_05_ambiguous_original_values_per_view(self):
        for index,expected in ((0,[None,None]),(47,[False,None])):
            with self.subTest(index=index):
                other=list(ORIGINAL)
                other[index]=0.6
                o=evaluate(fixture(references=(ORIGINAL,tuple(other),ORIGINAL,ORIGINAL)))["observations"][0]
                self.assertEqual(expected,o["receptor_variation"])
                self.assertEqual("AMBIGUOUS_REFERENCE",o["receptor_variation_status"][1])

    def test_06_no_reference_identity_or_bad_digest(self):
        o=evaluate(fixture(source="neutral-other"))["observations"][0]
        self.assertEqual([None,None],o["receptor_variation"])
        self.assertEqual(["MISSING_REFERENCE"]*2,o["receptor_variation_status"])
        r=fixture()
        break_reference(r,lambda e:e["source"].update(source_digest="unbound"))
        self.assertEqual([None,None],evaluate(r)["observations"][0]["receptor_variation"])

    def test_07_gains_losses_and_denominators_stay_separate(self):
        result=evaluate(fixture(decisions=((True,True),(True,False),(False,True))))
        group=result["groups"][0]
        for table in (group["public_retention"],group["relationship_retention"][s.ROLES[2]]):
            self.assertEqual(dict(N=3,D=2,R=1,L=1,status="ASSESSED",gains=1),table)
        self.assertEqual([0,0],group["false_admissions"])
        self.assertEqual("ERHALTUNG_NICHT_GEPRUEFT",
            evaluate(fixture(decisions=((False,True),)))["groups"][0]["public_retention"]["status"])

    def test_08_undetermined_reference_keeps_outcome_denominators(self):
        original=fixture(decisions=((True,True),(True,False),(False,True)))
        missing=deepcopy(original)
        break_reference(missing,lambda e:e["source"].pop("projection"))
        a,b=evaluate(original),evaluate(missing)
        self.assertEqual(a["groups"][0]["public_retention"],b["groups"][0]["public_retention"])
        self.assertEqual(a["groups"][0]["relationship_retention"],b["groups"][0]["relationship_retention"])
        self.assertEqual((None,None),b["groups"][0]["receptor_variation"])
        self.assertEqual([o["decisions"] for o in a["observations"]],[o["decisions"] for o in b["observations"]])
        self.assertFalse(subject.run.MAIN_GATE)
