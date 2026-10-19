"""Bounded paired checks and envelope in one canonical root traversal.

R is traversed twice, U once: the first R pass supplies its canonical prefix;
the second compares with U. SHA-256 digests cannot be concatenated. No raw spool.
This module has no policy execution; callers supply restartable sequence readers.
"""
import hashlib
import json
import time


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def need(ok,reason):
    if not ok:raise ValueError(reason)


def finish(record,sequences,*,build=False):
    """sequences maps /arm/field to a callable yielding (object, canonical bytes)."""
    n=len(record['source']);need(4<=n<=1024 and n%2==0,'FRAME_COUNT')
    need(record['neutral_only'] and not record['performance_claim'],'SCOPE')
    for arm in ('U','R'):
        part=record[arm]
        need(part['frames']==n and part['cleanup'] and part['reference_equal'],'ARM_COMPLETE')
    digest=hashlib.sha256();size=0;differences=[];counts={};passes={}
    timings=dict(hash_seconds=0.0,pair_check_seconds=0.0)
    def emit(data):
        nonlocal size
        start=time.perf_counter();digest.update(data);size+=len(data)
        timings['hash_seconds']+=time.perf_counter()-start
    def read(path):
        passes[path]=passes.get(path,0)+1
        yield from sequences[path]()
    def compare(field,a,b,ab,bb,i):
        start=time.perf_counter()
        try:
            if field in ('events','internal'):need(ab==bb,'PAIRED_STATE_EVENT:'+str(i))
            elif field=='rows':
                need(a['target']==b['target']==3+2*i,'TARGET_COMPLETENESS')
                need(a['updates']==b['updates'],'PAIRED_FEEDBACK')
            else:
                need(a['index']==b['index']==2+2*i,'FORECAST_COMPLETENESS')
                need(a['originals']==b['originals'],'PAIRED_ORIGINALS')
                for key in ('matches','hypotheses','input_indices','source_intervals','read_revision'):
                    need(a['receipt'][key]==b['receipt'][key],'PAIRED_FORECAST:'+key)
                if a['output']!=b['output'] and a['index']<n:
                    differences.append(dict(target=a['index']+1,U=a['output'],R=b['output'],
                        U_choice=a['selected'],R_choice=b['selected'],originals=a['originals']))
        finally:timings['pair_check_seconds']+=time.perf_counter()-start
    def walk(value,path):
        if path in sequences:
            emit(b'[');count=0
            if path.startswith('/U/'):
                field=path.rsplit('/',1)[1]
                for i,((a,ab),(b,bb)) in enumerate(zip(read(path),read('/R/'+field),strict=True)):
                    compare(field,a,b,ab,bb,i)
                    if count:emit(b',')
                    emit(ab);count+=1
                need(count==counts['/R/'+field],'PAIRED_EVENT_COUNT')
                if field=='rows':need(count==n//2-1,'TARGET_COMPLETENESS')
                if field=='forecasts':need(count==n//2,'FORECAST_COMPLETENESS')
            else:
                for _,data in read(path):
                    if count:emit(b',')
                    emit(data);count+=1
            counts[path]=count;emit(b']');return
        if path=='/differences':
            if build:record['differences']=differences;value=differences
            else:need(canonical(value)==canonical(differences),'DIAGNOSIS_EQUAL')
        if type(value) is dict:
            emit(b'{')
            for i,key in enumerate(sorted(value)):
                if i:emit(b',')
                emit(canonical(key));emit(b':');walk(value[key],path+'/'+key)
            emit(b'}')
        elif type(value) in (list,tuple):emit(canonical(value))
        else:emit(canonical(value))
    walk(record,'');emit(b'\n')
    need(record['paired_equal'],'PAIRED_FLAG')
    for arm in ('U','R'):need(record[arm]['censored_target']==n+1,'CENSORED_TARGET')
    return dict(original_bytes=size,original_sha256=digest.hexdigest()),dict(
        counts=counts,passes=passes,paired_equal=True,diagnosis_equal=True,**timings)


def live_sequences(record):
    from tools._s2uc_ura1_capture_integrity import canonical as capture_canonical
    def iterate(seq):
        for item in seq:yield item,capture_canonical(item)
    return {'/'+a+'/'+f:lambda seq=record[a][f]:iterate(seq)
            for a in ('U','R') for f in ('events','internal','forecasts','rows')}


def archive_sequences(reader,record):
    def iterate(number):
        for data in reader.records(number):yield json.loads(data),data
    return {'/'+a+'/'+f:lambda number=record[a][f]['$sequence']:iterate(number)
            for a in ('U','R') for f in ('events','internal','forecasts','rows')}
