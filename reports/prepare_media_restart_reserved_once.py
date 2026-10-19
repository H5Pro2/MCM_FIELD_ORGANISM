"""Static object attribution and format-reservation gate. No receptor execution."""
import ast
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OLD1 = ROOT/"reports/media-restart-qualification-20260913-01"
OLD2 = ROOT/"reports/media-restart-qualification-20260913-02"
OUT = ROOT/"reports/media-restart-qualification-20260913-03"
OWN = ("tools/_media_restart_evidence.py", "tools/_media_restart_checkpoint.py",
       "tools/_media_restart_reservations.py", "tests/test_media_restart_reserved.py",
       "reports/prepare_media_restart_reserved_once.py")


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def identity(path):
    data = Path(path).read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def attribution():
    roles = defaultdict(set)
    def visit(value, role="root"):
        if isinstance(value, dict) and "$media_object" in value:
            h = value["$media_object"]
            data = (OLD2/"objects"/(h+".json")).read_bytes()
            # This is administrative byte attribution, not a native verifier.
            if identity(OLD2/"objects"/(h+".json"))["sha256"] != h:
                raise ValueError("historical object identity changed")
            roles[h].add(role)
            visit(json.loads(data)["value"], role)
        elif isinstance(value, dict):
            for key, item in value.items():
                visit(item, key)
        elif isinstance(value, list):
            for item in value:
                visit(item, role+"[]")
    for folder in ("reference", "early-save", "early-restore", "late-save", "late-restore"):
        for name in ("record.json", "checkpoint.json"):
            path = OLD2/folder/name
            if path.exists():
                visit(json.loads(path.read_bytes()))
    groups = defaultdict(list)
    for path in sorted((OLD2/"objects").glob("*.json")):
        value = json.loads(path.read_bytes())
        if value["class"] == "metadata":
            groups[",".join(sorted(roles[path.stem]))].append(dict(object=path.stem, bytes=path.stat().st_size))
    groups = {key: dict(bytes=sum(x["bytes"] for x in rows), objects=rows) for key, rows in sorted(groups.items())}
    total = sum(value["bytes"] for value in groups.values())
    return dict(scope="Existing bytes only; no reconstruction of the missing first-run trigger sum",
                groups=groups, total=total, prior_reservation=40960, shortfall=total-40960)


def ref(kind, cap):
    return {"$media_object": "f"*64, "class": kind, "bytes": cap}


def wrapped_size(value, kind="metadata"):
    return len(raw(dict(value=value, **{"class": kind})))


def index_reserve(n):
    # Exact JSON formats using the existing item caps (OB.core_sizes).
    # Keys/digests have fixed width; byte-count digits use the corresponding cap.
    return dict(states=wrapped_size({format(i, "064x"): ref("native", 98333) for i in range(n+1)}),
        inputs=wrapped_size([ref("native", 16413)]*n),
        rows=wrapped_size([ref("native", 16413+2*128)]*n),
        source_receipts=wrapped_size([ref("nj", 1049)]*n),
        scans=wrapped_size([]), selections=wrapped_size([ref("metadata", 541)]*n))


def envelope(cut, completed, sources, metadata_dependencies):
    # The restored prefix reuses actual checkpoint contents. Its new suffix
    # is not assumed equal to a separately produced reference arm.
    states = 21+(cut+1)+(completed-cut)
    events = 20+cut+(completed-cut)
    native = states*98333+events*(16413+16413+2*128)
    indexes = sum(sum(index_reserve(n).values()) for n in (20, cut, completed))
    data = dict(native=native, metadata=metadata_dependencies+indexes,
                sources=sources, nj=events*1049, formations=events*1569,
                generations=events*1570, field=3*524288)
    data["shared"] = sum(data[k] for k in ("sources", "nj", "formations", "generations"))
    data["total"] = sum(data[k] for k in ("metadata", "sources", "native", "nj", "formations", "generations", "field"))
    return dict(cut=cut, completed=completed, known_format_reservation=data,
        uncredited_nonnegative=["selection receipt bodies", "common bindings and core heads",
            "role roots", "qualification logs and report", "temporary publication", "primary failure reserve",
            "verification"],
        interpretation="Partial reservation already suffices to reject the complete upper envelope; omitted classes are not zero.")


def prepare():
    from tools import _media_restart_checkpoint as c
    from tools import _media_restart_evidence as e
    c.require(not OUT.exists(), "PREPARATION_ID_USED")
    first = json.loads((OLD1/"preregistration.json").read_bytes())
    second = json.loads((OLD2/"preregistration.json").read_bytes())
    previous = {**first["inventory"], **second["inventory_changes"]}
    names = sorted(set(previous) | set(OWN))
    current = {name: identity(ROOT/name) for name in names}
    for name, expected in previous.items():
        if name not in OWN:
            c.require(current[name] == expected, "UNCHANGED_DEPENDENCY_CHANGED", name)
    charged = sorted(set(first["charged_sources"]) | set(second["inventory_changes"]) | set(OWN))
    external = [dict(path=str(ROOT/name), category="sources", **current[name]) for name in charged]
    for old in (OLD1, OLD2):
        for name in ("preregistration.json", "result.json", "stderr.log"):
            external.append(dict(path=str(old/name), category="metadata", **identity(old/name)))
    source = c.p.Source(str(ROOT/"sources/media-restart-neutral/qualification-20260913-03.bin"),
                        hashlib.sha256(bytes(range(256))*32).hexdigest(), 8192)
    manifest = c.p.build("media-restart-neutral-20260913-03", source, c.b.digest(current), mode=c.p.FULL_VERSION)
    tests = sorted(node.name for node in ast.walk(ast.parse((ROOT/OWN[3]).read_text()))
                   if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"))
    attribution_value = attribution()
    metadata_dependencies = sum(x["bytes"] for x in external if x["category"] == "metadata")
    source_bytes = sum(x["bytes"] for x in external if x["category"] == "sources")
    rows = [envelope(cut, completed, source_bytes, metadata_dependencies)
            for cut in range(1, 20) for completed in range(cut, 21)]
    violations = sorted({key for row in rows for key, cap in e.LIMITS.items()
                         if row["known_format_reservation"].get(key, 0) > cap})
    future = [dict(name="qualification_logs", paths=["stdout.log", "stderr.log"]+
                   [folder+ext for folder in ("reference", "early-save", "early-restore", "late-save", "late-restore")
                    for ext in (".stdout", ".stderr")], limit=8192, closed_by="result.json"),
              dict(name="result", paths=["result.json"], limit=1024, closed_by="result.json"),
              dict(name="report", paths=["REPORT.md"], limit=4096, closed_by="REPORT.md"),
              dict(name="balance", paths=["closure-balance.json"], limit=1024, closed_by="closure-balance.json")]
    binding = dict(version="media.restart-reserve-preparation.v3", ready=False, test_calls=0, tests=tests,
        inventory=current, external=external, manifest=c.asdict(manifest), future=future,
        limits=e.LIMITS, primary_failure_reserve=e.FAILURE_RESERVE,
        prior_objects=attribution_value, offered_cuts=list(range(1, 20)), positions_examined=len(rows),
        phases=["progress", "checkpoint publication", "restore publication", "PLAYER_CLOSE", "error closure", "final balance"],
        row_columns=["cut", "completed", "metadata", "sources", "native", "field", "nj", "formations", "generations", "shared", "total"],
        rows=[[row["cut"], row["completed"], *[row["known_format_reservation"][key] for key in
              ("metadata", "sources", "native", "field", "nj", "formations", "generations", "shared", "total")]] for row in rows],
        violations=violations,
        peak=max(rows, key=lambda x: x["known_format_reservation"]["total"]),
        reason="Independent current item caps already exceed the total. Historical actual equality is not a prospective format bound.",
        no_test_reason="Complete admission is not established; no payload creation or test invocation permitted.")
    OUT.mkdir()
    with (OUT/"preregistration.json").open("xb") as stream:
        stream.write(raw(binding))
    print(json.dumps(dict(status="PRESTART_BLOCKED", test_calls=0, tests_prepared=len(tests),
        historical_metadata=attribution_value["total"], shortfall=attribution_value["shortfall"],
        source_bytes=source_bytes, active_metadata_dependencies=metadata_dependencies,
        positions=len(rows), violations=violations, peak=binding["peak"],
        preregistration=identity(OUT/"preregistration.json"))))


if __name__ == "__main__":
    if sys.argv[1:] != ["prepare"]:
        raise SystemExit("Preparation only. Execution requires a proven complete envelope.")
    prepare()
