"""New run-boundary tests only. No sealed NR recipe is generated."""
from copy import deepcopy
from dataclasses import FrozenInstanceError
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from tools import _s2nr_private_run as run
from tools import _s2nr_private_run_verification as verify
from tools import _s2nr_private_evaluation as evaluate

OUT=Path(os.environ["S2NR_MAIN_QUAL_DIR"])
COUNTS=dict(neutral_pcm_generations=0,neutral_rgb_generations=0,audio_hops=0,audio_snapshots=0,
    nj_projections=0,visual_analyses=0,runtime_events=0,formations=0,field_contacts=0,scans=0,
    total_verifications=0,nr_payloads=0)


def archive(name,p):
    run.ng.ne.atomic_write(OUT/name,p)


def neutral_bound():
    pcm,rgb,_=run.source.generators()
    specs=(run.source.SourceSpec("neutral-audio","PCM",run.canonical(dict(sample_count=4800,sample_rate=48000,
        groups=[dict(seed="neutral-nr-run-only",partials=[dict(frequency_millihz=997000,amplitude_ratio=[0,1])])])).decode()),
        run.source.SourceSpec("neutral-visual","RGB",run.canonical(dict(algorithm="NH_SHA_GRID_RGB8_V1",
        seed="neutral-nr-run-grid",width=1920,height=1080,rows=8,columns=12,channels=3,format="RGB8",partial=False,visible_positions=None)).decode()))
    sources=[]
    for spec in specs:
        payload=(pcm if spec.kind=="PCM" else rgb)(spec.recipe())
        COUNTS["neutral_pcm_generations" if spec.kind=="PCM" else "neutral_rgb_generations"]+=1
        try:
            view=memoryview(payload).cast("B")
            try:
                sha=hashlib.sha256(view).hexdigest()
            finally:
                view.release()
        finally:
            del payload
        sources.append(run.sealed({**spec.payload(),"payload_sha256":sha},"source_digest"))
    events=[]
    for n,kind in enumerate((run.source.AV,run.source.A,run.source.AV,run.source.A),1):
        end=n*100000000
        a=dict(source_id="neutral-audio",clock_id="audio.sample",start_tick=(n-1)*4800,end_tick=n*4800,
            hop_start=(n-1)*10,hop_end=n*10,endpoint_snapshot_index=(n-1)*10,common_window=[end-10000000,end])
        v=None if kind==run.source.A else dict(source_id="neutral-visual",clock_id="video.frame",start_tick=3*n-1,
            end_tick=3*n,common_window=[(3*n-1)*1000000000//30,end])
        events.append(dict(event_id=f"e{n:02d}",ordinal=n,event_type=kind,field_clock_id="s2nr-neutral-main-clock",
            field_window=[(n-1)*100000000,end],auditory=a,visual=v))
    plan=run.sealed(dict(sources=sources,events=events),"execution_digest")
    return run.BoundExecution("NEUTRAL",run.canonical(plan).decode())


def checked(record,bound,config):
    COUNTS["total_verifications"]+=1
    return verify.verify_record(record,bound=bound,config=config)


def tearDownModule():
    archive("metrics.json",COUNTS)


class NRRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=run.nn.profile.build_config()
        cls.bound=neutral_bound()
        archive("neutral-plan.json",cls.bound.payload())
        cls.record=run.execute_once(cls.bound,cls.config,"s2nr-neutral-new-run",OUT/"neutral-main")
        m=cls.record["materialization"]
        COUNTS.update(audio_hops=m["audio_hops"],audio_snapshots=m["audio_snapshots"],nj_projections=m["nj_projections"],visual_analyses=m["visual_frames"])
        COUNTS["neutral_pcm_generations"]+=m["audio_windows"]
        COUNTS["neutral_rgb_generations"]+=m["visual_frames"]
        c=cls.record["comparison"]
        if c is not None:
            COUNTS.update(runtime_events=2*len(c["pairs"]),
                formations=sum(a["step"]["memory_status"]=="FORMATION_COMMITTED" for p in c["pairs"] for a in p["arms"]),
                field_contacts=sum(sum(len(t["frame"]["values"]) for t in c["inputs"][n]["field"]["timed_frames"])
                    for n,p in enumerate(c["pairs"]) for a in p["arms"] if a["step"]["perception_status"]=="FIELD_CONTACT_RECORDED"),
                scans=len(c["scans"]))
        cls.proof=checked(cls.record,cls.bound,cls.config)
        archive("neutral-proof.json",cls.proof)
        evaluation=run.sealed(dict(execution_digest=cls.bound.payload()["execution_digest"],cases=[
            dict(event_id="e02",cue_id="neutral-audio",target="neutral-audio",subtype="EXACT",phase="EARLY",prediction="A_RECENT"),
            dict(event_id="e04",cue_id="neutral-audio",target="neutral-audio",subtype="EXACT",phase="LATE",prediction="B_STABLE_AUDITORY")]),"evaluation_digest")
        cls.evaluation=evaluate.evaluate(cls.record,cls.proof,cls.bound,evaluation)
        archive("neutral-evaluation.json",cls.evaluation)

    def test_01_real_neutral_materialization_and_endpoint_times(self):
        self.assertEqual(run.metrics(4,2),self.record["materialization"])
        self.assertEqual("RECORDING_COMPLETE",self.record["status"])
        for n,p in enumerate(self.record["comparison"]["inputs"],1):
            self.assertEqual((10*(n-1),4800*(n-1),4800*n),tuple(p["projection"][k] for k in ("snapshot_index","window_start_tick","window_end_tick")))
            self.assertEqual(2,len(p["operations"]))
        self.assertEqual(4,len(self.record["source_receipts"]))

    def test_02_new_offline_parent_decoder_without_receptor_or_nj(self):
        with patch.object(run.nn.half,"project_auditory_half_v1",side_effect=AssertionError("no NJ")), \
             patch.object(run.receptors.LogSpectralReceptor,"analyze",side_effect=AssertionError("no receptor")):
            for p in self.record["comparison"]["inputs"]:
                value=verify.decode_parent(p,self.config)
                self.assertEqual(run.canonical(p),run.canonical(run.runtime.pack_input(value,self.config)))

    def test_03_continued_history_and_closed_lifecycle(self):
        c=self.record["comparison"]
        for i in range(2):
            first,cue,next_formation,last=[p["arms"][i] for p in c["pairs"]]
            self.assertEqual(first["memory"],cue["memory"])
            self.assertEqual(cue["memory"],next_formation["pre"]["memory_state_digest"])
            self.assertEqual(next_formation["memory"],last["memory"])
            self.assertEqual(2,c["states"][last["memory"]]["generation"])
            self.assertEqual("CLOSED",c["final"][i]["status"])

    def test_04_valid_abstention_remains_functionally_falsifiable(self):
        self.assertEqual("RECORDING_COMPLETE",self.proof["status"])
        o=self.evaluation["observations"][1]
        self.assertEqual([None,None],o["areas"])
        self.assertEqual([False,False],o["prediction_met"])
        self.assertTrue(self.proof["composition"]["baseline_equal"])

    def test_05_payload_failure_is_phased_and_does_not_start_runtime(self):
        p=self.bound.payload()
        p["sources"][0]["payload_sha256"]="0"*64
        p["sources"][0]=run.sealed({k:v for k,v in p["sources"][0].items() if k!="source_digest"},"source_digest")
        p=run.sealed({k:v for k,v in p.items() if k!="execution_digest"},"execution_digest")
        bound=run.BoundExecution("NEUTRAL",run.canonical(p).decode())
        with patch.object(run.receptors.LogSpectralReceptor,"analyze",side_effect=AssertionError("must stop before receptor")):
            result=run.execute_once(bound,self.config,"s2nr-neutral-payload-failure",OUT/"neutral-failure")
        COUNTS["neutral_pcm_generations"]+=1
        self.assertEqual(("PAYLOAD_HASH",1,"neutral-audio","PAYLOAD_HASH_INVALID"),tuple(result["failure"][k] for k in ("phase","ordinal","source_id","code")))
        self.assertEqual(run.metrics(),result["materialization"])
        self.assertIsNone(result["comparison"])
        proof=checked(result,bound,self.config)
        self.assertEqual("NOT_EVALUABLE",proof["status"])
        archive("failure-proof.json",proof)

    def test_06_source_time_projection_and_completeness_manipulations(self):
        for kind in ("source","time","projection","missing","swapped"):
            with self.subTest(kind=kind):
                bad=deepcopy(self.record)
                if kind=="source": bad["source_receipts"][0]["sources"]["auditory"]["source_id"]="foreign"
                elif kind=="time": bad["comparison"]["inputs"][1]["projection"]["window_end_tick"]+=1
                elif kind=="projection":
                    values=list(bad["comparison"]["inputs"][1]["projection"]["values"])
                    values[0]=0.3
                    bad["comparison"]["inputs"][1]["projection"]["values"]=values
                elif kind=="missing": bad["comparison"]["scans"].pop()
                else: bad["comparison"]["pairs"][0],bad["comparison"]["pairs"][1]=bad["comparison"]["pairs"][1],bad["comparison"]["pairs"][0]
                bad["comparison"]=run.sealed({k:v for k,v in bad["comparison"].items() if k!="record_digest"},"record_digest")
                bad=run.sealed({k:v for k,v in bad.items() if k!="record_digest"},"record_digest")
                with self.assertRaises(run.S2NRRunError): checked(bad,self.bound,self.config)

    def test_07_provenance_support_and_original_receptor_variation(self):
        self.assertEqual([False,False],self.evaluation["observations"][0]["receptor_variation"])
        formations=self.evaluation["formations"]
        self.assertEqual(2,len(formations))
        self.assertTrue(all(x["origin"]["sources"]==["neutral-audio"] for x in formations[1]["inventory"] if x["bank"]!="B_STABLE_VISUAL"))
        values=[0.25]*48
        indices=tuple(range(24))
        self.assertFalse(evaluate.variation(values[:24],indices,[values]))
        drift=[0.25000000000000006]*48
        self.assertTrue(evaluate.variation(drift[:24],indices,[values]))
        outside=list(values); outside[47]=0.5
        self.assertFalse(evaluate.variation(outside[:24],indices,[values]))
        self.assertIsNone(evaluate.variation(values[:24],indices,[]))
        self.assertIsNone(evaluate.variation(values[:24],indices,[values,drift]))

    def test_08_gains_losses_and_empty_denominators_separate(self):
        rows=deepcopy(self.evaluation["observations"][:1])*2
        rows[0]=deepcopy(rows[0]); rows[1]=deepcopy(rows[1])
        rows[0]["correct"],rows[0]["areas"]=[True,False],["A_RECENT",None]
        rows[1]["correct"],rows[1]["areas"]=[False,True],[None,"A_RECENT"]
        rows[0]["event_id"],rows[1]["event_id"]="loss","gain"
        g=evaluate.summarize(rows)[0]
        self.assertEqual((1,0,1),tuple(g["public_retention"]["A_RECENT"][k] for k in ("D","R","L")))
        self.assertEqual(["loss"],g["losses"])
        self.assertEqual(["gain"],g["gains"])
        self.assertEqual("ERHALTUNG_NICHT_GEPRUEFT",g["public_retention"]["B_STABLE_AUDITORY"]["status"])

    def test_09_closed_main_and_immutable_bound_plan(self):
        self.assertFalse(run.MAIN_GATE or run.runtime.MAIN_GATE or run.nn.MAIN_GATE or run.ng.MAIN_GATE)
        with self.assertRaisesRegex(run.S2NRRunError,"MAIN_GATE_CLOSED_OR_USED"):
            run.run_main_once(run.RUN_ID,run.ROOT/"reports/s2nr"/run.RUN_ID)
        self.assertFalse((run.ROOT/"reports/s2nr"/run.RUN_ID).exists())
        with self.assertRaises(FrozenInstanceError): self.bound.mode="MAIN"
        # Read-only historical seal/version check, no source generation.
        self.assertEqual(run.EXECUTION_DIGEST,run.load_execution().payload()["execution_digest"])

    def test_10_atomic_write_conflict_and_total_envelope(self):
        with self.assertRaises(FileExistsError):
            run.execute_once(self.bound,self.config,"s2nr-conflict",OUT/"neutral-main")
        limit=run.EXTRA_VERIFICATION_BUDGET["total_envelope_bound"]
        self.assertLess(limit,run.ng.MAX_BYTES)
        envelope=dict(metadata="m"*65536,states={str(i):"s"*98304 for i in range(15)},
            inputs=["i"*16384 for _ in range(18)],pairs=["p"*16384 for _ in range(18)],
            scans=[dict(arm=1,ordinal=18,role="DIRECT_BASELINE",value="r"*32768) for _ in range(16)])
        total=dict(comparison=envelope,source_envelope="e"*65536)
        self.assertLess(len(run.canonical(total)),limit)
        archive("size-evidence.json",dict(neutral=len(run.canonical(self.record)),complete_envelope=len(run.canonical(total)),
            bound=limit,maximum=run.ng.MAX_BYTES,extra_verification=run.EXTRA_VERIFICATION_BUDGET))
        with self.assertRaises(ValueError):
            run.ng.ne.atomic_write(OUT/"too-large.json",dict(data="x"*run.ng.MAX_BYTES))
        self.assertFalse((OUT/"too-large.json").exists())

    def test_11_full_main_counts_cannot_accept_neutral_prefix(self):
        bad=deepcopy(self.record)
        bad["comparison"]["mode"]="MAIN"
        bad["comparison"]=run.sealed({k:v for k,v in bad["comparison"].items() if k!="record_digest"},"record_digest")
        bad=run.sealed({k:v for k,v in bad.items() if k!="record_digest"},"record_digest")
        with self.assertRaisesRegex(run.S2NRRunError,"COMPOSITION_BINDING_INVALID"):
            checked(bad,self.bound,self.config)
        budget=run.runtime.limits((run.source.AV,)*14+(run.source.A,)*4)
        self.assertEqual((18,28,16,9792,8448),tuple(budget[k] for k in ("events","formations","scans","field_contacts","verification_value_comparisons")))

    def test_12_failure_progress_and_verification_required_for_evaluation(self):
        p=json.loads((OUT/"neutral-failure"/"recording.json").read_bytes())
        p["failure"]["ordinal"]=2
        p=run.sealed({k:v for k,v in p.items() if k!="record_digest"},"record_digest")
        with self.assertRaisesRegex(run.S2NRRunError,"FAILURE_PHASE_PROGRESS_INVALID"):
            checked(p,self.bound,self.config)
        proof={**self.proof,"record_digest":"0"*64}
        proof=run.sealed({k:v for k,v in proof.items() if k!="verification_digest"},"verification_digest")
        evaluation=run.sealed(dict(execution_digest=self.bound.payload()["execution_digest"],cases=[]),"evaluation_digest")
        with self.assertRaisesRegex(run.S2NRRunError,"EVALUATION_REQUIRES_VERIFICATION"):
            evaluate.evaluate(self.record,proof,self.bound,evaluation)
