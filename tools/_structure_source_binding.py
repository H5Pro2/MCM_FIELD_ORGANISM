"""Receptor-free, deterministic RGB source binding."""
import hashlib
import json

VERSION = 'structure-location.sources.v1'
GATE = False


class BindingError(ValueError):
    pass


def need(value, code):
    if not value:
        raise BindingError(code)


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(raw(value)).hexdigest()


def plans():
    sources = []
    rectangles = ([[0,0,480,90],[195,90,285,360]],
                  [[0,0,90,360],[90,135,480,225]])
    for background in ([], [[320,0,400,1080],[0,270,1920,330]]):
        for shape in rectangles:
            for x,y in ((640,405),(720,405),(640,465)):
                sources.append(dict(background=background, foreground=[
                    [a+x,b+y,c+x,e+y] for a,b,c,e in shape]))
    sources += [json.loads(raw(sources[0])), json.loads(raw(sources[6]))]
    execution = dict(version=VERSION, width=1920, height=1080, format='RGB8',
        base=[24]*3, background_color=[48]*3, foreground_color=[216]*3,
        profile='visual.grid12x8.channels3.source1920x1080.v1',
        sources=[dict(id=f'q{i+1:02}', frame_index=i, time=[i,30], recipe=r)
                 for i,r in enumerate(sources)])
    pairs=[]; criteria=[]
    for base in (0,6):
        for role in (0,3):
            anchor=base+role; other=base+3-role
            within=[]; between=[]
            for target in (anchor+1,anchor+2,other,other+1,other+2):
                pairs.append([anchor,target])
                (within if target in (anchor+1,anchor+2) else between).append(len(pairs)-1)
            for arm in ('RAW288','FORM144'):
                criteria.append(dict(arm=arm,kind='GLOBAL_STRICT',within=within,between=between))
                for j in (0,1):
                    criteria.append(dict(arm=arm,kind='PAIRED_STRICT',within=[within[j]],between=[between[j+1]]))
    pairs += [[0,12],[6,13]]
    evaluation=dict(pairs=pairs,criteria=criteria,exact_pairs=[20,21],
        roles=[dict(source=i,background=i//6,form=(i%6)//3,position=i%3) for i in range(12)],
        work=dict(differences=19008,verification_terms=19008,verification_sums=88,
                  criteria=24,exact_equalities=1728,receptor_calls=14,projection_calls=14))
    return execution,evaluation


def render(recipe, width, height):
    need(type(width) is int and type(height) is int and 0<width<=1920 and 0<height<=1080,'GEOMETRY')
    need(set(recipe)=={'background','foreground'},'RECIPE')
    data=bytearray([24])*(width*height*3)
    for key,color in (('background',48),('foreground',216)):
        for rect in recipe[key]:
            need(len(rect)==4 and all(type(v) is int for v in rect),'RECTANGLE')
            a,b,c,d=rect
            need(0<=a<c<=width and 0<=b<d<=height,'RECTANGLE')
            row=bytes([color])*((c-a)*3)
            for y in range(b,d):
                data[(y*width+a)*3:(y*width+c)*3]=row
    return data


def budget(sources, metadata, evidence, verification):
    parts=dict(sources=sources,metadata=metadata,evidence=evidence,verification=verification)
    violations=[k for k,limit in (('metadata',65536),('evidence',1048576),('verification',262144)) if parts[k]>limit]
    total=sum(parts.values())
    if total>4194304: violations.append('TOTAL')
    return dict(parts=parts,total=total,violations=violations)


def verify(record, execution, evaluation):
    need(record['execution_digest']==digest(execution) and record['evaluation_digest']==digest(evaluation),'ROOT')
    need(len(record['sources'])==14,'COUNT')
    for source,proof in zip(execution['sources'],record['sources'],strict=True):
        need(proof['id']==source['id'] and proof['source_digest']==digest(source),'SOURCE')
        need(proof['bytes']==6220800 and len(proof['sha256'])==64 and all(c in '0123456789abcdef' for c in proof['sha256']),'PAYLOAD_BINDING')
    groups={}
    for p in record['sources']: groups.setdefault(p['sha256'],[]).append(p['id'])
    need(record['collisions']==[v for v in groups.values() if len(v)>1],'COLLISIONS')
    need(record['sources'][0]['sha256']==record['sources'][12]['sha256'] and record['sources'][6]['sha256']==record['sources'][13]['sha256'],'EXACT')
    need(record['generated']==14,'COUNTER')
    return dict(status='BINDING_VALID',record_digest=digest(record),payload_regeneration=False,
                numerical_generation_reconstruction=False)
