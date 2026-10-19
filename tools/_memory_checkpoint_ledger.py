"""Physical artifact ledger; FIELD_CHECKPOINT is data, not metadata."""
import json
from pathlib import Path

LIMITS = dict(metadata=65536, sources=174080, shared=262144,
              verification=262144, total=4194304)


def size(value):
    return len(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii"))


def classify(physical_bytes, value):
    counts=dict(metadata=physical_bytes,sources=0,verification=0,field=0,nj=0,formations=0,generations=0,native=0,input_stock=0)
    def take(kind,amount):
        counts[kind]+=amount
        counts["metadata"]-=amount
    def visit(node):
        if not isinstance(node,dict):
            if isinstance(node,list):
                for item in node:visit(item)
            return
        if "verification_digest" in node:
            take("verification",size(node));return
        if node.get("schema")=="s2ob.caller.v2" and "rows" in node:
            for key in ("states","inputs","scans"):
                values=node[key].values() if key=="states" else node[key]
                for item in values:take("native",size(item))
            for row in node["rows"]:
                take("native",size({k:v for k,v in row.items() if k not in ("formation","generations")}))
                for kind,key in (("formations","formation"),("generations","generations")):
                    if row[key] is not None:take(kind,size(row[key]))
            for receipt in node["source_receipts"]:
                if receipt["nj"] is not None:take("nj",size(receipt))
            return
        for key,item in node.items():
            if key=="field" and node.get("schema")=="mcm.system-checkpoint.v1":
                take("field",size(item))
            elif key=="inventory" and "files" in item:
                take("sources",size(item))
            else:visit(item)
    visit(value)
    if counts["metadata"]<0:raise ValueError("LEDGER_CLASSIFICATION_NEGATIVE")
    return counts


def ledger(directory, decode, *, extra=()):
    rows=[]
    for path in sorted(Path(directory).iterdir()):
        if not path.is_file():continue
        raw=path.read_bytes()
        try:value=decode(raw)
        except (ValueError,KeyError,TypeError):value=None
        classes=classify(len(raw),value)
        if path.name=="neutral-read.pcm":
            classes["metadata"]=0;classes["input_stock"]=len(raw)
        rows.append(dict(path=path.name,bytes=len(raw),classes=classes))
    for name,raw,value in extra:
        rows.append(dict(path=name,bytes=len(raw),classes=classify(len(raw),value)))
    totals={key:sum(row["classes"][key] for row in rows) for key in
        ("metadata","sources","verification","field","nj","formations","generations","native","input_stock")}
    totals["shared"]=sum(totals[k] for k in ("sources","nj","formations","generations"))
    totals["total"]=sum(row["bytes"] for row in rows)
    violations=[k for k,v in LIMITS.items() if totals[k]>v]
    return dict(files=rows,totals=totals,limits=LIMITS,violations=violations)
