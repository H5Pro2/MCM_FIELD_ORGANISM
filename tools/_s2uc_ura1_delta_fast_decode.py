"""Independent incremental-size delta decoder; unchanged wire format and guards."""
import gzip
import hashlib
import io
import json


def need(ok,reason):
    if not ok:raise ValueError(reason)
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


class Reader:
    def __init__(self,blob):
        need(len(blob)<=524288,'GZIP_LIMIT')
        with gzip.GzipFile(fileobj=io.BytesIO(blob)) as source:data=source.read(4194305)
        need(len(data)<=4194304,'ENCODED_LIMIT')
        def unique(pairs):
            result={}
            for key,value in pairs:
                need(key not in result,'DUPLICATE_KEY');result[key]=value
            return result
        self.doc=json.loads(data,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('NONFINITE')))
        d=self.doc
        need(set(d)=={'format','values','paths','deltas','sequences','root','original_bytes','original_sha256'},'ENVELOPE')
        need(d['format']=='URA1_STATE_DELTA_V1','FORMAT')
        self.values=d['values'];self.paths=d['paths'];self.deltas=d['deltas'];self.sequences=d['sequences']
        need(all(type(x) is list for x in (self.values,self.paths,self.deltas,self.sequences)),'TABLES')
        need(len(self.values)+len(self.paths)+len(self.deltas)<=65536 and len(self.sequences)<=16,'TABLE_LIMIT')
        sizes=[];depths=[];edges=1;dictionary=0
        for i,node in enumerate(self.values):
            need(type(node) is list and len(node)==2,'VALUE_NODE');tag,body=node;refs=[]
            if tag=='scalar':
                need(body is None or type(body) in (str,int,float,bool),'SCALAR');size=len(canonical(body))
            elif tag=='array':
                need(type(body) is list,'ARRAY');refs=body;size=2+max(0,len(body)-1)
            elif tag=='object':
                need(type(body) is list,'OBJECT');keys=[];size=2+max(0,len(body)-1)
                for pair in body:
                    need(type(pair) is list and len(pair)==2 and type(pair[0]) is str,'MEMBER')
                    keys.append(pair[0]);refs.append(pair[1]);size+=len(canonical(pair[0]))+1
                need(keys==sorted(set(keys)),'KEYS')
            else:raise ValueError('VALUE_TAG')
            need(all(type(x) is int and 0<=x<i for x in refs),'VALUE_REFERENCE')
            size+=sum(sizes[x] for x in refs);depth=1+max((depths[x] for x in refs),default=0)
            need(size<=4194304 and depth<=128,'VALUE_EXPANSION')
            sizes.append(size);depths.append(depth);edges+=len(refs);dictionary+=len(canonical(node))
        self.sizes=sizes
        need(type(d['root']) is int and 0<=d['root']<len(self.values),'ROOT')
        for path in self.paths:
            need(type(path) is list and len(path)<=128 and all(type(k) in (str,int) for k in path),'PATH')
            dictionary+=len(canonical(path))
        def value_ref(ref):need(type(ref) is int and 0<=ref<len(self.values),'VALUE_REFERENCE')
        for changes in self.deltas:
            need(type(changes) is list,'CHANGES');dictionary+=len(canonical(changes))
            for op in changes:
                need(type(op) is list and len(op)>=2 and type(op[0]) is int and 0<=op[0]<len(self.paths),'PATH_REFERENCE')
                tag=op[1];need(type(tag) is int,'OP_TAG');edges+=1
                if tag==0:need(len(op)==3,'SET');value_ref(op[2]);edges+=1
                elif tag==1:need(len(op)==2 and self.paths[op[0]],'DELETE')
                elif tag==2:
                    need(len(op)==3 and type(op[2]) is list and op[2],'TEXT_PATCH')
                    previous=-1
                    for span in op[2]:
                        need(type(span) is list and len(span)==2 and type(span[0]) is int and span[0]>previous,'TEXT_SPAN')
                        value_ref(span[1]);value=self.values[span[1]]
                        need(value[0]=='scalar' and type(value[1]) is str and len(value[1])>0,'TEXT_VALUE')
                        previous=span[0]+len(value[1])-1;edges+=1
                else:raise ValueError('OP_TAG')
        indices=0
        for seq in self.sequences:
            need(type(seq) is list and len(seq)==2 and type(seq[0]) is int and type(seq[1]) is list,'SEQUENCE')
            if seq[0]==-1:need(not seq[1],'EMPTY_SEQUENCE')
            else:value_ref(seq[0]);need(sizes[seq[0]]+1<=262144,'INITIAL_SIZE');edges+=1;indices+=1
            need(all(type(x) is int and 0<=x<len(self.deltas) for x in seq[1]),'DELTA_REFERENCE')
            indices+=len(seq[1]);edges+=len(seq[1])
        need(indices<=65536 and edges<=262144 and dictionary<=4194304,'MANAGEMENT_LIMIT')
        self.stats=dict(encoded_bytes=len(data),gzip_bytes=len(blob),dictionary_bytes=dictionary,
                        table_entries=len(self.values)+len(self.paths)+len(self.deltas),reference_edges=edges,record_indices=indices)
    def value(self,ref):
        tag,body=self.values[ref]
        if tag=='scalar':return body
        if tag=='array':return [self.value(x) for x in body]
        return {k:self.value(x) for k,x in body}
    def records(self,number,observer=None):
        need(type(number) is int and 0<=number<len(self.sequences),'SEQUENCE_REFERENCE')
        initial,steps=self.sequences[number]
        if initial==-1:return
        state=self.value(initial);size=self.sizes[initial]
        data=canonical(state);need(len(data)==size,"SIZE_ACCOUNTING");yield data
        for step in steps:
            for op in self.deltas[step]:
                path=self.paths[op[0]];tag=op[1];parent=state
                for key in path[:-1]:
                    need((type(parent) is dict and type(key) is str and key in parent) or
                         (type(parent) is list and type(key) is int and 0<=key<len(parent)),'PATH_TRAVERSAL')
                    parent=parent[key]
                if path:
                    key=path[-1]
                    need((type(parent) is dict and type(key) is str) or
                         (type(parent) is list and type(key) is int and 0<=key<len(parent)),'PATH_TARGET')
                    if tag!=0:need(type(parent) is list or key in parent,'MISSING_TARGET')
                if tag==0:
                    need(self.sizes[op[2]]+1<=262144,'REPLACEMENT_SIZE');new=self.value(op[2])
                    if not path:size=self.sizes[op[2]];state=new
                    elif type(parent) is dict and key not in parent:
                        size+=len(canonical(key))+1+self.sizes[op[2]]+int(bool(parent));parent[key]=new
                    else:
                        size+=self.sizes[op[2]]-len(canonical(parent[key]));parent[key]=new
                elif tag==1:
                    need(type(parent) is dict,'DELETE_OBJECT_ONLY')
                    size-=len(canonical(key))+1+len(canonical(parent[key]))+int(len(parent)>1)
                    del parent[key]
                else:
                    text=parent[key] if path else state;need(type(text) is str,'TEXT_TARGET')
                    for start,ref in op[2]:
                        value=self.values[ref][1];need(start+len(value)<=len(text),'TEXT_RANGE')
                        size+=len(canonical(value))-len(canonical(text[start:start+len(value)]))
                        text=text[:start]+value+text[start+len(value):]
                    if path:parent[key]=text
                    else:state=text
                if observer:observer(state,size)
                need(size+1<=262144,'RECORD_LIMIT')
            data=canonical(state);need(len(data)==size,'SIZE_ACCOUNTING');yield data


def verify(blob,proof,expected=None,sink=None):
    reader=Reader(blob);doc=reader.doc;anchors=proof['collections']
    need(proof['format']=='URA1_CAPTURE_ANCHORS_V1' and len(anchors)<=16,'ANCHORS')
    full=hashlib.sha256();fold=hashlib.sha256();count=0;seen={};sequences=set()
    def emit(data,folded=True):
        nonlocal count
        count+=len(data);need(count<=doc['original_bytes'],'EXPANSION_LENGTH');full.update(data)
        if folded:fold.update(data)
        if sink:sink(data)
    def walk(value,path):
        if path in anchors:
            need(type(value) is dict and set(value)=={'$sequence'},'SEQUENCE_PLACEHOLDER')
            number=value['$sequence'];need(number not in sequences,'SEQUENCE_REUSE');sequences.add(number)
            digest=hashlib.sha256(b'[');size=1;records=0;emit(b'[',False)
            for data in reader.records(number):
                if records:digest.update(b',');size+=1;emit(b',',False)
                digest.update(data);size+=len(data);records+=1;emit(data,False)
            digest.update(b']');size+=1;emit(b']',False)
            actual=dict(sha256=digest.hexdigest(),bytes=size,count=records)
            need(actual==anchors[path],'CAPTURE_ANCHOR:'+path);seen[path]=actual
            fold.update(canonical({'$capture':actual}));return
        if type(value) is dict:
            emit(b'{')
            for i,key in enumerate(sorted(value)):
                if i:emit(b',')
                emit(canonical(key));emit(b':');walk(value[key],path+'/'+key)
            emit(b'}')
        elif type(value) is list:
            emit(b'[')
            for i,item in enumerate(value):
                if i:emit(b',')
                walk(item,path+'/'+str(i))
            emit(b']')
        else:emit(canonical(value))
    walk(reader.value(doc['root']),'');emit(b'\n')
    need(set(seen)==set(anchors) and len(sequences)==len(reader.sequences),'COLLECTION_COMPLETENESS')
    need(fold.hexdigest()==proof['folded_sha256'],'CAPTURE_SKELETON')
    need(count==doc['original_bytes'] and full.hexdigest()==doc['original_sha256'],'ENVELOPE_HASH')
    if expected:need(count==expected['original_bytes'] and full.hexdigest()==expected['original_sha256'],'PRIOR_RECORD_HASH')
    return dict(status='PASS_DELTA_INTEGRITY',reconstructed_bytes=count,reconstructed_sha256=full.hexdigest(),
                collections=seen,**reader.stats)
