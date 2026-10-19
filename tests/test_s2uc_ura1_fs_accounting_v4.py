import json
from pathlib import Path
import tempfile
import time
import unittest
from tools._s2uc_ura1_fs_accounting_v4 import Terminal,Ledger,inventory,raw,SLOT


class AccountingTests(unittest.TestCase):
    def test_F11_worker_writes_and_register_categories(self):
        with tempfile.TemporaryDirectory() as folder:
            t=Terminal(folder,time.monotonic());l=Ledger(t)
            l.write('neutral-source.json',dict(neutral=True),'source')
            l.write('neutral.json',dict(neutral=True))
            l.write('result.json',dict(status='neutral'),'closure')
            s=l.check()
            self.assertEqual(s['groups']['source'],len(raw(dict(neutral=True))))
            self.assertEqual(s['groups']['admin'],len(raw(dict(neutral=True))))
            self.assertEqual(s['groups']['closure'],SLOT+len(raw(dict(status='neutral'))))
            self.assertEqual(s['groups']['temp'],0)

    def test_F12_preflight_preserves_reserve(self):
        with tempfile.TemporaryDirectory() as folder:
            t=Terminal(folder,time.monotonic());l=Ledger(t)
            l.limits['export']=SLOT+4
            with self.assertRaisesRegex(RuntimeError,'EXPORT_LIMIT'):l.write('x.json',dict(x=1))
            t.fail('EXPECTED');t.save()
            self.assertEqual(json.loads(t.path.read_bytes())['first_failure'],'EXPECTED')
            self.assertEqual(t.path.stat().st_size,SLOT)

    def test_F13_bounded_unicode_diagnosis_and_first_cause(self):
        with tempfile.TemporaryDirectory() as folder:
            t=Terminal(folder,time.monotonic())
            for n in range(12):
                try:raise OSError(str(n)+'界'*10000)
                except OSError as exc:t.diagnose(exc,'monitor')
            t.save();v=json.loads(t.path.read_bytes())
            self.assertTrue(v['first_failure'].startswith('OSError:0'))
            self.assertLessEqual(len(raw(v['first_diagnostic'])),4096)
            self.assertTrue(v['first_diagnostic']['location'])
            self.assertLessEqual(len(raw(v)),SLOT)

    def test_F14_temp_to_final_category_exact(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);f=p/'neutral-source.json.partial';f.write_bytes(b'x'*101)
            before=inventory(p)
            f.rename(p/'neutral-source.json')
            after=inventory(p)
            self.assertEqual(before['total'],after['total'])
            self.assertEqual(before['groups']['temp'],101)
            self.assertEqual(after['groups']['source'],101)


if __name__=='__main__':unittest.main()
