"""Closed administrative references; native OC evidence is not transformed."""
from copy import deepcopy
from dataclasses import asdict
import ast
import hashlib
import json
from pathlib import Path

from tools import _s2oc_budget_closure as budget
from tools import _s2oc_qualification_archive as qa

b, prior = budget.b, budget.prior
VERSION = "s2oc.shared-administration.v2"
QUAL_ID = "s2oc-shared-closure-qualification-20260910-03"
TEST_COUNT = 30
QUAL_CAPS = {"qualification.zip":qa.QUAL_LIMIT-qa.RECEIPT_LIMIT+qa.INDEX_STORED_LIMIT,"package.json":768}
OWN = ("tools/_s2oc_shared_binding.py", "tools/_s2oc_budget_closure.py",
       "tools/_s2oc_bound_session.py", "tools/_s2oc_shared_verification.py",
       "tests/test_s2oc_shared_closure.py", "reports/s2oc/qualify_shared_copy_once.py",
       "reports/s2oc/run_bound_session_once.py", "reports/s2oc/KOPIERGRENZE_UND_LOGHUELLE.md",
       "tools/_s2ob_private_caller_binding.py", "tools/_s2oc_qualification_archive.py",
       "reports/s2oc/QUALIFIKATIONSHUELLE_6607.md")


def need(ok, code):
    if not ok:
        raise budget.BudgetError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inventory():
    ob = b.code_inventory()
    pending = set(OWN) | set(prior.OWN) | set(prior.old.OWN)
    found = {}
    while pending:
        name = pending.pop()
        if name in found or name in ob["files"]:
            continue
        raw = (b.ROOT/name).read_bytes()
        found[name] = [sha(raw), len(raw)]
        if not name.endswith(".py"):
            continue
        for node in ast.walk(ast.parse(raw.decode("utf-8-sig"))):
            modules = ([x.name for x in node.names] if isinstance(node, ast.Import) else
                       [node.module] + [node.module+"."+x.name for x in node.names]
                       if isinstance(node, ast.ImportFrom) and node.module and not node.level else [])
            for module in modules:
                if module.split(".")[0] not in ("tools", "tests", "reports", "mcm_field_organism"):
                    continue
                path = module.replace(".", "/")
                for candidate in (path+".py", path+"/__init__.py"):
                    if (b.ROOT/candidate).is_file():
                        pending.add(candidate)
    return dict(version=VERSION, ob=ob, connector=dict(sorted(found.items())))


def file_reference(kind, path):
    path = Path(path).resolve()
    need(path.is_relative_to(b.ROOT), "REFERENCE_PATH_INVALID")
    raw = path.read_bytes()
    return [kind, path.relative_to(b.ROOT).as_posix(), len(raw), sha(raw)]


def read_json(path):
    need(Path(path).stat().st_size <= b.LIMITS["total"], "REFERENCE_SIZE_INVALID")
    raw = Path(path).read_bytes()
    value = json.loads(raw)
    need(raw == b.canonical(value), "REFERENCE_ENCODING_INVALID")
    return value


def load_common(directory):
    directory=Path(directory)
    local,ref=directory/"common.json",directory/"common-reference.json"
    need(local.exists()!=ref.exists(),"COMMON_LOCATION_INVALID")
    if local.exists():return read_json(local)
    value=read_json(ref)
    need(set(value)=={"path","bytes","sha256"} and len(b.canonical(value))<=512,"COMMON_LOCATION_INVALID")
    path=(b.ROOT/value["path"]).resolve()
    need(not Path(value["path"]).is_absolute() and path.is_relative_to(b.ROOT)
         and path.suffix==".json","COMMON_LOCATION_INVALID")
    try:
        common=read_json(path)
    except OSError as exc:
        raise budget.BudgetError("COMMON_MISSING") from exc
    need(len(b.canonical(common))==value["bytes"] and sha(b.canonical(common))==value["sha256"],"COMMON_REFERENCE_INVALID")
    return common


def references(common):
    return tuple((k, p, n) for k, p, n, h in common["references"])


def build_common(manifest, inv, refs, qualification=None):
    b.validate_manifest(manifest)
    need(manifest.code_digest == b.digest(inv["ob"]), "CURRENT_CODE_INVALID")
    config = b.r.nn.profile.build_config()
    rule = b.r.ng.build_binding(config, "ALL_BANDS_24")
    rc = b.r.ng.runtime.build_minimal_runtime_config(runtime_id=manifest.run_id,
        max_event_count=len(manifest.events), source_binding_digest=manifest.manifest_digest,
        component_binding_digest=rule.binding_digest)
    rule_value=asdict(rule)
    need(all(inv["ob"]["files"].get(p,[None])[0]==h for p,h in rule.component_sources), "SOURCE_GROUP_INVALID")
    rule_value["component_sources"]={"$code_inventory":"ng-source-paths-v1"}
    return b.sealed(dict(version=VERSION, manifest=asdict(manifest), references=list(refs),
        inventory_sha256=sha(b.canonical(inv)), rule_binding=rule_value, runtime_config=asdict(rc),
        qualification=qualification, read_plan=budget.read_plan(manifest)), "common_digest")


def validate_common(common, inv, *, check_files=True, qualified=False):
    b.check_root(common, "common_digest")
    need(set(common) == {"version", "manifest", "references", "inventory_sha256", "rule_binding",
         "runtime_config", "qualification", "read_plan", "common_digest"}, "COMMON_FORM_INVALID")
    need(common["version"] == VERSION and common["inventory_sha256"] == sha(b.canonical(inv)), "COMMON_BINDING_INVALID")
    manifest = b.decode_manifest(common["manifest"])
    expected = build_common(manifest, inv, common["references"], common["qualification"])
    need(b.canonical(expected) == b.canonical(common), "COMMON_CONTENT_INVALID")
    paths = set()
    for ref in common["references"]:
        need(type(ref) in (tuple, list) and len(ref) == 4, "REFERENCE_INVALID")
        k, p, n, h = ref
        need(k in ("metadata", "sources") and type(p) is str and p not in paths
             and type(n) is int and n >= 0 and b.r.ng.stream._valid_digest(h), "REFERENCE_INVALID")
        path = (b.ROOT/p).resolve()
        need(not Path(p).is_absolute() and path.is_relative_to(b.ROOT), "REFERENCE_PATH_INVALID")
        paths.add(p)
        if check_files:
            try:
                need(file_reference(k, path) == list(ref), "REFERENCE_CHANGED")
            except OSError as exc:
                raise budget.BudgetError("REFERENCE_MISSING") from exc
    need(any(k == "sources" and n == len(b.canonical(inv)) and h == sha(b.canonical(inv))
             for k, p, n, h in common["references"]), "INVENTORY_REFERENCE_MISSING")
    if qualified:
        need(inv == inventory(), "CURRENT_CODE_CHANGED")
        qref = common["qualification"]
        need(type(qref) is list and qref in common["references"], "QUALIFICATION_REFERENCE_INVALID")
        parent=Path(qref[1]).parent
        need(qref[1]==(parent/"package.json").as_posix(),"QUALIFICATION_REFERENCE_INVALID")
        need(all(any(k=="metadata" and p==(parent/name).as_posix() and n<=cap
                     for k,p,n,h in common["references"]) for name,cap in QUAL_CAPS.items()),
             "QUALIFICATION_EVIDENCE_INVALID")
        q = qa.read_qualification(b.ROOT/parent)
        b.check_root(q, "result_digest")
        need(q["run_id"] == QUAL_ID and q["status"] == "QUALIFIED" and q["test_calls"] == 1
             and q["passed_tests"] == q["expected_tests"] == TEST_COUNT
             and q["exit_code"] == 0
             and q["source_digest"] == b.digest(inv) and q["hashes_unchanged"] is True
             and not q["budget_violations"] and q["gates"] is False, "QUALIFICATION_INVALID")
        expected=set(qa.FILES)-{"result.json"}
        need(set(q["evidence"])==expected,"QUALIFICATION_EVIDENCE_INVALID")
    return manifest


def qualified_common(manifest, directory):
    directory=Path(directory)
    inv=read_json(directory/"inventory.json")
    refs=[file_reference("sources",directory/"inventory.json")]
    refs.extend(file_reference("sources",b.ROOT/p) for p in OWN)
    refs.extend(file_reference("metadata",directory/name) for name in QUAL_CAPS)
    qref=next(ref for ref in refs if ref[1]==(directory/"package.json").resolve().relative_to(b.ROOT).as_posix())
    common=build_common(manifest,inv,refs,qref)
    validate_common(common,inv,qualified=True)
    return common,inv


def expanded_rule(common):
    rule=deepcopy(common["rule_binding"])
    need(rule["component_sources"]=={"$code_inventory":"ng-source-paths-v1"},"SOURCE_GROUP_INVALID")
    refs=[r for r in common["references"] if r[0]=="sources" and r[3]==common["inventory_sha256"]]
    need(len(refs)==1,"INVENTORY_REFERENCE_MISSING")
    k,p,n,h=refs[0]
    path=(b.ROOT/p).resolve()
    need(not Path(p).is_absolute() and path.is_relative_to(b.ROOT),"REFERENCE_PATH_INVALID")
    try:
        inv=read_json(path)
    except OSError as exc:
        raise budget.BudgetError("REFERENCE_MISSING") from exc
    need(len(b.canonical(inv))==n and sha(b.canonical(inv))==h,"REFERENCE_CHANGED")
    try:
        rule["component_sources"]=[[p,inv["ob"]["files"][p][0]] for p in b.r.ng.SOURCE_PATHS]
    except (KeyError,TypeError,IndexError) as exc:
        raise budget.BudgetError("SOURCE_GROUP_INVALID") from exc
    need(rule["binding_digest"]==b.digest({k:v for k,v in rule.items() if k!="binding_digest"}),"SOURCE_GROUP_INVALID")
    return rule


def substitutions(common):
    return dict(manifest=common["manifest"], references=[list(x) for x in references(common)],
        code_digest=common["manifest"]["code_digest"], rule_binding=expanded_rule(common),
        runtime_config=common["runtime_config"], qualification=common["qualification"])


def transform(record, session, common, *, expand=False):
    # Internal view only: never reconstruct the write-validating state pool.
    record, session = dict(record), dict(session)
    if record["execution"] is not None:
        record["execution"] = dict(record["execution"])
    values = substitutions(common)
    targets = [(record, "manifest", "manifest"), (record, "references", "references"),
               (record, "code_digest", "code_digest"), (session, "active_qualification", "qualification")]
    if record["execution"] is not None:
        targets += [(record["execution"], "binding", "rule_binding"),
                    (record["execution"], "runtime_config", "runtime_config")]
    for obj, key, source in targets:
        token = {"$oc_common": source}
        expected = token if expand else values[source]
        need(key in obj and b.canonical(obj[key]) == b.canonical(expected), "ADMIN_REFERENCE_CONFLICT")
        obj[key] = deepcopy(values[source] if expand else token)
    return record, session


def pack(record, session, common):
    r, s = transform(record, session, common)
    pin = sha(b.canonical(common))
    # Detach published values through the existing canonical wire form, not
    # through constructors or setters of native container subclasses.
    return tuple(json.loads(b.canonical(x)) for x in
        (dict(version=VERSION, common_sha256=pin, record=r),
         dict(version=VERSION, common_sha256=pin, session=s)))


def unpack(record, session, common):
    need(type(common) is dict, "COMMON_MISSING")
    b.check_root(common, "common_digest")
    pin = sha(b.canonical(common))
    need(set(record) == {"version", "common_sha256", "record"}
         and set(session) == {"version", "common_sha256", "session"}, "WIRE_FORM_INVALID")
    need(record["version"] == session["version"] == VERSION
         and record["common_sha256"] == session["common_sha256"] == pin, "COMMON_REFERENCE_INVALID")
    r, s = transform(record["record"], session["session"], common, expand=True)
    b.check_root(r, "record_digest")
    b.check_root(s, "session_digest")
    return tuple(json.loads(b.canonical(x)) for x in (r,s))


def ledger(record, session, common, *, attachments=(), proof_bytes=262144, report_bytes=512):
    # Same native classification as the existing ledger; replace only physical
    # administrative byte counts, then count the available common content once.
    result = budget.ledger(record, session, references(common), attachments=attachments, proof_bytes=proof_bytes)
    wr, ws = pack(record, session, common)
    c = result["contributions"]
    physical = [len(b.canonical(x)) for x in (wr, ws, common)]
    delta = sum(physical)-c["record"]-c["session"]
    c.update(record=physical[0], session=physical[1], common=physical[2])
    need(type(report_bytes) is int and 0 <= report_bytes <= 512, "REPORT_LIMIT")
    delta += report_bytes-c["report"]
    c["report"] = report_bytes
    for key in ("metadata", "total"):
        result["totals"][key] += delta
    result["violations"] = [k.upper()+"_LIMIT" for k, n in result["totals"].items() if n > b.LIMITS[k]]
    return result
