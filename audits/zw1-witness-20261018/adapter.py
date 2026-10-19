"""ZW1 envelope binding and descriptive counts; qualified semantic core unchanged."""
import hashlib
import json
from collections import Counter

def need(ok, code):
    if not ok:
        raise ValueError(code)

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def bind_case(number, entry, material, root, summary, receipt, source_sha):
    need(type(number) is int and 1<=number<=32, 'CASE_NUMBER')
    pair=(number+1)//2; label='A' if number%2 else 'B'
    need(entry['pair']==pair and entry['condition']==label, 'MANIFEST_PAIR_CONDITION')
    need(entry['path']==f'pair-{pair:02d}-{label}-source.json', 'SOURCE_PATH')
    need(entry['sha256']==source_sha, 'SOURCE_HASH')
    need(summary['replicate']==number and summary['pair']==pair and summary['condition']==label
         and summary['orientation']==(pair-1)%2, 'SUMMARY_PAIR_CONDITION')
    need(receipt['pair']==pair and receipt['orientation']==(pair-1)%2 and receipt['complete'] is True
         and set(receipt['conditions'])=={'A','B'}, 'RECEIPT_PAIR')
    condition=receipt['conditions'][label]
    need(condition['pair']==pair and condition['condition']==label and condition['complete'] is True
         and condition['cleanup'] is True and condition['integrity']=='PASS_DELTA_INTEGRITY', 'RECEIPT_CONDITION')
    need(condition['targets']==list(range(3,1024,2)), 'TARGETS')
    need(root['entry_revision']=='ZW1_V1' and root['neutral_only'] is False, 'ARCHIVE_REVISION')
    need(set(material)=={'catalog','ids'} and len(material['ids'])==1024, 'MATERIAL_SCOPE')
    need(all(type(i) is int and 0<=i<len(material['catalog']) for i in material['ids']), 'MATERIAL_INDEX')
    source=[material['catalog'][i] for i in material['ids']]
    need(root['source']==source, 'ARCHIVE_SOURCE')
    need(all(len(x)==48 for x in source), 'SOURCE_DIMENSION')
    return pair,label,source,condition

def descriptive(records):
    result={}
    for arm in ('E','F'):
        warm=[x for x in records if x['keeper']==arm and x['stage']=='warm_use']
        targets={};multiplicity=Counter(x['target'] for x in warm)
        for x in warm:
            value=(x['keeper_error'],x['other_error'])
            need(x['target'] not in targets or targets[x['target']]==value,'TARGET_ERROR_CONFLICT')
            targets[x['target']]=value
        result[arm]=dict(retention_events=sum(x['keeper']==arm and x['stage']=='retention' for x in records),
            warm_records=len(warm),unique_warm_targets=len(targets),
            unique_gain_targets=sum(a<b for a,b in targets.values()),
            unique_harm_targets=sum(a>b for a,b in targets.values()),
            unique_equal_targets=sum(a==b for a,b in targets.values()),
            event_gains=sum(x['keeper_error']<x['other_error'] for x in warm),
            event_harms=sum(x['keeper_error']>x['other_error'] for x in warm),
            gain_error_sum=sum(b-a for a,b in targets.values() if a<b),
            harm_error_sum=sum(a-b for a,b in targets.values() if a>b),
            multi_assigned_targets={str(k):v for k,v in multiplicity.items() if v>1})
    return result

def examples(records):
    """First enumerated instance per arm/type; illustrative, never a sample for counts."""
    answer={}
    for arm in ('E','F'):
        for kind in ('retention','gain','harm','equal'):
            for x in records:
                if x['keeper']!=arm:continue
                match=x['stage']=='retention' if kind=='retention' else x['stage']=='warm_use' and (
                    x['keeper_error']<x['other_error'] if kind=='gain' else
                    x['keeper_error']>x['other_error'] if kind=='harm' else x['keeper_error']==x['other_error'])
                if match:
                    value={k:v for k,v in x.items() if k!='output'}
                    if 'output' in x:value['output_sha256']=digest(x['output'])
                    answer[arm+'/'+kind]=value;break
    return answer
