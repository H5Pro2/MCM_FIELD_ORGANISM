"""Private versioned ledger; historical metadata defaults remain unchanged."""
from pathlib import Path
import hashlib
import json

VERSION='structure-location.ledger.v2-metadata98304'
LIMITS=dict(metadata=98304,verification=262144,total=4194304)
REAL_WORK=dict(differences=19008,exact_equalities=864,criteria=24)
VERIFY_WORK=dict(terms=19008,sums=88,exact_equalities=864)


class LedgerError(ValueError):
    pass


def need(value,code):
    if not value:raise LedgerError(code)


def classify(path):
    leaf=Path(path).name
    if leaf in ('record.json','partial.json','seal.json'):return 'evidence'
    if leaf=='verification.json':return 'verification'
    if path.endswith('.py'):return 'sources'
    return 'metadata'


def alternatives(caps):
    # A published evaluation is followed only by return/finally, not another
    # try-block operation. Failures may retain a record and a full partial.
    return {
        'success':{k:v for k,v in caps.items() if k not in ('partial.json','failure.json')},
        'failure':{k:v for k,v in caps.items() if k!='evaluation.json'},
    }


def measure(directory,references,caps,prospective=None):
    need(references['version']==VERSION,'LEDGER_VERSION')
    parts=dict(sources=0,metadata=0,evidence=0,verification=0)
    seen={};refparts=[]
    for ref in references['files']:
        path=ref['path'];kind=ref['kind'];size=ref['bytes']
        need(kind==classify(path),'REFERENCE_CLASS')
        need(type(size) is int and size>=0,'REFERENCE_SIZE')
        if path in seen:
            need(ref==seen[path],'REFERENCE_CONFLICT')
            continue
        seen[path]=ref;parts[kind]+=size;refparts.append(ref)
    files={p.name:p.stat().st_size for p in directory.iterdir() if p.is_file()} if directory.exists() else {}
    reference_totals=dict(parts)
    files.update(prospective or {})
    need(set(files)<=set(caps),'ARTIFACT_CLASS')
    for path,size in files.items():
        need(type(size) is int and size>=0,'ARTIFACT_SIZE')
        parts[classify(path)]+=size
    reserve=references.get('report_reserve',0)
    need(type(reserve) is int and reserve>=0,'RESERVE_SIZE')
    parts['metadata']+=reserve
    total=sum(parts.values())
    violations=[p for p,n in files.items() if n>caps[p]]
    for kind in ('metadata','verification'):
        if parts[kind]>LIMITS[kind]:violations.append(kind.upper())
    if total>LIMITS['total']:violations.append('TOTAL')
    reference_digest=hashlib.sha256(json.dumps(refparts,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return dict(version=VERSION,files=files,reference_totals=reference_totals,
        reference_count=len(refparts),reference_digest=reference_digest,parts=parts,
        metadata=parts['metadata'],reserve=reserve,total=total,limits=LIMITS,violations=violations)


def work(real,verification,neutral):
    need(set(real)==set(REAL_WORK) and set(verification)==set(VERIFY_WORK),'WORK_KEYS')
    for values,limits in ((real,REAL_WORK),(verification,VERIFY_WORK)):
        for key,value in values.items():
            need(type(value) is int and 0<=value<=limits[key],'WORK_LIMIT')
    need(neutral['basis'] in ('prospective','retrospective'),'NEUTRAL_BASIS')
    need(all(type(v) is int and v>=0 for k,v in neutral.items() if k!='basis'),'NEUTRAL_WORK')
    return dict(real=real,verification=verification,neutral=neutral)
