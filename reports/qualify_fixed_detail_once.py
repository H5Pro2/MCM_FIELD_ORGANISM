"""One prebound neutral qualification, never the selected MP4."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/s2oe/fixed-detail-qualification-20260912-01'
OWN=('tools/_s2oe_fixed_detail.py','tests/test_s2oe_fixed_detail.py','tests/s2oe_detail_worker.py',
     'reports/qualify_fixed_detail_once.py')


def raw(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def save(n,x):
    with (OUT/n).open('xb') as f:f.write(x if isinstance(x,bytes) else raw(x))


def inventory():
    pending=set(OWN);found={}
    while pending:
        name=pending.pop()
        if name in found:continue
        data=(ROOT/name).read_bytes();found[name]=[sha(data),len(data)]
        package=name[:-3].replace('/','.').split('.')[:-1]
        for n in ast.walk(ast.parse(data.decode('utf-8-sig'))):
            modules=[]
            if isinstance(n,ast.Import):modules=[x.name for x in n.names]
            if isinstance(n,ast.ImportFrom):
                prefix='.'.join(package[:len(package)-n.level+1]) if n.level else ''
                base='.'.join(x for x in (prefix,n.module) if x)
                modules=[base,*[base+'.'+x.name for x in n.names]]
            for module in modules:
                parts=module.split('.')
                if parts[0] not in ('tools','tests','mcm_field_organism'):continue
                for i in range(1,len(parts)+1):
                    for p in ('/'.join(parts[:i])+'.py','/'.join(parts[:i])+'/__init__.py'):
                        if (ROOT/p).is_file():pending.add(p)
    return found


def prepare():
    OUT.mkdir(exist_ok=False);files=inventory()
    tests=sorted(n.name for n in ast.walk(ast.parse((ROOT/OWN[1]).read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
    # All source bytes count physically, separate from spatial receipt supplements.
    code_bytes=sum(x[1] for x in files.values())
    reserves=dict(binding=12288,log=32768,result=4096,report=8192,balance=4096,claim=5,
        complete_envelope=327680,native_views=24576,information_control=32768,native_resources=8192)
    metadata=sum(reserves[k] for k in ('binding','log','result','report','balance','claim'))
    total=code_bytes+sum(reserves.values())
    from tools import _s2oe_fixed_detail as d
    comparison=dict(version=d.VERSION,spatial=d.SPATIAL,
        source_path='C:/Users/TV/Downloads/17138816-uhd_3840_2160_30fps.mp4',source_bytes=83498438,
        source_sha256='df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa',
        code=files,selection_numerators=list(range(1,92,10)),selection_denominator=20,
        views_per_media_frame=['OVERVIEW','DETAIL'],media_frames=10,control_images=2,analyses_per_arm=12,
        total_receptor_values=6912,control_comparisons_primary=576,control_comparisons_direct=576,
        native_rgb_buffer_bytes=24883200,output_rgb_buffers_max=2,shared_slot_bytes=6240000,
        process_limit=1073741824,job_limit=1073741824,frame_limit=400,packet_limit=2048,
        request_seconds=30,stop_seconds=5,real_gate=False,
        control='K0: 80 black then 80 white columns, period160; K1 reversed; RGB equal channels')
    value=dict(qualification_id=OUT.name,tests=tests,files=files,python=sys.version,reserves=reserves,
        budget=dict(source_files=code_bytes,metadata=metadata,spatial_supplement_max=24*2048+8192,total=total),
        limits=dict(metadata=65536,spatial_supplement=262144,total=4194304),comparison=comparison,
        native_test='in-memory yuv420p flat128 frames pts 0,1001,2002; no source file',real_media=False)
    save('preregistration.json',value)
    print(json.dumps(dict(tests=len(tests),binding_bytes=len(raw(value)),budget=value['budget'])))
    if len(raw(value))>reserves['binding'] or metadata>65536 or total>4194304:raise SystemExit('PRESTART_LIMIT')


def child():
    def guard(event,args):
        if event=='open' and isinstance(args[0],(str,bytes)):
            name=os.fsdecode(args[0]).lower()
            if name.endswith(('.mp4','.pcm','.rgb')):raise RuntimeError('REAL_MEDIA_FORBIDDEN')
    sys.addaudithook(guard)
    import unittest
    suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2oe_fixed_detail')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    save('tests.json',dict(tests=result.testsRun,errors=len(result.errors),failures=len(result.failures),success=result.wasSuccessful()))
    return 0 if result.wasSuccessful() else 1


def qualify():
    bound=json.loads((OUT/'preregistration.json').read_bytes())
    if bound['files']!=inventory():raise SystemExit('SOURCE_CHANGED')
    save('qualification.claim',b'once\n')
    env=dict(os.environ,DETAIL_QUAL_OUT=str(OUT))
    with (OUT/'qualification.log').open('xb') as log:
        result=subprocess.run([sys.executable,'-m','reports.qualify_fixed_detail_once','child'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    sizes={p.name:p.stat().st_size for p in OUT.iterdir() if p.is_file()}
    tests=json.loads((OUT/'tests.json').read_bytes()) if (OUT/'tests.json').exists() else {}
    caps={'preregistration.json':12288,'qualification.log':32768,'tests.json':2048,'native-views.json':24576,
        'native-resources.json':8192,'information-control.json':32768,'complete-envelope.json':327680,'qualification.claim':5}
    violations=[name for name,size in sizes.items() if name not in caps or size>caps[name]]
    ok=result.returncode==0 and tests.get('tests')==16 and tests.get('success') and bound['files']==inventory() and not violations
    save('result.json',dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',tests=tests,exit_code=result.returncode,
        violations=violations,source_hashes_unchanged=bound['files']==inventory(),gates=False,
        metadata_reserve=bound['budget']['metadata'],all_sources_bytes=bound['budget']['source_files'],files=sizes,
        total_before_result=bound['budget']['source_files']+sum(sizes.values()),real_media=False))
    print('QUALIFIED' if ok else 'NOT_QUALIFIED')
    if not ok:raise SystemExit(1)


if __name__=='__main__':
    if sys.argv[1]=='child':raise SystemExit(child())
    {'prepare':prepare,'qualify':qualify}[sys.argv[1]]()
