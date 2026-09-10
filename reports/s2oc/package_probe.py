"""Administrative byte packaging only; no receptor, runtime or project imports."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT/"tools/_s2oc_private_evidence_package.py"
spec = importlib.util.spec_from_file_location("evidence_zip", MODULE)
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)


def main():
    old = ROOT/"reports/s2oc/s2oc-session-qualification-20260910-01"
    out = ROOT/"reports/s2oc/package-probe-bound"
    out.mkdir(exist_ok=False)
    names = [x.relative_to(old).as_posix() for x in old.rglob("*") if x.is_file()]
    before = {n:[(old/n).stat().st_size,hashlib.sha256((old/n).read_bytes()).hexdigest()] for n in names}
    p.create_package(old,out/"evidence.zip",names)
    measured = p.verify_package(out/"evidence.zip",old)
    after = {n:[(old/n).stat().st_size,hashlib.sha256((old/n).read_bytes()).hexdigest()] for n in names}
    p.require(before == after, "ORIGINALS_CHANGED")
    prior = json.loads((old/"final-balance.json").read_bytes())
    result = dict(**measured, original_directory=old.relative_to(ROOT).as_posix(), originals_unchanged=True,
        entire_prior_metadata_included=prior["runtime_session_metadata"],
        complete_failure_log_bytes=before["stderr.txt"][0],
        code_sha256=hashlib.sha256(MODULE.read_bytes()).hexdigest(),
        boundary="Additional administrative copy of all prior files; no claim that historical storage was removed or retroactively conformant.")
    with (out/"probe.json").open("xb") as f: f.write(p.canonical(result))
    print(json.dumps(result))


if __name__ == "__main__":main()
