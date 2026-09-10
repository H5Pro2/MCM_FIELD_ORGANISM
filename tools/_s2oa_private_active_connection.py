"""Prospective OA qualification closure and byte accounting; stdlib only.

No source generation, project imports, qualification execution or runtime calls.
The pending manifest alone never qualifies a connection.
"""
import hashlib
import json
from pathlib import Path

DIRECTORY = "reports/s2oa/active-connection"
MANIFEST = DIRECTORY + "/manifest.json"
INVENTORY = DIRECTORY + "/inventory.json"
OUTCOME = DIRECTORY + "/qualification.json"
SCHEMA = "s2oa.active-connection.v1"
QUALIFICATION_BYTES = 4096
REPORT_BYTES = 512
LIMITS = dict(metadata=65536, sources=174080, nj=22528, formations=30720,
              generations=30720, shared=262144, total=4194304)
RESERVES = dict(nj=22528, formations=30720, generations=30720)
OWN = ("tools/_s2oa_private_active_connection.py",
       "reports/s2oa/prepare_active_connection.py", INVENTORY)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


class ActiveConnectionError(ValueError):
    def __init__(self, code, balance=None):
        self.code = code
        self.balance = balance
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise ActiveConnectionError(code)


def measure(metadata, sources, reservations, other_total=0):
    """Measure first; oversize input returns ALL contributions and violations."""
    require(set(reservations) == set(RESERVES), "RESERVE_CLASS_INVALID")
    require(all(type(n) is int and n >= 0 for n in
                [*metadata.values(), *sources.values(), *reservations.values(), other_total]),
            "BYTE_COUNT_INVALID")
    violations = []
    for sizes, name in ((metadata, "metadata"), (sources, "sources")):
        for item, size in sizes.items():
            if size > LIMITS[name]:
                violations.append(dict(code=name.upper()+"_ITEM_LIMIT", item=item,
                                       actual=size, limit=LIMITS[name]))
        if sum(sizes.values()) > LIMITS[name]:
            violations.append(dict(code=name.upper()+"_TOTAL_LIMIT", item=name,
                                   actual=sum(sizes.values()), limit=LIMITS[name]))
    for key, size in reservations.items():
        if size > LIMITS[key]:
            violations.append(dict(code=key.upper()+"_RESERVE_LIMIT", item=key,
                                   actual=size, limit=LIMITS[key]))
    shared = sum(sources.values()) + sum(reservations.values())
    total = sum(metadata.values()) + shared + other_total
    for key, size in (("shared", shared), ("total", total)):
        if size > LIMITS[key]:
            violations.append(dict(code=key.upper()+"_LIMIT", item=key,
                                   actual=size, limit=LIMITS[key]))
    balance = dict(metadata_bytes=sum(metadata.values()), source_bytes=sum(sources.values()),
                   reservations=dict(reservations), shared_reserved_bytes=shared,
                   shared_remaining_bytes=LIMITS["shared"]-shared,
                   metadata_remaining_bytes=LIMITS["metadata"]-sum(metadata.values()),
                   total_reserved_bytes=total, total_remaining_bytes=LIMITS["total"]-total)
    return dict(metadata=dict(metadata), sources=dict(sources), reservations=dict(reservations),
                other_total=other_total, balance=balance, violations=violations)


def enforce(report):
    if report["violations"]:
        raise ActiveConnectionError(report["violations"][0]["code"], report)
    return report["balance"]


def inspect_envelope(value):
    """Pure serialization accounting, including identifiers in nested receipts."""
    core = value["execution"]
    p = value["bindings"]
    size = lambda x: len(canonical(x))
    groups = dict(states=[], inputs=[], scans=[], steps=[], nj=[], formations=[], generations=[])
    if core is not None:
        groups["states"] = list(core["states"].values())
        groups["inputs"] = core["inputs"]
        groups["scans"] = core["scans"]
        groups["steps"] = [{k:v for k,v in row.items() if k not in ("formation", "generations")}
                           for row in core["rows"]]
        groups["nj"] = [x for x in core["source_receipts"] if x["nj"] is not None]
        for key, member in (("formations", "formation"), ("generations", "generations")):
            groups[key] = [row[member] for row in core["rows"] if row[member] is not None]
    sizes = {key:list(map(size, xs)) for key,xs in groups.items()}
    core_bytes = 0 if core is None else size(core)
    runtime_meta = core_bytes-sum(sum(xs) for xs in sizes.values())
    shell = size(value)-core_bytes
    reservations = {key:sum(sizes[key]) for key in RESERVES}
    metadata = {**p["metadata_items"], "runtime":runtime_meta, "shell":shell, "report":REPORT_BYTES}
    report = measure(metadata, p["source_items"], reservations,
                     core_bytes-runtime_meta-sum(reservations.values()))
    caps = dict(states=(21,98304), inputs=(28,16384), scans=(16,32767), steps=(28,16384),
                nj=(22,1024), formations=(20,1536), generations=(20,1536))
    for group, (count, cap) in caps.items():
        if len(sizes[group]) > count:
            report["violations"].append(dict(code=group.upper()+"_COUNT_LIMIT", item=group,
                                              actual=len(sizes[group]), limit=count))
        for index, n in enumerate(sizes[group]):
            if n > cap:
                report["violations"].append(dict(code=group.upper()+"_ITEM_LIMIT",
                    item=group+"/"+str(index), actual=n, limit=cap))
    report.update(whole_record_bytes=size(value), core_bytes=core_bytes,
                  metadata_runtime_bytes=runtime_meta, item_sizes=sizes)
    completion = 2*262144+4
    total = report["balance"]["total_reserved_bytes"]+completion
    report.update(completion_reserved_bytes=completion, complete_total_bytes=total,
                  complete_remaining_bytes=LIMITS["total"]-total)
    if total > LIMITS["total"]:
        report["violations"].append(dict(code="COMPLETE_TOTAL_LIMIT",item="complete",
                                          actual=total,limit=LIMITS["total"]))
    return report


def file_reference(root, relative):
    require(type(relative) is str and not Path(relative).is_absolute(), "ACTIVE_REFERENCE_INVALID")
    target = (root/relative).resolve()
    require(target.is_relative_to(root.resolve()) and target.relative_to(root.resolve()).as_posix()==relative,
            "ACTIVE_REFERENCE_INVALID")
    try:
        raw = target.read_bytes()
    except FileNotFoundError as exc:
        raise ActiveConnectionError("ACTIVE_REFERENCE_MISSING") from exc
    return dict(path=relative, sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def load(root, current_hashes):
    """One full current attestation, never accumulated historical pass counts."""
    root = Path(root)
    mraw = (root/MANIFEST).read_bytes()
    manifest = json.loads(mraw)
    require(manifest.get("schema") == SCHEMA and manifest.get("main_gate") is False,
            "ACTIVE_MANIFEST_INVALID")
    require(manifest.get("limits")==LIMITS
            and manifest.get("qualification_reserved_bytes")==QUALIFICATION_BYTES
            and manifest.get("report_reserved_bytes")==REPORT_BYTES,"ACTIVE_LIMITS_INVALID")
    require(manifest["manifest_digest"] == digest({k:v for k,v in manifest.items()
                                                  if k != "manifest_digest"}), "ACTIVE_DIGEST_INVALID")
    require(manifest["code_hashes"] == current_hashes, "ACTIVE_CODE_CHANGED")
    for group in ("metadata_dependencies", "source_dependencies", "verification_dependencies"):
        for ref in manifest[group]:
            require(file_reference(root, ref["path"]) == ref, "ACTIVE_REFERENCE_INVALID")
    inventory = json.loads((root/INVENTORY).read_bytes())
    require(manifest["inventory_sha256"] == hashlib.sha256((root/INVENTORY).read_bytes()).hexdigest(),
            "ACTIVE_INVENTORY_INVALID")
    require((root/OUTCOME).is_file(), "ACTIVE_QUALIFICATION_MISSING")
    raw = (root/OUTCOME).read_bytes()
    require(len(raw) <= QUALIFICATION_BYTES, "ACTIVE_QUALIFICATION_LIMIT")
    outcome = json.loads(raw)
    require(outcome.get("schema") == "s2oa.active-qualification.v1"
            and outcome.get("status") == "QUALIFIED" and outcome.get("test_calls") == 1
            and outcome.get("main_gate_after") is False, "ACTIVE_NOT_QUALIFIED")
    require(outcome["result_digest"] == digest({k:v for k,v in outcome.items() if k != "result_digest"})
            and outcome["manifest_sha256"] == hashlib.sha256(mraw).hexdigest()
            and outcome["code_before"] == outcome["code_after"] == digest(current_hashes),
            "ACTIVE_QUALIFICATION_BINDING_INVALID")
    require(outcome["tests"] == [[row["id"], "PASS"] for row in inventory["tests"]],
            "ACTIVE_COVERAGE_INVALID")
    return manifest, file_reference(root, MANIFEST), file_reference(root, OUTCOME)
