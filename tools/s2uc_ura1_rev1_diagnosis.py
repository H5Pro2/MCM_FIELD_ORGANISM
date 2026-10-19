"""Read-only REV1 archive diagnosis. No policies, generators, bootstrap or replay."""
import gc
import hashlib
import json
import struct
import sys
import time
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from tools._s2uc_ura1_delta_fast_decode import Reader
from tools.s2uc_ura1_runtime_qualify import install_job
from tools import _s2uc_hx1_windows as win

ROOT=Path(__file__).resolve().parents[1]
ARC=ROOT/'reports/s2uc/ura1-rev1-comparison-16h-01'
OUT=ROOT/'reports/s2uc/ura1-rev1-diagnosis-20261016-01'
SEAL='f1e703453235ec15fe22cfe9f6b7c41465e1903fc53e505079e9511f8994d762'
REASONS=('NO_ELIGIBLE_CONTEXT','COLD_ONLY','NO_ESTIMATED_IMPROVEMENT','TIED_IMPROVEMENT','SELECTED_BY_ERROR')
CELL=struct.Struct('<QddBBBB4x')
BEGIN=0


def check():
    if time.monotonic()-BEGIN>54000:raise TimeoutError('DIAGNOSIS_DEADLINE')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def raw(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()


def save(name,value):
    data=raw(value)
    used=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    if used+len(data)>2097152:raise ValueError('ADMINISTRATION_LIMIT')
    with (OUT/name).open('xb') as file:file.write(data)


def sequence(reader,root,proof,arm,field):
    digest=hashlib.sha256(b'[');size=1;count=0
    for index,data in enumerate(reader.records(root[arm][field]['$sequence'])):
        check()
        if index:digest.update(b',');size+=1
        digest.update(data);size+=len(data);count+=1
        yield index,json.loads(data),hashlib.sha256(data).hexdigest()
    digest.update(b']');size+=1
    assert dict(bytes=size,count=count,sha256=digest.hexdigest())==proof['collections'][f'/{arm}/{field}']


def hypotheses(forecast):
    result=[]
    for match,h in zip(forecast['receipt']['matches'],forecast['receipt']['hypotheses'],strict=True):
        if h['eligible']:
            result.append(dict(key=[0 if match['role']=='retained' else 1,match['generation'],match['offset']],
                origin=match['ordinals'],offset=match['offset'],ec=h['ec'],ep=h['ep'],delta=h['delta'],ticket=h['ticket']))
    return result


def identity(h):return tuple(h['origin']),h['offset']


def classify(hs):
    warm=[h for h in hs if h['ec'] is not None]
    if not hs:return REASONS[0]
    if not warm:return REASONS[1]
    negatives=[h['ec']-h['ep'] for h in warm if h['ec']<h['ep']]
    if not negatives:return REASONS[2]
    return REASONS[3] if negatives.count(min(negatives))>1 else REASONS[4]


def balance(rows):
    deltas=[F(x['u_error'])-F(x['r_error']) for x in rows]
    return dict(count=len(rows),different=sum(x['different'] for x in rows),better=sum(d<0 for d in deltas),
        worse=sum(d>0 for d in deltas),equal=sum(d==0 for d in deltas),
        gain=str(sum((-d for d in deltas if d<0),F())),harm=str(sum((d for d in deltas if d>0),F())),net=str(-sum(deltas,F())))


def stock(state):
    result={}
    for role,items in ((0,state['stock']['retained']),(1,[state['stock']['candidate']] if state['stock']['candidate'] else [])):
        for item in items:result[tuple(item['ordinals'])]=(role,item['generation'])
    return result


def cells(state):
    result={};bank=bytes.fromhex(state['bank'])
    if not bank:return result
    assert len(bank)==416
    for i in range(6):
        g,ec,ep,role,off,quality,valid=CELL.unpack_from(bank,i*32)
        if valid:result[role,g,off]=[ec,ep]
    return result


def case(number):
    reader=Reader((ARC/f'case-{number:02d}.delta.json.gz').read_bytes())
    root=reader.value(reader.doc['root']);proof=read(ARC/f'case-{number:02d}-capture.json')
    assert root['paired_equal'] and not root['neutral_only']
    forecasts={};outcomes={};checked=[]
    for arm in ('U','R'):
        forecasts[arm]={};outcomes[arm]={}
        for index,value,digest in sequence(reader,root,proof,arm,'forecasts'):
            t=value['index']+1
            forecasts[arm][t]=dict(hs=hypotheses(value),selected=value['selected'],output=value['output'],
                decision=value['receipt']['decision'],position=index,sha256=digest)
        for index,value,digest in sequence(reader,root,proof,arm,'rows'):
            outcomes[arm][value['target']]=dict(error=value['error'],updates=value['updates'],position=index,sha256=digest)
        checked.extend([f'/{arm}/forecasts',f'/{arm}/rows'])
    coldset=set();rows=[];cold=[]
    for t in range(515,640,4):
        u,r=forecasts['U'][t],forecasts['R'][t];ur,rr=outcomes['U'][t],outcomes['R'][t]
        hs=u['hs'];assert hs==r['hs'] and ur['updates']==rr['updates']
        reason=classify(hs);assert reason==u['decision'] and reason in REASONS
        assert (u['selected'] is not None)==(reason==REASONS[4])
        warm=sum(h['ec'] is not None for h in hs)
        warmth='none' if not hs else 'cold' if not warm else 'warm' if warm==len(hs) else 'mixed'
        for h in hs:
            if h['ec'] is None:
                assert h['ep'] is None and h['delta'] is None
                coldset.add(identity(h))
                cold.append(dict(target=t,key=h['key'],origin=h['origin'],offset=h['offset'],forecast_position=u['position']))
        delta=F(ur['error'])-F(rr['error'])
        rows.append(dict(case=number,target=t,reason=reason,outcome='better' if delta<0 else 'worse' if delta>0 else 'equal',
            u_error=ur['error'],r_error=rr['error'],different=u['output']!=r['output'],warm=warmth,eligible=min(2,len(hs)),
            choice='both_persistence' if u['selected'] is None and r['selected'] is None else 'mixed' if (u['selected'] is None)!=(r['selected'] is None) else 'same_context' if u['selected']==r['selected'] else 'different_context',
            selected_u=u['selected'],selected_r=r['selected'],output_u=u['output'][0],output_r=r['output'][0],actual=root['source'][t-1][0],
            hypotheses=hs,forecast_position=u['position'],row_position=ur['position'],forecast_sha256=u['sha256']))
    # Histories are keyed by original frame identity plus offset, not transient role/generation.
    histories={key:dict(appearances=[],feedback=[],events=[],internal=[]) for key in coldset}
    for t,u in forecasts['U'].items():
        if t>640:continue
        updates=outcomes['U'].get(t,{}).get('updates',[])
        for h in u['hs']:
            key=identity(h)
            if key not in histories:continue
            histories[key]['appearances'].append(dict(target=t,key=h['key'],ec=h['ec'],ep=h['ep'],position=u['position']))
            matching=[v for v in updates if v['key']==h['key']]
            assert len(matching)==1
            histories[key]['feedback'].append(dict(target=t,**matching[0],position=outcomes['U'][t]['position']))
    previous={};previous_cells={}
    for index,value,digest in sequence(reader,root,proof,'U','events'):
        state=value['state'];frame=state['accepted'];stage=value['stage']
        if frame>640:continue
        if stage not in ('perception:after','feedback:after'):continue
        current=stock(state);bank=cells(state)
        for key,history in histories.items():
            origin,off=key;prior=previous.get(origin);now=current.get(origin)
            oldcell=previous_cells.get((*prior,off)) if prior else None
            newcell=bank.get((*now,off)) if now else None
            if prior!=now or oldcell!=newcell:
                history['events'].append(dict(position=index,sha256=digest,frame=frame,stage=stage,
                    before_key=None if prior is None else [*prior,off],after_key=None if now is None else [*now,off],
                    before_cell=oldcell,after_cell=newcell))
        previous,previous_cells=current,bank
    checked.append('/U/events')
    # Explicit internal lifecycle witnesses accompany the outer-state transition history.
    for index,value,digest in sequence(reader,root,proof,'U','internal'):
        state=value['state'];frame=state['accepted']
        if frame>640 or value['event']!='return' or value['method'] not in ('close_segment','_promote'):continue
        for key,history in histories.items():
            origin,off=key
            if any(e['frame']==frame and e['before_key']!=e['after_key'] for e in history['events']):
                now=stock(state).get(origin)
                history['internal'].append(dict(position=index,sha256=digest,frame=frame,method=value['method'],key=None if now is None else [*now,off]))
    checked.append('/U/internal')
    cold_records=[]
    for row in cold:
        history=histories[identity(row)];t=row['target']
        prior=[x for x in history['feedback'] if x['target']<t]
        # Feedback with accepted=f belongs to target f+1, after the forecast at f.
        events=[x for x in history['events'] if x['frame']+int(x['stage']=='feedback:after')<t]
        admissions=[x for x in events if x['before_key'] is None and x['after_key'] is not None]
        assert admissions,('COLD_ORIGIN_NOT_FOUND',number,t,row)
        previous_warm=[x for x in events if x['after_cell'] is not None]
        cold_records.append(dict(**row,prior_feedback_count=len(prior),prior_live_feedback_count=sum(x['live'] for x in prior),
            prior_warm_cell_seen=bool(previous_warm),first_admission_frame=admissions[0]['frame'],
            first_admission_position=admissions[0]['position'],age_since_admission_frames=t-1-admissions[0]['frame'],
            lineage_id=','.join(map(str,row['origin']))+':'+str(row['offset'])))
    history_records=[dict(origin=list(origin),offset=off,**history) for (origin,off),history in sorted(histories.items())]
    value=dict(case=number,rows=rows,cold=cold_records,histories=history_records,checked_collections=checked,
               reader_limits=reader.stats,archives_in_memory=1)
    save(f'case-{number:02d}.json',value)
    return value


def main():
    global BEGIN,OUT
    if len(sys.argv)>1:
        if len(sys.argv)!=3 or sys.argv[1]!='--output':raise ValueError('OUTPUT_ARGUMENT')
        OUT=Path(sys.argv[2]).resolve()
        if not OUT.is_relative_to(ROOT/'reports/s2uc') or OUT.is_relative_to(ARC):raise ValueError('OUTPUT_SCOPE')
    BEGIN=time.monotonic();install_job()
    assert sha(ARC/'delivery-closure.json')==SEAL
    closure=read(ARC/'delivery-closure.json')
    bindings={}
    for name,item in closure['files'].items():
        path=(ARC/name).resolve();assert path.is_relative_to(ARC)
        assert path.stat().st_size==item['bytes'] and sha(path)==item['sha256']
        bindings[str(path.relative_to(ROOT)).replace('\\','/')]=item['sha256']
    OUT.mkdir(exist_ok=False)
    bindings[str((ARC/'delivery-closure.json').relative_to(ROOT)).replace('\\','/')]=SEAL
    for path in (Path(__file__),ROOT/'tools/_s2uc_ura1_delta_fast_decode.py',ROOT/'tools/_s2uc_hx1_windows.py',ROOT/'tools/s2uc_ura1_runtime_qualify.py',ROOT/'tools/_s2uc_multi_error.py'):
        bindings[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path)
    save('bindings.json',dict(files=bindings,input_delivery_sha256=SEAL,scope='Q129-160 only; earlier stored lifecycle is provenance',
        example_rule='first case ascending, then target ascending, for each reason and outcome; absent combinations explicit'))
    allrows=[];cold=[];history=[];case_meta=[]
    for number in range(1,33):
        value=case(number);allrows.extend(value['rows'])
        cold.extend(dict(case=number,**x) for x in value['cold'])
        history.extend(dict(case=number,**x) for x in value['histories'])
        case_meta.append(dict(case=number,reader_limits=value['reader_limits'],collections=value['checked_collections']))
        del value;gc.collect()
        print(json.dumps(dict(completed_archives=number,seconds=round(time.monotonic()-BEGIN,3))),flush=True)
    assert len(allrows)==1024 and len({(x['case'],x['target']) for x in allrows})==1024
    total=balance(allrows)
    assert total==dict(count=1024,different=418,better=222,worse=196,equal=606,gain='303/4',harm='247/4',net='14')
    stats=read(ARC/'statistics.json');assert stats['primary']['verdict']=='INCONCLUSIVE'
    expected=stats['secondary'][0]
    for key in ('count','better','worse','equal','gain','harm','net'):assert total[key]==expected[key]
    groups=[];examples=[]
    for reason in REASONS:
        selected=[x for x in allrows if x['reason']==reason]
        groups.append(dict(reason=reason,all=balance(selected),different=balance([x for x in selected if x['different']])))
        for direction in ('better','worse','equal'):
            candidates=[x for x in selected if x['outcome']==direction]
            examples.append(dict(reason=reason,outcome=direction,first=None if not candidates else candidates[0]))
    partitions=[]
    for field,labels in [('warm',('none','cold','mixed','warm')),('eligible',(0,1,2)),('choice',('both_persistence','mixed','same_context','different_context'))]:
        for label in labels:
            selected=[x for x in allrows if x[field]==label];actual=balance(selected)
            original=next(x for x in stats['diagnosis'] if x['partition']==field and x['label']==label)
            for key in ('count','better','worse','equal','gain','harm','net'):assert actual[key]==original[key]
            partitions.append(dict(partition=field,label=label,**actual))
    # Cross tables are separate partitions, not extra observations.
    cross=[]
    for reason in REASONS:
        for field in ('warm','eligible'):
            for label in sorted({str(x[field]) for x in allrows}):
                selected=[x for x in allrows if x['reason']==reason and str(x[field])==label]
                if selected:cross.append(dict(reason=reason,partition=field,label=label,**balance(selected)))
    cold_summary=dict(hypothesis_occurrences=len(cold),targets=len({(x['case'],x['target']) for x in cold}),lineages=len(history),
        with_prior_feedback=sum(x['prior_feedback_count']>0 for x in cold),with_prior_live_feedback=sum(x['prior_live_feedback_count']>0 for x in cold),
        with_prior_warm_cell=sum(x['prior_warm_cell_seen'] for x in cold),roles=dict(Counter(str(x['key'][0]) for x in cold)),
        age_frames=dict(Counter(str(x['age_since_admission_frames']) for x in cold)))
    save('result.json',dict(status='PASS_ARCHIVE_DIAGNOSIS',primary_verdict_unchanged='INCONCLUSIVE',total=total,reasons=groups,
         partitions=partitions,cross_tables=cross,cold_summary=cold_summary,case_metadata=case_meta))
    save('examples.json',examples)
    save('cold-index.json',cold)
    for name,digest in bindings.items():assert sha(ROOT/name)==digest
    save('resources.json',dict(seconds=time.monotonic()-BEGIN,job=win.snapshot(),active_process_limit=2,actual_processes=1,
        worker_limit_seconds=54000,total_limit_seconds=57600,max_archives_in_memory=1,admin_limit=2097152,export_limit=67108864,
        no_new_sources=True,no_policy_execution=True,no_alternative_outputs=True,no_bootstrap=True,no_significance_tests=True))
    print(json.dumps(dict(status='PASS',total=total,reasons=groups,cold=cold_summary)),flush=True)


if __name__=='__main__':main()
