"""Fixed prospective B-only diagnostic. No receptor or memory calls."""
import math
from tools import _structure_source_binding as source
from tools import _s2kq_private_partial_cue_retrieval_336 as historical

VERSION='visual-b.exact-or-max32.v1'
TAU=1.0/255.0
resolve_a=historical._resolve_a
decide=historical._decide


class DiagnosticError(ValueError):
    pass


def need(ok,code):
    if not ok:raise DiagnosticError(code)


def validate(cue,slots,rule):
    need(rule in ('EXACT','MAX32_RGB8_STEP'),'RULE')
    need(type(cue) is tuple and len(cue)==32 and len(slots)==4,'SHAPE')
    need(all(type(v) is float and math.isfinite(v) and 0<=v<=1 for v in cue),'VALUES')
    for slot in slots:
        need(set(slot)=={'occupied','support','values'} and type(slot['occupied']) is bool,'SLOT')
        need((not slot['occupied'] and slot['support'] is None and slot['values']==()) or
             (slot['occupied'] and type(slot['support']) is int and 1<=slot['support']<=3
              and type(slot['values']) is tuple and len(slot['values'])==288
              and all(type(v) is float and math.isfinite(v) and 0<=v<=1 for v in slot['values'])),'SLOT_VALUES')


def scan(cue,slots,rule):
    validate(cue,slots,rule);rows=[]
    for n,slot in enumerate(slots):
        ready=slot['occupied'] and slot['support']>=3
        terms=[dict(index=i,difference=abs(cue[i]-slot['values'][i])) for i in range(32)] if ready and rule!='EXACT' else []
        hit=ready and (all(cue[i]==slot['values'][i] for i in range(32)) if rule=='EXACT'
                       else max(t['difference'] for t in terms)<=TAU)
        rows.append(dict(slot=n,eligible=ready,matched=hit,terms=terms))
    return dict(rule=rule,rows=rows,matches=[r['slot'] for r in rows if r['matched']])


def direct(cue,slots,rule):
    validate(cue,slots,rule);records=[];hits=[]
    for n in range(4):
        slot=slots[n];ready=slot['occupied'] and slot['support']>=3
        match=bool(ready);terms=[];largest=0.0
        if ready:
            for i in range(32):
                if rule=='EXACT':
                    if cue[i]!=slot['values'][i]:match=False
                else:
                    delta=cue[i]-slot['values'][i]
                    delta=abs(delta)
                    terms.append(dict(index=i,difference=delta))
                    if delta>largest:largest=delta
            if rule!='EXACT':match=largest<=1.0/255.0
        records.append(dict(slot=n,eligible=ready,matched=match,terms=terms))
        if match:hits.append(n)
    return dict(rule=rule,rows=records,matches=hits)


def classify(reference,alternative,target):
    return dict(retained=bool(target and reference and alternative),lost=bool(target and reference and not alternative),
        gained=bool(target and not reference and alternative),new_false=bool(not target and not reference and alternative),
        prevented_false=bool(not target and reference and not alternative))


def plans():
    execution=dict(version=VERSION,rules=['EXACT','MAX32_RGB8_STEP'],tau_hex=TAU.hex(),indices=list(range(32)),
        frozen_memory_digest='d75c7665327470e58344839a1285156c9d2bb24a252f664e6c70b431827f785a',
        rows=[dict(id=f'vb-{i+1:02}',base=base,level=level,rectangle=rect,
                   window=[26+6*i,27+6*i],time_base=[1,30]) for i,(base,level,rect) in enumerate(
            (('q04',0,False),('q05',0,False),('q06',0,False),('q06',1,False),
             ('q06',-1,False),('q01',0,False),('q06',0,True)))])
    evaluation=dict(version=VERSION,roles=['learned','learned','learned','new_level','new_level','hidden_structure','visible_structure'],
        target=[True,True,True,True,True,False,False],groups=[3,2,1,1],D_zero='ERHALTUNG_NICHT_GEPRUEFT')
    return execution,evaluation


def modify_and_occlude(data,width,height,level,rectangle):
    need(type(width) is int and type(height) is int and 0<width<=1920 and 0<height<=1080,'GEOMETRY')
    need(type(data) is bytearray and len(data)==width*height*3 and width%12==0 and height%8==0,'GEOMETRY')
    need(level in (-1,0,1) and type(rectangle) is bool,'RECIPE')
    if level:
        for i in range(len(data)):
            value=data[i]+level;need(0<=value<=255,'NO_CLIPPING');data[i]=value
    w,h=width//12,height//8
    if rectangle:
        for y in range(h):data[y*width*3:y*width*3+w*3]=bytes([216])*(w*3)
    for y in range(height):
        for x in range(width):
            cell=(y//h)*12+x//w
            for ch in range(3):
                if cell*3+ch>=32:data[(y*width+x)*3+ch]=0


def verify_sources(record,execution,evaluation,environment_digest):
    """Binding-only check; deliberately no generator or scan calls."""
    need(record['execution_digest']==source.digest(execution) and
         record['evaluation_digest']==source.digest(evaluation),'ROOT')
    need(record['environment_binding']==environment_digest,'ENVIRONMENT')
    need(record['generated']==7 and len(record['sources'])==7,'COUNT')
    groups={}
    for row,proof in zip(execution['rows'],record['sources'],strict=True):
        need(proof['id']==row['id'] and proof['source_digest']==source.digest(row),'SOURCE')
        need(proof['original_sha256']==row['original_sha256'],'ORIGINAL_PAYLOAD')
        h=proof['sha256']
        need(proof['bytes']==6220800 and type(h) is str and len(h)==64 and
             all(c in '0123456789abcdef' for c in h),'PAYLOAD_BINDING')
        groups.setdefault(h,[]).append(proof['id'])
    need(record['collisions']==[g for g in groups.values() if len(g)>1],'COLLISIONS')
    need(record['sources'][2]['sha256']==record['sources'][5]['sha256'],'VISIBLE_SOURCE_CONTROL')
    return dict(status='BINDING_VALID',record_digest=source.digest(record),
        payload_regeneration=False,numerical_generation_reconstruction=False,
        receptor_comparison=False)
