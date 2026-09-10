"""Lossless administrative references only; no perception or runtime semantics."""
from copy import deepcopy
from tools import _s2oa_private_runtime_binding as r
from tools import _s2oa_private_event_ids as ids

SCHEMA = "s2oa.administrative-references.v1"
QUAL_ID = "s2oa-compact-reference-qualification-20260910-01"
TEST_COUNT = 16
OLD_RESULT = "9ba20ce38d5c6f19f0f4e19efe00958bfe7e5bab5584ae4098dd56322f42fce8"
REPLACED = {
    "tools/_s2oa_private_main_binding.py": "24869766496df629ee4e2ac4f603bc4ab326ed19a1db61d101c8e73942b83080",
    "tools/_s2oa_private_main_verification.py": "5bd56f70f5f6ca8f83710b2a1b210cb42a833483c3b2ab24f1657ee2d05d2fc5",
}
OWN = ("tools/_s2oa_private_compact_references.py", "tests/test_s2oa_private_compact_references.py",
       "reports/s2oa/qualify_compact_references_once.py", "reports/s2oa/COMPACT_REFERENCE_QUALIFIKATIONSBINDUNG.md")


def pack_group(group,expected_directory):
    directories={row["path"].rsplit("/",1)[0] for row in group.values()}
    r.require(len(directories)==1,"REFERENCE_DIRECTORY_INVALID")
    directory=directories.pop()
    r.require(directory==expected_directory,"REFERENCE_DIRECTORY_INVALID")
    r.require(all(row["path"]==directory+"/"+name for name,row in group.items()),"REFERENCE_NAME_INVALID")
    return dict(files={name:[row["sha256"],row["bytes"]] if "bytes" in row else [row["sha256"]]
        for name,row in group.items()})


def pack(value,manifest):
    x=deepcopy(value)
    r.require("storage" not in x,"ALREADY_COMPACT")
    body={k:v for k,v in x.items() if k!="record_digest"}
    r.require(x["record_digest"]==r.digest(body),"RECORD_DIGEST_INVALID")
    expanded_digest=x["record_digest"]
    p=x["bindings"]
    if p is not None:
        p["admin_files"]=pack_group(p["admin_files"],"reports/s2oa/"+r.admin.RUN_ID)
        for role,qid in (("previous",r.QUAL_ID),("main","s2oa-main-binding-qualification-20260910-01")):
            p["qualifications"][role]=pack_group(p["qualifications"][role],"reports/s2oa/"+qid)
        for role,qid in (("event_ids",ids.QUAL_ID),("correction",QUAL_ID)):
            q=p["qualifications"][role]
            r.require(set(q)=={"qualification_id","files"} and q["qualification_id"]==qid,"REFERENCE_DIRECTORY_INVALID")
            del q["qualification_id"]
        m=p["event_ids"]
        ex=dict(execution_digest=p["execution_digest"],events=[dict(ordinal=n,event_id=f"e{n:02d}") for n in range(1,29)])
        ids.validate(m,ex)
        p["event_ids"]=dict(schema="s2oa.event-id-reference.v1",expanded_digest=m["id_binding_digest"])
    core=x["execution"]
    if core is not None:
        rows=core["binding"]["component_sources"];keys=sorted(manifest)
        r.require(all(type(row) in (list,tuple) and len(row)==2 and manifest.get(row[0])==row[1] for row in rows),"COMPONENT_REFERENCE_INVALID")
        core["binding"]["component_sources"]=dict(schema="s2oa.qualified-source-reference.v1",
            manifest_digest=r.digest(manifest),indices=[keys.index(row[0]) for row in rows],expanded_digest=r.digest(rows))
    x["storage"]=dict(schema=SCHEMA,expanded_digest=expanded_digest)
    return r.sealed({k:v for k,v in x.items() if k!="record_digest"},"record_digest")


def unpack(value,manifest):
    """Independent reconstruction: no pack/ID producer calls."""
    try:
        x=deepcopy(value);wire_digest=x["record_digest"]
        r.require(wire_digest==r.digest({k:v for k,v in x.items() if k!="record_digest"}),"RECORD_DIGEST_INVALID")
        storage=x.pop("storage")
        r.require(set(storage)=={"schema","expanded_digest"} and storage["schema"]==SCHEMA,"STORAGE_FORM_INVALID")
        p=x["bindings"]
        if p is not None:
            for parent,key,has_bytes,qid in ((p,"admin_files",False,r.admin.RUN_ID),
                    (p["qualifications"],"previous",True,r.QUAL_ID),
                    (p["qualifications"],"main",True,"s2oa-main-binding-qualification-20260910-01")):
                group=parent[key]
                r.require(type(group) is dict and set(group)=={"files"},"REFERENCE_FORM_INVALID")
                restored={}
                for name,row in group["files"].items():
                    r.require(name in ("binding.json","preregistration.json","result.json","verification.json","stdout.txt","stderr.txt")
                        and type(row) is list and len(row)==(2 if has_bytes else 1),"REFERENCE_FORM_INVALID")
                    restored[name]=dict(path="reports/s2oa/"+qid+"/"+name,sha256=row[0])
                    if has_bytes:restored[name]["bytes"]=row[1]
                parent[key]=restored
            for role,qid in (("event_ids",ids.QUAL_ID),("correction",QUAL_ID)):
                q=p["qualifications"][role]
                r.require(type(q) is dict and set(q)=={"files"},"REFERENCE_FORM_INVALID")
                q["qualification_id"]=qid
            ref=p["event_ids"]
            r.require(type(ref) is dict and set(ref)=={"schema","expanded_digest"}
                      and ref["schema"]=="s2oa.event-id-reference.v1","ID_REFERENCE_INVALID")
            m=dict(schema="s2oa.event-id-binding.v1",execution_digest=p["execution_digest"],
                columns=["ordinal","plan_id","technical_id"],rows=[[n,"e"+str(n).zfill(2),"s2oa-event-e"+str(n).zfill(2)] for n in range(1,29)])
            r.require(r.digest(m)==ref["expanded_digest"],"ID_REFERENCE_INVALID")
            p["event_ids"]={**m,"id_binding_digest":ref["expanded_digest"]}
        if x["execution"] is not None:
            ref=x["execution"]["binding"]["component_sources"]
            r.require(type(ref) is dict and set(ref)=={"schema","manifest_digest","indices","expanded_digest"}
                and ref["schema"]=="s2oa.qualified-source-reference.v1"
                and ref["manifest_digest"]==r.digest(manifest),"COMPONENT_REFERENCE_INVALID")
            keys=sorted(manifest)
            r.require(type(ref["indices"]) is list and len(ref["indices"])==len(set(ref["indices"]))
                and all(type(i) is int and 0<=i<len(keys) for i in ref["indices"]),"COMPONENT_REFERENCE_INVALID")
            rows=[[keys[i],manifest[keys[i]]] for i in ref["indices"]]
            r.require(r.digest(rows)==ref["expanded_digest"],"COMPONENT_REFERENCE_INVALID")
            x["execution"]["binding"]["component_sources"]=rows
        r.require(r.digest({k:v for k,v in x.items() if k!="record_digest"})==storage["expanded_digest"],"REFERENCE_RECONSTRUCTION_INVALID")
        return x
    except r.S2OAError:
        raise
    except (KeyError,TypeError,ValueError,IndexError) as exc:
        raise r.S2OAError("REFERENCE_FORM_INVALID") from exc
