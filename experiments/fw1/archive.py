"""Independent FW1 archive semantics; no productive reset or observer imports."""
import hashlib,json,struct
from tools._s2uc_ura1_delta_fast_decode import Reader,verify as integrity
from tools._s2uc_er1_stock_structural import stock_equal
from .archive_reference import Reference

def raw(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def check(ok,reason):
    if not ok:raise ValueError(reason)
def stock_digest(events):
    h=hashlib.sha256()
    for e in events:
        h.update(raw(dict(stage=e['stage'],state={k:v for k,v in e['state'].items() if k!='bank'})))
    return h.hexdigest()

def verify(blob,proof,expected):
    checked=integrity(blob,proof,expected);reader=Reader(blob);root=reader.value(reader.doc['root'])
    check(root['entry_revision']=='FW1_V1' and root['neutral_only'] is True,'ARCHIVE_SCOPE')
    source=root['source'];check(0<len(source)<=128 and len(source)%4==0,'ARCHIVE_FRAMES')
    def records(ref):return (json.loads(x) for x in reader.records(ref['$sequence']))
    digests={};resets={}
    for mode in ('KEEP','RESET'):
        arm=root[mode];digests[mode]=stock_digest(records(arm['events']))
        boundaries=(e['state'] for e in records(arm['events']) if e['stage']=='perception:after')
        forecasts=iter(records(arm['forecasts']));rows=iter(records(arm['rows']));ref=Reference(mode)
        for i,v in enumerate(source,1):
            if ref.pending:
                f=ref.feedback(i,v)
                check(raw(next(rows))==raw(dict(target=i,error=f['error'],updates=f['updates'])),'ARCHIVE_FEEDBACK')
            f=ref.perceive(i,v);state=next(boundaries)
            check(state['accepted']==i and stock_equal(state['stock'],ref.stock.snapshot()),'ARCHIVE_STOCK')
            bank=bytes.fromhex(state['bank']);check(len(bank)==416,'ARCHIVE_BANK')
            cells={}
            for slot in range(6):
                g,ec,ep,role,off,q,valid=struct.unpack_from('<QddBBBB4x',bank,slot*32)
                check(valid in (0,1),'ARCHIVE_VALID')
                if valid:
                    check(q==0 and (role,g,off) not in cells,'ARCHIVE_CELL_KEY')
                    cells[(role,g,off)]=(ec,ep)
            check(cells==ref.cells,'ARCHIVE_CELLS')
            if f:
                actual=next(forecasts);check(actual['index']==i,'ARCHIVE_FORECAST_INDEX')
                check(raw(actual['selected'])==raw(f['chosen']) and actual['output']==list(f['output']),'ARCHIVE_OUTPUT')
                receipt=actual['receipt'];check(receipt['decision']==f['decision'],'ARCHIVE_DECISION')
                matches=[dict(key=[{'retained':0,'candidate':1}[m['role']],m['generation'],m['offset']],ordinals=m['ordinals'],factors=m['factors']) for m in receipt['matches']]
                check(raw(matches)==raw(f['matches']),'ARCHIVE_MATCHES')
                hs=[h for h in receipt['hypotheses'] if h['eligible']]
                check(len(hs)==len(f['hypotheses']),'ARCHIVE_TICKETS')
                for j,(h,want) in enumerate(zip(hs,f['hypotheses'],strict=True)):
                    check(h['ticket']==j and (None if h['ec'] is None else (h['ec'],h['ep']))==want['before'],'ARCHIVE_FROZEN_ERRORS')
                    g,role,off,q,_=struct.unpack_from('<QBBBB4x',bank,208+16*j)
                    check((role,g,off)==want['key'] and q==0,'ARCHIVE_FROZEN_KEY')
                    check(state['frozen'][j]['ordinal']==want['original'] and state['frozen'][j]['values']==list(want['values']),'ARCHIVE_FROZEN_ORIGINAL')
                check(state['pframe']['values']==list(f['persistence']),'ARCHIVE_PERSISTENCE')
                check(actual['originals']==[dict(key=list(h['key']),ordinal=h['original']) for h in f['hypotheses']],'ARCHIVE_ORIGINALS')
        check(next(rows,None) is None and next(forecasts,None) is None and next(boundaries,None) is None,'ARCHIVE_COUNTS')
        check(root[mode]['resets']==ref.resets,'ARCHIVE_RESETS');resets[mode]=ref.resets
        ref.finish();check(arm['cleanup'],'ARCHIVE_CLEANUP')
    check(digests['KEEP']==digests['RESET'],'PAIR_STOCK_IDENTITY')
    return checked|dict(fw1_reference_equal=True,stock_digest=digests['KEEP'],resets=resets)
