"""One bound stored PCM window and its half-amplitude derivative only."""
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import tracemalloc
import time

from tools.s2uc_k2_check import ROOT,state,tu
from tools.s2uc_factor_hint_check import HintMeter
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_factor_hint import FactorHintArm

OUT=ROOT/'reports/s2uc/pcm-half-20260930-01'


def half_payload(payload):
    if len(payload)!=19200:return None,{'length_valid':False}
    samples=struct.unpack('<4800f',payload)
    valid=all(math.isfinite(x) and abs(x)<=1 for x in samples)
    if not valid:return None,{'length_valid':True,'values_valid':False}
    half=struct.pack('<4800f',*(x*.5 for x in samples))
    values=struct.unpack('<4800f',half)
    underflows=[i for i,(x,y) in enumerate(zip(samples,values)) if x!=0 and y==0]
    subnormals=[i for i,y in enumerate(values) if 0<abs(y)<2.**-126]
    restored=struct.pack('<4800f',*(y*2 for y in values))
    differences=[i for i in range(4800) if restored[i*4:i*4+4]!=payload[i*4:i*4+4]]
    info=dict(length_valid=True,values_valid=True,underflow_indices=underflows,half_subnormal_indices=subnormals,
              roundtrip_mismatch_indices=differences,roundtrip_bit_equal=restored==payload,
              nonzero_samples=sum(x!=0 for x in samples),half_sha256=hashlib.sha256(half).hexdigest())
    return (None if underflows or subnormals or differences else half),info


def band_comparison(original,actual):
    expected=original*.5
    def bits(x):return struct.pack('>d',x)
    def ordered(x):
        n=int.from_bytes(bits(x),'big')
        return (~n & ((1<<64)-1)) if n>>63 else n|(1<<63)
    return dict(original=original,original_hex=original.hex(),expected_half=expected,expected_half_hex=expected.hex(),
                actual=actual,actual_hex=actual.hex(),numeric_equal=actual==expected,bit_equal=bits(actual)==bits(expected),
                absolute_difference=abs(actual-expected),ulp_distance=abs(ordered(actual)-ordered(expected)),
                expected_subnormal=0<abs(expected)<sys.float_info.min,actual_subnormal=0<abs(actual)<sys.float_info.min,
                expected_underflow=original!=0 and expected==0)


def measured(call):
    before=tracemalloc.get_traced_memory()[0];tracemalloc.reset_peak();start=time.perf_counter_ns()
    result=call()
    current,peak=tracemalloc.get_traced_memory()
    return result,dict(elapsed_ns=time.perf_counter_ns()-start,incremental_python_peak_bytes=max(0,peak-before),net_python_bytes=current-before)


def process(payload,config_values):
    import numpy as np
    from mcm_field_organism.log_spectral_receptor import LogSpectralConfig,LogSpectralReceptor
    from mcm_field_organism.broadband_hearing_path import AuditoryReceptorState,AuditoryReceptorContact
    from tools import _s2nj_private_auditory_output_projection as nj
    config=LogSpectralConfig(**config_values);receptor=LogSpectralReceptor(config)
    before=hashlib.sha256(payload).hexdigest()
    samples=np.frombuffer(payload,dtype='<f4')
    raw=receptor.analyze(samples)
    contact=AuditoryReceptorContact.ACTIVE_ENERGY if any(raw) else AuditoryReceptorContact.ACTIVE_ZERO
    raw_state=AuditoryReceptorState('auditory',nj.RAW_GEOMETRY,0,0,4800,receptor.channel_ids,raw,contact)
    raw_digest=raw_state.digest()
    projection=nj.project_auditory_half_v1(raw_state,config=config,source_profile_digest=nj.RAW_PROFILE_DIGEST)
    assert hashlib.sha256(payload).hexdigest()==before and raw_state.digest()==raw_digest
    return dict(raw=list(raw),raw_digest=raw_digest,projection=asdict(projection),config=asdict(config),
                pcm_sha256=before,immutable=True,numpy_version=np.__version__)


def memory(original,half):
    profile=original['projection']['profile_digest'];x=tuple(original['projection']['values']);y=tuple(half['projection']['values'])
    outputs={};common=None
    for name,cls in [('E',ProvisionalHintArm),('F',FactorHintArm)]:
        arm=cls(profile,name+'/pcm-half');meter=HintMeter();receipts=[]
        for occurrence in (1,2):
            for j in range(4):meter.call(arm,'form',tu.Frame(x,profile,arm.owner,f'origin-{occurrence}',(occurrence-1)*4+j+1))
            receipts.append(meter.call(arm,'close_segment',f'origin-{occurrence}'))
        before=state(arm)
        if common is None:common=before
        else:assert before==common
        hints=[]
        for repeat in range(2):
            meter.hint_positions+=3
            assert meter.call(arm,'hint',tu.Frame(y,profile,arm.owner,f'half-hint-{repeat}',10000)) is None
            result=meter.call(arm,'hint',tu.Frame(y,profile,arm.owner,f'half-hint-{repeat}',10001))
            assert state(arm)==before
            hints.append(result)
        assert hints[0]==hints[1]
        expected_factors=[f for f in (.5,1.,2.) if all(a*f==b for a,b in zip(x,y))]
        if name=='F':
            expected=[dict(role='retained',generation=1,formation='origin-1',ordinals=[1,2,3,4],offset=o,factors=expected_factors) for o in range(3)] if expected_factors else []
        else:
            expected=[dict(role='retained',generation=1,formation='origin-1',ordinals=[1,2,3,4],offset=o) for o in range(3)] if x==y else []
        assert hints[0]['matches']==expected
        assert hints[0]['decision']==('ABSTAIN_AMBIGUOUS' if expected else 'ABSTAIN_NO_MATCH')
        assert meter.peak_trace<=16 and meter.peak_hint<=2
        outputs[name]=dict(formation_receipts=receipts,hints=hints,origin_pcm=original['pcm_sha256'],
                          hint_pcm=half['pcm_sha256'],state_unchanged=True,repeat_identical=True,meter=meter.summary())
        arm.close_owner();assert all(v==0 for v in arm.resources().values())
    return outputs


def run():
    raw=(OUT/'preregistration.json').read_bytes();p=json.loads(raw)
    report=dict(preregistration_sha256=hashlib.sha256(raw).hexdigest(),source=p['source'])
    bindings=all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in p['bindings'].items())
    payload=(ROOT/p['source']).read_bytes()
    report['source_sha256']=hashlib.sha256(payload).hexdigest()
    if not bindings or report['source_sha256']!=p['expected_sha256']:
        report['status']='INPUT_BINDING_FAILED'
    else:
        tracemalloc.start()
        (half,checks),derivation_cost=measured(lambda:half_payload(payload))
        report.update(preconditions=checks,derivation_resources=derivation_cost)
        if half is None:report['status']='INPUT_PRECONDITION_FAILED_NO_PROCESSING'
        else:
            with (OUT/'half-test-derivative.pcm').open('xb') as f:f.write(half)
            original,ocost=measured(lambda:process(payload,p['config']))
            derived,hcost=measured(lambda:process(half,p['config']))
            report.update(status='EVALUATED_STORED_PCM',original=original,half=derived,processing_resources={'original':ocost,'half':hcost})
            report['bands']=[dict(index=i,carrier=original['projection']['carrier_ids'][i],
                receptor=band_comparison(original['raw'][i],derived['raw'][i]),
                nj=band_comparison(original['projection']['values'][i],derived['projection']['values'][i])) for i in range(48)]
            report['memory'],report['memory_with_observer_resources']=measured(lambda:memory(original,derived))
            report['exact_factor_nj']=all(b['nj']['numeric_equal'] for b in report['bands'])
            report['bit_factor_nj']=all(b['nj']['bit_equal'] for b in report['bands'])
        tracemalloc.stop()
    report['bindings_unchanged']=all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in p['bindings'].items())
    report['runtime']=dict(python=sys.version,executable=sys.executable)
    report['notes']=['Half PCM is a labelled derivative of existing bytes, not regenerated signal.',
        'Only two receptor analyzes and two NJ projections. Repetitive memory frames reuse measured outputs, not independent perceptions.',
        'Exact numeric and bit comparisons have no tolerance. Original and half get fresh identical receptors.',
        'tracemalloc includes Python/runtime setup and observer allocations; not full native numpy or process RAM. Phase peaks not additive.',
        'Memory16+2 excludes PCM/receptor/observer; no original-source run or registry action.']
    with (OUT/'result.json').open('x') as f:json.dump(report,f,indent=2)
    print(report['status'],report.get('exact_factor_nj'),report.get('bit_factor_nj'))
    return report


if __name__=='__main__':run()
