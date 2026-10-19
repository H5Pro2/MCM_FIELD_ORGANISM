import copy
import tempfile
import unittest
from pathlib import Path
from fractions import Fraction as F
from unittest.mock import patch
from tools import _s2uc_ura1_v2_sources as src
from tools import _s2uc_ura1_v2_source_reference as sr
from tools import _s2uc_ura1_v2_stats as st
from tools import _s2uc_ura1_v2_stats_reference as ref
from tools._s2uc_ura1_v2_series import Ledger,LIMITS,execute,policy_case


def artificial_reports():
    """32 numerical tables, not stories, sources or policy executions."""
    return [dict(replicate=r,orientation=(r-1)%2,complete=True,rows=[dict(
        target=3+2*i,U=float((r%4)/16+(i%5)/64),R=float(((r+1)%4)/16+(i%3)/64),
        cue=('X' if (i//2)%2==0 else 'Y') if i%2==0 else None,
        eligible=i%3,warm=('none','cold','mixed','warm')[i%4],same_output=i%2==0,
        choice=('both_persistence','mixed','same_context','different_context')[i%4]) for i in range(511)]) for r in range(1,33)]


class PreparationTests(unittest.TestCase):
    def test_P01_research_gate_and_neutral_recipe(self):
        with patch.object(src.hashlib,'sha256',side_effect=AssertionError('RESEARCH_HASH_FORBIDDEN')):
            with self.assertRaises(PermissionError):src.generate(1,neutral=False)
            with self.assertRaises(PermissionError):sr.verify({},1,neutral=False)
        for r in (1,2):
            v=src.generate(r);self.assertTrue(sr.verify(v,r)['reference_equal'])
            for field in ('ids','catalog','draws','orientation','neutral_only'):
                x=copy.deepcopy(v)
                if field=='ids':x[field][0]=1-x[field][0]
                elif field=='catalog':x[field][0][0]+=.01
                elif field=='draws':x[field]['continuation']+=1
                else:x[field]=not x[field]
                with self.assertRaises(ValueError):sr.verify(x,r)

    def test_P02_draw_rejection_limit_and_hand_permutation(self):
        s=src.Stream(1,'continuation',draw=lambda d:(2**64-1) if d==0 else 0)
        self.assertEqual(s.below(3),0);self.assertEqual(s.cursor,2)
        t=src.Stream(1,'dependent-A',draw=lambda _:0)
        self.assertEqual(t.shuffle([0,1,2]),[1,2,0]);self.assertEqual(t.cursor,2)
        bad=src.Stream(1,'continuation',draw=lambda _:2**64-1)
        with self.assertRaisesRegex(ValueError,'DRAW_LIMIT'):bad.below(3)
        self.assertEqual(bad.cursor,4096)

    def test_P03_matrix_orientation_quantiles_and_zero_boundary(self):
        from tools.s2uc_ura1_prepare_v2 import PREP
        data=(PREP/'bootstrap.bin').read_bytes()
        self.assertTrue(ref.verify_matrix(data))
        damaged=bytearray(data);damaged[0]^=1
        with self.assertRaises(ValueError):ref.verify_matrix(damaged)
        with self.assertRaises(ValueError):st.interval([F()]*32,damaged)
        for value in (F(-1,4),F(),F(1,4)):
            self.assertEqual(st.interval([value]*32,data),[str(value)]*2)
            self.assertEqual(ref.interval([value]*32,data),[str(value)]*2)
        self.assertEqual(st.quantile([F(0),F(10)],F(1,40)),F(1,4))

    def test_P04_complete_targets_and_diagnostic_rejection(self):
        base=artificial_reports();st.validate(base)
        for fault in ('case','duplicate','target','orientation','cue','nan','label'):
            v=copy.deepcopy(base)
            if fault=='case':v.pop()
            elif fault=='duplicate':v[0]['replicate']=2
            elif fault=='target':v[0]['rows'].pop()
            elif fault=='orientation':v[0]['orientation']=1
            elif fault=='cue':v[0]['rows'][0]['cue']='Y'
            elif fault=='nan':v[0]['rows'][0]['U']=float('nan')
            else:v[0]['rows'][0]['warm']='invalid'
            with self.assertRaises(ValueError):st.validate(v)

    def test_P05_cumulative_budgets_and_final_deadline(self):
        with tempfile.TemporaryDirectory() as p:
            now=[0];limits=LIMITS|dict(worker_seconds=10,total_seconds=12,administration=30)
            l=Ledger(p,0,0,clock=lambda:now[0],limits=limits)
            l.write('a.json',{'x':'1'*8})
            with self.assertRaises(ValueError):l.write('b.json',{'x':'2'*8})
            now[0]=10.1
            with self.assertRaisesRegex(TimeoutError,'WORKER'):l.check()
            l.final=True;l.check();now[0]=12.1
            with self.assertRaisesRegex(TimeoutError,'GLOBAL'):l.check()
            self.assertFalse(list(Path(p).glob('*.partial')))
        with tempfile.TemporaryDirectory() as p:
            l=Ledger(p,0,0,clock=lambda:0,limits=LIMITS|dict(export=5))
            with self.assertRaisesRegex(ValueError,'EXPORT'):l.write('x.json',{'x':1})

    def test_P06_series_count_abort_and_cleanup(self):
        with tempfile.TemporaryDirectory() as p:
            l=Ledger(p,0,0,clock=lambda:0);seen=[]
            def run(n,v,ledger):seen.append(n);return dict(replicate=n,cleanup=n!=2)
            with self.assertRaisesRegex(ValueError,'SERIES_CLEANUP'):execute([(1,None),(2,None),(3,None)],run,l,[1,2,3])
            self.assertEqual(seen,[1,2])
            with self.assertRaisesRegex(ValueError,'SERIES_CASES'):execute([(1,None)],run,l,[1,2])
            with self.assertRaisesRegex(ValueError,'SERIES_CASES'):execute([(1,None),(1,None)],run,l,[1,1])

    def test_P07_short_policy_reset_and_terminal_cleanup(self):
        from tools import _s2uc_ura1_v2_engine as engine
        import tools._s2uc_ura1_delta_encode as codec
        catalog=[[x+j/4096 for j in range(48)] for x in (.125,.875,.5,.25,.75,.0625)]
        material=dict(catalog=catalog,ids=[0,2,3,5,0,2,3,5])
        arms=[];create=engine.create
        def tracked(mode):
            a=create(mode);arms.append(a);return a
        with tempfile.TemporaryDirectory() as p,patch.object(engine,'create',tracked):
            l=Ledger(p,0,0,clock=lambda:0)
            rs=execute([(1,material),(2,material)],lambda n,v,l:policy_case(n,v,l,neutral=True),l,[1,2])
            self.assertEqual(rs[0]['rows'],rs[1]['rows']);self.assertEqual(len({id(x) for x in arms}),4)
            self.assertTrue(all(a.closed and not any(a.bank) for a in arms));self.assertIsNone(codec.ACTIVE)

        with tempfile.TemporaryDirectory() as p,patch.object(engine,'create',tracked):
            l=Ledger(p,0,0,clock=lambda:0)
            with patch.object(engine.Reference,'perceive',side_effect=ValueError('INJECTED_REFERENCE')):
                with self.assertRaisesRegex(ValueError,'INJECTED_REFERENCE'):policy_case(1,material,l,neutral=True)
            self.assertTrue(all(a.closed and not any(a.bank) for a in arms));self.assertIsNone(codec.ACTIVE)

    def test_P08_binding_admission_and_exclusive_target(self):
        import json,sys
        from tools import s2uc_ura1_prepare_v2 as run
        from tools._s2uc_ura1_v2_series import raw
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=root/'prestart.json';auth=root/'authorization.json';target=root/'target'
            with patch.object(run,'AUTH',auth),patch.object(run,'TARGET',target):
                b=dict(limits=LIMITS,runtime=run.runtime(),target=str(target),files={},call=[sys.executable,'-m','tools.s2uc_ura1_prepare_v2','run',str(p),str(auth)])
                def seal():p.write_bytes(raw(b));p.with_suffix('.sha256').write_text(run.sha(p))
                seal();_,digest=run.validate_binding(p)
                with self.assertRaises(FileNotFoundError):run.authorization(auth,digest)
                auth.write_bytes(raw(dict(kind='URA1_RESEARCH_ONCE_V2',prestart_sha256='0'*64,allow_research=True)))
                with self.assertRaises(PermissionError):run.authorization(auth,digest)
                b['limits']=LIMITS|dict(total_seconds=57601);seal()
                with self.assertRaises(ValueError):run.validate_binding(p)
                target.mkdir()
                with self.assertRaises(FileExistsError):target.mkdir(exist_ok=False)


if __name__=='__main__':unittest.main()
