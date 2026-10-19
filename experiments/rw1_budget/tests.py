"""Targeted artificial ledger fault tests, no perception/projector/policy imports."""
from pathlib import Path
import copy,os
from .incremental import JournalBudget,CAPS,CONTROL

def rejected(fn,text=None):
    try:fn()
    except (ValueError,OSError) as e:
        if text and text not in str(e):raise AssertionError(str(e))
        return str(e)
    raise AssertionError('EXPECTED_REJECTION')

def run(folder):
    names=[];roots=[]
    def make(name,caps=None,base=()):
        root=Path(folder)/'artificial-tests'/name;roots.append(root)
        return JournalBudget(root,base,create=True,caps=caps)
    x=make('create-append')
    x.write('observer/log.jsonl',{'fixture':1},append=True,role='supervisor')
    x.write('observer/log.jsonl',{'fixture':2},append=True,role='worker')
    a=x.reconcile();assert a['matched'] and len((x.target/'observer/log.jsonl').read_bytes().splitlines())==2
    names.append('exclusive-create-and-append-balance')
    rejected(lambda:x.write('observer/log.jsonl',b'x'),'EXCLUSIVE_EXISTS');names.append('exclusive-existing-file-rejected')
    for group in ('material','observer','closure'):
        caps=dict(CAPS);caps[group]=5000
        x=make('partition-'+group,caps)
        rejected(lambda:x.write(group+'/large.fixture',bytes(5001)),'LIMIT_'+group)
        assert not (x.target/group/'large.fixture').exists();names.append('partition-'+group)
    caps=dict(CAPS,total=40000);x=make('global-reserve',caps)
    rejected(lambda:x.write('material/large.fixture',bytes(8000)),'LIMIT_total');names.append('global-limit-preserves-32768-reserve')
    x=make('file-limit');rejected(lambda:x.write('material/projection-000.json',bytes(8193)),'PROJECTION_SIZE');names.append('projection-file-limit')
    x=make('counter-event');rejected(lambda:x.write('observer/counts.jsonl',bytes(513),append=True),'COUNTER_SIZE');names.append('counter-event-limit')
    x=make('traversal');rejected(lambda:x.write('../escaped.fixture',b'x'),'OUTPUT_SCOPE');names.append('path-traversal')
    x=make('control-protection');rejected(lambda:x.write(CONTROL+'journal.jsonl',b'x'),'OUTPUT_SCOPE');names.append('control-writer-protection')
    for mode in ('fail','partial'):
        x=make('write-'+mode);original=x._write
        def faulty(p,data,openmode):
            if p.name=='victim.fixture':
                if mode=='fail':raise OSError('ARTIFICIAL_WRITE_FAILURE')
                return original(p,data[:3],openmode)
            return original(p,data,openmode)
        x._write=faulty
        rejected(lambda:x.write('material/victim.fixture',b'artificial payload'))
        rejected(lambda:x.write('material/again.fixture',b'x'),'LEDGER_POISONED')
        rejected(lambda:JournalBudget(x.target,expected_snapshot=x.snapshot_hash),'INCOMPLETE_TRANSACTION')
        names.append('failed-or-partial-write-durable-poison-'+mode)
    x=make('partial-journal');original=x._write
    def broken_journal(p,data,mode):
        if p==x.journal:return original(p,data[:12],mode)
        return original(p,data,mode)
    x._write=broken_journal
    rejected(lambda:x.write('material/victim.fixture',b'x'),'PARTIAL_JOURNAL')
    rejected(lambda:JournalBudget(x.target,expected_snapshot=x.snapshot_hash),'PARTIAL_JOURNAL');names.append('partial-journal-rejected')
    x=make('unexpected-file');(x.target/'observer/foreign.fixture').write_bytes(b'foreign artificial file')
    rejected(x.reconcile,'INDEPENDENT_INVENTORY_MISMATCH');names.append('unaccounted-file-final-audit')
    x=make('changed-file');x.write('observer/known.fixture',b'abc')
    (x.target/'observer/known.fixture').write_bytes(b'longer artificial value')
    rejected(lambda:x.write('observer/known.fixture',b'x',append=True),'EXISTING_FILE_CHANGED');names.append('changed-append-target')
    x=make('same-size-change');x.write('observer/known.fixture',b'abc');p=x.target/'observer/known.fixture';p.write_bytes(b'xyz')
    old=x.files['observer/known.fixture']['mtime'];os.utime(p,ns=(old+10000000,old+10000000))
    rejected(x.reconcile,'INDEPENDENT_INVENTORY_MISMATCH');names.append('same-size-mtime-change')
    x=make('deleted-file');x.write('observer/known.fixture',b'abc');(x.target/'observer/known.fixture').unlink()
    rejected(x.reconcile,'INDEPENDENT_INVENTORY_MISMATCH');names.append('missing-file-final-audit')
    base=Path(folder)/'artificial-tests/inherited';base.mkdir(parents=True);(base/'base.fixture').write_bytes(b'base')
    x=make('inherited-change',base=[base]);(base/'new.fixture').write_bytes(b'new')
    rejected(x.reconcile,'INHERITED_INVENTORY_MISMATCH');names.append('inherited-tree-change')
    x=make('two-cooperative-writers');y=JournalBudget(x.target,expected_snapshot=x.snapshot_hash)
    for i in range(4):
        x.write('observer/shared.jsonl',{'supervisor':i},append=True,role='supervisor')
        y.write('observer/shared.jsonl',{'worker':i},append=True,role='worker')
    assert x.reconcile()==y.reconcile();names.append('stale-writer-sync-and-common-lock')
    x=make('snapshot-change');data=x.snapshot.read_bytes();x.snapshot.write_bytes(data+b' ')
    rejected(lambda:x.write('observer/x',b'x'),'SNAPSHOT_CHANGED');names.append('snapshot-modification')
    x=make('reservation-before-begin');caps=dict(x.caps);x.caps['observer']=x.totals['observer']+100
    rejected(lambda:x.write('observer/x',b'x'),'LIMIT_observer');assert x.journal.stat().st_size==0
    names.append('transaction-reservation-precedes-BEGIN')
    x=make('journal-prefix-change');x.write('observer/x',b'x')
    data=x.journal.read_bytes().replace(b'worker',b'Worker',1);x.journal.write_bytes(data)
    rejected(x.reconcile,'FULL_JOURNAL_INTEGRITY');names.append('already-read-journal-prefix-change')
    return dict(passed=True,tests=names,count=len(names),synthetic_only=True,no_receptor_nj_policy=True,
                limitation='Unregistered additions are rejected at independent reconciliation; cooperative writers must exclusively own the output roots. No adversarial filesystem isolation claimed.')
