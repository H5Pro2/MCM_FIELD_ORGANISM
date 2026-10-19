"""New admission only; payload, worker and native runtime calls are forbidden."""
import copy
import json
import unittest
from unittest.mock import patch
from tools import _s2oe_media_session as m
from tools import _s2oe_local_player as player
from reports import qualify_uhd_admission_once as q


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.common=m.s.read_json(q.OUT/"prepared-common.json")
        self.manifest=m.p.decode(self.common["manifest"])
        self.inv=m.s.inventory()
        for target in ((m,"NativeRuntime"),(m.uhd.profile.worker,"WorkerDecoder")):
            self.enterContext(patch.object(*target,side_effect=AssertionError("NATIVE_CALL_FORBIDDEN")))

    def test_full_valid_admission(self):
        m.check_common(self.manifest,self.common,self.inv)

    def test_wrong_limits_rejected_before_initialization(self):
        for key in ("process_commit_bytes","job_commit_bytes"):
            with self.subTest(key=key):
                common=copy.deepcopy(self.common)
                common["decoder_resource_profile"][key]=536870912
                m.p.MAIN_GATE=True
                with self.assertRaises(m.uhd.profile.worker.WorkerError) as exc:
                    m.start(self.manifest,common,self.inv,q.OUT/"forbidden")
                self.assertEqual(exc.exception.code,"UHD_PROFILE_INVALID")
                self.assertFalse(m.p.MAIN_GATE)

    def test_mixed_run_and_source_bindings(self):
        for key,value,code in (("run_id","other-private-run","UHD_RUN_INVALID"),
                ("source",dict(self.common["decoder_profile"]["source"],sha256="0"*64),"UHD_SOURCE_INVALID")):
            with self.subTest(key=key):
                common=copy.deepcopy(self.common)
                profile=common["decoder_profile"]
                profile[key]=value
                profile.pop("profile_digest")
                profile["profile_digest"]=m.uhd.profile.sha(m.uhd.profile.canonical(profile))
                with self.assertRaises(m.uhd.profile.worker.WorkerError) as exc:
                    m.check_common(self.manifest,common,self.inv)
                self.assertEqual(exc.exception.code,code)

    def test_actual_resource_binding(self):
        digest=m.uhd.validate(self.manifest,self.common)
        resource=dict(private_profile=m.uhd.profile.VERSION,private_profile_digest=digest,
            private_run_id=self.manifest.run_id,process_commit_limit=1073741824,job_commit_limit=1073741824)
        m.uhd.verify_resources(self.manifest,self.common,resource)
        for key in ("process_commit_limit","job_commit_limit"):
            with self.subTest(key=key):
                with self.assertRaises(m.uhd.profile.worker.WorkerError) as exc:
                    m.uhd.verify_resources(self.manifest,self.common,dict(resource,**{key:536870912}))
                self.assertEqual(exc.exception.code,"UHD_RESOURCE_INVALID")

    def test_attestation_must_be_available(self):
        refs=[r for r in self.common["references"] if not r[1].endswith("decoder-uhd-sequence-20260911-01/verification.json")]
        with self.assertRaises(m.uhd.profile.worker.WorkerError) as exc:m.uhd.check_anchors(refs)
        self.assertEqual(exc.exception.code,"UHD_ATTESTATION_MISSING")

    def test_private_budget_and_default(self):
        self.assertEqual(m.p.SESSION_LIMITS["sources"],327680)
        self.assertEqual(m.b.LIMITS["sources"],174080)
        self.assertEqual(m.uhd.profile.worker.COMMIT_BYTES,536870912)
        self.assertEqual(m.p.SESSION_LIMITS["metadata"],131072)
        self.assertEqual(m.p.SESSION_LIMITS["shared"],393216)
        self.assertEqual(m.p.SESSION_LIMITS["total"],4194304)
        from tools._s2oc_shared_verification import synthetic_forms
        pair=synthetic_forms(self.common,0)[0]
        base=m.p.ledger(*pair,self.common)
        available=327680-base["totals"]["sources"]
        self.assertGreaterEqual(available,0)
        equal=m.p.ledger(*pair,self.common,attachments=(("sources","@edge",available),))
        over=m.p.ledger(*pair,self.common,attachments=(("sources","@edge",available+1),))
        self.assertNotIn("SOURCES_LIMIT",equal["violations"])
        self.assertIn("SOURCES_LIMIT",over["violations"])
