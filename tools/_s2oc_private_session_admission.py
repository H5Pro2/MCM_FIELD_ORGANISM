"""Versioned active admission; unchanged OC session and OB processing mechanics."""
from dataclasses import asdict
import ast
import hashlib
import json
from pathlib import Path
from threading import Lock

from tools import _s2oc_private_caller_session as old

b = old.b
VERSION = "s2oc.active-admission.v1"
QUAL_ID = "s2oc-admission-qualification-20260910-01"
MAIN_GATE = False
OWN = ("tools/_s2oc_private_session_admission.py",
       "tests/test_s2oc_private_session_admission.py",
       "reports/s2oc/qualify_admission_once.py",
       "reports/s2oc/AKTIVE_ZULASSUNG.md")
BOUNDARY = ("The active receipt checks qualification provenance, coverage and current code/profile; "
            "it does not repeat historical tests or read archived transactions at session start. "
            "The connector delta is separately qualified; historical coverage is not its qualification.")


class AdmissionError(old.S2OCError):
    pass


def need(ok, code, balance=None):
    if not ok:
        raise AdmissionError(code, balance)


def raw_hash(raw):
    return hashlib.sha256(raw).hexdigest()


def inventory():
    return dict(version=VERSION, ob=b.code_inventory(), oc=old.sources(),
                connector={p: [raw_hash((b.ROOT/p).read_bytes()), (b.ROOT/p).stat().st_size] for p in OWN})


def create_admission(directory):
    """Exactly one archive integrity pass, no test/owner/receptor execution."""
    out = Path(directory)
    need(not out.exists(), "ADMISSION_OUTPUT_CONFLICT")
    inv = inventory()
    archive = old.QUAL_DIR/"evidence.zip"
    measured = old.package.verify_package(archive)
    stamp_raw = (old.QUAL_DIR/"package.json").read_bytes()
    stamp = json.loads(stamp_raw)
    qraw = old.packed_file(archive, "result.json")
    q = json.loads(qraw)
    b.check_root(q, "result_digest")
    need(stamp["sha256"] == measured["sha256"] and stamp["status"] == "QUALIFIED"
         and not stamp["violations"] and q["status"] == "QUALIFIED"
         and q["run_id"] == old.QUAL_ID and q["passed_tests"] == q["expected_tests"] == 29
         and q["test_calls"] == 1 and q["hashes_unchanged"] is True and q["gates"] is False,
         "ARCHIVE_QUALIFICATION_INVALID")
    need(q["source_digest"] == b.digest(dict(ob=inv["ob"], session=inv["oc"]))
         and q["session_sources_digest"] == b.digest(inv["oc"]), "ARCHIVE_CODE_CHANGED")
    for name, h in q["files"].items():
        need(raw_hash(old.packed_file(archive, name)) == h, "ARCHIVE_FILE_CHANGED")
    tests = sorted(n.name for n in ast.walk(ast.parse((b.ROOT/old.OWN[1]).read_text(encoding="utf-8")))
                   if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    pr = json.loads(old.packed_file(archive, "preregistration.json"))
    need(len(tests) == 29 and b.digest(tests) == pr["test_inventory_digest"], "ARCHIVE_COVERAGE_INVALID")
    new_tests = sorted(n.name for n in ast.walk(ast.parse((b.ROOT/OWN[1]).read_text(encoding="utf-8")))
                       if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    # OB qualification is checked at issuance, not made an implicit session dependency.
    b.qualified_references(inv["ob"])
    obr = (b.QUAL_DIR/"result.json").read_bytes()
    receipt = b.sealed(dict(version=VERSION, status="ADMITTED", qualification_id=old.QUAL_ID,
        qualification_result=q, coverage=tests, profile_digest=b.r.half.PROFILE_DIGEST,
        config_digest=b.CONFIG_DIGEST, inventory_sha256=raw_hash(b.canonical(inv)),
        ob_result_sha256=raw_hash(obr), schema=b.SCHEMA, session_schema=old.SCHEMA,
        connector_qualification_id=QUAL_ID,
        connector_scope=dict(tests=new_tests, test_inventory_digest=b.digest(new_tests),
            boundary="Prospective connector test inventory, not a historical pass count."), boundary=BOUNDARY,
        archive=dict(path=archive.relative_to(b.ROOT).as_posix(), sha256=measured["sha256"],
            package_sha256=raw_hash(stamp_raw), stored_bytes=archive.stat().st_size,
            expanded_bytes=measured["expanded_total"], index_bytes=measured["index_expanded"],
            files=82, integrity_checked=True)), "admission_digest")
    need(len(b.canonical(receipt)) <= b.LIMITS["metadata"], "ADMISSION_LIMIT")
    out.mkdir()
    save(out/"inventory.json", inv)
    save(out/"admission.json", receipt)
    return raw_hash(b.canonical(receipt))


def save(path, value):
    b.r.ng.ne.atomic_write(path, value, b.LIMITS["total"])


def read_admission(directory, trusted_sha256):
    """The digest pin is supplied by the caller's prebound authorization."""
    try:
        directory = Path(directory)
        need((directory/"admission.json").stat().st_size <= 65536
             and (directory/"inventory.json").stat().st_size <= 174080, "ADMISSION_LIMIT")
        raw = (directory/"admission.json").read_bytes()
        need(raw_hash(raw) == trusted_sha256, "ADMISSION_INTEGRITY_INVALID")
        a = json.loads(raw)
        b.check_root(a, "admission_digest")
        iraw = (directory/"inventory.json").read_bytes()
        need(raw_hash(iraw) == a["inventory_sha256"], "ADMISSION_INVENTORY_INVALID")
        inv = json.loads(iraw)
        need(inv == inventory(), "ADMISSION_CODE_CHANGED")
        need(a["version"] == VERSION and a["status"] == "ADMITTED" and a["boundary"] == BOUNDARY
             and a["profile_digest"] == b.r.half.PROFILE_DIGEST and a["config_digest"] == b.CONFIG_DIGEST
             and a["schema"] == b.SCHEMA and a["session_schema"] == old.SCHEMA
             and a["connector_qualification_id"] == QUAL_ID, "ADMISSION_BINDING_INVALID")
        q = a["qualification_result"]
        b.check_root(q, "result_digest")
        tests = sorted(n.name for n in ast.walk(ast.parse((b.ROOT/old.OWN[1]).read_text(encoding="utf-8")))
                       if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
        need(a["qualification_id"] == q["run_id"] == old.QUAL_ID and q["status"] == "QUALIFIED"
             and q["passed_tests"] == q["expected_tests"] == len(a["coverage"]) == 29
             and a["coverage"] == tests and q["test_calls"] == 1
             and q["hashes_unchanged"] is True and q["gates"] is False
             and q["source_digest"] == b.digest(dict(ob=inv["ob"], session=inv["oc"]))
             and a["archive"]["integrity_checked"] is True, "ADMISSION_COVERAGE_INVALID")
        return a, inv, (("metadata", "admission.json", len(raw)), ("sources", "inventory.json", len(iraw)))
    except AdmissionError:
        raise
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise AdmissionError("ADMISSION_INVALID") from exc


def ledger(record, binding, references, proof_bytes=262144):
    """Each physical dependency once; no unassigned qualification allowance."""
    core = record.get("execution")
    shape = b.core_sizes(core) if core is not None else None
    groups = {} if shape is None else {k: sum(v) for k, v in shape["items"].items()}
    rb, sb = len(b.canonical(record)), len(b.canonical(binding))
    prefix = binding.get("failed_prefix_steps", [])
    need(len(prefix) <= 28 and all(len(b.canonical(x)) <= 16384 for x in prefix), "SESSION_RESULT_LIMIT")
    data = sum(groups.values()) + sum(len(b.canonical(x)) for x in prefix)
    refs = [list(x) for x in references]
    need(len({x[1] for x in refs}) == len(refs) and all(k in ("metadata", "sources") and type(n) is int and n >= 0
         for k, p, n in refs), "REFERENCE_INVALID")
    sources = sum(n for k, p, n in refs if k == "sources")
    meta = rb + sb - data + sum(n for k, p, n in refs if k == "metadata") + 512
    totals = dict(metadata=meta, sources=sources, verification=proof_bytes,
                  nj=groups.get("nj", 0), formations=groups.get("formations", 0), generations=groups.get("generations", 0))
    totals["shared"] = sources + sum(totals[k] for k in ("nj", "formations", "generations"))
    totals["total"] = rb+sb+sum(n for k, p, n in refs)+512+proof_bytes
    return dict(totals=totals, contributions=dict(references=refs, record=rb, session=sb, native=groups,
        prefix_steps=sum(len(b.canonical(x)) for x in prefix), report=512, verification=proof_bytes),
        violations=[k.upper()+"_LIMIT" for k, v in totals.items() if v > b.LIMITS[k]])


def preflight(manifest, refs):
    """Manifest-derived native maxima plus the existing entire metadata ceiling.

    The unused metadata capacity is a bounded failure envelope, not extra bytes
    added to already counted metadata. Success and failure share this capacity.
    """
    x = b.validate_manifest(manifest)
    native = dict(states=(x["formations"]+1)*98304, inputs=x["events"]*16384,
        steps=x["events"]*16384, scans=x["scans"]*32767, nj=x["audio"]*1024,
        formations=x["formations"]*1536, generations=x["formations"]*1536)
    sources = sum(n for k, p, n in refs if k == "sources")
    fixed = sum(n for k, p, n in refs if k == "metadata") + 512
    totals = dict(metadata=65536, sources=sources, verification=262144,
        nj=native["nj"], formations=native["formations"], generations=native["generations"],
        shared=sources+native["nj"]+native["formations"]+native["generations"],
        total=sum(native.values())+65536+sources+262144)
    result = dict(counts=x, native=native, fixed_metadata=fixed,
        manifest_bytes=len(b.canonical(asdict(manifest))), totals=totals,
        violations=[k.upper()+"_LIMIT" for k, v in totals.items() if v > b.LIMITS[k]])
    need(not result["violations"] and fixed+result["manifest_bytes"] < 65536, "PREFLIGHT_LIMIT", result)
    return result


def open_session(manifest, directory, *, admission_directory, admission_sha256):
    global MAIN_GATE
    try:
        need(MAIN_GATE, "SESSION_GATE_CLOSED")
        a, inv, refs = read_admission(admission_directory, admission_sha256)
        need(manifest.code_digest == b.digest(inv["ob"]), "SESSION_CODE_INVALID")
        plan = preflight(manifest, refs)
        path = Path(directory)
        need(not path.exists() and path.parent.is_dir(), "SESSION_OUTPUT_CONFLICT")
        c = Session.__new__(Session)
        c._lock, c._manifest_bytes = Lock(), b.canonical(asdict(manifest))
        c._manifest = b.decode_manifest(json.loads(c._manifest_bytes))
        c._path, c._mode, c._refs = path, "CALLER", refs
        c._sources = inv
        c._active_qualification = dict(version=VERSION, admission_sha256=admission_sha256,
            inventory_sha256=a["inventory_sha256"], admission_directory=str(Path(admission_directory).resolve()))
        c._runtime = c._materializer = None
        c._terminal, c._returned, c._phase = None, [], "RUNTIME_INIT"
        c._preflight = plan
        path.mkdir()
        try:
            c._runtime, c._materializer = b.CallerRuntime(c._manifest), b.Materializer(c._manifest)
            c._check_progress_budget()
        except Exception as exc:
            c._fail(exc, "RUNTIME_INIT", None)
            raise
        return c
    finally:
        MAIN_GATE = False


class Session(old.Session):
    def _binding(self, record):
        # Preserve the qualified immutable return/progress form; version the admission separately.
        return super()._binding(record)

    def _publish(self, record):
        need(self._terminal is None, "SESSION_ALREADY_PUBLISHED")
        binding = self._binding(record)
        result = ledger(record, binding, self._refs)
        need(not result["violations"], "SESSION_PACKAGE_LIMIT", result)
        save(self._path/"session.json", binding)
        save(self._path/"record.json", record)
        self._terminal = b.canonical(record)
        return self._terminal

    def _check_progress_budget(self):
        c = self._runtime
        # Exact current full success header, without close() or any state transition.
        final = asdict(c.subject.snapshot())
        final["status"] = "CLOSED"
        core = b.sealed(dict(schema=b.SCHEMA, status="RECORDING_COMPLETE", run_id=c.run_id,
            config_digest=c.config.config_digest, runtime_config=c.rc, binding=asdict(c.binding),
            initial=c.initial, final=final, inputs=c.packed, source_receipts=c.source,
            rows=c.rows, states=c.states,
            scans=[dict(ordinal=n, role=role, value=asdict(x)) for (n, role), x in sorted(c.scans.items())],
            failure=None, main_gate=False), "record_digest")
        record = self._record(core)
        binding = self._binding(record)
        if len(c.rows) > len(self._returned):
            binding["returned_results"].append(dict(ordinal=len(c.rows), sha256="0"*64, byte_count=16384))
        measured = ledger(record, binding, self._refs)
        need(not measured["violations"], "SESSION_PACKAGE_LIMIT", measured)
        # A full copy of the structured ledger fits in the remaining failure capacity.
        # Native evidence has already been counted; no second 16-KiB reserve is added.
        diagnostic = len(b.canonical(measured))
        remaining = 65536-measured["totals"]["metadata"]
        source = max((len(p.source_id) for e in self._manifest.events for p in (e.pcm, e.rgb) if p), default=0)
        failure_fields = dict(phase=max(b.PHASES, key=len), ordinal=len(self._manifest.events),
            source_id="x"*source, completed_events=len(c.rows), code="SESSION_PACKAGE_LIMIT",
            error_class="AdmissionError", last_snapshot_digest="0"*64, final=final, balance=measured)
        failure_bytes = len(b.canonical(failure_fields))
        need(failure_bytes <= remaining, "FAILURE_ENVELOPE_LIMIT", measured)
        self._last_budget = dict(measured=measured, remaining_error_metadata=remaining,
            structured_budget_error_bytes=failure_bytes, diagnostic_bytes=diagnostic,
            boundary="Actual other error fields are checked in full at publication; no truncation.")


def verify_session_once(directory):
    path = Path(directory)
    with (path/"verification.claim").open("xb") as f:
        f.write(b"once")
    raw = (path/"record.json").read_bytes()
    record = json.loads(raw)
    binding = json.loads((path/"session.json").read_bytes())
    active = binding["active_qualification"]
    a, inv, refs = read_admission(active["admission_directory"], active["admission_sha256"])
    count = old.verify_binding(binding, record, inv)
    # Reuse the independent native verification, not its historical archive-loading entry.
    proof = old.verifier.verify(record, b.decode_manifest(record["manifest"]), refs)
    result = b.sealed(dict(version=VERSION, returned_results=count, core=proof,
        admission_digest=a["admission_digest"], session_digest=binding["session_digest"],
        read_only=True, evaluation_allowed=proof["evaluation_allowed"]), "verification_digest")
    size = len(b.canonical(result))+4
    measured = ledger(record, binding, refs, size)
    need(not measured["violations"] and raw == (path/"record.json").read_bytes(), "CLOSURE_INVALID", measured)
    save(path/"verification.json", result)
    return result, measured
