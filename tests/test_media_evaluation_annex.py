import os
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from tools import _media_evaluation_annex as a

OUT = Path(os.environ["MEDIA_ANNEX_QUAL_OUT"])


def fixture():
    account = dict(version="neutral", completed=20, materializer=dict(audio=20,nj=20,visual=20),
        work=dict(prior=dict(packets=1), parts=dict(replay=dict(packets=2), regular=dict(packets=3))))
    proof = dict(status="RECORDING_COMPLETE", evaluation_allowed=True,
        rows=[dict(ordinal=n,equal=True) for n in range(1,21)],
        core_equal=True,selections_equal=True,final_field_equal=True)
    return NS(manifest_digest="1"*64), proof, dict(reference=account,restore20=account)


class Annex(unittest.TestCase):
    def store(self):
        s = a.e.Store(OUT/self._testMethodName, budget_profile=a.profile.payload(), publication_plan=a.plan())
        s.publish_profile()
        return s

    def test_01_complete_structure(self):
        s=self.store()
        with patch.object(a.entry.p,"verify_comparison",side_effect=AssertionError("no verification")), \
             patch.object(a.entry.c,"Session",side_effect=AssertionError("no session")):
            result=a.evaluate_once(s,*fixture())
        self.assertEqual(s.read(s.root/"evaluation.json"),result)
        self.assertEqual(result["status"],"CONFIRMED")
        self.assertEqual(len(result["rows"]),20)
        self.assertEqual(len(list((s.root/"objects").iterdir())),21)

    def test_02_unknown_positions(self):
        p=a.e.publication.Plan.bind(a.plan())
        for role in ("evaluation.json#/rows/20","evaluation.json#/rows/x","evaluation.json#/rows/0/extra","other.json"):
            with self.subTest(role=role),self.assertRaises(a.e.publication.PlanError) as caught:
                p.offer(role,"native",1)
            self.assertEqual(caught.exception.code,"PUBLICATION_POSITION_MISSING")

    def test_03_size_boundary(self):
        p=a.e.publication.Plan.bind(a.plan())
        p.offer("evaluation.json#/rows/19","native",128)
        with self.assertRaises(a.e.publication.PlanError) as caught:
            p.offer("evaluation.json#/rows/19","native",129)
        self.assertEqual(caught.exception.code,"PUBLICATION_POSITION_SIZE")

    def test_04_one_use(self):
        s=self.store()
        a.evaluate_once(s,*fixture())
        before={p.name:p.read_bytes() for p in s.root.iterdir() if p.is_file()}
        with self.assertRaises(a.entry.w.RestartError) as caught:
            a.evaluate_once(s,*fixture())
        self.assertEqual(caught.exception.code,"ANNEX_ALREADY_USED")
        self.assertEqual(before,{p.name:p.read_bytes() for p in s.root.iterdir() if p.is_file()})

    def test_05_complete_rows_required(self):
        for change in ("missing","swapped","extra"):
            with self.subTest(change=change):
                m,p,v=fixture()
                if change=="missing": p["rows"].pop()
                elif change=="swapped": p["rows"][0],p["rows"][1]=p["rows"][1],p["rows"][0]
                else: p["rows"][0]["formation"]={"bad":1}
                with self.assertRaises(a.entry.w.RestartError) as caught: a.shape(p)
                self.assertEqual(caught.exception.code,"ANNEX_ROWS_FORM")

    def test_06_negative_evaluable(self):
        s=self.store()
        m,p,v=fixture()
        p["core_equal"]=False
        p["rows"][0]["equal"]=False
        self.assertEqual(a.evaluate_once(s,m,p,v)["status"],"FALSIFIED")

    def test_07_evaluation_gate(self):
        s=self.store()
        m,p,v=fixture()
        p["evaluation_allowed"]=False
        with self.assertRaises(a.entry.w.RestartError) as caught: a.evaluate_once(s,m,p,v)
        self.assertEqual(caught.exception.code,"ANNEX_EVALUATION_BLOCKED")
        self.assertFalse((s.root/"run.claim").exists())

    def test_08_plan_completeness_and_budget(self):
        plan=a.plan()
        plan["positions"].pop(3)
        with self.assertRaises(a.e.publication.PlanError): a.e.publication.Plan.bind(plan)
        s=self.store()
        s.preflight()
        with self.assertRaises(a.e.publication.PlanError) as caught:
            s._write(s.root/"result.json",b"x"*8193,"metadata")
        self.assertEqual(caught.exception.code,"PUBLICATION_POSITION_SIZE")


if __name__ == "__main__": unittest.main()
