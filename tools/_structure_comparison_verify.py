"""Offline verifier: no rendering, receptor, projection, or subtraction calls."""
import math
from tools import _structure_source_binding as s


class VerificationError(ValueError):
    pass


def need(value,code):
    if not value:raise VerificationError(code)


def numbers(values,length):
    need(type(values) is list and len(values)==length,'VECTOR_SIZE')
    result=[]
    for x in values:
        need(type(x) is str,'VALUE_FORM')
        try:v=float.fromhex(x)
        except ValueError as exc:raise VerificationError('VALUE_FORM') from exc
        need(math.isfinite(v) and 0<=v<=1 and v.hex()==x,'VALUE_DOMAIN')
        result.append(v)
    return result


def verify(record,binding):
    need(record['version']=='structure-location.comparison.v1' and record['status']=='RECORDING_COMPLETE','STATUS')
    need(record['binding_digest']==s.digest(binding) and record['execution_digest']==s.digest(binding['execution'])
         and record['evaluation_digest']==binding['evaluation_digest'],'ROOT')
    need(len(record['rows'])==14 and len(binding['pairs'])==22,'COMPLETENESS')
    for i,(row,src,payload) in enumerate(zip(record['rows'],binding['execution']['sources'],binding['seal']['sources'],strict=True)):
        need(row['id']==src['id'] and row['frame_index']==src['frame_index'] and row['time']==src['time']
             and row['source_digest']==s.digest(src) and row['payload_sha256']==payload['sha256'],'SOURCE_BINDING')
        raw=numbers(row['raw'],288)
        if row['form'] is None:
            need(row['form_status']=='NO_FORM_ACTIVATION' and row['pose'] is None and row['projection_digest'] is None,'MISSING_FORM')
        else:
            form=numbers(row['form'],144)
            need(row['form_status']=='AVAILABLE' and isinstance(row['pose'],dict),'FORM_BINDING')
            need(abs(math.fsum(form)-1.0)<=1e-12,'FORM_MASS')
            projection=dict(schema='s2lv.private-pose-form-projection.v1',input_values_digest=s.digest(raw),
                pose=row['pose'],form_descriptor=dict(schema='s2lv.form-descriptor.v1',grid_size=12,
                    normalization='UNIT_TOTAL_MASS',values=form))
            need(s.digest(projection)==row['projection_digest'],'PROJECTION_DIGEST')
    need(len(record['primary'])==len(record['direct'])==44,'PAIR_COUNT')
    terms_checked=0;sums=0;expected_work=0
    for k in range(44):
        pair=k//2;arm='RAW288' if k%2==0 else 'FORM144';field='raw' if k%2==0 else 'form'
        q,r=binding['pairs'][pair];length=288 if k%2==0 else 144
        available=record['rows'][q][field] is not None and record['rows'][r][field] is not None
        for bank in ('primary','direct'):
            entry=record[bank][k]
            need(entry['pair']==pair and entry['indices']==[q,r] and entry['arm']==arm,'PAIR_BINDING')
            if not available:
                need(entry['status']=='UNAVAILABLE' and entry['mean'] is None and entry['terms']==[],'MISSING_PAIR')
            else:
                need(entry['status']=='AVAILABLE','PAIR_STATUS')
                terms=numbers(entry['terms'],length)
                need((sum(terms)/length).hex()==entry['mean'],'SUM')
                sums+=1;terms_checked+=length;expected_work+=length
        need(record['primary'][k]==record['direct'][k],'DIRECT_MISMATCH')
    need(len(record['exact'])==2,'EXACT_COUNT')
    equalities=0
    for n,pair in enumerate((20,21)):
        q,r=binding['pairs'][pair];entry=record['exact'][n]
        need(entry['pair']==pair,'EXACT_BINDING')
        for field in ('raw','form'):
            a,b=record['rows'][q][field],record['rows'][r][field]
            if a is None or b is None:need(entry[field] is None,'EXACT_MISSING')
            else:
                flags=[]
                for x,y in zip(a,b,strict=True):flags.append(x==y)
                equalities+=len(flags);need(flags==entry[field],'EXACT_FLAGS')
        need(entry['pose_equal']==(record['rows'][q]['pose']==record['rows'][r]['pose']),'POSE_EQUALITY')
    need(record['counts']==dict(receptors=14,projections=14,differences=expected_work,exact_equalities=equalities),'COUNTERS')
    need(terms_checked<=19008 and sums<=88 and equalities<=864,'VERIFY_BUDGET')
    need(len(s.raw(record))<=1048576,'RECORD_LIMIT')
    return dict(status='EVIDENCE_VALID',evaluation_allowed=True,record_digest=s.digest(record),
        work=dict(terms=terms_checked,sums=sums,exact_equalities=equalities),
        repeated_perception=False,repeated_differences=False,
        boundary='Checks stored terms, sums, direct agreement and digests; no RGB/projection reconstruction.')
