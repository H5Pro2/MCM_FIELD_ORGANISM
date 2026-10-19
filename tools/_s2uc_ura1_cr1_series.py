"""CR1 C/U orchestration; unchanged resource limits and codec."""
from tools._s2uc_ura1_v2_series import LIMITS, raw

def policy_case(number,source,ledger,*,neutral=False):
    from tools import _s2uc_ura1_cr1_engine as engine
    from tools import _s2uc_ura1_delta_encode as codec
    from tools._s2uc_ura1_cr1_fused import finish,live_sequences
    from tools._s2uc_ura1_cr1_archive import verify
    from tools._s2uc_ura1_capture_integrity import manifest
    from tools._s2uc_ura1_v2_sources import frames
    values=frames(source);encoded=raw(values)
    if len(values)>128 if neutral else len(values)!=1024:raise ValueError('CASE_FRAME_SCOPE')
    engine.VALIDATE=lambda v:None if raw(v)==encoded else (_ for _ in ()).throw(ValueError('CASE_MATERIAL'))
    engine.CHECKPOINT=lambda *args:ledger.check()
    arms=[];original=engine.create
    def create(mode):
        arm=original(mode);arms.append(arm);return arm
    engine.create=create
    try:
        with codec.store(ledger.folder) as owner:
            u=engine.run_arm(values,'U',trace=True);r=engine.run_arm(values,'C',trace=True)
            record=dict(neutral_only=neutral,source=[list(v) for v in values],U=u,C=r,paired_equal=True,differences=[],performance_claim=False)
            expected,checks=finish(record,live_sequences(record),build=True);proof=manifest(record)
            ledger.write(f'case-{number:02d}-capture.json',proof)
            path=ledger.folder/f'case-{number:02d}.delta.json.gz'
            codec.write_archive(record,path,expected);ledger.register(path,'archive');ledger.check()
            verified=verify(path.read_bytes(),proof,expected);ledger.check()
            rows=[]
            for uf,rf,ur,rr in zip(u['forecasts'],r['forecasts'],u['rows'],r['rows']):
                target=ur['target'];hs=[h for h in uf['receipt']['hypotheses'] if h['eligible']]
                warm=sum(h['ec'] is not None for h in hs)
                klass='none' if not hs else 'cold' if warm==0 else 'warm' if warm==len(hs) else 'mixed'
                uc,rc=uf['selected'],rf['selected']
                choice='both_persistence' if uc is None and rc is None else 'mixed' if (uc is None)!=(rc is None) else 'same_context' if uc==rc else 'different_context'
                rows.append(dict(target=target,U=ur['error'],C=rr['error'],cue=('X' if source['ids'][target-3]==0 else 'Y') if target%4==3 else None,
                    eligible=min(2,len(hs)),warm=klass,same_output=uf['output']==rf['output'],choice=choice))
            del record,u,r
        if not owner.closed or owner.pool.nodes or owner.deltas:raise ValueError('STORE_CLEANUP')
        return dict(replicate=number,orientation=(number-1)%2,complete=True,rows=rows,cleanup=True,
            source_neutral=neutral,integrity=verified['status'],counts=checks['counts'])
    finally:
        engine.create=original;engine.CHECKPOINT=lambda *args:None
        engine.VALIDATE=lambda _:(_ for _ in ()).throw(ValueError('UNARMED'))
        for arm in arms:
            if not arm.closed:arm._terminate()
        if any(not a.closed or any(a.bank) for a in arms):raise ValueError('ARM_CLEANUP')
