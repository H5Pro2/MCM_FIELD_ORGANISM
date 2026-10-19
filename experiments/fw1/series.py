"""One neutral measured pass per policy; serial independent archived reconstruction."""
import time
from . import engine
from .archive import verify,stock_digest
from tools import _s2uc_ura1_delta_encode as codec
from tools._s2uc_ura1_capture_integrity import manifest,full_record_digest
from tools._s2uc_ura1_v2_series import raw

def policy_case(number,source,ledger):
    values=[tuple(source['catalog'][i]) for i in source['ids']]
    if not 0<len(values)<=128 or len(values)%4:raise PermissionError('NEUTRAL_SCOPE')
    encoded=raw(values);engine.VALIDATE=lambda v:engine.need(raw(v)==encoded,'CASE_MATERIAL')
    engine.CHECKPOINT=lambda *args:ledger.check()
    started=time.monotonic()
    try:
        with codec.store(ledger.folder) as owner:
            keep=engine.run_arm(values,'KEEP');reset=engine.run_arm(values,'RESET')
            engine.need(stock_digest(keep['events'])==stock_digest(reset['events']),'STOCK_IDENTITY')
            root=dict(entry_revision='FW1_V1',neutral_only=True,source=values,KEEP=keep,RESET=reset)
            expected=full_record_digest(root);proof=manifest(root)
            ledger.write(f'case-{number:02d}-capture.json',proof)
            path=ledger.folder/f'case-{number:02d}.gz';sizes=codec.write_archive(root,path,expected);ledger.register(path,'archive')
            verified=verify(path.read_bytes(),proof,expected);ledger.check()
            kr=list(keep['rows']);rr=list(reset['rows'])
            targets=[r['target'] for r in kr]
            engine.need(targets==[r['target'] for r in rr],'TARGET_PAIR')
            resources=dict(KEEP=keep['resources'],RESET=reset['resources'],dictionary=owner.bytes,nodes=owner.entries,edges=owner.edges,indices=owner.indices,collections=len(owner.items),record_peak=owner.record_peak,temp_peak=owner.temp_peak,**sizes)
            report=dict(complete=True,cleanup=True,integrity=verified['status'],stock_equal=True,stock_digest=verified['stock_digest'],targets=targets,KEEP=[r['error'] for r in kr],RESET=[r['error'] for r in rr],resets=verified['resets']['RESET'],resources=resources,seconds=time.monotonic()-started,executions=dict(policy=2,live_reference=2,archive_reference=2))
            ledger.write(f'case-{number:02d}-summary.json',report)
        engine.need(owner.closed and codec.ACTIVE is None,'STORE_CLEANUP')
        return report
    finally:
        engine.CHECKPOINT=lambda *args:None
        engine.VALIDATE=lambda _:(_ for _ in ()).throw(PermissionError('UNARMED'))
