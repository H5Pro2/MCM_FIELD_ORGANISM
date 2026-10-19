"""Prestart controls and integrity tests; all policy fixtures <=8 frames."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import s2uc_ura1_delta_size_once as runner
from tools import _s2uc_ura1_delta_encode as archive
from tools._s2uc_ura1_delta_encode import collection
from tools._s2uc_ura1_capture_integrity import manifest,full_record_digest
from tools._s2uc_ura1_delta_decode import verify


class SizeTests(unittest.TestCase):
    def test_S01_binding_material_runtime_limits_and_code(self):
        with tempfile.TemporaryDirectory() as parent:
            path=Path(parent)/'prestart.json'
            b=dict(limits=runner.LIMITS,target=str(runner.TARGET),runtime=runner.runtime(),
                   material=dict(frames=1024,sha256=hashlib.sha256(runner.raw(runner.material())).hexdigest()),
                   files={'tools/_s2uc_ura1.py':runner.sha(runner.ROOT/'tools/_s2uc_ura1.py')},
                   call=[runner.sys.executable,'-m','tools.s2uc_ura1_delta_size_once','run',str(path.resolve())])
            def write(value):
                path.write_bytes(runner.raw(value));path.with_suffix('.sha256').write_text(runner.sha(path))
            write(b);runner.validate_binding(path,True)
            for field in ('limits','target','runtime','material','files','call'):
                changed=json.loads(json.dumps(b))
                if field=='limits':changed[field]['encoded']+=1
                elif field=='target':changed[field]+='-other'
                elif field=='runtime':changed[field]['version']='wrong'
                elif field=='material':changed[field]['sha256']='0'*64
                elif field=='files':changed[field]['tools/_s2uc_ura1.py']='0'*64
                else:changed[field]=[]
                write(changed)
                with self.subTest(field=field),self.assertRaises(ValueError):runner.validate_binding(path,True)
            write(b);path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'PRESTART_HASH'):runner.validate_binding(path)

    def test_S02_exclusive_marker_consumed(self):
        with tempfile.TemporaryDirectory() as parent:
            runner.reserve(parent,'a'*64);first=(Path(parent)/'START.json').read_bytes()
            with self.assertRaises(FileExistsError):runner.reserve(parent,'b'*64)
            self.assertEqual(first,(Path(parent)/'START.json').read_bytes())

    def test_S03_small_end_to_end_independent_integrity(self):
        from tools._s2uc_ura1_direct_neutral import blocks
        with tempfile.TemporaryDirectory() as parent:
            result=runner.execute_case(Path(parent),blocks([(.125,.25)]*2),small=True)
            self.assertEqual(result['status'],'PASS_SMALL')
            self.assertEqual(result['integrity'],'PASS_DELTA_INTEGRITY')
            self.assertTrue(result['paired_equal']);self.assertTrue(result['store_released'])
            proof=json.loads((Path(parent)/'capture-integrity.json').read_text())
            self.assertEqual(len(proof['collections']),8)

    def test_S04_independent_anchors_reject_rehashed_encoder_corruption(self):
        for fault in ('value','missing','swapped'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as parent,archive.store(parent) as owner:
                seq=collection()
                seq.append(dict(original=3,values=[.25],cells=[.1,.2],ticket=[1,1,0]))
                seq.append(dict(original=7,values=[.75],cells=[.3,.4],ticket=[0,2,0]))
                seq.append(dict(original=11,values=[.5],cells=[.5,.6],ticket=[0,3,0]))
                record=dict(events=seq,neutral=True);proof=manifest(record)
                if fault=='missing':seq.ids.pop()
                elif fault=='swapped':seq.ids.reverse()
                else:
                    for i,(tag,body) in enumerate(owner.pool.nodes):
                        if tag=='scalar' and type(body) is float and body==.25:
                            owner.pool.nodes[i]=(tag,.375);break
                # Envelope checksum is recomputed over corrupted encoder output.
                expected=full_record_digest(record)
                target=Path(parent)/'case.gz';archive.write_archive(record,target,expected)
                with self.assertRaisesRegex(ValueError,'CAPTURE_'):verify(target.read_bytes(),proof)

    def test_S05_dictionary_abort_progress_cleanup(self):
        from tools._s2uc_ura1_direct_neutral import blocks
        with tempfile.TemporaryDirectory() as parent:
            result=runner.execute_case(Path(parent),blocks([(.125,.25)]*2),small=True,inject_limit=1024)
            self.assertEqual(result['status'],'TECHNICAL_ABORT')
            self.assertIn('DICTIONARY_LIMIT',result['first_failure'])
            self.assertTrue(result['store_released'])
            self.assertTrue(all(x['closed'] and x['bank_zero'] and x['originals_released'] for x in result['arm_cleanup']))
            self.assertFalse((Path(parent)/'case.delta.json.gz').exists())
            self.assertTrue((Path(parent)/'partial-capture-integrity.json').exists())

    def test_S06_small_hull_unchanged_and_large_requires_exact_material(self):
        from tools._s2uc_ura1_direct_neutral import run_arm,blocks
        with self.assertRaisesRegex(ValueError,'NEUTRAL_ONLY_MAX_128_FRAMES'):
            run_arm(blocks([(.125,.25)]*33),'U',trace=True)
        with tempfile.TemporaryDirectory() as parent:
            with self.assertRaisesRegex(ValueError,'FIXED_MATERIAL_ONLY'):
                runner.execute_case(Path(parent),blocks([(.125,.25)]*2))
        for name in ('ura1-neutral-development-20261014-01','ura1-codec-development-20261014-01','ura1-resource-development-20261014-01','ura1-direct-development-20261015-01','ura1-size-neutral-20261015-01','ura1-delta-development-20261015-01'):
            folder=runner.ROOT/'reports/s2uc'/name
            for path,entry in json.loads((folder/'closure.json').read_text())['files'].items():
                self.assertEqual(runner.sha(folder/path),entry['sha256'])

    def test_S07_export_preparation_and_administration_guards(self):
        with tempfile.TemporaryDirectory() as parent:
            target=Path(parent)/'check.json'
            with patch.object(runner,'treebytes',return_value=runner.LIMITS['export']):
                with self.assertRaisesRegex(ValueError,'EXPORT_LIMIT'):runner.save(target,{'x':1})
            with patch.object(runner,'treebytes',return_value=runner.LIMITS['preparation']):
                with self.assertRaisesRegex(ValueError,'PREPARATION_LIMIT'):runner.save(runner.PREP/'check.json',{'x':1})
            with patch.object(runner,'TARGET',Path(parent)):
                (Path(parent)/'occupied.json').write_bytes(b'x'*runner.LIMITS['administration'])
                with self.assertRaisesRegex(ValueError,'ADMINISTRATION_LIMIT'):runner.save(target,{'x':1})
            self.assertFalse(target.exists())


if __name__=='__main__':unittest.main()
