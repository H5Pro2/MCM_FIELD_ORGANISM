"""One prospectively bound connection qualification; never compares real cues."""
import ast
import json
import subprocess
import sys
from pathlib import Path
from reports import seal_visual_b_once as prior
from reports import run_visual_b_comparison as entry
from tools import _visual_b_comparison as c
from tools import _visual_b_ledger as ledger

ROOT=prior.ROOT
OUT=ROOT/'reports/s2oe/visual-b-connection-qualification-20260912-02'
SEAL=ROOT/entry.SEAL
CAPS={'inventory.json':32768,'preregistration.json':8192,'qualification.json':1024,
      'qualification.log':8192,'REPORT.md':4096,'balance.json':4096,'claim':5,
      'admission.json':4096,'admission-final.json':4096,'frozen-binding.json':98304}


def write(name,value):
    raw=prior.s.raw(value)
    c.frozen.require(len(raw)<=CAPS[name],'QUALIFICATION_ITEM_LIMIT:'+name)
    with (OUT/name).open('xb') as f:f.write(raw)


def prepare():
    c.frozen.require(not OUT.exists(),'OUTPUT_EXISTS')
    files=prior.inventory()
    initial=['tools/_visual_b_frozen.py','tools/_visual_b_comparison.py','tools/_visual_b_ledger.py',
             'reports/qualify_visual_b_connection.py','reports/run_visual_b_comparison.py',
             'tests/test_visual_b_connection.py']
    for name in prior.code_closure(initial):
        files[name]=dict(kind='sources',**prior.pin(ROOT/name))
    for name in ('preregistration.json','inventory.json','execution.json','evaluation.json',
                 'qualification.json','qualification.log','seal.json','verification.json'):
        path=SEAL/name
        files[path.relative_to(ROOT).as_posix()]=dict(kind='evidence' if name=='seal.json' else
            'sources' if name=='inventory.json' else 'verification' if name=='verification.json' else
            'metadata',**prior.pin(path))
    session=prior.MEM+'session.json'
    files[session]=dict(kind='metadata',**prior.pin(ROOT/session))
    extra=[dict(name='qualification/'+n,bytes=cap,kind='sources' if n=='inventory.json' else
                'evidence' if n=='frozen-binding.json' else 'metadata') for n,cap in CAPS.items()]
    # A single sequential neutral workspace is bounded by the same full run
    # envelopes. It is deleted between tests; not accumulated across fixtures.
    upper=ledger.preflight(files,extra)
    summary=dict(version=ledger.VERSION,qualification_caps=CAPS,run_caps=ledger.RUN_CAPS,
        limits=ledger.LIMITS,alternatives=[dict(alternative=a['alternative'],parts=a['parts'],
            violations=a['violations']) for a in upper['alternatives']],violations=upper['violations'])
    print(json.dumps(summary))
    ledger.enforce(upper)
    tests=sorted(n.name for n in ast.walk(ast.parse((ROOT/initial[-1]).read_text()))
                 if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
    # Only stored provenance/codec bindings are resolved here. No scan or receptor.
    frozen,_,_=entry.load_frozen(ROOT,entry.read(SEAL/'execution.json'))
    registration=dict(version=c.VERSION,files_digest=c.frozen.digest(files),tests=tests,balance=summary,
        interpreter=prior.pin(Path(sys.executable)),python=sys.version,main_authorized=False,
        numpy_version=entry.np.__version__,numpy_init=prior.pin(Path(entry.np.__file__)),
        frozen_binding_digest=frozen['binding_digest'],
        work=dict(real_receptor=0,real_comparison=0,neutral_groups=len(tests),
            future_sources=7,future_b_slot_records=112,future_band_terms=448,
            future_a_slots=168,future_a_visible=5376,future_a_internal=4032,
            verifier_b_slots=56,verifier_band_terms=224,verifier_a_slots=84,
            provenance_state_decodes_per_pass=4,provenance_passes_per_run=2),
        native_fixture_boundary='codec-native synthetic evidence; historical numerical memory proof not replayed')
    for value,cap in ((files,CAPS['inventory.json']),(registration,CAPS['preregistration.json']),
                      (frozen,CAPS['frozen-binding.json'])):
        c.frozen.require(len(prior.s.raw(value))<=cap,'PRESTART_ITEM')
    OUT.mkdir()
    write('inventory.json',files);write('preregistration.json',registration);write('frozen-binding.json',frozen)


def run():
    registration=entry.read(OUT/'preregistration.json');files=entry.read(OUT/'inventory.json')
    c.frozen.require(c.frozen.digest(files)==registration['files_digest'],'INVENTORY')
    c.frozen.require(prior.pin(Path(sys.executable))==registration['interpreter'],'INTERPRETER')
    prior.check(files)
    with (OUT/'claim').open('xb') as f:f.write(b'once\n')
    with (OUT/'qualification.log').open('xb') as log:
        p=subprocess.run([sys.executable,'-m','unittest','tests.test_visual_b_connection','-v'],
                         cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    prior.check(files)
    success=p.returncode==0 and (OUT/'qualification.log').stat().st_size<=CAPS['qualification.log']
    result=dict(status='QUALIFIED' if success else 'NOT_QUALIFIED',tests=len(registration['tests']),
        calls=1,exit_code=p.returncode,log=prior.pin(OUT/'qualification.log'),gates=False,
        version=c.VERSION,inventory_digest=c.frozen.digest(files),sources_unchanged=True)
    write('qualification.json',result)
    if success:
        names=('inventory.json','preregistration.json','qualification.json','qualification.log','frozen-binding.json')
        references={(OUT/n).relative_to(ROOT).as_posix():dict(kind='sources' if n=='inventory.json' else
            'evidence' if n=='frozen-binding.json' else 'metadata',**prior.pin(OUT/n)) for n in names}
        permit=dict(version=c.VERSION,budget_version=ledger.VERSION,authorized=False,
            run_id='visual-b-frozen-comparison-20260912-01',
            output='reports/s2oe/visual-b-frozen-comparison-20260912-01',references=references,
            inventory=(OUT/'inventory.json').relative_to(ROOT).as_posix(),
            qualification=(OUT/'qualification.json').relative_to(ROOT).as_posix())
        permit['frozen_binding']=(OUT/'frozen-binding.json').relative_to(ROOT).as_posix()
        permit['environment']={k:registration[k] for k in ('interpreter','numpy_version','numpy_init')}
        c.frozen.require(not (ROOT/permit['output']).exists(),'OUTPUT_USED')
        write('admission.json',permit)
    sizes={p.name:p.stat().st_size for p in OUT.iterdir() if p.is_file()}
    charged=dict(files)
    for name,cap in CAPS.items():
        charged['qualification/'+name]=dict(kind='sources' if name=='inventory.json' else
            'evidence' if name=='frozen-binding.json' else 'metadata',bytes=sizes.get(name,cap))
    upper=ledger.preflight(charged)
    summary=dict(files=sizes,remaining_reserves={n:v for n,v in CAPS.items() if n not in sizes},
        alternatives=[dict(alternative=a['alternative'],parts=a['parts'],violations=a['violations']) for a in upper['alternatives']],
        violations=upper['violations'],gates=False)
    write('balance.json',summary)
    print(json.dumps(result));print(json.dumps(summary))
    ledger.enforce(upper)
    c.frozen.require(success,'QUALIFICATION_STOP')


if __name__=='__main__':
    {'prepare':prepare,'run':run}[sys.argv[1]]()
