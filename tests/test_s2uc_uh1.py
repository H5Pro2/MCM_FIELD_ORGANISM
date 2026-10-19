"""UH1 N1-N7. Fixed neutral data only; research source replay forbidden."""
import copy
import gzip
import io
import json
import math
import struct
import tempfile
import unittest
from pathlib import Path
from fractions import Fraction as F
from unittest.mock import patch
from tools._s2uc_uh1_h import HintMean,CONTROL,BUFFER,OUTPUT,SLOT
from tools._s2uc_uh1_reference import Reference
from tools import _s2uc_uh1_engine as engine
from tools import _s2uc_uh1_sources as source
from tools import _s2uc_uh1_stats as stats
from tools import s2uc_uh1 as run
OUTPUT_DIR=None
OUTPUT=None
def vector(x):return tuple(float(x+j/4096) for j in range(48))
def feed(h,r,v):
    i=h.index+1;a=h.accept(i,v);b=r.accept(i,v)
    if a!=b or bytes(h.bank)!=r.state():raise AssertionError('REFERENCE_DIFFERENCE')
    return a
def block(h,r,a,y=.75):
    for v in (vector(a),vector(.5),vector(y),vector(.0625)):feed(h,r,v)
def short():
    x=source.load(source.plan()['cases'][0],neutral=True);x['ids']=x['ids'][:48];return x
def tables():
    out=[]
    for spec in source.plan()['cases']:
        rows=[]
        for t in range(3,1024,2):
            q=t%4==3;r=dict(target=t,U=.5 if q else .25,H=.25)
            if q:r.update(cue='X' if (t//4)%2==0 else 'Y',H_known=True,H_replaced=False);r['class']='V3'
            rows.append(r)
        out.append(spec|dict(rows=rows,complete=True))
    return out

class UHTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=None if OUTPUT else tempfile.TemporaryDirectory(prefix='uh1-focused-')
        cls.folder=OUTPUT or Path(cls.tmp.name)
        cls.data=stats.matrix_bytes();cls.draws=stats.verify_matrix(cls.data)
    @classmethod
    def tearDownClass(cls):
        if cls.tmp:cls.tmp.cleanup()
    def test_N1_input_bits_and_gate(self):
        for i,v in [(2,vector(.1)),(1,()),(1,tuple([float('nan')]*48)),(1,tuple([float('inf')]*48))]:
            h=HintMean()
            with self.assertRaises(ValueError):h.accept(i,v)
            self.assertTrue(h.closed);self.assertEqual(sum(h.bank),1)
        for changed in (tuple([math.nextafter(.125,1.0)]+list(vector(.125))[1:]),vector(.5)):
            h=HintMean();r=Reference();block(h,r,.125)
            feed(h,r,changed);feed(h,r,vector(.5));self.assertEqual(h.kind,2)
        h=HintMean();r=Reference()
        for v in (tuple([0.0]*48),vector(.5),vector(.25),vector(.0625),tuple([-0.0]*48),vector(.5)):feed(h,r,v)
        self.assertEqual(h.kind,2)
        with self.assertRaises(PermissionError):source.load(source.plan()['cases'][0])
        source.validate_all()
        with patch.object(source.hx,'choices',side_effect=AssertionError('RESEARCH_GENERATOR')):source.load(source.plan()['cases'][0],neutral=True)
    def test_N2_unknown_known_freeze(self):
        h=HintMean();r=Reference()
        feed(h,r,vector(.125));feed(h,r,vector(.5))
        self.assertEqual(h.word(1152),0);self.assertEqual(h.kind,2)
        frozen=bytes(h.bank[3136:]);self.assertEqual(frozen,struct.pack('<48d',*vector(.5)))
        feed(h,r,vector(.75));self.assertEqual(h.word(1152),1)
        feed(h,r,vector(.0625));feed(h,r,vector(.125));feed(h,r,vector(.5))
        old=bytes(h.bank[3136:]);self.assertEqual(old,struct.pack('<48d',*vector(.75)))
        self.assertEqual(feed(h,r,vector(.25)),.5)
        self.assertEqual(old,struct.pack('<48d',*vector(.75)))
        self.assertEqual(struct.unpack_from('<d',h.bank,768)[0],.5)
    def test_N3_two_slots_third_eviction(self):
        h=HintMean();r=Reference()
        for a in (.125,.875,.125,.375):block(h,r,a)
        self.assertEqual((h.word(1160),h.word(2328)),(3,4))
        feed(h,r,vector(.875));feed(h,r,vector(.5));self.assertEqual(h.kind,2)
        feed(h,r,vector(.25));self.assertEqual(h.word(1160),5)
        self.assertEqual(h.word(1152),1)
    def test_N4_rounding_tickets_and_reference_corruption(self):
        h=HintMean();r=Reference()
        for y in (.1,.2,.9,.3,.625):block(h,r,.125,y)
        for offset,value in ((CONTROL+16,99),(CONTROL+25,8)):
            h=HintMean();r=Reference();block(h,r,.125);feed(h,r,vector(.125));feed(h,r,vector(.5))
            if offset==CONTROL+16:h.put(offset,value)
            else:h.bank[offset]=value
            with self.assertRaises(ValueError):h.accept(7,vector(.25))
            self.assertTrue(h.closed)
        original=HintMean._accept
        def corrupt(h,i,v):
            result=original(h,i,v)
            if i==2:h.bank[3136]^=1
            return result
        with patch.object(HintMean,'_accept',corrupt):
            with self.assertRaisesRegex(ValueError,'H_STATE_REFERENCE'):engine.replay(short(),short=True)
        import tools._s2uc_hx1_replay as u
        with patch.object(u,'select',return_value=(0,999,0)):
            with self.assertRaisesRegex(ValueError,'SELECTION_REFERENCE'):engine.replay(short(),short=True)
    def test_N5_boundaries_and_fault_cleanup(self):
        h=HintMean();h.accept(1,vector(.125));h.accept(2,vector(.5));h.put(CONTROL+8,256)
        with self.assertRaisesRegex(ValueError,'H_COUNTER'):h.accept(3,vector(.25))
        self.assertTrue(h.closed)
        for partial in (0,1,2,4):
            h=HintMean()
            for i in range(1,partial+1):h.accept(i,vector(.5))
            with self.assertRaises(ValueError):h.finish()
            self.assertEqual(sum(h.bank),1)
            with self.assertRaises(ValueError):h.finish()
        h=HintMean();r=Reference();block(h,r,.125);block(h,r,.875)
        h.put(1160,1);h.put(2328,1);r.slots[0]['stamp']=r.slots[1]['stamp']=1
        block(h,r,.375);self.assertEqual(h.word(1160),3)
        # Reach the legal upper endpoint without executing any research source.
        h=HintMean();r=Reference()
        for _ in range(256):block(h,r,.125)
        self.assertEqual(h.word(1152),256);self.assertEqual(h.word(CONTROL+8),256)
        h.finish();r.close();self.assertEqual(bytes(h.bank),r.state())
        # Inject allocation/write failure at each mutation boundary, no production hooks.
        faults={}
        for method in ('vector','copy','put'):
            original=getattr(HintMean,method)
            def broken(obj,*args,_original=original):
                _original(obj,*args);raise MemoryError('NEUTRAL_WRITE_FAULT')
            h=HintMean();meter=engine.Meter(h)
            if method=='copy':h.accept(1,vector(.125));index=2
            else:index=1
            with patch.object(HintMean,method,broken):
                with self.assertRaises(MemoryError):meter.call('failure',lambda:h.accept(index,vector(.5)))
            self.assertEqual(sum(h.bank),1);faults[method]=meter.peak
        if OUTPUT:run.save(OUTPUT/'N5-error-heaps.json',faults)
    def test_N6_U_and_complete_statistics(self):
        from tests import test_s2uc_multi_error as fixtures
        names=['test_T02_cold','test_T03_ties_and_negative_zero','test_T04_different_history_and_order','test_T05_six_and_nine','test_T06_loss_no_resurrection','test_T07_promotion_open_ticket','test_T08_original_not_current_store','test_T09_invalid','test_T10_every_publication_field','test_T11_reentrancy_end_and_double','test_R02_resources']
        stream=io.StringIO();r=unittest.TextTestRunner(stream=stream).run(unittest.TestSuite(fixtures.MultiTests(n) for n in names));self.assertTrue(r.wasSuccessful(),stream.getvalue())
        if OUTPUT:run.save(OUTPUT/'N6-U-tests.json',dict(count=r.testsRun,output=stream.getvalue()))
        for value,verdict in [(F(1,8),'H_VORTEIL_BELEGT'),(F(-1,8),'H_ERWARTUNG_WIDERLEGT_U_VORTEIL'),(F(0),'LEISTUNGSRICHTUNG_NICHT_NACHGEWIESEN')]:
            ci=stats.checked_ci([value]*32,self.draws);self.assertEqual(stats.verdict(ci),verdict)
        self.assertEqual(stats.verdict(['0','1']),'LEISTUNGSRICHTUNG_NICHT_NACHGEWIESEN')
        stats.checked_ci([F(i-15,32) for i in range(32)],self.draws)
        with self.assertRaises(ValueError):stats.verify_matrix(b'\xff'+self.data[1:])
        rows=tables();v=stats.aggregate(rows,self.data);self.assertEqual(v['primary']['mean'],'1/4');self.assertEqual(len(v['secondary']),30)
        self.assertEqual(v['secondary'][0]['harm'],'2048');self.assertEqual(v['secondary'][0]['gain'],'0')
        with self.assertRaises(ValueError):stats.aggregate(rows[:-1],self.data)
        rows[0]['rows'].pop()
        with self.assertRaises(ValueError):stats.aggregate(rows,self.data)
        if OUTPUT:run.save(OUTPUT/'N6-statistics.json',dict(primary=v['primary'],bootstrap_sha256=v['bootstrap_sha256'],secondary_records=30))
    def test_N7_resources_export_supervisor_and_gates(self):
        h=HintMean();ref=Reference();meter=engine.Meter(h)
        for a in (.125,.875,.125,.375,.875):
            for v in (vector(a),vector(.5),vector(.75),vector(.0625)):
                i=h.index+1;actual=meter.call('third_hint',lambda:h.accept(i,v));expected=ref.accept(i,v)
                self.assertEqual(actual,expected);self.assertEqual(bytes(h.bank),ref.state())
        meter.call('abort',h.abort)
        if OUTPUT:run.save(OUTPUT/'N7-third-hint-resources.json',dict(own_heap_peak=meter.peak,phases=meter.phases,numeric_upper=3928))
        self.assertEqual(source.hx.digest('HX1-schema-48-float64'),source.PROFILE)
        result=engine.replay(short(),short=True)
        self.assertLessEqual(result['resources']['H']['own_heap_peak'],32768)
        folder=self.folder/'export';folder.mkdir();ledger=run.Ledger(folder)
        ledger.packed('small-case.json.gz',result)
        self.assertEqual(source.raw(json.loads(gzip.decompress((folder/'small-case.json.gz').read_bytes()))),source.raw(result))
        for name,size in [('x-source.json',32769),('x-case.json.gz',524289),('admin.json',2*1048576+1)]:
            with self.assertRaises(ValueError):ledger.write_bytes(name,b'x'*size)
        with self.assertRaisesRegex(ValueError,'CASE_EXPANSION'):ledger.packed('big-case.json.gz',{'x':'x'*(4*1048576)})
        with self.assertRaisesRegex(ValueError,'EXPORT_LIMIT'):run.Ledger(folder,charged=64*1048576).write('over.json',{})
        def invalid():raise PermissionError('NO_AUTHORIZATION')
        c=run.supervise(self.folder/'invalid',invalid,neutral=True);self.assertFalse(c['worker_started'])
        for fault in ('start_error','crash','worker_error','export','cancel','memory'):
            c=run.supervise(self.folder/('fault-'+fault),lambda:(dict(cases=[]),0),neutral=True,fault=fault)
            self.assertEqual(c['status'],'NOT_EVALUABLE');self.assertFalse(c['worker_alive'])
        self.assertTrue(source.read(self.folder/'fault-memory/memory-enforcement.json')['allocation_rejected'])
        c=run.supervise(self.folder/'timeout',lambda:(dict(cases=[]),0),neutral=True,seconds=3,reserve_seconds=2,fault='hang')
        self.assertFalse(c['worker_alive']);self.assertEqual(c['status'],'NOT_EVALUABLE')
        h=source.sha(self.folder/'invalid/closure.json')
        self.assertEqual(run.supervise(self.folder/'invalid',invalid,neutral=True)['status'],'REJECTED_EXISTING_OUTPUT')
        self.assertEqual(source.sha(self.folder/'invalid/closure.json'),h)
        with patch.object(run,'OUT',self.folder/'pending'),patch.object(run,'verify_prestart'),patch.object(run,'expected_authorization',return_value={'status':'AUTHORIZED_ONCE'}):
            p=self.folder/'pending.json';run.save(p,{'status':'PENDING_SEPARATE_AUTHORIZATION'})
            self.assertFalse(run.run(p)['worker_started'])
        original=source.sha
        with patch.object(source,'sha',side_effect=lambda p:'bad' if str(p).endswith('manifest.json') else original(p)):
            with self.assertRaises(ValueError):source.validate_all()
        if run.BINDING.exists():
            with patch.object(source,'sha',side_effect=lambda p:'bad' if str(p).endswith('_s2uc_uh1_h.py') else original(p)):
                with self.assertRaisesRegex(ValueError,'CODE_BINDING'):run.verify_code()
        if OUTPUT:run.save(OUTPUT/'N7-short-resources.json',result['resources'])

if __name__=='__main__':unittest.main()
