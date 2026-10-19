"""ER1 admitted archive checks: capture integrity plus independent semantic replay."""
import json,struct
from tools._s2uc_ura1_delta_fast_decode import Reader,verify as integrity
from tools._s2uc_er1_reference import Reference
from tools._s2uc_er1_run_observer import compare

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def check(ok,reason):
    if not ok:raise ValueError(reason)
def verify(blob,proof,expected):
    report=integrity(blob,proof,expected);reader=Reader(blob)
    def expand(x):
        if isinstance(x,dict):
            if set(x)=={'$sequence'}:return [json.loads(v) for v in reader.records(x['$sequence'])]
            return {k:expand(v) for k,v in x.items()}
        if isinstance(x,list):return [expand(v) for v in x]
        return x
    record=reader.value(reader.doc['root'])
    # Decode internal event streams only in the integrity pass; retain only
    # the small semantic boundary projection for independent reconstruction.
    def boundaries(sequence):
        for encoded in reader.records(sequence):
            event=json.loads(encoded)
            if event['stage']=='perception:after':yield event
    for mode in ('E','F'):
        arm=record[mode]
        arm['events']=boundaries(arm['events']['$sequence'])
        for key in ('forecasts','rows'):arm[key]=expand(arm[key])
    record['observer']=expand(record['observer'])
    check(0<len(record['source'])<=128 if record['neutral_only'] else len(record['source'])==1024,'ARCHIVE_SCOPE')
    for mode in ('E','F'):
        ref=Reference(mode);arm=record[mode];forecasts=iter(arm['forecasts']);rows=iter(arm['rows'])
        after=iter(arm['events']);blocks=[]
        for i,v in enumerate(record['source'],1):
            if ref.pending:
                feedback=ref.feedback(i,v)
                check(canonical(next(rows))==canonical(dict(target=i,error=feedback['error'],updates=feedback['updates'])),'ARCHIVE_FEEDBACK')
            forecast=ref.perceive(i,v)
            boundary=next(after);state=boundary['state']
            if i%4==0:blocks.append(dict(stage='perception:after',state=dict(stock=state['stock'],accepted=i)))
            check(canonical(state['stock'])==canonical(ref.stock.snapshot()),'ARCHIVE_STOCK')
            bank=bytes.fromhex(state['bank']);check(len(bank)==416,'ARCHIVE_BANK_SIZE')
            cells={}
            for slot in range(6):
                generation,ec,ep,role,offset,quality,valid=struct.unpack_from('<QddBBBB4x',bank,slot*32)
                if valid:cells[(role,generation,offset)]=(ec,ep)
            check(cells==ref.cells,'ARCHIVE_CELLS')
            if forecast:
                actual=next(forecasts)
                check(canonical(actual['selected'])==canonical(forecast['chosen']),'ARCHIVE_CHOICE')
                check(actual['output']==list(forecast['output']),'ARCHIVE_OUTPUT')
                receipt=actual['receipt']
                check(receipt['decision']==forecast['decision'],'ARCHIVE_DECISION')
                matches=[dict(key=[{'retained':0,'candidate':1}[m['role']],m['generation'],m['offset']],ordinals=m['ordinals'],factors=m['factors']) for m in receipt['matches']]
                check(canonical(matches)==canonical(forecast['matches']),'ARCHIVE_MATCHES')
                eligible=[h for h in receipt['hypotheses'] if h['eligible']]
                check(len(eligible)==len(forecast['hypotheses']),'ARCHIVE_ELIGIBILITY')
                for number,(h,expected_h) in enumerate(zip(eligible,forecast['hypotheses'],strict=True)):
                    check((None if h['ec'] is None else (h['ec'],h['ep']))==expected_h['before'] and h['ticket']==number,'ARCHIVE_PRE_FEEDBACK')
                check(actual['originals']==[dict(key=list(h['key']),ordinal=h['original']) for h in forecast['hypotheses']],'ARCHIVE_ORIGINAL')
        check(next(rows,None) is None and next(forecasts,None) is None and next(after,None) is None,'ARCHIVE_COUNTS')
        ref.finish();check(arm['cleanup'],'ARCHIVE_CLEANUP');arm['events']=blocks
    check(canonical(record['observer'])==canonical(compare(record['E'],record['F'])),'ARCHIVE_OBSERVER')
    from tools._s2uc_er1_run_mechanisms import witnesses
    check(canonical(expand(record['mechanisms']))==canonical(witnesses(record['observer'],record['source'])),'ARCHIVE_MECHANISMS')
    return report|dict(er1_reference_equal=True)
