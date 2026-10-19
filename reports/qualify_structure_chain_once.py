"""Bind and qualify the direct PPB connector, without a real chain run."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tools import _structure_ppb_chain as c
from tools import _structure_ppb_table as inputs

ROOT=Path(__file__).resolve().parents[1]
Q=ROOT/'reports/s2oe/structure-location-chain-qualification-20260912-04'
ARCHIVE=ROOT/'reports/s2oe/structure-location-chain-qualification-20260912-02/previous_diagnostic.py'
RUN=ROOT/'reports/s2oe/structure-location-chain-20260912-01'
RAW=ROOT/'reports/s2oe/structure-location-comparison-20260912-01'
SEALED=ROOT/'reports/s2oe/structure-location-source-seal-20260912-01'
PAIR=ROOT/'reports/s2oe/structure-location-ppb-20260912-01'
CAPS={'record.json':900000,'partial.json':900000,'verification.json':32768,
      'evaluation.json':8192,'failure.json':8192,'balance.json':2048,'run.claim':5,'verification.claim':5}
QCAPS={'preregistration.json':8192,'qualification.log':4096,'result.json':1024,
       'balance.json':4096,'main-binding.json':2048,'authorization.json':512,'qualification.claim':5,
       'neutral-record.json':900000,'neutral-verification.json':2048,'neutral-failure-progress.json':40960}

ERROR_VERSION='ppb-chain.bounded-error.v1'
TEXT_LIMIT=512


def failure_evidence(exc,phase,progress,binding):
    # Do not invoke arbitrary __str__, or serialize exception chains.
    known={'SOURCE_TIME','VECTOR_SIZE','STATE_LIMIT','RECORD_LIMIT','ROOT','CONFIG',
           'CHAIN','ORDER','STATE_DIGEST','POST_GENERATION','EVALUATION_GATE'}
    arg=exc.args[0] if type(exc) is c.ChainError and len(exc.args)==1 else None
    code=arg if type(arg) is str and arg in known else 'UNKNOWN_ERROR'
    message=exc.args[0] if len(exc.args)==1 and type(exc.args[0]) is str else None
    # ASCII JSON escaping has at most twelve bytes per Unicode code point.
    prefix=message[:TEXT_LIMIT] if message is not None else ''
    limited=message is not None and len(message)>TEXT_LIMIT
    chains=progress.get('chains',[])
    last=next((dict(chain=x['chain'],state_index=len(x['states'])-1,
                    digest=c.s.digest(x['states'][-1])) for x in reversed(chains) if x['states']),None)
    return dict(version=ERROR_VERSION,status='NOT_EVALUABLE',primary_code=code,
        phase=phase if phase in ('ADVANCE','VERIFY','EVALUATE') else 'UNKNOWN',
        completed=progress.get('completed',0),binding_digest=c.s.digest(binding),
        last_state=last,state_file='partial.json',diagnostic=prefix,
        diagnostic_status='DIAGNOSTIC_LIMIT_REACHED' if limited else 'MESSAGE_ONLY',
        diagnostic_complete=False,traceback_stored=False)


def capture(command,log,env):
    # One bounded pipe read; never accumulate child output in memory.
    child=subprocess.Popen(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    remaining=QCAPS['qualification.log'];exceeded=False
    try:
        while True:
            chunk=child.stdout.read1(min(1024,remaining+1))
            if not chunk:break
            over=len(chunk)>remaining
            log.write(chunk[:remaining]);remaining-=min(remaining,len(chunk))
            if over:
                exceeded=True;child.kill();break
        return child.wait(),exceeded
    finally:
        if child.poll() is None:child.kill();child.wait()
        child.stdout.close()


def pin(path):
    data=path.read_bytes();return [hashlib.sha256(data).hexdigest(),len(data)]


def save(directory,name,value):
    path=directory/name;temp=directory/(name+'.tmp')
    c.need(not path.exists(),'OUTPUT_EXISTS')
    data=c.s.raw(value)
    limit=(QCAPS if directory==Q else CAPS).get(name)
    c.need(limit is not None and len(data)<=limit,'OUTPUT_SIZE')
    with temp.open('xb') as f:f.write(data)
    temp.rename(path)


def alternatives(refs,extra):
    # A temporary file replaces its absent destination; it is not a second copy.
    return {name:measure(refs,dict(extra,**{k:v for k,v in CAPS.items() if k not in excluded}))
        for name,excluded in (('success',('partial.json','failure.json')),
                              ('failure',()))}


def close_failure(directory,exc,phase,progress,binding):
    primary=failure_evidence(exc,phase,progress,binding)
    try:
        if not (directory/'partial.json').exists():save(directory,'partial.json',progress)
        if not (directory/'failure.json').exists():save(directory,'failure.json',primary)
        return dict(status='NOT_EVALUABLE',primary=primary,secured=True)
    except Exception:
        return dict(status='CLOSURE_NOT_SECURED',primary=primary,secured=False)


def finish_balance(directory,refs,closure):
    try:
        sizes={p.name:p.stat().st_size for p in directory.iterdir() if p.is_file()}
        sizes['balance.json']=CAPS['balance.json']
        balance=measure(refs,sizes)
        balance['overs']=[n for n,size in sizes.items()
                          if size>CAPS.get(n.removesuffix('.tmp'),0)]
        save(directory,'balance.json',balance)
        if balance['violations'] or balance['overs']:
            return dict(status='CLOSURE_NOT_SECURED',primary=closure.get('primary'),secured=False)
        return closure
    except Exception:
        return dict(status='CLOSURE_NOT_SECURED',primary=closure.get('primary'),secured=False)


def kind(name):
    name=name.removesuffix('.tmp')
    if Path(name).name in ('record.json','seal.json','partial.json','neutral-record.json','neutral-failure-progress.json'):return 'evidence'
    if Path(name).name in ('verification.json','neutral-verification.json'):return 'verification'
    return 'sources' if name.endswith('.py') else 'metadata'


def measure(refs,extra):
    report='reports/s2oe/STRUCTURE_CHAIN_FORMAT_BOUND.md'
    occupied=refs.get(report,[None,0])[1]
    parts=dict(metadata=max(0,8192-occupied),evidence=0,sources=0,verification=0)
    for name,(_,size) in refs.items():parts[kind(name)]+=size
    for name,size in extra.items():parts[kind(name)]+=size
    total=sum(parts.values());violations=[]
    if parts['metadata']>98304:violations.append('METADATA')
    if parts['verification']>262144:violations.append('VERIFICATION')
    if total>4194304:violations.append('TOTAL')
    return dict(parts=parts,total=total,report_reserve=8192,violations=violations)


def collect():
    pending={'reports/qualify_structure_chain_once.py','tools/_structure_ppb_chain.py','tests/test_structure_ppb_chain.py'};found={}
    while pending:
        name=pending.pop()
        if name in found:continue
        found[name]=pin(ROOT/name);package=name[:-3].replace('/','.').split('.')[:-1]
        for n in ast.walk(ast.parse((ROOT/name).read_text(encoding='utf-8-sig'))):
            mods=[]
            if isinstance(n,ast.Import):mods=[x.name for x in n.names]
            if isinstance(n,ast.ImportFrom):
                prefix='.'.join(package[:len(package)-n.level+1]) if n.level else ''
                base='.'.join(x for x in (prefix,n.module) if x);mods=[base,*[base+'.'+x.name for x in n.names]]
            for mod in mods:
                pathparts=mod.split('.')
                if pathparts[0] not in ('tools','reports','mcm_field_organism','tests'):continue
                for i in range(1,len(pathparts)+1):
                    for p in ('/'.join(pathparts[:i])+'.py','/'.join(pathparts[:i])+'/__init__.py'):
                        if (ROOT/p).is_file():pending.add(p)
    for path in (RAW/'record.json',RAW/'verification.json',SEALED/'execution.json',SEALED/'seal.json',
                 SEALED/'evaluation.json',PAIR/'table.json',PAIR/'verification.json',PAIR/'preregistration.json',
                 ARCHIVE,ROOT/'tools/_s2oe_visual_transition_diagnostic.py',
                 ROOT/'reports/s2oe/visual-transition-e03-e04-20260912-03/binding.json',
                 ROOT/'docs/STRUKTUR_LAGE_PPB_VERLAUFSPLAN.md'):
        found[path.relative_to(ROOT).as_posix()]=pin(path)
    found['reports/s2oe/STRUCTURE_CHAIN_FORMAT_BOUND.md']=pin(ROOT/'reports/s2oe/STRUCTURE_CHAIN_FORMAT_BOUND.md')
    original=json.loads((PAIR/'preregistration.json').read_bytes())['files']
    for name in ('mcm_field_organism/_ppb1_reference.py','tools/_s2jw_default_live_profile.py'):
        c.need(found[name]==original[name],'RULE_CHANGED')
    historical=json.loads((ROOT/'reports/s2oe/visual-transition-e03-e04-20260912-03/binding.json').read_bytes())
    c.need(pin(ARCHIVE)==historical['files']['tools/_s2oe_visual_transition_diagnostic.py'],'ARCHIVED_RULE_CHANGED')
    return found


def check(refs):
    for name,value in refs.items():c.need(pin(ROOT/name)==value,'SOURCE_CHANGED')


def prepare():
    c.need(not (Q/'preregistration.json').exists() and not RUN.exists(),'OUTPUT_EXISTS')
    refs=collect()
    extra={f'qualification/{k}':v for k,v in QCAPS.items()}
    budgets=alternatives(refs,extra)
    value=dict(version=c.VERSION,references=refs,sequences=c.SEQUENCES,config_digest=c.config().digest(),
        budgets=budgets,qualification_caps=QCAPS,run_caps=CAPS,
        work=dict(real_transitions=9,real_productive_differences=2592,real_diagnostic_differences=5184,
            real_verification_differences=2592,real_update_components_each_path=1728,
            neutral_transitions_max=10,neutral_diagnostic_differences_max=7488,
            neutral_productive_differences_max=2592,neutral_verification_attempts_max=12,
            neutral_verification_differences_max=31104,neutral_update_components_max=22464),
        tests=[n.name for n in ast.walk(ast.parse((ROOT/'tests/test_structure_ppb_chain.py').read_text()))
               if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')],
        interpreter=pin(Path(sys.executable)),python=sys.version,main_authorized=False)
    print(json.dumps(dict(binding_bytes=len(c.s.raw(value)),budgets=budgets)))
    c.need(len(c.s.raw(value))<=QCAPS['preregistration.json'] and all(not x['violations'] for x in budgets.values()),'PRESTART_LIMIT')
    Q.mkdir(exist_ok=True);save(Q,'preregistration.json',value)


def qualify():
    b=json.loads((Q/'preregistration.json').read_bytes());check(b['references'])
    with (Q/'qualification.claim').open('xb') as f:f.write(b'once\n')
    with (Q/'qualification.log').open('xb') as log:
        exit_code,overflow=capture([sys.executable,'-m','unittest','tests.test_structure_ppb_chain','-v'],log,
            dict(os.environ,PPB_CHAIN_NEUTRAL=str(Q),PPB_CHAIN_ARCHIVE=str(ARCHIVE)))
    check(b['references'])
    sizes={p.name:p.stat().st_size for p in Q.iterdir() if p.is_file()
           and p.relative_to(ROOT).as_posix() not in b['references']}
    overs=[name for name,n in sizes.items() if n>QCAPS[name]]
    balance=measure(b['references'],dict(sizes,**{'result.json':1024,'balance.json':4096,'main-binding.json':2048,'authorization.json':512}))
    ok=exit_code==0 and not overflow and not overs and not balance['violations']
    save(Q,'result.json',dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',test_calls=1,tests=len(b['tests']),
        exit_code=exit_code,diagnostic_status='DIAGNOSTIC_LIMIT_REACHED' if overflow else 'COMPLETE',
        diagnostic_complete=not overflow,overs=overs,gates=False,sources_unchanged=True))
    save(Q,'balance.json',dict(balance,files=sizes))
    print(json.dumps(dict(status='QUALIFIED' if ok else 'NOT_QUALIFIED',balance=balance)))
    if not ok:raise SystemExit('STOP_NO_RETRY')


def bind():
    b=json.loads((Q/'preregistration.json').read_bytes());check(b['references'])
    c.need(json.loads((Q/'result.json').read_bytes())['status']=='QUALIFIED' and not RUN.exists(),'NOT_READY')
    refs=dict(b['references']);refs.update({p.relative_to(ROOT).as_posix():pin(p) for p in Q.iterdir() if p.is_file()})
    extra={'future/main-binding.json':2048,'future/authorization.json':512}
    budgets=alternatives(refs,extra)
    c.need(all(not x['violations'] for x in budgets.values()),'MAIN_LIMIT')
    value=dict(version=c.VERSION,run_id=RUN.name,authorized=False,
        prerequisite=pin(Q/'preregistration.json'),qualification=pin(Q/'result.json'),budgets=budgets)
    c.need(len(c.s.raw(value))<=2048,'MAIN_BINDING_SIZE');save(Q,'main-binding.json',value)
    print(json.dumps(dict(binding=pin(Q/'main-binding.json'),budgets=budgets)))


def run():
    b=json.loads((Q/'preregistration.json').read_bytes());check(b['references'])
    main=json.loads((Q/'main-binding.json').read_bytes());auth=json.loads((Q/'authorization.json').read_bytes())
    c.need(main['prerequisite']==pin(Q/'preregistration.json') and main['qualification']==pin(Q/'result.json'),'ADMISSION')
    c.need(auth==dict(run_id=RUN.name,binding_sha256=pin(Q/'main-binding.json')[0],authorized=True),'AUTHORIZATION')
    c.need(not RUN.exists() and pin(Path(sys.executable))==b['interpreter'],'OUTPUT_OR_ENVIRONMENT')
    refs=dict(b['references']);refs.update({p.relative_to(ROOT).as_posix():pin(p) for p in Q.iterdir() if p.is_file()})
    c.need(all(not row['violations'] for row in alternatives(refs,{}).values()),'RUN_BUDGET')
    load=lambda path:json.loads(path.read_bytes())
    e=load(SEALED/'execution.json');vectors,_=inputs.extract(load(RAW/'record.json'),load(RAW/'verification.json'),e,load(SEALED/'seal.json'),load(SEALED/'evaluation.json'))
    pairs=load(PAIR/'table.json');pairproof=load(PAIR/'verification.json')
    c.need(pairproof['status']=='EVIDENCE_VALID' and pairproof['table_digest']==c.s.digest(pairs),'PAIR_PROOF')
    RUN.mkdir();(RUN/'run.claim').write_bytes(b'once\n');progress={};phase='ADVANCE'
    closure=dict(status='RECORDING_COMPLETE',secured=True)
    try:
        c.MAIN_GATE=True
        result=c.generate(vectors,e['sources'],main,progress)
        save(RUN,'record.json',result);phase='VERIFY';(RUN/'verification.claim').write_bytes(b'once\n')
        proof=c.verify(load(RUN/'record.json'),vectors,e['sources'],main)
        save(RUN,'verification.json',proof);phase='EVALUATE'
        save(RUN,'evaluation.json',c.evaluate(result,proof,pairs['rows']))
    except Exception as exc:
        closure=close_failure(RUN,exc,phase,progress,main)
    finally:
        c.MAIN_GATE=False
        closure=finish_balance(RUN,refs,closure)
    print(json.dumps(closure))
    if closure['status']!='RECORDING_COMPLETE':raise SystemExit('STOP_NO_RETRY')


if __name__=='__main__':{'prepare':prepare,'qualify':qualify,'bind':bind,'run':run}[sys.argv[1]]()
