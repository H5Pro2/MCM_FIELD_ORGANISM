"""Exactly one measured/captured policy pass per arm; no replay of production."""
import time
from tools._s2uc_ura1_v2_series import LIMITS,raw
from tools._s2uc_er1_run_mechanisms import witnesses,summarize

def policy_case(number,source,ledger,*,neutral=False):
    from tools import _s2uc_er1_run_engine as engine
    from tools import _s2uc_ura1_delta_encode as codec
    from tools._s2uc_er1_run_observer import compare,archive_form
    from tools._s2uc_er1_run_archive import verify
    from tools._s2uc_ura1_capture_integrity import manifest,full_record_digest
    from tools._s2uc_ulz1_resources import deep
    values=[tuple(source['catalog'][i]) for i in source['ids']]
    if (not 0<len(values)<=128 if neutral else len(values)!=1024):raise ValueError('CASE_SCOPE')
    if not neutral:
        from tools.s2uc_er1_research_prepare import validate_admission,AUTH
        validate_admission(AUTH,ledger.folder)
    encoded=raw(values);engine.VALIDATE=lambda v:engine.need(raw(v)==encoded,'CASE_MATERIAL')
    engine.CHECKPOINT=lambda *args:ledger.check()
    arms=[];original=engine.create;started=time.monotonic()
    def create(mode):
        if len(arms)>=2:raise ValueError('POLICY_EXECUTION_LIMIT')
        arm=original(mode);arms.append(arm);return arm
    engine.create=create
    try:
        with codec.store(ledger.folder) as owner:
            e=engine.run_arm(values,'E',trace=False);f=engine.run_arm(values,'F',trace=False)
            policy_seconds=time.monotonic()-started
            observation=compare(e,f);chains=witnesses(observation,values);mechanisms=codec.collection()
            for item in chains:mechanisms.append(item)
            record=dict(neutral_only=neutral,source=[list(v) for v in values],E=e,F=f,observer=archive_form(observation,codec.collection),mechanisms=mechanisms)
            expected=full_record_digest(record);proof=manifest(record)
            ledger.write(f'case-{number:02d}-capture.json',proof)
            path=ledger.folder/f'case-{number:02d}.gz'
            sizes=codec.write_archive(record,path,expected);ledger.register(path,'archive');ledger.check()
            begin=time.monotonic();verified=verify(path.read_bytes(),proof,expected);archive_seconds=time.monotonic()-begin;ledger.check()
            rows=[]
            for a,b in zip(observation['E']['targets'],observation['F']['targets'],strict=True):
                if a['target']!=b['target']:raise ValueError('TARGET_PAIR')
                rows.append(dict(target=a['target'],E=a['error'],F=b['error'],warm=any(h['warm'] and h['chosen'] for h in a['hypotheses']),E_warm=any(h['warm'] and h['chosen'] for h in a['hypotheses']),F_warm=any(h['warm'] and h['chosen'] for h in b['hypotheses'])))
            resources=dict(E=e['resources'],F=f['resources'],observer_deep=deep(observation),mechanisms_deep=deep(chains),dictionary=owner.bytes,nodes=owner.entries,edges=owner.edges,indices=owner.indices,collections=len(owner.items),record_peak=owner.record_peak,temp_peak=owner.temp_peak,**sizes)
            report=dict(replicate=number,orientation=(number-1)%2,complete=True,rows=rows,cleanup=True,integrity=verified['status'],mechanisms=summarize(chains),counts=observation['counts'],cost_balance=observation['cost_balance'],resources=resources,timing=dict(policy_and_live_reference_seconds=policy_seconds,archive_reference_seconds=archive_seconds,total_seconds=time.monotonic()-started),executions=dict(policy=2,live_reference=2,archive_reference=2,extra_policy_measurement=0))
            ledger.write(f'case-{number:02d}-summary.json',{k:v for k,v in report.items() if k!='rows'})
        if not owner.closed or codec.ACTIVE is not None:raise ValueError('STORE_CLEANUP')
        return report
    finally:
        engine.create=original;engine.CHECKPOINT=lambda *args:None
        engine.VALIDATE=lambda _:(_ for _ in ()).throw(PermissionError('UNARMED'))
        for arm in arms:
            if not arm.closed:arm._terminate()
        if any(not a.closed or any(a.bank) for a in arms):raise ValueError('ARM_CLEANUP')
