"""P2 byte contract and complete, fail-closed accounting across all owned roots."""
from pathlib import Path
from types import MappingProxyType
from tools import _s2uc_inventory_v7 as inventory
from tools._s2uc_resource_contract_v7 import CATEGORIES, _need as need

VERSION = 's2uc.resources.p2'
LIMITS = MappingProxyType(dict(code=1048576, metadata=131072, static_shared=1572864,
    shared=1703936, record=262144, verification=262144, error=65536,
    terminal=32768, minimal=16384, staging=245760, total=4194304))
RESERVES = MappingProxyType(dict(record=245760, verification=131072))
FILES = dict.fromkeys(('binding.json','manifest.json','source-context.json','claim.json',
    'config.json','bootstrap.json','parent-admission.json','child-admission.json',
    'after-imports.json','facts.json'), 'metadata')
FILES.update(dict.fromkeys(('inventory.json','resources.json','ledger.json','result.json',
    'process-exit.json','preservation.json','protocol.json','test-result.json','unittest.log',
    'REPORT.txt','progress.json'), 'static_shared'))
FILES.update({'record.json':'record','verification.json':'verification','provenance.json':'verification',
    'terminal.json':'terminal','appendix-terminal.json':'terminal','error.json':'error',
    'appendix-error.json':'error','stderr.txt':'error','stdout.txt':'static_shared',
    'minimal.json':'minimal','publication.tmp':'staging'})

def contract():
    return dict(version=VERSION, limits=dict(LIMITS), reserves=dict(RESERVES),
        protocol_per_file=32768, active_inventory_per_file=16384,
        child_job_commit_bytes=640*1048576, parent_process_limited=False,
        real_execution_authorized=False)

def account(amounts):
    need(type(amounts) is dict and set(amounts)==set(CATEGORIES), 'P2_CATEGORIES')
    need(all(type(v) is int and v>=0 for v in amounts.values()), 'P2_SIZE')
    shared=sum(amounts[k] for k in ('static_shared','error','terminal','minimal'))
    total=sum(amounts.values())
    errors=['limit:'+k for k in CATEGORIES if amounts[k]>LIMITS[k]]
    errors += ['reserve:'+k for k in RESERVES if amounts[k]>RESERVES[k]]
    if shared>LIMITS['shared']: errors.append('limit:shared')
    if total>LIMITS['total']: errors.append('limit:total')
    return dict(categories=dict(amounts), shared_bytes=shared,total_bytes=total,
                within_limits=not errors,violations=errors)

def closure_reservation(actual):
    """Prospective envelope, not additional measured bytes or a success claim."""
    reserved=dict(actual)
    for k in ('record','verification','error','terminal','minimal','staging'):
        reserved[k]=max(reserved[k],RESERVES.get(k,LIMITS[k]))
    return account(reserved)

class Ledger:
    def __init__(self, inv, roots, inputs):
        self.inv=inv
        self.roots=[Path(p).absolute() for p in roots]
        need(len(set(self.roots))==len(self.roots), 'P2_DUPLICATE_ROOT')
        for a in self.roots:
            need(not a.is_symlink() and not a.is_junction() and a.resolve()==a,
                 'P2_ROOT_ALIAS')
            need(all(a==b or not a.is_relative_to(b) for b in self.roots), 'P2_NESTED_ROOT')
        self.inputs=inputs

    def snapshot(self):
        amounts=dict.fromkeys(CATEGORIES,0); files=[]; identities={}; paths=set()
        def add(root,name,category,expected=None,active=False):
            path=(root/name).absolute()
            need(path not in paths,'P2_DUPLICATE_FILE')
            ref,_,identity=inventory.read_file(root,name)
            need(identity not in identities,'P2_FILE_ALIAS')
            identities[identity]=path;paths.add(path)
            if expected is not None: need(all(ref[k]==expected[k] for k in ref),'P2_INPUT_CHANGED:'+name)
            if active and Path(name).name in ('inventory.json','protocol.json'):
                need(ref['bytes']<=(16384 if name.endswith('inventory.json') else 32768),
                     'P2_PER_FILE_LIMIT')
            amounts[category]+=ref['bytes']
            if category!='code': files.append(dict(path=path.as_posix(),category=category,**{k:v for k,v in ref.items() if k!='path'}))
        for ref in self.inv['files']: add(inventory.ROOT,ref['path'],'code',ref)
        need(amounts['code']==self.inv['code_bytes'],'P2_CODE_COUNT')
        for row in self.inputs:
            add(inventory.ROOT,row['ref']['path'],row['category'],row['ref'])
        for root in self.roots:
            need(root.is_dir(),'P2_ROOT_MISSING')
            for path in sorted(root.rglob('*')):
                need(not path.is_symlink() and not path.is_junction(),'P2_PATH_ALIAS')
                if path.is_dir(): continue
                name=path.relative_to(root).as_posix()
                need(path.name in FILES,'P2_UNCLASSIFIED:'+name)
                add(root,name,FILES[path.name],active=True)
        actual=account(amounts)
        return dict(version=VERSION,files=files,actual=actual,
            reserved_closure=closure_reservation(amounts),accounting_complete=True)

    def admit(self):
        result=self.snapshot()
        need(result['actual']['within_limits'],'P2_ACTUAL_BUDGET')
        need(result['reserved_closure']['within_limits'],'P2_CLOSURE_BUDGET')
        return result

    def project(self, category, size):
        measured=self.admit()
        for k in ('staging',category):
            amounts=dict(measured['actual']['categories']); amounts[k]+=size
            need(account(amounts)['within_limits'],'P2_PUBLICATION_BUDGET')
        return measured
