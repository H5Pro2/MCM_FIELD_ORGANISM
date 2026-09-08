"""Independent direct arithmetic and separately charged offline verification."""
import struct
from tools import _s2nt_private_comparison as c


def direct_pair(pair,q,r):
    # No productive distance/equality helper; equality has its own offline ledger.
    differences = []
    for index in range(48):
        value = q.half[index] - r.half[index]
        if value < 0.0:
            value = -value
        elif value == 0.0:
            value = 0.0
        differences.append(dict(original_index=index,value=value))
    return c.sealed(dict(**pair,source_state_digest=q.materialized_digest,reference_state_digest=r.materialized_digest,
        terms=differences,mean=sum([entry["value"] for entry in differences])/48),"pair_digest")


def verify_comparison(record,anchors):
    c.check_root(record,"comparison_digest")
    c.require(record["schema"] == "s2nt.diagnostic-comparison.v1" and record["status"] == "RECORDING_COMPLETE"
        and record["evaluation"] is None,"RECORD_FORM_INVALID")
    c.require(len(c.canonical(record)) <= c.MAX_OUTPUT_BYTES,"OUTPUT_SIZE_EXCEEDED")
    inputs = record["inputs"]
    sources = c.bind_inputs(inputs["plan"],inputs["materialization"],inputs["verification"],anchors)
    by_id = {s.source_id:s for s in sources}
    work = dict(halvings=0,terms=0,equalities=0,sums=0,order_checks=0)
    for source in sources:
        for raw,half in zip(source.raw,source.half,strict=True):
            c.require(struct.pack("<d",raw*0.5) == struct.pack("<d",half),"HALVING_INVALID")
            work["halvings"] += 1
    pairs = inputs["plan"]["pairs"]
    c.require(len(record["primary"]) == len(record["direct"]) == len(pairs) == 25,"PAIR_COUNT_INVALID")
    for pair,primary,direct in zip(pairs,record["primary"],record["direct"],strict=True):
        q,r = by_id[pair["source_id"]],by_id[pair["reference_id"]]
        for row in (primary,direct):
            c.check_root(row,"pair_digest")
            c.require(all(row[k] == v for k,v in pair.items()) and row["source_state_digest"] == q.materialized_digest
                and row["reference_state_digest"] == r.materialized_digest,"PAIR_SOURCE_INVALID")
            c.require(type(row["terms"]) is list and len(row["terms"]) == 48,"TERM_COUNT_INVALID")
            values = []
            for index,entry in enumerate(row["terms"]):
                c.require(type(entry["original_index"]) is int and entry["original_index"] == index,"TERM_INDEX_INVALID")
                value = abs(q.half[index]-r.half[index])
                c.require(type(entry["value"]) is float and struct.pack("<d",entry["value"]) == struct.pack("<d",value),"TERM_VALUE_INVALID")
                values.append(entry["value"])
                work["terms"] += 1
            c.require(type(row["mean"]) is float and row["mean"].hex() == (sum(values)/48).hex(),"SUM_ARITHMETIC_INVALID")
            work["sums"] += 1
        c.require(primary["terms"] == direct["terms"] and primary["mean"].hex() == direct["mean"].hex(),"BASELINE_DIFFERS")
        for name in ("raw","half"):
            left,right = getattr(q,name),getattr(r,name)
            indices = []
            for index in range(48):
                if left[index].hex() != right[index].hex():
                    indices.append(index)
                work["equalities"] += 1
            c.require(primary[name+"_different_indices"] == indices and type(primary[name+"_equal"]) is bool
                and primary[name+"_equal"] == (len(indices) == 0),"EQUALITY_INVALID")
    c.require(record["work"] == dict(primary_differences=1200,direct_differences=1200,equality_components=2400)
        and record["limits"] == c.LIMITS,"WORK_BINDING_INVALID")
    c.require(work == dict(halvings=672,terms=2400,equalities=2400,sums=50,order_checks=0),"VERIFICATION_WORK_INVALID")
    result = c.sealed(dict(status="S2NT_COMPARISON_VERIFIED",comparison_digest=record["comparison_digest"],
        anchors=dict(execution_digest=anchors.execution_digest,materialization_digest=anchors.materialization_digest,
            verification_digest=anchors.verification_digest),baseline_equal=True,read_only=True,
        work=work,source_regenerations=0,receptor_calls=0,nj_calls=0,evaluation_allowed=True),"verification_digest")
    c.require(len(c.canonical(result)) <= c.MAX_VERIFICATION_BYTES,"VERIFICATION_SIZE_EXCEEDED")
    return result
