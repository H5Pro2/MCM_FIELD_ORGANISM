"""Bound finite comparison. Evaluation roles never enter perception calls."""
import hashlib
import json
import math
import traceback
import numpy as np
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor
from tools._s2lv_private_pose_form_projection import project_pose_form, S2LVProjectionError
from tools import _structure_source_binding as source

VERSION = 'structure-location.comparison.v1'
MAIN_GATE = False
CAPS = {'record.json':1048576, 'partial.json':1048576,
        'verification.json':8192, 'evaluation.json':16384, 'failure.json':16384,
        'balance.json':2048, 'run.claim':5, 'verification.claim':5}


class ComparisonError(ValueError):
    pass


def need(value, code):
    if not value: raise ComparisonError(code)


def publish(path, value):
    need(not path.exists(), 'OUTPUT_EXISTS')
    tmp = path.with_suffix(path.suffix+'.tmp')
    with tmp.open('xb') as f: f.write(source.raw(value))
    tmp.rename(path)


def hexes(values):
    need(all(type(v) is float and math.isfinite(v) for v in values), 'VALUE_DOMAIN')
    return [v.hex() for v in values]


def distance(a, b):
    terms = [abs(a[i]-b[i]) for i in range(len(a))]
    return dict(terms=hexes(terms), mean=(sum(terms)/len(terms)).hex())


def direct_distance(a, b):
    # Independent term construction; retain Python's historical sum semantics.
    differences = []
    for left, right in zip(a, b, strict=True):
        differences.append(abs(left-right))
    answer = sum(differences)/len(differences)
    return {'terms':[float.hex(v) for v in differences], 'mean':float.hex(answer)}


def perceive(payload, frame_index):
    image = np.frombuffer(payload, dtype=np.uint8).reshape(1080,1920,3)
    state = LocalChannelGridReceptor().analyze(image, frame_index=frame_index)
    raw = state.channel_values
    try:
        projection = project_pose_form(raw)
    except S2LVProjectionError as exc:
        if str(exc) != 'visual state has no form activation': raise
        return dict(raw=hexes(raw), form=None, pose=None, projection_digest=None,
                    form_status='NO_FORM_ACTIVATION')
    return dict(raw=hexes(raw), form=hexes(projection.form_descriptor.values),
                pose=projection.pose.canonical_payload(), projection_digest=projection.digest(),
                form_status='AVAILABLE')


def compare(rows, pairs):
    primary=[]; direct=[]; count=0
    for pair_id,(q,r) in enumerate(pairs):
        for arm,field in (('RAW288','raw'),('FORM144','form')):
            a,b=rows[q][field],rows[r][field]
            header=dict(pair=pair_id,indices=[q,r],arm=arm)
            if a is None or b is None:
                primary.append(dict(header,status='UNAVAILABLE',terms=[],mean=None))
                direct.append(dict(header,status='UNAVAILABLE',terms=[],mean=None))
            else:
                av=tuple(float.fromhex(x) for x in a);bv=tuple(float.fromhex(x) for x in b)
                primary.append(dict(header,status='AVAILABLE',**distance(av,bv)))
                direct.append(dict(header,status='AVAILABLE',**direct_distance(av,bv)))
                count += 2*len(av)
    need(count<=19008,'WORK_LIMIT')
    return primary,direct,count


def exact(rows,pairs):
    result=[];count=0
    for pair in (20,21):
        q,r=pairs[pair];fields={}
        for field in ('raw','form'):
            a,b=rows[q][field],rows[r][field]
            fields[field]=None if a is None or b is None else [x==y for x,y in zip(a,b,strict=True)]
            if fields[field] is not None:count+=len(fields[field])
        fields.update(pair=pair,pose_equal=rows[q]['pose']==rows[r]['pose'])
        result.append(fields)
    return result,count


def ledger(directory, references, prospective=None):
    if isinstance(references,dict):
        from tools._structure_comparison_ledger import measure
        return measure(directory,references,CAPS,prospective)
    files={p.name:p.stat().st_size for p in directory.iterdir() if p.is_file()} if directory.exists() else {}
    files.update(prospective or {})
    need(set(files)<=set(CAPS),'ARTIFACT_CLASS')
    metadata=sum(n for p,n in files.items() if p not in ('record.json','partial.json','verification.json'))
    # Bound manifest/report reserve is counted even before their publication.
    metadata+=12288
    total=references+sum(files.values())+12288
    violations=[p for p,n in files.items() if n>CAPS[p]]
    if metadata>65536:violations.append('METADATA')
    if total>4194304:violations.append('TOTAL')
    return dict(files=files,metadata=metadata,references=references,reserve=12288,total=total,violations=violations)


def evaluate(record, verification, evaluation):
    need(verification.get('status')=='EVIDENCE_VALID' and verification.get('evaluation_allowed') is True
         and verification.get('record_digest')==source.digest(record),'EVALUATION_FORBIDDEN')
    need(source.digest(evaluation)==record['evaluation_digest'],'EVALUATION_BINDING')
    lookup={(r['pair'],r['arm']):r['mean'] for r in record['primary']}
    outcomes=[]
    for index,c in enumerate(evaluation['criteria']):
        left=[lookup[(i,c['arm'])] for i in c['within']]
        right=[lookup[(i,c['arm'])] for i in c['between']]
        if None in left+right:
            outcomes.append(dict(index=index,criterion=c,status='UNAVAILABLE',margin=None));continue
        worst=max(float.fromhex(x) for x in left);nearest=min(float.fromhex(x) for x in right)
        outcomes.append(dict(index=index,criterion=c,status='PASS' if worst<nearest else 'TIE' if worst==nearest else 'FAIL',
            margin=(nearest-worst).hex(),within_max=worst.hex(),between_min=nearest.hex()))
    gains=[];losses=[]
    for start in (0,6,12,18):
        a,b=outcomes[start],outcomes[start+3]
        if a['status']!='PASS' and b['status']=='PASS':gains.append(start//6)
        if a['status']=='PASS' and b['status']!='PASS':losses.append(start//6)
    return dict(status='DESCRIPTIVE_ONLY',N=24,criteria=outcomes,roles=evaluation['roles'],
                global_form_gains=gains,global_form_losses=losses,exact=record['exact'],
                identity_claim=False,automatic_integration=False)


def execute(binding, directory, references, loader, evaluation):
    global MAIN_GATE
    need(MAIN_GATE is True,'GATE_CLOSED');MAIN_GATE=False
    need(not directory.exists(),'OUTPUT_EXISTS')
    if isinstance(references,dict):
        from tools._structure_comparison_ledger import alternatives
        choices=alternatives(CAPS).values()
    else:
        choices=[CAPS]
    for choice in choices:
        need(not ledger(directory,references,choice)['violations'],'PREFLIGHT_LIMIT')
    directory.mkdir();(directory/'run.claim').write_bytes(b'once\n')
    rows=[];phase='SOURCE';record=None;payload=None
    try:
        execution=binding['execution']
        for src,proof in zip(execution['sources'],binding['seal']['sources'],strict=True):
            phase='PAYLOAD';payload=loader(src)
            need(len(payload)==proof['bytes'] and hashlib.sha256(payload).hexdigest()==proof['sha256'],'PAYLOAD_HASH')
            phase='PERCEPTION';values=perceive(payload,src['frame_index'])
            rows.append(dict(values,id=src['id'],source_digest=source.digest(src),time=src['time'],
                             frame_index=src['frame_index'],payload_sha256=proof['sha256']))
            del payload;payload=None
        phase='COMPARE';primary,direct,count=compare(rows,binding['pairs'])
        exact_rows,exact_count=exact(rows,binding['pairs'])
        record=dict(version=VERSION,status='RECORDING_COMPLETE',binding_digest=source.digest(binding),
            execution_digest=source.digest(execution),evaluation_digest=binding['evaluation_digest'],
            rows=rows,primary=primary,direct=direct,exact=exact_rows,
            counts=dict(receptors=len(rows),projections=len(rows),differences=count,exact_equalities=exact_count))
        phase='RECORD';need(len(source.raw(record))<=CAPS['record.json'],'RECORD_LIMIT')
        publish(directory/'record.json',record)
        # Verification is imported separately and never calls perception or distance helpers.
        from tools._structure_comparison_verify import verify
        phase='VERIFY';(directory/'verification.claim').write_bytes(b'once\n')
        proof=verify(json.loads((directory/'record.json').read_bytes()),binding)
        publish(directory/'verification.json',proof)
        phase='EVALUATION'
        result=evaluate(record,proof,evaluation)
        need(len(source.raw(result))<=CAPS['evaluation.json'],'EVALUATION_LIMIT')
        publish(directory/'evaluation.json',result)
        return record,proof
    except Exception as exc:
        publish(directory/'partial.json',dict(rows=rows))
        publish(directory/'failure.json',dict(status='NOT_EVALUABLE',phase=phase,completed=len(rows),
            error=str(exc),traceback=traceback.format_exc(),gates=False))
        raise
    finally:
        payload=None;MAIN_GATE=False
        balance=ledger(directory,references,{'balance.json':2048})
        publish(directory/'balance.json',balance)
        need(not balance['violations'],'FINAL_LIMIT')
