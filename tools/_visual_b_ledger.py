"""Private comparison budgets; historical ledgers remain unchanged."""
from pathlib import Path
from tools import _visual_b_frozen as f

VERSION='visual-b.comparison.metadata131072.v1'
LIMITS=dict(metadata=131072,evidence=1048576,verification=262144,total=4194304)
RUN_CAPS={'record.json':231417,'binding.json':98304,'verification.json':4096,
          'evaluation.json':16384,'error.json':4096,'balance.json':4096,'REPORT.md':4096,'claim':5}
KINDS={'record.json':'evidence','binding.json':'evidence','verification.json':'verification'}


class BudgetError(f.FrozenBindingError):
    def __init__(self,balance):
        self.balance=balance
        super().__init__('BUDGET_INVALID')


def totals(contributions):
    parts=dict(sources=0,metadata=0,evidence=0,verification=0)
    for row in contributions:
        f.require(row['kind'] in parts and type(row['bytes']) is int and row['bytes']>=0,'LEDGER_FORM')
        parts[row['kind']]+=row['bytes']
    parts['total']=sum(parts.values())
    return dict(version=VERSION,parts=parts,contributions=contributions,
                violations=[key for key,limit in LIMITS.items() if parts[key]>limit])


def preflight(files,extra=()):
    common=[dict(name=name,kind=p['kind'],bytes=p['bytes']) for name,p in files.items()]+list(extra)
    alternatives=[]
    for status in ('success','failure'):
        names=[n for n in RUN_CAPS if not (status=='success' and n=='error.json') and
               not (status=='failure' and n=='evaluation.json')]
        entries=common+[dict(name=n,kind=KINDS.get(n,'metadata'),bytes=RUN_CAPS[n]) for n in names]
        # Interrupted atomic publication may coexist with completed artifacts.
        # Reserve one largest temporary in addition, including in success preflight.
        entries.append(dict(name='temporary-publication',kind='evidence',bytes=max(RUN_CAPS.values())))
        value=totals(entries);value['alternative']=status;alternatives.append(value)
    return dict(version=VERSION,alternatives=alternatives,
                violations=[(r['alternative'],v) for r in alternatives for v in r['violations']])


def measure(directory,files,*,phase,completed):
    entries=[dict(name=name,kind=p['kind'],bytes=p['bytes']) for name,p in files.items()]
    violations=[];sizes={}
    for path in sorted(Path(directory).iterdir()):
        if not path.is_file():
            violations.append('UNEXPECTED_DIRECTORY');continue
        name=path.name;base=name[:-4] if name.endswith('.tmp') else name
        size=path.stat().st_size;sizes[name]=size
        if base not in RUN_CAPS:violations.append('UNEXPECTED_FILE:'+name)
        elif size>RUN_CAPS[base]:violations.append('ITEM_LIMIT:'+name)
        entries.append(dict(name=name,kind=KINDS.get(base,'metadata'),bytes=size))
        if name.endswith('.tmp'):violations.append('TEMPORARY_REMAINS:'+name)
    for name in ('balance.json','REPORT.md'):
        entries.append(dict(name=name+':remaining-reserve',kind='metadata',
                            bytes=max(0,RUN_CAPS[name]-sizes.get(name,0))))
    value=totals(entries);value['violations']+=violations
    # Reference details are already available in the bound inventory; do not
    # recursively embed an ever-growing copy into its own balance file.
    reference_bytes=sum(p['bytes'] for p in files.values())
    return dict(version=VERSION,parts=value['parts'],files=sizes,
                reference_bytes=reference_bytes,references_digest=f.digest(files),
                remaining_report_and_balance_reserved=True,violations=value['violations'],
                phase=phase,completed=completed)


def enforce(value):
    if value['violations']:raise BudgetError(value)
    return value
