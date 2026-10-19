"""Focused V4 admission and unchanged-recipe checks; no research material."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import s2uc_ura1_prepare_v4 as run
from tools import _s2uc_ura1_v4_sources as src
from tools import _s2uc_ura1_v4_source_reference as ref
from tools import _s2uc_ura1_v3_sources as old


class PreparationV4Tests(unittest.TestCase):
    def test_N01_research_generation_locked_before_hash(self):
        with patch.object(src.hashlib,'sha256',side_effect=AssertionError('FORBIDDEN_RESEARCH_HASH')):
            with self.assertRaises(PermissionError):src.generate(1,neutral=False)
            with self.assertRaises(PermissionError):ref.verify({},1,neutral=False)

    def test_N02_only_neutral_recipe_and_independent_reference(self):
        for r in (1,2):
            value=src.generate(r)
            self.assertEqual(value,old.generate(r))
            self.assertTrue(ref.verify(value,r)['reference_equal'])

    def test_N03_source_changes_are_namespace_and_admission_only(self):
        base=Path(old.__file__).read_text().replace('prepare_v3','prepare_v4').replace('source/v3','source/v4')
        self.assertEqual(base,Path(src.__file__).read_text())
        base=(run.ROOT/'tools/_s2uc_ura1_v3_source_reference.py').read_text().replace('_ura1_v3_sources','_ura1_v4_sources').replace('source/v3','source/v4')
        self.assertEqual(base,Path(ref.__file__).read_text())

    def test_N04_authorization_required_and_old_kind_rejected(self):
        with tempfile.TemporaryDirectory() as d,patch.object(run,'AUTH',Path(d)/'authorization.json'):
            with self.assertRaises(FileNotFoundError):run.authorization(run.AUTH,'a'*64)
            run.AUTH.write_text(json.dumps(dict(kind='URA1_RESEARCH_ONCE_V3',prestart_sha256='a'*64,allow_research=True)))
            with self.assertRaises(PermissionError):run.authorization(run.AUTH,'a'*64)

    def test_N05_existing_target_cannot_resume(self):
        with tempfile.TemporaryDirectory() as d,patch.object(run,'TARGET',Path(d)),patch.object(run,'install_job'),patch.object(run,'validate_binding',return_value=({},'a'*64)),patch.object(run,'authorization'),patch.object(run,'launch',side_effect=AssertionError('NO_LAUNCH')):
            with self.assertRaises(FileExistsError):run.run('unused','unused')

    def test_N06_new_target_and_authorization_absent(self):
        self.assertFalse(run.TARGET.exists())
        self.assertFalse(run.AUTH.exists())
        self.assertEqual(run.NAMESPACE,'MCM-URA1/source/v4')


    def test_N07_integrated_components_and_disabled_research_faults(self):
        import time
        from tools import _s2uc_ura1_fs_accounting_v4 as fs
        self.assertIs(run.Terminal,fs.Terminal)
        self.assertIs(run.supervise,fs.supervise)
        self.assertTrue(issubclass(run.IntegratedLedger,fs.Ledger))
        with tempfile.TemporaryDirectory() as d:
            t=run.Terminal(d,time.monotonic());t.begin(2)
            l=run.IntegratedLedger(t,0,'research');l.arm_started=True;l.check()
            self.assertFalse(l.fired)
            self.assertFalse(list(Path(d).glob('neutral-*')))

if __name__=='__main__':unittest.main()
