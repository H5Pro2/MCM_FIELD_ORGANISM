"""Descriptive archive-only FW1 assignment. Never instantiate a policy/reference."""
import gzip, hashlib, json, math, sys, time
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools._s2uc_ura1_delta_fast_decode import Reader
from tools.s2uc_ura1_runtime_qualify import install_job
from tools._s2uc_hx1_windows import snapshot
SOURCE = ROOT/'reports/s2uc/fw1-comparison-16h-01'
OUT = ROOT/'reports/s2uc/fw1-diagnosis-20261019-02'
PREP = ROOT/'reports/s2uc/fw1-diagnosis-preservation-20261019-01'
WORKFLOW = 'b01b8240-5575-4662-810f-b75dae53266e'
OVERVIEWS = ('README.md','AKTUELLER_FORSCHUNGSWEG.md','docs/README.md')
MANIFEST_SHA = '923a45079a44747c7b09d98e14874fdd435f89eb39fe09d59f396fcfd7520c91'

def need(ok, reason):
    if not ok: raise ValueError(reason)
def read(p): return json.loads(p.read_bytes())
def raw(x): return (json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, data):
    if not isinstance(data,bytes): data=raw(data)
    need(len(data)<=4194304,'WRITE_SIZE')
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f: f.write(data)

def hypotheses(receipt):
    result={}
    for m,h in zip(receipt['matches'],receipt['hypotheses'],strict=True):
        if not h['eligible']: continue
        key=(0 if m['role']=='retained' else 1,m['generation'],m['offset'])
        need(m['role'] in ('retained','candidate') and key not in result,'KEY')
        ec,ep=h['ec'],h['ep']
        need((ec is None)==(ep is None),'HALF_COLD')
        if ec is not None: need(all(math.isfinite(v) for v in (ec,ep)),'NONFINITE')
        result[key]=None if ec is None else (ec,ep)
    return result

def category(a,b):
    need(a.keys()==b.keys(),'HYPOTHESIS_STOCK_MISMATCH')
    if any((a[k] is None)!=(b[k] is None) for k in a): return 1
    if any(a[k]!=b[k] for k in a): return 2
    return 3

def provenance(key,index,resets,updates):
    eligible=[r for r in resets if key[0]==0 and r['generation']==key[1]
              and key[2] in r['offsets'] and r['end']<index]
    if not eligible: return dict(state='NO_PRIOR_DELETION',reset=None,feedback=[])
    reset=max(eligible,key=lambda r:r['end'])
    feedback=[u for u in updates.get(key,[]) if reset['end']<u['target']<index]
    return dict(state='UPDATED' if feedback else 'NOT_YET_UPDATED',reset=reset['end'],feedback=feedback)

def empty(): return dict(targets=0,gains=0,harms=0,ties=0,error_sum=F(0))
def add(b,d):
    b['targets']+=1;b['error_sum']+=d
    b['gains' if d<0 else 'harms' if d>0 else 'ties']+=1
def serial(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
    if isinstance(x,list):return [serial(v) for v in x]
    return x

def verify_history(relocated=False):
    need(sha(SOURCE/'delivery-closure.json')==MANIFEST_SHA,'HISTORICAL_MANIFEST')
    m=read(SOURCE/'delivery-closure.json')
    for name,v in m['files'].items():
        p=SOURCE/name;need(p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],'HISTORY:'+name)
    for name,v in m['external_files'].items():
        p=PREP/name if relocated and name in OVERVIEWS else ROOT/name
        need(p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],'EXTERNAL:'+name)
    return dict(files=len(m['files']),external_files=len(m['external_files']),manifest_sha256=MANIFEST_SHA)

def main():
    started=time.monotonic();install_job()
    need(not OUT.exists(),'EXCLUSIVE_OUTPUT')
    OUT.mkdir(parents=True)
    write(OUT/'start.json',dict(workflow=WORKFLOW,policy=0,references=0,bootstrap=0,archive_decodes_planned=32))
    try:
        history=verify_history()
        for name in OVERVIEWS:
            if not (PREP/name).exists():write(PREP/name,(ROOT/name).read_bytes())
            need((PREP/name).read_bytes()==(ROOT/name).read_bytes(),'SNAPSHOT')
        write(OUT/'historical-verification-before.json',history)
        groups={g:{c:empty() for c in (1,2,3)} for g in ('A','B','ALL')}
        linked={g:{} for g in groups};examples={};peaks={};empty_sets=Counter();multiple=Counter()
        for number in range(1,33):
            need(time.monotonic()-started<54000,'DEADLINE')
            label='A' if number%2 else 'B'
            s=read(SOURCE/f'case-{number:02d}-summary.json')
            need(s['targets']==list(range(3,1024,2)) and s['complete'] and s['stock_equal'],'SUMMARY')
            r=Reader((SOURCE/f'case-{number:02d}.gz').read_bytes());root=r.value(r.doc['root'])
            for k,v in r.stats.items():peaks[k]=max(peaks.get(k,0),v)
            def records(mode,stream):return [json.loads(v) for v in r.records(root[mode][stream]['$sequence'])]
            rows={mode:records(mode,'rows') for mode in ('KEEP','RESET')}
            forecasts={mode:records(mode,'forecasts') for mode in ('KEEP','RESET')}
            need(root['RESET']['resets']==s['resets'],'RESET_METADATA')
            updates={}
            for row in rows['RESET']:
                for u in row['updates']:
                    if u['live']:updates.setdefault(tuple(u['key']),[]).append(dict(target=row['target'],ec=u['ec'],ep=u['ep'],original=u['original']))
            evidence=[]
            need(all(len(rows[m])==511 and len(forecasts[m])==512 for m in rows),'STREAM_LENGTH')
            for i,target in enumerate(s['targets']):
                a,b=(forecasts[m][i] for m in ('KEEP','RESET'))
                need(a['index']==b['index']==target-1,'INDEX')
                for mode in rows:
                    need(rows[mode][i]['target']==target and rows[mode][i]['error']==s[mode][i],'ERROR_SOURCE')
                aa,bb=hypotheses(a['receipt']),hypotheses(b['receipt']);cat=category(aa,bb)
                need(a['receipt']['matches']==b['receipt']['matches'],'MATCH_IDENTITY')
                d=F(rows['KEEP'][i]['error'])-F(rows['RESET'][i]['error'])
                details=[]
                for key in sorted(aa):
                    link=provenance(key,target-1,s['resets'],updates)
                    details.append(dict(key=list(key),keep=aa[key],reset_values=bb[key],different=aa[key]!=bb[key],**link))
                states=sorted({h['state'] for h in details if h['different']})
                signature='+'.join(states) or 'NO_DIFFERENCE'
                for g in (label,'ALL'):
                    add(groups[g][cat],d)
                    add(linked[g].setdefault(str(cat)+':'+signature,empty()),d)
                    if not aa:empty_sets[g]+=1
                    if len(aa)>1:multiple[g]+=1
                record=dict(case=number,pair=(number+1)//2,condition=label,target=target,category=cat,
                            error_keep=rows['KEEP'][i]['error'],error_reset=rows['RESET'][i]['error'],difference=str(d),
                            selected_keep=a['selected'],selected_reset=b['selected'],hypotheses=details,
                            differing_states=states)
                evidence.append(record)
                outcome='gain' if d<0 else 'harm' if d>0 else 'tie'
                example_key=f'{label}/C{cat}/{outcome}/{signature}'
                examples.setdefault(example_key,record)
            data=b''.join(raw(v) for v in evidence)
            need(len(data)<=4194304 and max(map(lambda v:len(raw(v)),evidence))<=262144,'EVIDENCE_SIZE')
            blob=gzip.compress(data,mtime=0);need(len(blob)<=524288,'EVIDENCE_GZIP')
            write(OUT/f'case-{number:02d}.jsonl.gz',blob)
            peaks['evidence_encoded']=max(peaks.get('evidence_encoded',0),len(data))
            peaks['evidence_gzip']=max(peaks.get('evidence_gzip',0),len(blob))
            with (OUT/'progress.jsonl').open('ab') as f:f.write(raw(dict(case=number,targets=len(evidence),seconds=time.monotonic()-started)))
            del r,root,rows,forecasts,evidence,updates
        old=read(SOURCE/'descriptive.json')['groups'];totals={}
        for label in groups:
            total={k:sum(v[k] for v in groups[label].values()) for k in empty()};totals[label]=total
            expected=old[label] if label!='ALL' else {k:old['A'][k]+old['B'][k] for k in ('gains','harms','ties')}
            for k in ('gains','harms','ties'):need(total[k]==expected[k],'CONSERVATION:'+label+k)
            expected_sum=F(old[label]['error_sum']) if label!='ALL' else F(old['A']['error_sum'])+F(old['B']['error_sum'])
            need(total['error_sum']==expected_sum and total['targets']==(16352 if label=='ALL' else 8176),'CONSERVATION_SUM')
        write(OUT/'diagnosis.json',serial(dict(groups=groups,totals=totals,linked=linked,empty_sets=dict(empty_sets),multiple_hypotheses=dict(multiple),conservation='PASS',archive_decodes=32)))
        write(OUT/'examples.json',dict(rule='First in ascending case then target for each condition/category/outcome/differing-state-set; no replacement or cherry picking.',examples=examples))
        write(OUT/'historical-verification-after.json',verify_history())
        job=snapshot();need(job['peak_job_committed_bytes']<=536870912,'JOB_LIMIT')
        write(OUT/'resources.json',dict(seconds=time.monotonic()-started,job=job,actual_processes=1,peaks=peaks,
            policy=0,reference_replays=0,bootstrap=0,new_sources=0,archive_decodes=32,
            exploratory_archive_inspections=1,aborted_attempt_archive_decodes=1,aborted_attempt='fw1-diagnosis-20261019-01: field-name collision before first case output; failure retained',exploratory_note='Before implementation: one bounded case-01 inspection; not an analytical rerun.'))
        write(OUT/'terminal.json',dict(status='DIAGNOSIS_COMPLETE',workflow=WORKFLOW,targets=16352,conservation='PASS'))
        print(json.dumps(serial(dict(groups=groups,linked=linked,empty_sets=dict(empty_sets),multiple=dict(multiple)))))
    except BaseException as exc:
        write(OUT/'failure.json',dict(type=type(exc).__name__,error=str(exc),seconds=time.monotonic()-started))
        raise

if __name__=='__main__':main()
