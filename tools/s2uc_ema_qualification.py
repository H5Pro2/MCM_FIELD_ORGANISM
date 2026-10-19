"""Bind the unexecuted counterprobe plan; execute neutral qualification only."""
import ast
import json
import sys
import unittest
from pathlib import Path
from tools.s2uc_factor_material import ROOT,sha,read
from tests import test_s2uc_paired_error_ema as tests

PLAN=ROOT/'docs/S2UC_EMA_GEGENPROBENPLAN_20261001.json'
BINDING=ROOT/'docs/S2UC_EMA_IMPLEMENTIERUNGSBINDUNG_20261001.json'


def save(path,value):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)


def hashes():
    pending=['tools/_s2uc_paired_error_ema.py','tools/_s2uc_paired_error_replay.py',
        'tools/s2uc_ema_qualification.py','tests/test_s2uc_paired_error_ema.py'];found=set()
    while pending:
        name=pending.pop()
        if name in found:continue
        found.add(name)
        for node in ast.walk(ast.parse((ROOT/name).read_text(encoding='utf-8'))):
            modules=[]
            if isinstance(node,ast.Import):modules=[a.name for a in node.names]
            elif isinstance(node,ast.ImportFrom) and node.module:modules=[node.module]+[node.module+'.'+a.name for a in node.names]
            for module in modules:
                file=module.replace('.','/')+'.py'
                if module.startswith(('tools.','tests.','mcm_field_organism.')) and (ROOT/file).is_file():pending.append(file)
    return {n:sha(ROOT/n) for n in sorted(found)}


def prepare():
    plan=dict(status='BOUND_NOT_AUTHORIZED',version='s2uc.ema.counterprobe.v1',
        selection_policy='paired_error_ema_v1',alpha=.5,tie='PERSISTENCE',initial='PERSISTENCE',
        retrieval='exact_v1',continuation='legacy_v1',arithmetic='mae48 ordered binary64 scalar sum k0..47, /48; same E/K/P function',
        state=dict(max_cells=12,packed_cell_bytes=32,ticket_count=1,packed_ticket_bytes=32,
            extra_python_bytes_cap=16384,max_frames=18,max_proposal_vectors=2,
            metadata_integer_limits='active variant: time/ordinal <2^63; generation positive uint64'),
        stories=['constant','switch_return'],frames_per_story=200,arms=['E','K','P'],
        prototype=dict(U='1/8',V='1/4',W='3/4',Z='7/8',components=48),
        warmup='U,V,W,Z twice; normal admission only',cycles=24,
        cycle='G(j,0),G(j,1),G(j,2),G(j,3),U,V,Y(j),T(j)',
        recipes=dict(G='15/16+(4*j+k)/8192; j1..24,k0..3',T='13/16+j/4096',
            constant_Y='W',switch_return_Y='W for j1..8; V for j9..16; W for j17..24'),
        primary_targets=[15+8*j for j in range(24)],
        secondary_targets=[t for t in range(3,200,2) if t not in {15+8*j for j in range(24)}],
        censored_final_target=201,system_inputs='numeric frames only; no case labels or switch timing',
        deliberately_retained_A='unique guards replace query candidates; variable tails prevent promotion; ordinary unchanged memory rules',
        criteria=dict(switch='primary MAE E strictly below K and P on all24 targets',
            stable='after first usable retained-key outcome no excess error versus K; cold-start cost remains included',
            adaptation='better available proposal by third primary target of each phase and thereafter',
            recovery='context selection returns in final stable phase',
            disclosure='all gains/harms,24 primary and75 secondary separate; no general learning benefit claim'),
        output_directory='reports/s2uc/ema-counterprobe-20261001-01',
        execution_authorized=False,implementation_qualification_only=True)
    save(PLAN,plan)
    save(BINDING,dict(status='IMPLEMENTATION_BOUND_PROBE_NOT_AUTHORIZED',plan_sha256=sha(PLAN),
        code=hashes(),python=sys.version,python_executable_sha256=sha(sys.executable),
        contract_sha256=sha(ROOT/'docs/S2UC_PROGNOSEERFAHRUNG_ENTSCHEIDUNGSVERTRAG_20261001.txt'),
        numerical_contract_sha256=sha(ROOT/'docs/S2UC_EMA_NUMERIK_20261001.txt')))


def qualify(folder):
    out=Path(folder).resolve();assert out.is_relative_to((ROOT/'reports/s2uc').resolve())
    b=read(BINDING);assert b['code']==hashes() and sha(PLAN)==b['plan_sha256']
    assert b['python']==sys.version and b['python_executable_sha256']==sha(sys.executable)
    assert not (ROOT/read(PLAN)['output_directory']).exists()
    out.mkdir(exist_ok=False);save(out/'before.json',dict(binding_sha256=sha(BINDING),code=b['code']))
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.PairedErrorTests)
    with (out/'tests.txt').open('x',encoding='utf-8') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    unchanged=b['code']==hashes()
    save(out/'facts.json',tests.FACTS)
    final=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),
        success=result.wasSuccessful() and unchanged,code_unchanged=unchanged,
        failure_details=[(str(t),s) for t,s in result.failures],error_details=[(str(t),s) for t,s in result.errors],
        counterprobe_executed=False)
    save(out/'test-result.json',final);print(json.dumps(final,indent=2))
    return 0 if final['success'] else 1


if __name__=='__main__':
    if sys.argv[1:]==['prepare']:prepare()
    elif len(sys.argv)==3 and sys.argv[1]=='qualify':raise SystemExit(qualify(sys.argv[2]))
    else:raise SystemExit('prepare | qualify <new neutral report directory>')
