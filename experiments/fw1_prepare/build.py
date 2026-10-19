"""Preparation actions: matrix once, artificial statistics, bound neutral fixtures."""
import hashlib,json,sys,time
from pathlib import Path
from .entry import ROOT,PREP,CONFIGS,TARGETS,LIMITS,code_paths,exact_call,sha,runtime,journal,write_exclusive,auth_path

def matrix_once():
    journal('matrix_generation_started',rows=10000,columns=16)
    started=time.monotonic();path=PREP/'bootstrap.bin'
    with path.open('xb') as f:
        for a in range(10000):
            f.write(bytes(2*(int.from_bytes(hashlib.sha256(f'MCM-FW1/bootstrap/v1/row={a}/column={c}'.encode()).digest()[:8],'big')%8)+c//8 for c in range(16)))
    journal('matrix_generation_completed',bytes=path.stat().st_size,sha256=sha(path))
    journal('matrix_reference_started')
    data=path.read_bytes()
    if len(data)!=160000:raise ValueError('MATRIX_LENGTH')
    for i,value in enumerate(data):
        row,column=divmod(i,16)
        digest=hashlib.sha256(('MCM-FW1/bootstrap/v1/row=%d/column=%d'%(row,column)).encode('utf-8')).hexdigest()
        expected=2*(int(digest[:16],16)&7)+(0 if column<8 else 1)
        if value!=expected:raise ValueError('MATRIX_RECIPE')
    journal('matrix_reference_completed',bytes_compared=len(data))
    write_exclusive(PREP/'matrix-binding.json',dict(namespace='MCM-FW1/bootstrap/v1',rows=10000,columns=16,bytes=len(data),sha256=sha(path),reference_equal=True,seconds=time.monotonic()-started))

def artificial_statistics():
    from experiments.fw1.statistics import primary,reference
    started=time.monotonic();records=[]
    for pair in range(1,17):
        conditions={}
        for c,label in enumerate(('A','B')):
            conditions[label]=dict(pair=pair,condition=label,complete=True,cleanup=True,stock_equal=True,integrity='PASS_DELTA_INTEGRITY',targets=list(range(3,1024,2)),KEEP=[((pair*7+i*3+c)%31)/64 for i in range(511)],RESET=[((pair*3+i*5+c)%29)/64 for i in range(511)],resets=[dict(end=12,deleted=1)])
        records.append(dict(pair=pair,orientation=(pair-1)%2,complete=True,conditions=conditions))
    write_exclusive(PREP/'artificial-errors.json',records)
    matrix=(PREP/'bootstrap.bin').read_bytes();h=sha(PREP/'bootstrap.bin')
    journal('full_statistics_primary_started',artificial=True,arm_errors=32704)
    a=primary(records,matrix,neutral=False,digest=h);journal('full_statistics_primary_completed')
    journal('full_statistics_reference_started',artificial=True)
    b=reference(records,matrix,neutral=False,digest=h);journal('full_statistics_reference_completed')
    if any(a[k]!=b[k] for k in ('mean','pairs','ci','informative','verdict')):raise ValueError('STATISTICS_REFERENCE')
    write_exclusive(PREP/'artificial-statistics.json',dict(primary=a,reference=b,equal=True,seconds=time.monotonic()-started,scientific_result=False,matrix_sha256=h))

def neutral_sources(mode):
    from . import sources
    if mode not in ('short','fullsize'):raise PermissionError('NEUTRAL_ONLY')
    blocks=24 if mode=='short' else 256
    journal('neutral_source_pair_generation_started',mode=mode,pair=1,blocks=blocks)
    description=sources.generate(1,blocks);journal('neutral_source_pair_generation_completed',mode=mode)
    journal('neutral_source_pair_reference_started',mode=mode)
    independent=sources.reconstruct(1,blocks)
    if description!=independent:raise ValueError('NEUTRAL_SOURCE_REFERENCE')
    entries=[]
    for label in ('A','B'):
        value=sources.materialize(description,label);sources.verify_material(value,independent,label)
        path=PREP/f'{mode}-{label}-source.json';write_exclusive(path,value)
        entries.append(dict(pair=1,condition=label,path=path.relative_to(ROOT).as_posix(),sha256=sha(path)))
    journal('neutral_source_pair_reference_completed',mode=mode,conditions=2)
    return entries

def bind(mode,entries,qualification):
    c=dict(kind='FW1_PRESTART',mode=mode,target=str(TARGETS[mode]),pairs=16 if mode=='research' else 1,frames=96 if mode=='short' else 1024,namespace='MCM-FW1/source/v1' if mode=='research' else 'MCM-FW1/neutral/v1',limits=LIMITS,runtime=runtime(),files={name:sha(ROOT/name) for name in code_paths()},qualification={p.relative_to(ROOT).as_posix():sha(p) for p in qualification},sources=entries,matrix_sha256=sha(PREP/'bootstrap.bin'))
    c['call']=exact_call(c);path=CONFIGS[mode];write_exclusive(path,c);path.with_suffix('.sha256').write_text(sha(path)+'\n')
    return c

def neutral_authorization(c):
    if c['mode'] not in ('short','fullsize'):raise PermissionError('NO_RESEARCH_AUTH_ISSUER')
    write_exclusive(auth_path(c),dict(kind='FW1_NEUTRAL_ONCE',prestart_sha256=sha(CONFIGS[c['mode']]),target=c['target'],allow_research=False))

if __name__=='__main__':
    from tools.s2uc_ura1_runtime_qualify import install_job
    from tools import _s2uc_hx1_windows as win
    install_job()
    action=sys.argv[1]
    try:
        if action=='matrix':matrix_once();artificial_statistics()
        elif action in ('short','fullsize'):
            c=bind(action,neutral_sources(action),[PREP/'matrix-binding.json',PREP/'artificial-statistics.json',PREP/'inherited-fw1.json']);neutral_authorization(c)
        else:raise PermissionError('BUILD_ACTION')
        write_exclusive(PREP/f'{action}-preparation-resource.json',win.snapshot())
    except BaseException as exc:
        journal('preparation_failure',action=action,error=type(exc).__name__+':'+str(exc));raise
