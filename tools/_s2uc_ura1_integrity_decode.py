"""Independent DAG reconstruction checked against capture-time array anchors."""
import gzip
import hashlib
import io
import json


def require(ok,reason):
    if not ok:raise ValueError(reason)


def verify(blob,proof):
    require(len(blob)<=524288,'GZIP_LIMIT')
    with gzip.GzipFile(fileobj=io.BytesIO(blob)) as source:encoded=source.read(4194305)
    require(len(encoded)<=4194304,'ENCODED_LIMIT')
    def unique(pairs):
        obj={}
        for key,value in pairs:
            require(key not in obj,'DUPLICATE_KEY');obj[key]=value
        return obj
    doc=json.loads(encoded,object_pairs_hook=unique,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('NONFINITE')))
    require(set(doc)=={'format','nodes','root','original_bytes','original_sha256'},'ENVELOPE')
    require(doc['format']=='URA1_JSON_DAG_V1' and proof['format']=='URA1_CAPTURE_ANCHORS_V1','FORMAT')
    nodes=doc['nodes'];depths=[]
    require(type(nodes) is list and 0<len(nodes)<=65536,'NODES')
    require(type(doc['root']) is int and doc['root']==len(nodes)-1,'ROOT')
    edges=0
    for index,node in enumerate(nodes):
        require(type(node) is list and len(node)==2,'NODE')
        tag,body=node;refs=[]
        if tag=='object':
            require(type(body) is list,'OBJECT');keys=[]
            for member in body:
                require(type(member) is list and len(member)==2 and type(member[0]) is str,'MEMBER')
                keys.append(member[0]);refs.append(member[1])
            require(keys==sorted(set(keys)),'KEY_ORDER')
        elif tag=='array':require(type(body) is list,'ARRAY');refs=body
        elif tag=='scalar':require(body is None or type(body) in (str,int,float,bool),'SCALAR')
        else:raise ValueError('TAG')
        edges+=len(refs);require(edges<=262144,'EDGE_LIMIT')
        require(all(type(ref) is int and 0<=ref<index for ref in refs),'REFERENCE')
        depth=1+max((depths[ref] for ref in refs),default=0)
        require(depth<=128,'DEPTH');depths.append(depth)
    anchors=proof['collections'];require(len(anchors)<=16,'ANCHOR_COUNT')
    full=hashlib.sha256();folded=hashlib.sha256();total=0;current=None;seen={}
    literal=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    def emit(data):
        nonlocal total
        full.update(data);total+=len(data)
        require(total<=doc['original_bytes'],'EXPANSION_LENGTH')
        if current is None:folded.update(data)
        else:current['hash'].update(data);current['bytes']+=len(data)
    def walk(ref,path):
        nonlocal current
        tag,body=nodes[ref];anchored=path in anchors
        if anchored:
            require(current is None and tag=='array','ANCHOR_SHAPE')
            current={'hash':hashlib.sha256(),'bytes':0}
        if tag=='scalar':emit(literal(body))
        elif tag=='array':
            emit(b'[')
            for i,child in enumerate(body):
                if i:emit(b',')
                walk(child,path+'/'+str(i))
            emit(b']')
        else:
            emit(b'{')
            for i,(key,child) in enumerate(body):
                if i:emit(b',')
                emit(literal(key));emit(b':');walk(child,path+'/'+key)
            emit(b'}')
        if anchored:
            actual=dict(sha256=current['hash'].hexdigest(),bytes=current['bytes'],count=len(body))
            require(actual==anchors[path],'CAPTURE_ANCHOR:'+path)
            seen[path]=actual;current=None;folded.update(literal({'$capture':actual}))
    walk(doc['root'],'');emit(b'\n')
    require(set(seen)==set(anchors),'ANCHOR_COMPLETENESS')
    require(folded.hexdigest()==proof['folded_sha256'],'CAPTURE_SKELETON')
    require(total==doc['original_bytes'] and full.hexdigest()==doc['original_sha256'],'ENVELOPE_HASH')
    return dict(status='PASS_CAPTURE_INTEGRITY',collections=seen,reconstructed_bytes=total,
                reconstructed_sha256=full.hexdigest(),folded_sha256=folded.hexdigest(),
                encoded_bytes=len(encoded),gzip_bytes=len(blob))
