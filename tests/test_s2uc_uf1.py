"""UF1 contract N1-N7 and G1-G6; hand values and neutral sources only."""
import gzip,io,json,math,struct,tempfile,unittest,sys
from pathlib import Path
from fractions import Fraction as Q
from unittest.mock import patch
from tools._s2uc_uf1_f import HintFrequency,CONTROL,BUFFER,OUTPUT,SLOT,SIZE
from tools._s2uc_uf1_reference import Reference
from tools import _s2uc_uf1_engine as engine
from tools import _s2uc_uf1_sources as source
from tools import _s2uc_uf1_stats as stats
from tools import s2uc_uf1 as run
OUTPUT=None

def vector(x):return tuple(float(x+j/4096) for j in range(48))
def feed(h,r,v):
    i=h.index+1;a=h.accept(i,v);b=r.accept(i,v)
    if a!=b or bytes(h.bank)!=r.state():raise AssertionError('REFERENCE_DIFFERENCE')
    return a
def block(h,r,x=.125,y=.25):
    for v in (vector(x),vector(.5),vector(y),vector(.0625)):feed(h,r,v)
def short():
    v=source.load(source.plan()['cases'][0],neutral=True);v['ids']=v['ids'][:48];return v
def tables():
    out=[]
    for spec in source.plan()['cases']:
        rows=[]
        for t in range(3,1024,2):
            r=dict(target=t,U=.5 if t%4==3 else .25,F=.25)
            if t%4==3:r.update(cue='X' if (t//4)%2==0 else 'Y',F_known=True,F_replaced=False,F_class='F2');r['class']='V3'
            rows.append(r)
        out.append(spec|dict(rows=rows,complete=True))
    return out

def numeric_census(fn):
    """External line/exception census of live baseline-frame scalar/copy payloads."""
    peak=0;events=0
    def trace(frame,event,arg):
        nonlocal peak,events
        if frame.f_code.co_filename.endswith('_s2uc_uf1_f.py'):
            events+=1;seen=set();total=0;current=frame
            while current:
                if current.f_code.co_filename.endswith('_s2uc_uf1_f.py'):
                    for name,value in current.f_locals.items():
                        if name in ('self','values') or id(value) in seen:continue
                        seen.add(id(value))
                        if type(value) in (int,float):total+=8
                        elif type(value) is bool:total+=1
                        elif type(value) in (bytes,bytearray):total+=len(value)
                current=current.f_back
            peak=max(peak,total)
        return trace
    prior=sys.gettrace();sys.settrace(trace)
    try:fn()
    finally:sys.settrace(prior)
    # Four scalar results in C calls between Python trace events, conservatively reserved.
    return dict(observed_live_scratch_payload=peak,c_call_scalar_reserve=32,
        measured_plus_reserve=peak+32,trace_events=events,bank_bytes=4304,
        conservative_contract_scratch=408,conservative_contract_total=4712)

class FrequencyTests(unittest.TestCase):
    def test_N1_input_and_bits(self):
        for i,v in [(2,vector(.1)),(1,()),(1,(float('nan'),)*48),(1,(float('inf'),)*48)]:
            h=HintFrequency()
            with self.assertRaises(ValueError):h.accept(i,v)
            self.assertTrue(h.closed)
        h=HintFrequency();r=Reference()
        for v in ((0.,)*48,vector(.5),vector(.25),vector(.0625),(-0.,)*48,vector(.5)):feed(h,r,v)
        self.assertEqual(h.kind,1)
        h=HintFrequency();r=Reference()
        for y in ((0.,)*48,(-0.,)*48):
            for v in (vector(.125),vector(.5),y,vector(.0625)):feed(h,r,v)
        self.assertEqual((h.word(1536),h.word(1544)),(1,1))
        for changed in (tuple([math.nextafter(.125,1.)]+list(vector(.125))[1:]),vector(.5)):
            h=HintFrequency();r=Reference();block(h,r)
            feed(h,r,changed);feed(h,r,vector(.5));self.assertEqual(h.kind,1)

    def test_N2_freeze_and_feedback(self):
        h=HintFrequency();r=Reference();feed(h,r,vector(.125));feed(h,r,vector(.5))
        self.assertEqual(h.kind,1);self.assertEqual(h.word(1536),0)
        self.assertEqual(bytes(h.bank[3920:]),struct.pack('<48d',*vector(.5)))
        feed(h,r,vector(.25));feed(h,r,vector(.0625));feed(h,r,vector(.125))
        stamp=h.word(1552);feed(h,r,vector(.5));self.assertEqual(h.word(1552),stamp)
        self.assertEqual((h.kind,h.value),(3,0));frozen=bytes(h.bank[3920:])
        self.assertEqual(feed(h,r,vector(.75)),.5);self.assertEqual(frozen,struct.pack('<48d',*vector(.25)))
        self.assertEqual((h.word(1536),h.word(1544)),(1,1))
        feed(h,r,vector(.0625));feed(h,r,vector(.125));feed(h,r,vector(.5));self.assertEqual(h.kind,2)
        feed(h,r,vector(.25));self.assertEqual((h.word(1536),h.word(1544)),(2,1))

    def test_N3_majority_changes(self):
        for a,b in ((.25,.75),(.75,.25)):
            h=HintFrequency();r=Reference();expected=[.5,a,.5,a,.5]
            for y,pred in zip((a,b,a,b,b),expected):
                feed(h,r,vector(.125));feed(h,r,vector(.5))
                self.assertEqual(bytes(h.bank[3920:]),struct.pack('<48d',*vector(pred)))
                feed(h,r,vector(y));feed(h,r,vector(.0625))
            feed(h,r,vector(.125));feed(h,r,vector(.5))
            self.assertEqual(h.value,1);self.assertEqual(bytes(h.bank[3920:]),struct.pack('<48d',*vector(b)))
            self.assertEqual((h.word(1536),h.word(1544)),(2,3))

    def test_N4_hint_eviction(self):
        h=HintFrequency();r=Reference()
        for x in (.125,.875,.125):block(h,r,x)
        feed(h,r,vector(.375));feed(h,r,vector(.5));self.assertEqual(h.kind,1)
        self.assertEqual((h.word(1552),h.word(3112)),(3,2))
        feed(h,r,vector(.75));self.assertEqual((h.word(1552),h.word(3112)),(3,4))
        feed(h,r,vector(.0625));feed(h,r,vector(.875));feed(h,r,vector(.5));self.assertEqual(h.kind,1)
        feed(h,r,vector(.25));self.assertEqual(h.word(1536),1)
        h=HintFrequency();r=Reference();block(h,r,.125);block(h,r,.875)
        h.put(1552,1);h.put(3112,1);r.slots[0]['stamp']=r.slots[1]['stamp']=1
        block(h,r,.375);self.assertEqual(h.word(1552),3)

    def test_N5_third_value_terminal_before_learning(self):
        for third in (vector(.375),tuple([math.nextafter(.25,1.)]+list(vector(.25))[1:])):
            h=HintFrequency();r=Reference();block(h,r,y=.25);block(h,r,y=.75)
            feed(h,r,vector(.125));feed(h,r,vector(.5));before=bytes(h.bank)
            # Observe pre-cleanup failure to prove no learning mutation; then public abort path.
            with patch.object(HintFrequency,'abort'):
                with self.assertRaisesRegex(ValueError,'F_VALUE_CAPACITY'):h.accept(11,third)
                self.assertEqual(bytes(h.bank),before)
            with self.assertRaisesRegex(ValueError,'F_VALUE_CAPACITY'):h.accept(11,third)
            with self.assertRaisesRegex(ValueError,'F_VALUE_CAPACITY'):r.accept(11,third)
            self.assertEqual(bytes(h.bank),r.state());self.assertTrue(h.closed)
            with self.assertRaises(ValueError):h.accept(12,vector(.0625))
        h=HintFrequency();r=Reference()
        for v in ((0.,)*48,(-0.,)*48):
            for x in (vector(.125),vector(.5),v,vector(.0625)):feed(h,r,x)
        feed(h,r,vector(.125));feed(h,r,vector(.5))
        with self.assertRaisesRegex(ValueError,'F_VALUE_CAPACITY'):h.accept(11,vector(.25))

    def test_N6_invariants_tickets_end_and_faults(self):
        for offset,value in ((CONTROL+16,99),(CONTROL+25,8),(CONTROL+26,1),(CONTROL+24,2)):
            h=HintFrequency();r=Reference();block(h,r);feed(h,r,vector(.125));feed(h,r,vector(.5))
            if offset==CONTROL+16:h.put(offset,value)
            else:h.bank[offset]=value
            with self.assertRaises(ValueError):h.accept(7,vector(.25))
            self.assertTrue(h.closed)
        h=HintFrequency();r=Reference();block(h,r);feed(h,r,vector(.125));feed(h,r,vector(.5));h.bank[3920]^=1
        with self.assertRaises(ValueError):h.accept(7,vector(.25))
        h=HintFrequency();r=Reference();block(h,r);block(h,r,y=.75);h.copy(1152,768,384)
        with self.assertRaisesRegex(ValueError,'DUPLICATE_VALUES'):h.accept(9,vector(.125))
        for partial in (0,1,2,4):
            h=HintFrequency()
            for i in range(1,partial+1):h.accept(i,vector(.5))
            with self.assertRaises(ValueError):h.finish()
            with self.assertRaises(ValueError):h.finish()
        h=HintFrequency();r=Reference()
        for _ in range(256):block(h,r)
        self.assertEqual(h.word(1536),256);self.assertEqual(h.word(CONTROL+8),256)
        h.finish();r.finish();self.assertEqual(bytes(h.bank),r.state())
        h=HintFrequency();r=Reference();block(h,r);feed(h,r,vector(.125));feed(h,r,vector(.5))
        h.put(CONTROL+8,256);h.put(1536,256)
        with self.assertRaisesRegex(ValueError,'F_COUNTER'):h.accept(7,vector(.25))
        faults={}
        for method in ('vector','copy','put'):
            original=getattr(HintFrequency,method)
            def broken(obj,*args,_original=original):_original(obj,*args);raise MemoryError('NEUTRAL_WRITE_FAULT')
            h=HintFrequency();meter=engine.Meter(h)
            if method=='copy':h.accept(1,vector(.125));index=2
            else:index=1
            with patch.object(HintFrequency,method,broken):
                with self.assertRaises(MemoryError):meter.call('failure',lambda:h.accept(index,vector(.5)))
            self.assertTrue(h.closed);faults[method]=meter.peak
        if OUTPUT:run.save(OUTPUT/'N6-error-heaps.json',faults)

    def test_N7_full_bank_transients(self):
        h=HintFrequency();r=Reference();meter=engine.Meter(h)
        for x,y in ((.125,.25),(.125,.75),(.875,.25),(.875,.75),(.125,.25),(.375,.25)):
            for v in (vector(x),vector(.5),vector(y),vector(.0625)):
                i=h.index+1;actual=meter.call('feedback' if i%4==3 else 'perception',lambda:h.accept(i,v))
                self.assertEqual(actual,r.accept(i,v));self.assertEqual(bytes(h.bank),r.state())
        meter.call('abort',h.abort)
        self.assertEqual(len(h.bank),4304);self.assertLessEqual(meter.peak,32768)
        # Third-value error is also metered.
        h=HintFrequency();r=Reference();block(h,r);block(h,r,y=.75);feed(h,r,vector(.125));feed(h,r,vector(.5));m=engine.Meter(h)
        with self.assertRaisesRegex(ValueError,'F_VALUE_CAPACITY'):m.call('third_value',lambda:h.accept(11,vector(.375)))
        result=engine.replay(short(),short=True)
        self.assertEqual(result['reference_advances'],{'U':48,'F':48})
        def paths():
            f=HintFrequency()
            for x,y in ((.125,.25),(.125,.75),(.875,.25),(.875,.75),(.125,.25),(.375,.25)):
                for v in (vector(x),vector(.5),vector(y),vector(.0625)):f.accept(f.index+1,v)
            f.abort()
            f=HintFrequency()
            for y in (.25,.75):
                for v in (vector(.125),vector(.5),vector(y),vector(.0625)):f.accept(f.index+1,v)
            f.accept(9,vector(.125));f.accept(10,vector(.5))
            try:f.accept(11,vector(.375))
            except ValueError:pass
        census=numeric_census(paths);self.assertLessEqual(census['measured_plus_reserve'],408)
        if OUTPUT:run.save(OUTPUT/'N7-resources.json',dict(bank_bytes=4304,numeric_conservative_upper=4712,numeric_limit=5120,numeric_census=census,own_heap_peak=meter.peak,phase_peaks=meter.phases,third_value_error_heap=m.peak,short_resources=result['resources']))

    def test_G3_statistics(self):
        data=stats.matrix_bytes();draws=stats.verify_matrix(data)
        for x,v in [(Q(1,8),'F_VORTEIL_BELEGT'),(Q(-1,8),'U_VORTEIL_GEGEN_F_BELEGT'),(Q(0),'KEIN_EINDEUTIGER_UNTERSCHIED_NACHGEWIESEN')]:self.assertEqual(stats.verdict(stats.checked_ci([x]*32,draws)),v)
        for ci in (['-1','0'],['0','1']):self.assertEqual(stats.verdict(ci),'KEIN_EINDEUTIGER_UNTERSCHIED_NACHGEWIESEN')
        stats.checked_ci([Q(i-15,32) for i in range(32)],draws)
        with self.assertRaises(ValueError):stats.verify_matrix(b'\xff'+data[1:])
        rows=tables();a=stats.aggregate(rows,data);self.assertEqual(a['primary']['mean'],'1/4')
        self.assertEqual(len(a['secondary']),30);self.assertEqual(len(a['diagnosis']),704);self.assertEqual(len(a['story_means']),640)
        self.assertEqual(a['secondary'][0]['harm'],'2048')
        with self.assertRaises(ValueError):stats.aggregate(rows[:-1],data)
        rows[0]['rows'].pop()
        with self.assertRaises(ValueError):stats.aggregate(rows,data)
        if OUTPUT:run.save(OUTPUT/'G3-statistics.json',dict(primary=a['primary'],bootstrap_sha256=a['bootstrap_sha256'],secondary_records=30,diagnosis_records=704,story_means=640))

    def test_G4_U_and_reference_corruption(self):
        from tests import test_s2uc_multi_error as fixtures
        names=['test_T02_cold','test_T03_ties_and_negative_zero','test_T04_different_history_and_order','test_T05_six_and_nine','test_T06_loss_no_resurrection','test_T07_promotion_open_ticket','test_T08_original_not_current_store','test_T09_invalid','test_T10_every_publication_field','test_T11_reentrancy_end_and_double','test_R02_resources']
        stream=io.StringIO();r=unittest.TextTestRunner(stream=stream).run(unittest.TestSuite(fixtures.MultiTests(n) for n in names));self.assertTrue(r.wasSuccessful(),stream.getvalue())
        if OUTPUT:run.save(OUTPUT/'G4-U-tests.json',dict(count=r.testsRun,output=stream.getvalue()))
        original=HintFrequency._accept
        def corrupt(h,i,v):
            result=original(h,i,v)
            if i==2:h.bank[3920]^=1
            return result
        with patch.object(HintFrequency,'_accept',corrupt):
            with self.assertRaisesRegex(ValueError,'F_STATE_REFERENCE'):engine.replay(short(),short=True)
        import tools._s2uc_hx1_replay as u
        with patch.object(u,'select',return_value=(0,999,0)):
            with self.assertRaisesRegex(ValueError,'SELECTION_REFERENCE'):engine.replay(short(),short=True)

    def test_G5_supervisor_and_export(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td) if OUTPUT is None else OUTPUT
            export=folder/'export';export.mkdir();ledger=run.Ledger(export)
            result=engine.replay(short(),short=True);ledger.packed('small-case.json.gz',result)
            self.assertEqual(source.raw(json.loads(gzip.decompress((export/'small-case.json.gz').read_bytes()))),source.raw(result))
            for name,size in [('x-source.json',32769),('x-case.json.gz',524289),('admin.json',2*1048576+1)]:
                with self.assertRaises(ValueError):ledger.write_bytes(name,b'x'*size)
            with self.assertRaisesRegex(ValueError,'CASE_EXPANSION'):ledger.packed('big-case.json.gz',{'x':'x'*(4*1048576)})
            with self.assertRaisesRegex(ValueError,'EXPORT_LIMIT'):run.Ledger(export,charged=64*1048576).write('over.json',{})
            def invalid():raise PermissionError('NO_AUTHORIZATION')
            self.assertFalse(run.supervise(folder/'invalid',invalid,neutral=True)['worker_started'])
            for fault in ('start_error','crash','worker_error','export','cancel','memory'):
                c=run.supervise(folder/('fault-'+fault),lambda:(dict(cases=[]),0),neutral=True,fault=fault)
                self.assertEqual(c['status'],'NOT_EVALUABLE');self.assertFalse(c['worker_alive'])
            self.assertTrue(source.read(folder/'fault-memory/memory-enforcement.json')['allocation_rejected'])
            c=run.supervise(folder/'timeout',lambda:(dict(cases=[]),0),neutral=True,seconds=3,reserve_seconds=2,fault='hang')
            self.assertEqual(c['status'],'NOT_EVALUABLE');self.assertFalse(c['worker_alive'])
            old=source.sha(folder/'invalid/closure.json');self.assertEqual(run.supervise(folder/'invalid',invalid,neutral=True)['status'],'REJECTED_EXISTING_OUTPUT');self.assertEqual(source.sha(folder/'invalid/closure.json'),old)
            with patch.object(run,'OUT',folder/'pending'),patch.object(run,'verify_prestart'),patch.object(run,'expected_authorization',return_value={'status':'AUTHORIZED_ONCE'}):
                f=folder/'pending.json';run.save(f,{'status':'PENDING_SEPARATE_AUTHORIZATION'});self.assertFalse(run.run(f)['worker_started'])
            if run.BINDING.exists():
                old=source.sha
                with patch.object(source,'sha',side_effect=lambda p:'bad' if str(p).endswith('_s2uc_uf1_f.py') else old(p)):
                    with self.assertRaisesRegex(ValueError,'CODE_BINDING'):run.verify_code()

    def test_G6_analytical_vectors(self):
        a=tuple(.25 if j%2 else .75 for j in range(48));b=tuple(.75 if j%2 else .25 for j in range(48))
        loss=lambda x,p:sum(p*abs(Q(u)-Q(v))+(1-p)*abs(Q(u)-Q(w)) for u,v,w in zip(x,a,b))/48
        for p,major in ((Q(3,4),a),(Q(1,4),b)):
            mean=tuple(float(p*Q(x)+(1-p)*Q(y)) for x,y in zip(a,b))
            self.assertEqual(loss(major,p),Q(1,8));self.assertEqual(loss(mean,p),Q(3,16))
        self.assertEqual(loss((.5,)*48,Q(1,2)),Q(1,4))
        self.assertGreater(loss((1.,)*48,Q(1,2)),Q(1,4))

class RecipeTests(unittest.TestCase):
    def test_G1a_research_gate_no_hashing(self):
        with patch.object(source.hashlib,'sha256',side_effect=AssertionError('NO_RESEARCH_HASH')):
            for fn in (lambda:source.Stream(1,'continuation'),lambda:source.choices(1),
                       lambda:source.reference_choices(1),lambda:source.materialize(source.plan()['cases'][0])):
                with self.assertRaises(PermissionError):fn()
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises((PermissionError,FileNotFoundError)):
                source.admit(Path(td)/'missing-auth.json',td)

    def test_G1b_rng_boundaries(self):
        limit=(1<<64)-((1<<64)%3)
        s=source.Stream(1,'continuation',neutral=True,draw=lambda d:limit if d==0 else limit-1)
        self.assertEqual(s.below(3),(limit-1)%3);self.assertEqual(s.d,2)
        s=source.Stream(1,'continuation',neutral=True,draw=lambda d:0)
        self.assertEqual(s.below(1),0);self.assertEqual(s.d,1)
        s.d=4095;self.assertEqual(s.below(256),0)
        with self.assertRaisesRegex(ValueError,'RANDOM_DRAW_LIMIT'):s.below(1)
        s=source.Stream(1,'continuation',neutral=True,draw=lambda d:(1<<64)-1)
        with self.assertRaisesRegex(ValueError,'RANDOM_DRAW_LIMIT'):s.below(3)
        for n in (0,257,True):
            with self.assertRaises(ValueError):source.Stream(1,'continuation',neutral=True).below(n)

    def test_G1c_independent_neutral_recipe_and_quotas(self):
        from collections import Counter
        null_tables=[]
        for r in range(1,33):
            a=source.choices(r,neutral=True);b=source.reference_choices(r,neutral=True)
            self.assertEqual(a,b)
            ys,d,n,counts=a
            self.assertEqual(Counter(ys),{3:128,4:128});self.assertEqual(Counter(d),{0:128,1:128})
            self.assertEqual(Counter(n),{0:128,1:128})
            table=Counter(zip(d,ys));expected=(96,32,32,96) if r%2 else (32,96,96,32)
            self.assertEqual(tuple(table[k] for k in ((0,3),(0,4),(1,3),(1,4))),expected)
            null_tables.append(Counter(zip(n,ys)))
            self.assertTrue(all(0<v<=4096 for v in counts.values()))
        self.assertTrue(any(v[0,3]!=64 for v in null_tables))
        # Reference does not delegate to production permutation or choices.
        with patch.object(source,'choices',side_effect=AssertionError('SHARED_ORACLE')):
            self.assertEqual(source.reference_choices(1,neutral=True)[0].count(3),128)

    def test_G2a_manifest_seal_and_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td);manifest,mh=source.seal_sources(folder,run.Ledger(folder),neutral=True)
            self.assertEqual(len(manifest['entries']),64)
            for spec in source.plan()['cases']:
                v=source.load_sealed(folder,spec,manifest,mh)
                source.validate_record(v,spec,neutral=True)
            spec=source.plan()['cases'][0];f=folder/(spec['id']+'-source.json')
            f.write_bytes(f.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'SOURCE_CHANGED'):source.load_sealed(folder,spec,manifest,mh)
            (folder/'manifest.json').write_bytes(b'{}\n')
            with self.assertRaisesRegex(ValueError,'MANIFEST_CHANGED'):source.load_sealed(folder,spec,manifest,mh)
        spec=source.plan()['cases'][0];v=source.load(spec,neutral=True);v['ids'][2]=4
        with self.assertRaisesRegex(ValueError,'SOURCE_RECIPE_REFERENCE'):source.validate_record(v,spec,neutral=True)

    def test_G3b_null_boundaries_and_pair_mapping(self):
        self.assertEqual(stats.verdict(['-1','0']),'KEIN_EINDEUTIGER_UNTERSCHIED_NACHGEWIESEN')
        self.assertEqual(stats.verdict(['0','1']),'KEIN_EINDEUTIGER_UNTERSCHIED_NACHGEWIESEN')
        rows=tables();rows[-1]=rows[0]
        with self.assertRaisesRegex(ValueError,'COMPLETE_PAIRS'):stats.aggregate(rows,stats.matrix_bytes())
        self.assertFalse(source.plan()['known_sources'])

    def test_G2b_all_sources_before_first_policy(self):
        import time
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td);seen=[]
            def observe(record,check):
                manifest=source.read(folder/'manifest.json')
                self.assertEqual(len(manifest['entries']),64)
                self.assertEqual(len(list(folder.glob('*-source.json'))),64)
                self.assertTrue(all(source.sha(folder/e['path'])==e['sha256'] for e in manifest['entries']))
                seen.append(True);raise ValueError('NEUTRAL_STOP_BEFORE_POLICY')
            with patch.object(run.windows,'worker_membership'),patch.object(run.engine,'replay',side_effect=observe):
                with self.assertRaisesRegex(ValueError,'NEUTRAL_STOP_BEFORE_POLICY'):
                    run.execute(folder,source.plan(),0,time.monotonic_ns()+int(30e9),neutral=True)
            self.assertEqual(seen,[True]);self.assertTrue((folder/'worker-error.json').exists())

    def test_G5b_archive_roundtrip_and_corruption(self):
        import hashlib,zipfile
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td);packed=folder/'evidence.zip';name='a-case.json.gz'
            original=source.raw({'hand':'neutral'});gz=gzip.compress(original,compresslevel=9,mtime=0)
            run.save(folder/'closure.json',{'files':{name:{'bytes':len(gz),'sha256':hashlib.sha256(gz).hexdigest()}}})
            payload=len(name).to_bytes(4,'little')+len(original).to_bytes(8,'little')+name.encode()+original
            with zipfile.ZipFile(packed,'x',compression=zipfile.ZIP_LZMA) as z:z.writestr('bundle.bin',payload)
            with patch.object(run,'QUAL',folder),patch.object(run,'PACKED',packed):run.verify_archive()
            with zipfile.ZipFile(packed,'w',compression=zipfile.ZIP_LZMA) as z:z.writestr('bundle.bin',payload[:-1]+b' ')
            with patch.object(run,'QUAL',folder),patch.object(run,'PACKED',packed):
                with self.assertRaisesRegex(ValueError,'ARCHIVE_HASH'):run.verify_archive()

if __name__=='__main__':unittest.main()
