"""Explicit OD-only administrative budget; native OC processing is unchanged."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from threading import Lock
from types import MappingProxyType

from tools import _s2od_private_terminal_client as client

old, verification, s, b = client.entry, client.verification, client.s, client.b
VERSION = "s2od.sources-budget.v1"
LIMITS = MappingProxyType(dict(b.LIMITS, sources=196608))
ATTACHMENTS = (("metadata", "@evaluation", 8192), ("metadata", "@dispatch", 1536),
               ("metadata", "@final-balance", 8192), ("metadata", "@common-reference", 512),
               ("metadata", "@release", 3072))
MAIN_GATE = False
POLICY_NAME = "od-budget.json"


def policy():
    return dict(version=VERSION, limits=dict(LIMITS), historical_sources=174080,
                scope="Private OD terminal connection only; no native limit change.")


def validate_policy(common):
    refs = [r for r in common["references"] if Path(r[1]).name == POLICY_NAME]
    client.need(len(refs) == 1, "OD_BUDGET_BINDING_INVALID")
    ref = refs[0]
    client.need(ref == s.file_reference("metadata", b.ROOT/ref[1])
                and s.read_json(b.ROOT/ref[1]) == policy(), "OD_BUDGET_BINDING_INVALID")
    own = s.file_reference("sources", Path(__file__))
    client.need(own in common["references"], "OD_BUDGET_SOURCE_UNBOUND")
    return ref[3]


def violations(totals):
    client.need(set(totals) == set(LIMITS) and all(type(n) is int and n >= 0 for n in totals.values()),
                "OD_TOTALS_INVALID")
    return [k.upper()+"_LIMIT" for k,n in totals.items() if n > LIMITS[k]]


def ledger(*args, **kwargs):
    value = s.ledger(*args, **kwargs)
    value["violations"] = violations(value["totals"])
    return value


def require_budget(rows, phase, ordinal, completed):
    if any(r["violations"] for r in rows.values()):
        detail = old.budget.diagnostic(rows, phase, ordinal, completed)
        for alternative in detail["alternatives"].values():
            alternative["limits"] = dict(LIMITS)
        detail["od_version"] = VERSION
        client.need(len(b.canonical(detail)) <= old.budget.ERROR_LIMIT, "OD_DIAGNOSTIC_LIMIT")
        raise old.budget.BudgetError("COMBINED_RUNTIME_METADATA_LIMIT", detail)


class Session(old.Session):
    def _check_progress_budget(self):
        rows = {name: ledger(*pair, self._common, attachments=ATTACHMENTS)
                for name,pair in zip(("success", "failure"), self._forms())}
        require_budget(rows, "EVIDENCE", min(len(self._runtime.rows)+1,len(self._manifest.events)),
                       len(self._runtime.rows))
        self._last_budget = rows

    def _publish(self, record):
        s.need(self._terminal is None, "SESSION_ALREADY_PUBLISHED")
        binding = self._binding(record)
        actual = ledger(record, binding, self._common, attachments=ATTACHMENTS)
        require_budget({"actual": actual}, self._phase, None, len(self._runtime.rows) if self._runtime else 0)
        wr, ws = s.pack(record, binding, self._common)
        s.prior.save(self._path/"record.json", wr)
        s.prior.save(self._path/"session.json", ws)
        self._terminal = b.canonical(record)
        return self._terminal


def open_session(common, inv, directory, *, common_path):
    global MAIN_GATE
    client.need(MAIN_GATE is True, "MAIN_GATE_CLOSED")
    MAIN_GATE = False
    manifest = s.validate_common(common, inv, qualified=True)
    validate_policy(common)
    path, cp = Path(directory), Path(common_path).resolve()
    client.need(not path.exists() and path.parent.is_dir(), "SESSION_OUTPUT_CONFLICT")
    client.need(cp.is_relative_to(b.ROOT) and cp.suffix == ".json"
                and b.canonical(s.read_json(cp)) == b.canonical(common), "COMMON_REFERENCE_INVALID")
    location = dict(path=cp.relative_to(b.ROOT).as_posix(), bytes=len(b.canonical(common)),
                    sha256=s.sha(b.canonical(common)))
    client.need(len(b.canonical(location)) <= 512, "COMMON_LOCATION_INVALID")
    for n in range(len(manifest.events)+1):
        rows = {name: ledger(*pair, common, attachments=ATTACHMENTS)
                for name,pair in zip(("success", "failure"), verification.synthetic_forms(common,n))}
        require_budget(rows, "PREFLIGHT", n or None, n)
    session = Session.__new__(Session)
    session._lock, session._manifest_bytes = Lock(), b.canonical(asdict(manifest))
    session._manifest, session._common = manifest, deepcopy(common)
    session._sources, session._refs = inv, s.references(common)
    session._active_qualification = common["qualification"]
    session._path, session._mode = path, "CALLER"
    session._terminal, session._returned, session._phase = None, [], "RUNTIME_INIT"
    session._runtime = session._materializer = None
    path.mkdir()
    s.prior.save(path/"common-reference.json", location)
    try:
        session._runtime = b.CallerRuntime(manifest)
        session._materializer = b.Materializer(manifest, track_reads=True)
        session._check_progress_budget()
    except Exception as exc:
        session._fail(exc, "RUNTIME_INIT", None)
        raise
    return session


def verify_once(directory, inv):
    path = Path(directory)
    with (path/"verification.claim").open("xb") as f:
        f.write(b"once")
    common = s.load_common(path)
    s.validate_common(common, inv, qualified=True)
    pin = validate_policy(common)
    wr, ws = s.read_json(path/"record.json"), s.read_json(path/"session.json")
    record, session = s.unpack(wr, ws, common)
    result = verification.verify_record(record, session, common, inv)
    result = b.sealed({k:v for k,v in result.items() if k != "verification_digest"}
                      | dict(od_budget_version=VERSION, od_budget_sha256=pin), "verification_digest")
    actual = ledger(record, session, common, attachments=ATTACHMENTS,
                    proof_bytes=len(b.canonical(result))+4)
    require_budget({"actual": actual}, "VERIFICATION", None, len(session["returned_results"]))
    s.need(wr == s.read_json(path/"record.json") and ws == s.read_json(path/"session.json")
           and common == s.load_common(path), "EVIDENCE_CHANGED")
    s.prior.save(path/"verification.json", result)
    return result, actual


class TerminalClient(client.TerminalClient):
    def __init__(self, *args):
        super().__init__(*args)
        validate_policy(self.common)

    def _verify(self):
        if self.verified:
            return None
        self.verified = True
        proof, _ = verify_once(self.output, self.inv)
        return proof

    def command(self, command):
        global MAIN_GATE
        if type(command) is not str or command.strip() != "open":
            return super().command(command)
        if self.attempted or self.ended:
            MAIN_GATE = False
            raise client.ClientError("CLIENT_ALREADY_USED")
        client.need(MAIN_GATE is True, "MAIN_GATE_CLOSED")
        self.attempted = True
        try:
            self.session = open_session(self.common, self.inv, self.output, common_path=self.common_path)
        except Exception as primary:
            self.ended = True
            if (self.output/"record.json").is_file():
                try:
                    self._verify()
                except Exception as closure:
                    primary.add_note("Client verification: " + getattr(closure, "code", type(closure).__name__))
            raise
        finally:
            MAIN_GATE = False
        return "OPEN 0/" + str(len(self.events))
