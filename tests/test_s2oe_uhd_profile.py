"""Only new profile boundaries; no historical browser/worker tests."""
from dataclasses import dataclass,replace
import json
import unittest
from unittest.mock import patch
from tools import _s2oe_uhd_profile as p


@dataclass(frozen=True)
class Source:
    path:str="neutral-uhd-profile.mp4"
    sha256:str="a"*64
    size:int=64


def changed(raw,change):
    data=json.loads(raw)
    data.pop("profile_digest")
    change(data)
    data["profile_digest"]=p.sha(p.canonical(data))
    return p.canonical(data)


class Stub:
    def __init__(self,source,*,diagnostic_arm):
        assert diagnostic_arm=="COMMIT_1024"
        self.resources=dict(process_commit_limit=1073741824,job_commit_limit=1073741824)
        self.closed=False

    def close(self):
        self.closed=True


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.source=Source()
        self.run="neutral-profile-run-01"
        self.raw=p.bind(self.source,self.run)

    def error(self,code,raw,source=None,run=None):
        with self.assertRaises(p.worker.WorkerError) as exc:
            p.validate(raw,source or self.source,run or self.run)
        self.assertEqual(exc.exception.code,code)

    def test_immutable_profile_and_default(self):
        self.assertIsInstance(self.raw,bytes)
        self.assertEqual(p.validate(self.raw,self.source,self.run),json.loads(self.raw)["profile_digest"])
        self.assertEqual(p.worker.COMMIT_BYTES,536870912)

    def test_false_process_and_job_limits_independently(self):
        for field in ("process_commit_bytes","job_commit_bytes"):
            with self.subTest(field=field):
                raw=changed(self.raw,lambda d:d["config"].update({field:536870912}))
                self.error("UHD_PROFILE_INVALID",raw)

    def test_other_configuration_rejected(self):
        for field in ("video_threads","queue_capacity","request_seconds","stop_seconds"):
            with self.subTest(field=field):
                self.error("UHD_PROFILE_INVALID",changed(self.raw,lambda d:d["config"].update({field:999})))

    def test_source_and_run_separation(self):
        self.error("UHD_SOURCE_INVALID",self.raw,source=replace(self.source,sha256="b"*64))
        self.error("UHD_RUN_INVALID",self.raw,run="neutral-profile-run-02")

    def test_code_and_integrity(self):
        self.error("UHD_CODE_INVALID",changed(self.raw,lambda d:d["code"].update({p.OWN[0]:"c"*64})))
        data=json.loads(self.raw)
        data["source"]["size"]=65
        self.error("UHD_DIGEST_INVALID",p.canonical(data))

    def test_factory_and_active_limit_failure(self):
        with patch.object(p.worker,"WorkerDecoder",Stub):
            decoder=p.open_decoder(self.source,self.raw,self.run)
        self.assertEqual(decoder.resources["private_run_id"],self.run)
        decoder.close()
        bad=Stub(self.source,diagnostic_arm="COMMIT_1024")
        bad.resources["job_commit_limit"]=536870912
        with patch.object(p.worker,"WorkerDecoder",return_value=bad):
            with self.assertRaises(p.worker.WorkerError) as exc:
                p.open_decoder(self.source,self.raw,self.run)
        self.assertEqual(exc.exception.code,"UHD_ACTIVE_LIMIT_INVALID")
        self.assertTrue(bad.closed)
