"""Fresh synthetic parent; no historical perception is executed."""
from dataclasses import asdict, replace
import json
from pathlib import Path
import tempfile
import unittest
from tools import _s2oe_immediate_visual_input as p


def fixture(path):
    from tools import _s2oe_immediate_visual_control as control
    from mcm_field_organism.broadband_hearing_path import AuditoryReceptorState, AuditoryReceptorContact
    n = control.nn
    config = n.profile.build_config()
    raw = AuditoryReceptorState("auditory", n.half.RAW_GEOMETRY,40,19200,24000,
        tuple(b.channel_id for b in n.half.spectral.logarithmic_bands(n.LogSpectralConfig())),
        (0.5,)*48,AuditoryReceptorContact.ACTIVE_ENERGY)
    vp = config.profile.profile.visual_config
    vt = n.CommonFieldTime("s2ob-caller-field-clock",466666666,500000000)
    visual = n.OrganismTimedReceptorFrame(n.ReceptorContactFrame("visual",vp.geometry_id,
        "neutral.visual.14","video.frame",14,15,vp.carrier_ids,(0.25,)*288),vt)
    bound = n.bind_event(config=config,event_id="media-event-03",ordinal=3,
        event_type="COMPLETE_AV_PERCEPTION",field_start_tick=300000000,
        common_time=vt,
        raw_audio=raw,pcm_digest="1"*64,visual=visual,rgb_digest="2"*64,visual_time_binding=vt)
    item = n.ng.pack_input(bound.event,config)
    receipt = dict(nj=dict(pcm_digest="1"*64),rgb_digest="2"*64,source_digest=bound.event.source_digest)
    parent = dict(record=dict(execution=dict(inputs=[None,None,item],source_receipts=[None,None,receipt],
                                            config_digest=config.config_digest)))
    raw_parent = p.canonical(parent)
    path.write_bytes(raw_parent)
    binding = p.ParentBinding(str(path),len(raw_parent),p.sha(raw_parent),bound.event.event_digest,
                              config.config_digest,True)
    return raw_parent,binding


def administrative_fixture(path):
    # Structural provenance fixture only; not a native formation input.
    event=dict(event_id="media-event-03",ordinal=3,event_type="COMPLETE_AV_PERCEPTION",
               event_digest="3"*64,source_digest="4"*64)
    item=dict(event=event,operation=dict(auditory_payload_digest="1"*64,visual_payload_digest="2"*64),
        field=dict(timed_frames=[dict(frame=dict(modality_id="auditory",values=[0.25]*48)),
                                 dict(frame=dict(modality_id="visual",values=[0.25]*288))]))
    receipt=dict(nj=dict(pcm_digest="1"*64),rgb_digest="2"*64,source_digest="4"*64)
    parent=dict(record=dict(execution=dict(inputs=[None,None,item],source_receipts=[None,None,receipt],
                                          config_digest="5"*64)))
    data=p.canonical(parent)
    path.write_bytes(data)
    return data,p.ParentBinding(str(path),len(data),p.sha(data),"3"*64,"5"*64,True)


class InputTests(unittest.TestCase):
    body_calls = 0

    def _callTestMethod(self, method):
        type(self).body_calls += 1
        return super()._callTestMethod(method)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/"neutral-parent.json"
        self.raw,self.binding = administrative_fixture(self.path)

    def rejects(self,code,fn):
        with self.assertRaises(p.InputError) as caught:
            fn()
        self.assertEqual(code,caught.exception.code)

    def altered(self,change):
        obj=json.loads(self.raw); change(obj["record"]["execution"])
        raw=p.canonical(obj)
        return raw,replace(self.binding,byte_count=len(raw),sha256=p.sha(raw))

    def test_01_full_parent_and_exact_extract(self):
        e=p.extract(self.raw,self.binding)
        self.assertTrue(p.verify_extract(e,self.raw,self.binding))
        self.assertEqual(288,len(json.loads(e)["input"]["field"]["timed_frames"][1]["frame"]["values"]))

    def test_02_missing_parent(self):
        self.path.unlink()
        self.rejects("PARENT_MISSING",lambda:p.read_extract(self.binding,dict(bytes=0,operations=0)))

    def test_03_tampered_parent(self):
        self.rejects("PARENT_CONTENT_INVALID",lambda:p.extract(self.raw+b" ",self.binding))

    def test_04_wrong_event(self):
        raw,b=self.altered(lambda x:x["inputs"][2]["event"].update(event_id="other-event"))
        self.rejects("EVENT_BINDING_INVALID",lambda:p.extract(raw,b))

    def test_05_missing_values(self):
        raw,b=self.altered(lambda x:x["inputs"][2]["field"]["timed_frames"][0]["frame"].update(values=[]))
        self.rejects("VALUES_BINDING_INVALID",lambda:p.extract(raw,b))

    def test_06_tampered_excerpt(self):
        e=p.extract(self.raw,self.binding)
        obj=json.loads(e);obj["input"]["field"]["timed_frames"][1]["frame"]["values"][0]=0.5
        self.rejects("EXTRACTION_RELATION_INVALID",lambda:p.verify_extract(p.canonical(obj),self.raw,self.binding))

    def test_07_wrong_profile(self):
        self.rejects("PROFILE_BINDING_INVALID",lambda:p.extract(self.raw,replace(self.binding,config_digest="0"*64)))

    def test_08_source_binding(self):
        raw,b=self.altered(lambda x:x["source_receipts"][2].update(rgb_digest="3"*64))
        self.rejects("SOURCE_BINDING_INVALID",lambda:p.extract(raw,b))

    def test_09_read_bytes_not_storage_multiplicity(self):
        r=dict(bytes=0,operations=0)
        p.read_extract(self.binding,r);p.read_extract(self.binding,r)
        self.assertEqual(dict(bytes=2*len(self.raw),operations=2),r)
        measured=p.balance(self.binding,metadata=0,sources=0,verification=0,supplement=0,data=0)
        self.assertEqual(len(self.raw),measured["totals"]["total"])

    def test_10_scope_closed(self):
        self.rejects("HISTORICAL_CLASS_SCOPE_INVALID",lambda:replace(self.binding,neutral=False).validate())

    def test_11_historical_limit(self):
        replace(self.binding,byte_count=p.HISTORICAL_LIMIT).validate()
        self.rejects("HISTORICAL_INPUT_LIMIT",lambda:replace(self.binding,byte_count=p.HISTORICAL_LIMIT+1).validate())

    def test_12_global_limit(self):
        common=dict(metadata=0,sources=0,verification=0,supplement=0)
        m=p.balance(self.binding,**common,data=p.LIMITS["total"]-len(self.raw))
        p.enforce_balance(m)
        m=p.balance(self.binding,**common,data=p.LIMITS["total"]-len(self.raw)+1)
        self.assertEqual(["total"],m["violations"])
        self.rejects("BUDGET_EXCEEDED",lambda:p.enforce_balance(m))

    def test_13_existing_class_limits(self):
        for key in ("metadata","sources","verification"):
            with self.subTest(key=key):
                args=dict(metadata=0,sources=0,verification=0,supplement=0,data=0)
                args[key]=p.LIMITS[key]+1
                self.assertIn(key,p.balance(self.binding,**args)["violations"])

    def test_14_native_empty_formation_immediate(self):
        from tools import _s2oe_immediate_visual_control as control
        self.raw,self.binding = fixture(self.path)
        e=p.extract(self.raw,self.binding)
        result=control.run(e,self.binding,run_id="neutral-immediate-visual",neutral=True)
        self.assertEqual("RECORDING_COMPLETE",result["status"])
        self.assertEqual(["ABSTAIN_NO_CONTEXT","ADMIT_SINGLE_CONTEXT"],
                         [s["primary"]["decision"] for s in result["scans"]])
        for s in result["scans"]:
            a,b=s["primary"],s["direct"]
            for key in ("decision","public_candidate_count","prestate_digest","poststate_digest"):
                self.assertEqual(a[key],b[key])
            self.assertEqual(a["prestate_digest"],a["poststate_digest"])
            self.assertTrue(all(v is None for v in s["cue"]["values"][32:]))
        self.assertEqual(0,result["field_calls"]+result["receptor_calls"]+result["nj_calls"])
        for s in result["states"]:
            self.assertLessEqual(len(p.canonical(s)),98304)
        self.assertLessEqual(len(p.canonical(result["formation"])),1536)
        for s in result["scans"]:
            for key in ("primary","direct"):
                self.assertLess(len(p.canonical(s[key])),32768)
        self.assertLessEqual(len(p.canonical(result)),393216)

    def test_15_extraction_immutable(self):
        e=p.extract(self.raw,self.binding)
        obj=json.loads(e);obj["index"]=0
        self.assertEqual(e,p.extract(self.raw,self.binding))

    def test_16_real_gate_closed(self):
        from tools import _s2oe_immediate_visual_control as control
        self.rejects("MAIN_GATE_CLOSED",lambda:control.run(b"",self.binding,run_id="no-run",neutral=False))

    def test_17_shared_limit(self):
        m=p.balance(self.binding,metadata=0,sources=174080,verification=0,supplement=88065,data=0)
        self.assertEqual(["shared"],m["violations"])

    def test_18_invalid_parent_structure(self):
        raw=b"{}";b=replace(self.binding,byte_count=len(raw),sha256=p.sha(raw))
        self.rejects("PARENT_FORM_INVALID",lambda:p.extract(raw,b))

    def test_19_presentation_values_and_origin(self):
        from tools import _s2oe_immediate_visual_control as control
        value=json.loads(p.extract(self.raw,self.binding));before=p.canonical(value)
        presentations=[control.presentation(value,i) for i in range(3)]
        parsed=[json.loads(x) for x in presentations]
        self.assertEqual(3,len({x["presentation_id"] for x in parsed}))
        self.assertEqual(3,len({x["presentation_digest"] for x in parsed}))
        self.assertEqual(1,len({x["values_digest"] for x in parsed}))
        self.assertTrue(all(x["parent_sha256"]==self.binding.sha256 and not x["measurement"] for x in parsed))
        self.assertEqual(before,p.canonical(value))

    def test_20_presentation_foreign_origin(self):
        from tools import _s2oe_immediate_visual_control as control
        value=json.loads(p.extract(self.raw,self.binding))
        blob=control.presentation(value,2);value["parent_sha256"]="0"*64
        self.rejects("PRESENTATION_BINDING_INVALID",lambda:control.validate_presentation(blob,value,2))

    def test_21_stale_presentation(self):
        from tools import _s2oe_immediate_visual_control as control
        value=json.loads(p.extract(self.raw,self.binding))
        changed=json.loads(control.presentation(value,2));changed["visual_window"]=[14,15]
        changed["presentation_digest"]=p.sha(p.canonical({k:v for k,v in changed.items() if k!="presentation_digest"}))
        self.rejects("PRESENTATION_BINDING_INVALID",lambda:control.validate_presentation(p.canonical(changed),value,2))

    def test_22_contradictory_session_time(self):
        from tools import _s2oe_immediate_visual_control as control
        value=json.loads(p.extract(self.raw,self.binding))
        changed=json.loads(control.presentation(value,2));changed["visual_session_window"]=[300000000,333333333]
        changed["presentation_digest"]=p.sha(p.canonical({k:v for k,v in changed.items() if k!="presentation_digest"}))
        self.rejects("PRESENTATION_BINDING_INVALID",lambda:control.validate_presentation(p.canonical(changed),value,2))
