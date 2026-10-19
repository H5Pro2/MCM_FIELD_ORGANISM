"""Read stored raw vectors using the original PPB distance, without updates."""
import math
from mcm_field_organism._ppb1_reference import normalized_mean_l1_distance
from tools import _structure_source_binding as s

VERSION='structure-location.ppb-offline.v1'
THRESHOLD=0.01


def need(value,code):
    if not value:raise s.BindingError(code)


def vector(values):
    need(len(values)==288,'VECTOR_SIZE')
    result=tuple(float.fromhex(x) for x in values)
    need(all(math.isfinite(x) and 0<=x<=1 and x.hex()==text for x,text in zip(result,values,strict=True)),'VECTOR_DOMAIN')
    return result


def extract(record,proof,execution,seal,evaluation):
    need(proof['status']=='EVIDENCE_VALID' and proof['evaluation_allowed']
         and proof['record_digest']==s.digest(record),'PARENT_PROOF')
    need(record['status']=='RECORDING_COMPLETE' and record['execution_digest']==s.digest(execution)
         and record['evaluation_digest']==s.digest(evaluation),'ROOT_BINDING')
    need(seal['execution_digest']==s.digest(execution) and len(record['rows'])==14,'SOURCE_COUNT')
    need(execution['profile']=='visual.grid12x8.channels3.source1920x1080.v1','PROFILE')
    vectors=[]
    for row,src,receipt in zip(record['rows'],execution['sources'],seal['sources'],strict=True):
        need(row['source_digest']==receipt['source_digest']==s.digest(src)
             and row['id']==src['id']==receipt['id'] and row['payload_sha256']==receipt['sha256']
             and row['frame_index']==src['frame_index'] and row['time']==src['time'],'SOURCE_BINDING')
        vectors.append(vector(row['raw']))
    rows=[r for r in record['primary'] if r['arm']=='RAW288']
    need(len(rows)==len(evaluation['pairs'])==22,'PAIR_COUNT')
    for i,row in enumerate(rows):
        need(row['pair']==i and row['indices']==evaluation['pairs'][i] and row['status']=='AVAILABLE','PAIR_BINDING')
        need(len(row['terms'])==288,'TERM_COUNT')
    return vectors,rows


def decision(distance,previous):
    return dict(distance=distance.hex(),previous_sum=previous.hex(),
        threshold=THRESHOLD.hex(),matched=distance<=THRESHOLD,
        previous_matched=previous<=THRESHOLD,numeric_changed=distance.hex()!=previous.hex(),
        decision_changed=(distance<=THRESHOLD)!=(previous<=THRESHOLD),
        difference_from_sum=(distance-previous).hex())


def table(vectors,old_rows):
    need(len(vectors)==14 and len(old_rows)==22,'INPUT_COUNT')
    rows=[]
    for i,old in enumerate(old_rows):
        q,r=old['indices'];distance=normalized_mean_l1_distance(vectors[q],vectors[r])
        rows.append(dict(pair=i,indices=[q,r],**decision(distance,float.fromhex(old['mean']))))
    return dict(version=VERSION,rows=rows,primary_differences=6336,threshold=THRESHOLD.hex())


def verify(result,old_rows):
    """Independent fsum of previously verified terms, not a PPB-helper replay."""
    need(result['version']==VERSION and result['primary_differences']==6336
         and len(result['rows'])==len(old_rows)==22 and result['threshold']==THRESHOLD.hex(),'TABLE_FORM')
    for i,(row,old) in enumerate(zip(result['rows'],old_rows,strict=True)):
        need(row['pair']==i and row['indices']==old['indices'],'PAIR_BINDING')
        terms=vector(old['terms']);expected=math.fsum(terms)/288
        previous=float.fromhex(old['mean'])
        need(row['distance']==expected.hex() and row['previous_sum']==old['mean'] and row['threshold']==THRESHOLD.hex(),'DISTANCE')
        need(row['matched']==(expected<=THRESHOLD) and row['previous_matched']==(previous<=THRESHOLD)
             and row['numeric_changed']==(expected.hex()!=old['mean'])
             and row['decision_changed']==((expected<=THRESHOLD)!=(previous<=THRESHOLD))
             and row['difference_from_sum']==(expected-previous).hex(),'DECISION')
    return dict(status='EVIDENCE_VALID',table_digest=s.digest(result),read_only=True,
                verification_terms=6336,verification_sums=22,new_differences=0,
                boundary='Independent summation of the already verified stored per-band terms.')
