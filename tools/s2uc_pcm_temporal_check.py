"""Fixed temporal chirp experiment; no changes to perception or memory arms."""
import hashlib, json, math, platform, struct, sys, time, tracemalloc
from fractions import Fraction
from pathlib import Path
from tools.s2uc_pcm_half_check import ROOT, half_payload, band_comparison, process, measured
from tools.s2uc_k2_check import state, tu
from tools.s2uc_factor_hint_check import HintMeter
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_factor_hint import FactorHintArm

OUT=ROOT/'reports/s2uc/pcm-temporal-20260930-01'
SOURCE=ROOT/'sources/s2uc/temporal-chirp-v1/sequence.pcm'
CONFIG=dict(sample_rate=48000,window_size=4800,hop_size=480,band_count=48,min_frequency=50.,max_frequency=18000.)

def sha(b): return hashlib.sha256(b).hexdigest()
def save(p,obj):
    with p.open('x',encoding='utf-8') as f: json.dump(obj,f,indent=2)
def generate():
    data=bytearray()
    for n in range(19200):
        t=float(n)/48000.0
        a=400.0*t
        b=4500.0*t
        c=b*t
        d=a+c
        e=2.0*math.pi
        phase=e*d
        sample64=0.125*math.sin(phase)
        data.extend(struct.pack('<f',sample64))
    return bytes(data)
def oracle(v,h,factor):
    result=[]
    for o in range(3):
        fs=[f for f in ((.5,1.,2.) if factor else (1.,)) if all(
            Fraction(x)*Fraction(f)==Fraction(y) for j in range(2) for x,y in zip(v[o+j],h[j]))]
        if fs:
            m=dict(role='retained',generation=1,formation='origin-1',ordinals=[1,2,3,4],offset=o)
            if factor:m['factors']=fs
            result.append(m)
    return result

def memory(v,halves,profile):
    outputs={}; common=None
    for name,cls in [('E',ProvisionalHintArm),('F',FactorHintArm)]:
        arm=cls(profile,name+'/temporal'); meter=HintMeter(); receipts=[]
        for occurrence in (1,2):
            for j,x in enumerate(v):
                meter.call(arm,'form',tu.Frame(tuple(x),profile,arm.owner,f'origin-{occurrence}',(occurrence-1)*4+j+1))
            receipts.append(meter.call(arm,'close_segment',f'origin-{occurrence}'))
        before=state(arm)
        if common is None:common=before
        else:assert before==common
        cases={}
        for label,hint in [('original',v[1:3]),('half',halves),('reverse',[v[2],v[1]])]:
            expected=oracle(v,hint,name=='F'); results=[]
            for repeat in range(2):
                meter.hint_positions+=3
                segment=f'{label}-{repeat}'
                assert meter.call(arm,'hint',tu.Frame(tuple(hint[0]),profile,arm.owner,segment,10000)) is None
                result=meter.call(arm,'hint',tu.Frame(tuple(hint[1]),profile,arm.owner,segment,10001))
                assert state(arm)==before
                assert result['matches']==expected
                decision='ABSTAIN_NO_MATCH' if not expected else 'ABSTAIN_AMBIGUOUS' if len(expected)>1 else 'CONFIRMED_RETAINED_MATCH'
                assert result['decision']==decision
                results.append(result)
            assert results[0]==results[1]
            cases[label]=dict(results=results,oracle=expected,readonly=True,repeat_identical=True)
        assert meter.peak_trace<=16 and meter.peak_hint<=2 and meter.peak_total<=18
        outputs[name]=dict(state=before,receipts=receipts,cases=cases,meter=meter.summary())
        arm.close_owner(); assert all(x==0 for x in arm.resources().values())
    return outputs

def register():
    import numpy as np
    import mcm_field_organism.log_spectral_receptor
    import mcm_field_organism.broadband_hearing_path
    import tools._s2nj_private_auditory_output_projection
    OUT.mkdir(parents=True,exist_ok=False)
    files={}
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p:
            p=Path(p).resolve()
            if p.is_relative_to(ROOT) and p.suffix=='.py': files[p.relative_to(ROOT).as_posix()]=sha(p.read_bytes())
    for f in ['tools/s2uc_pcm_temporal_check.py','tests/test_s2uc_pcm_temporal.py','docs/S2UC_PCM_ZEITSEQUENZ_SIGNALENTWURF_20260930.txt']:
        files[f]=sha((ROOT/f).read_bytes())
    p=dict(bindings=files,config=CONFIG,source=SOURCE.relative_to(ROOT).as_posix(),
      formula='Float32((1/8)*sin(2*pi*(400*t+4500*t*t))), t=n/48000; n=0..19199',
      computation='t=n/48000; a=400*t; b=4500*t; c=b*t; d=a+c; e=2*pi; phase=e*d; sample64=.125*sin(phase); pack <f',
      windows=[[i*4800,(i+1)*4800] for i in range(4)],target_offset=1,
      criteria=['No signal optimization','Numeric and bit factor equality reported separately','All 48 bands for W2/W3 raw and NJ','All six original window pairs raw and NJ','Full exact-rational oracle match sets','Repeated hints readonly','16+2 frame budget','Negative factor or uniqueness findings are valid'],
      runtime=dict(python=sys.version,executable=sys.executable,executable_sha256=sha(Path(sys.executable).read_bytes()),platform=platform.platform(),numpy=np.__version__,math_origin=getattr(math,'__file__','built-in'),pi_hex=math.pi.hex()),
      scope='SYNTHETIC_LOCAL_TEMPORAL_TEST_ONLY; no original source run',created_ns=time.time_ns())
    save(OUT/'preregistration.json',p)

def run():
    pr=(OUT/'preregistration.json').read_bytes(); p=json.loads(pr)
    assert all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    assert p['config']==CONFIG and p['runtime']['python']==sys.version
    assert sha(Path(sys.executable).read_bytes())==p['runtime']['executable_sha256']
    r=dict(preregistration_sha256=sha(pr),runtime=p['runtime'],resources={})
    tracemalloc.start()
    payload,r['resources']['generation']=measured(generate)
    repeat,r['resources']['reproduction']=measured(generate)
    values=struct.unpack('<19200f',payload)
    r['input_checks']=dict(bytes=len(payload),samples=len(values),finite=all(math.isfinite(x) for x in values),max_abs=max(map(abs,values)),reproducible=payload==repeat)
    assert len(payload)==76800 and r['input_checks']['finite'] and r['input_checks']['max_abs']<=.125 and payload==repeat
    del repeat,values
    SOURCE.parent.mkdir(parents=True,exist_ok=False)
    with SOURCE.open('xb') as f:f.write(payload)
    assert SOURCE.read_bytes()==payload
    payload=SOURCE.read_bytes()
    windows=[payload[i*19200:(i+1)*19200] for i in range(4)]
    provenance=dict(scope=p['scope'],source=p['source'],sha256=sha(payload),bytes=len(payload),samples=19200,format='mono-float32-le',sample_rate=48000,preregistration_sha256=sha(pr),windows=[dict(samples=p['windows'][i],sha256=sha(w)) for i,w in enumerate(windows)])
    save(SOURCE.parent/'provenance.json',provenance); r['provenance']=provenance
    halves=[];r['derivations']=[]
    for i in (1,2):
        (h,check),cost=measured(lambda:half_payload(windows[i]))
        assert h is not None and check['roundtrip_bit_equal']
        with (OUT/f'half-W{i+1}.pcm').open('xb') as f:f.write(h)
        halves.append(h);r['derivations'].append(dict(window=i+1,parent_sha256=sha(windows[i]),checks=check,cost=cost))
    save(OUT/'input-binding.json',dict(source=provenance,derivations=r['derivations']))
    processed=[]; r['resources']['processing']=[]
    for w in windows+halves:
        result,cost=measured(lambda:process(w,CONFIG));processed.append(result);r['resources']['processing'].append(cost)
    r['processed']=processed
    def observe():
        bands=[]
        for i,j in [(1,4),(2,5)]:
            for k in range(48):
                bands.append(dict(window=i+1,index=k,carrier=processed[i]['projection']['carrier_ids'][k],receptor=band_comparison(processed[i]['raw'][k],processed[j]['raw'][k]),nj=band_comparison(processed[i]['projection']['values'][k],processed[j]['projection']['values'][k])))
        pairs=[]
        for i in range(4):
            for j in range(i+1,4):
                row=dict(windows=[i+1,j+1])
                for kind in ('raw','nj'):
                    a=processed[i]['raw'] if kind=='raw' else processed[i]['projection']['values']
                    b=processed[j]['raw'] if kind=='raw' else processed[j]['projection']['values']
                    row[kind]=dict(equal=a==b,factors=[f for f in (.5,1.,2.) if all(Fraction(x)*Fraction(f)==Fraction(y) for x,y in zip(a,b))],different_band_count=sum(x!=y for x,y in zip(a,b)))
                pairs.append(row)
        return dict(bands=bands,pairs=pairs)
    r['comparisons'],r['resources']['comparison_observer']=measured(observe)
    v=[x['projection']['values'] for x in processed[:4]]; h=[x['projection']['values'] for x in processed[4:]]
    start=time.perf_counter_ns();r['memory']=memory(v,h,processed[0]['projection']['profile_digest'])
    r['resources']['memory_with_observer_elapsed_ns']=time.perf_counter_ns()-start
    r['bindings_unchanged']=all(sha((ROOT/f).read_bytes())==h for f,h in p['bindings'].items())
    assert r['bindings_unchanged'] and sha(SOURCE.read_bytes())==provenance['sha256']
    r['processing_calls']=dict(receptor=6,nj=6)
    r['notes']=['Receptor local coordinates are 0..4800; global window intervals are bound in provenance.', 'Second presentation is test replay, not a second recording.', 'Phase tracemalloc peaks are nonadditive and exclude complete native/process RAM. Memory call peaks include tracing; no observer-free RAM claim.', 'PCM files: 76800 source + 38400 derivatives bytes; buffers and observer outside 16+2.', 'No E/F, confirmation or perception code changed.']
    r['status']='EVALUATED_SYNTHETIC_TEMPORAL_PCM';tracemalloc.stop();save(OUT/'result.json',r)
    print(r['status']);print(json.dumps({a:{k:v['results'][0] for k,v in d['cases'].items()} for a,d in r['memory'].items()},indent=2))
    return r
if __name__=='__main__':
    if sys.argv[1:] == ['register']: register()
    elif sys.argv[1:] == ['run']: run()
    else: raise SystemExit('register | run')
