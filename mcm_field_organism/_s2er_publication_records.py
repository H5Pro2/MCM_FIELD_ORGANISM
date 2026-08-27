"""Private S2-EQ data validation. No publisher, platform probe or runner at import."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re


EO_DIGEST = "2696e89a576152c908501356a001290bea738f821038331536ddfb40fdb53141"
EQ_DIGEST = "96a881ee5302f07d30af071b81f7b378c32bf33c2ab1676c9f773cf95340c76c"
BACKEND = "s2eo.file-scoped-ntfs.v1"
STUDY = "s2dr.tspm1.h1-h7.56.v1"
_EQ_FILE = "S2EQ_STATISCHER_KORREKTURVERTRAG_DER_PUBLIKATIONSBINDUNGEN_V1.json"
_EO_FILE = "S2EO_STATISCHER_DATEIBEZOGENER_VEROEFFENTLICHUNGSVERTRAG_V1.json"

# No bootstrap or registration API is installed. A separately audited host must
# bind any future context independently of submitted records, without source edits.
_TRUSTED_ADMISSION: ContextVar[frozenset[str]] = ContextVar(
    "s2er_independently_reviewed_contexts", default=frozenset()
)


class PublicationError(ValueError):
    def __init__(self, code: str, detail: str, *, native_error: int | None = None):
        super().__init__(detail)
        self.code = code
        self.native_error = native_error


def require(ok: bool, detail: str, code: str = "PUBLICATION_BINDING_MISMATCH") -> None:
    if not ok:
        raise PublicationError(code, detail)


def _unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "duplicate JSON key", "INVALID_PUBLICATION_SCHEMA")
        value[key] = item
    return value


def _bad_constant(value):
    raise PublicationError("INVALID_PUBLICATION_SCHEMA", "nonfinite JSON constant")


def loads(raw: bytes) -> object:
    require(type(raw) is bytes, "immutable bytes required", "INVALID_PUBLICATION_SCHEMA")
    return json.loads(raw, object_pairs_hook=_unique, parse_constant=_bad_constant)


def encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, separators=(",", ":")).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(encoded(value)).hexdigest()


def raw_digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _core():
    from . import _tspm1_s2dr_private_comparison
    return _tspm1_s2dr_private_comparison


def _contract():
    directory = Path(__file__).resolve().parents[1] / "docs"
    contracts = []
    for name, expected in ((_EO_FILE, EO_DIGEST), (_EQ_FILE, EQ_DIGEST)):
        value = loads((directory / name).read_bytes())
        require(type(value) is dict, "contract object required")
        declared = value.pop("artifact_digest")
        require(declared == expected == digest(value), "publication contract changed")
        contracts.append(value)
    eo, eq = contracts
    require(all(digest(eo[key]) == expected for key, expected in
                eq["preserved_s2eo_sections"].items()), "S2-EO sections changed")
    return eq


def canonical_path(value: object) -> str:
    require(type(value) is str and bool(re.fullmatch(r"[A-Z]:\\.*", value)),
            "local canonical DOS path required")
    require("/" not in value and "\x00" not in value and ":" not in value[2:],
            "device, stream or path separator alias")
    path = PureWindowsPath(value)
    require(str(path) == value and path.is_absolute(), "path is not canonical")
    for part in path.parts[1:]:
        require(part not in (".", "..") and not part.endswith((".", " "))
                and not any(ord(c) < 32 or c in '<>"|?*' for c in part),
                "ambiguous path component")
        base = part.split(".", 1)[0].upper()
        require(not re.fullmatch(r"CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9]", base),
                "reserved device name")
    return value


def _type(name: str, value: object, forms: dict) -> None:
    if name.startswith("optional["):
        if value is not None:
            _type(name[9:-1], value, forms)
    elif name.startswith("list["):
        require(type(value) is list, "list required")
        for item in value:
            _type(name[5:-1], item, forms)
    elif name.startswith("literal-integer:"):
        require(type(value) is int and value == int(name.split(":", 1)[1]), "integer literal differs")
    elif name.startswith("literal:"):
        require(type(value) is str and value == name.split(":", 1)[1], "literal differs")
    elif name in forms:
        require(type(value) is dict and set(value) == set(forms[name]), "record fields differ: " + name)
        for field, field_type in forms[name].items():
            _type(field_type, value[field], forms)
        if "record_digest" in value:
            require(value["record_digest"] == digest({k: v for k, v in value.items()
                                                      if k != "record_digest"}), "record digest differs")
    elif name in ("Digest", "Hex16", "Hex32"):
        width = {"Digest": 64, "Hex16": 16, "Hex32": 32}[name]
        require(type(value) is str and re.fullmatch("[0-9a-f]{" + str(width) + "}", value) is not None,
                "invalid hexadecimal identity")
    elif name in ("Integer", "PositiveInteger", "NonnegativeInteger"):
        require(type(value) is int and (name == "Integer" or value >= (1 if name == "PositiveInteger" else 0)),
                "invalid integer")
    elif name == "NonemptyText":
        require(type(value) is str and bool(value), "nonempty text required")
    elif name == "LocalId":
        require(type(value) is str and re.fullmatch(r"[a-z0-9][a-z0-9.-]*", value) is not None, "invalid local ID")
    elif name == "CanonicalPath":
        canonical_path(value)
    elif name == "RelativePath":
        require(type(value) is str and bool(value) and "\\" not in value and ":" not in value
                and all(p not in ("", ".", "..") for p in value.split("/")), "invalid source path")
    elif name == "ExistingAttemptJournalEntry":
        _core()._unrecord("AttemptJournalEntry", value)
    else:
        enums = {"GateId": ("G1", "G2", "G3", "G4", "G5"),
                 "CaseStatus": ("OBSERVED_COMPLETE", "NOT_RUN", "INCOMPLETE"),
                 "RecordingStatus": ("COMPLETE", "INCOMPLETE"),
                 "AssessmentStatus": ("ACCEPTED", "BLOCKED", "INCOMPLETE")}
        require(name in enums and type(value) is str and value in enums[name], "unknown type or enum")


@dataclass(frozen=True, slots=True)
class PrivateRecord:
    kind: str
    raw: bytes

    def payload(self) -> dict:
        eq = _contract()
        require(self.kind in eq["data_forms"] and "record_digest" in eq["data_forms"][self.kind],
                "private record kind required")
        value = loads(self.raw)
        _type(self.kind, value, eq["data_forms"])
        require(encoded(value) == self.raw, "noncanonical private record")
        return value


def make_record(kind: str, **fields) -> dict:
    schema = _contract()["data_forms"][kind]["schema_version"].split(":", 1)[1]
    value = {"schema_version": schema, **fields}
    value["record_digest"] = digest(value)
    return PrivateRecord(kind, encoded(value)).payload()


def _sorted_unique(values: list, key: str) -> None:
    keys = [v[key] for v in values]
    require(bool(keys) and keys == sorted(set(keys)), "noncanonical or duplicate " + key)


def file_references(value: object) -> tuple[dict, ...]:
    found = {}

    def collect(item):
        if type(item) is dict:
            if set(item) == {"path", "byte_count", "raw_sha256"}:
                prior = found.setdefault(item["path"], item)
                require(prior == item, "conflicting file references")
            else:
                for child in item.values():
                    collect(child)
        elif type(item) is list:
            for child in item:
                collect(child)
    collect(value)
    return tuple(found[p] for p in sorted(found))


def validate_bundle(raw: bytes) -> dict:
    """Validate values only; trusted admission precedes native I/O in the owner."""
    value = loads(raw)
    require(type(value) is dict and set(value) == set("SPAWUFBQC"), "publication bundle fields differ")
    require(encoded(value) == raw, "noncanonical publication bundle")
    core = _core()
    for key, kind in (("S", "SourceManifest"), ("P", "ExecutionPlan"), ("A", "ExecutionAuthorization")):
        core._unrecord(kind, value[key])
    for key, kind in (("W", "PublicationPlan"), ("U", "PublicationAuthorization"),
                      ("F", "PlatformProfile"), ("B", "PlatformReport"),
                      ("Q", "PlatformAcceptance"), ("C", "AdmissionContext")):
        PrivateRecord(kind, encoded(value[key])).payload()
    s, p, a, w, u, f, b, q, c = (value[k] for k in "SPAWUFBQC")
    require(w["execution_plan_digest"] == p["record_digest"] == a["execution_plan_digest"], "plan binding")
    require(w["execution_authorization_digest"] == a["record_digest"] == u["execution_authorization_digest"], "authorization binding")
    require(w["source_manifest_digest"] == p["source_manifest_digest"] == s["record_digest"], "source binding")
    require(a["study_id"] == STUDY and type(a["authorized_attempt_count"]) is int
            and a["authorized_attempt_count"] == 1
            and a["execution_domain_digest"] == digest(p["execution_domain"]), "core authorization differs")
    require(u["publication_plan_digest"] == w["record_digest"] and
            c["publication_authorization_digest"] == u["record_digest"], "private authorization binding")
    require(w["platform_acceptance_digest"] == c["platform_acceptance_digest"] == q["record_digest"], "acceptance binding")
    require(q["platform_profile_digest"] == b["platform_profile_digest"] == c["platform_profile_digest"] == f["record_digest"], "profile binding")
    require(q["platform_report_digest"] == c["platform_report_digest"] == b["record_digest"], "report binding")
    for field, expected in (("backend_contract_id", BACKEND), ("s2eo_contract_digest", EO_DIGEST), ("s2eq_contract_digest", EQ_DIGEST)):
        require(w[field] == f[field] == expected, "backend or contract drift")
    for field in ("platform_context", "parent_directories", "publisher_sources"):
        require(w[field] == f[field] == b[field] == c[field], "platform/source applicability differs",
                "BLOCKED_PLATFORM_PREREQUISITE")
    require(f["recorder_sources"] == b["recorder_sources"] == c["recorder_sources"], "recorder source differs")
    for field in ("code_audit", "documentation_basis", "parent_establishment_evidence"):
        require(q[field] == c[field], "independent evidence differs")
    _sorted_unique(w["publisher_sources"], "repository_relative_path")
    _sorted_unique(f["recorder_sources"], "repository_relative_path")
    context, parents, paths = w["platform_context"], w["parent_directories"], w["publication_paths"]
    domain = p["execution_domain"]
    require(context["host"] == domain["host_identity"] and
            context["runtime_identity_digest"] == digest(s["runtime_identity"]), "host/runtime binding",
            "BLOCKED_PLATFORM_PREREQUISITE")
    for parent in parents.values():
        require(parent["identity"]["volume"] == context["volume"], "cross-volume parent")
    final, staging = p["publication_paths"]["final"], p["publication_paths"]["staging"]
    ledger = domain["durable_ledger_root"]
    expected_paths = {"final": final, "staging": staging,
                      "study_reservation": str(PureWindowsPath(ledger) / STUDY),
                      "target_reservation": final + ".reservation.json",
                      "completion_marker": final + ".completed.json",
                      "authorization": str(PureWindowsPath(ledger) / (STUDY + ".authorization.json")),
                      "durable_ledger_root": ledger, "flat_record_prefix": STUDY + "."}
    require(paths == expected_paths and p["publication_paths"]["reservation"] == paths["study_reservation"], "path derivation differs")
    expected_parents = {"repository": domain["canonical_repository_path"], "git_common": domain["canonical_git_common_dir"],
                        "ledger": ledger, "output": str(PureWindowsPath(final).parent)}
    require({k: v["path"] for k, v in parents.items()} == expected_parents
            and str(PureWindowsPath(staging).parent) == expected_parents["output"], "parent roles differ")
    require(PureWindowsPath(final).is_relative_to(PureWindowsPath(expected_parents["repository"]))
            and PureWindowsPath(ledger).is_relative_to(PureWindowsPath(expected_parents["git_common"])), "escaped publication domain")
    require(q["status"] == "ACCEPTED" and b["process_exit_code"] == 0
            and b["recording_status"] == "COMPLETE" and b["isolated_attempt_id"] != "s2em.001",
            "platform report not accepted", "BLOCKED_PLATFORM_PREREQUISITE")
    case_ids = [v["case_id"] for v in f["cases"]]
    require(bool(case_ids) and len(set(case_ids)) == len(case_ids)
            and case_ids == [v["case_id"] for v in b["cases"]], "platform case inventory differs")
    study_ids = {STUDY, *(item["cell_id"] for item in p["registry_payload"]["cell_plans"])}
    require(all(identifier not in study_ids and not identifier.startswith(STUDY + ".")
                for identifier in (*case_ids, b["isolated_attempt_id"])), "platform attempt aliases study")
    gates = ["G1", "G2", "G3", "G4", "G5"]
    require([v["gate_id"] for v in q["gates"]] == gates, "gate inventory differs")
    for spec, observed in zip(f["cases"], b["cases"], strict=True):
        require(bool(spec["gates"]) and spec["gates"] == sorted(set(spec["gates"])), "case gate order")
        require(observed["status"] == "OBSERVED_COMPLETE", "missing platform case", "BLOCKED_PLATFORM_PREREQUISITE")
        failure = observed["first_native_failure"]
        require(failure is None or failure["case_id"] == spec["case_id"], "native failure source differs")
    for gate in q["gates"]:
        require(gate["status"] == "ACCEPTED", "platform gate open", "BLOCKED_PLATFORM_PREREQUISITE")
        _sorted_unique(gate["basis_artifacts"], "path")
        selected = gate["case_ids"]
        require(selected == [x for x in case_ids if x in selected]
                and len(selected) == len(set(selected)), "gate case order differs")
        require(all(gate["gate_id"] in f["cases"][case_ids.index(x)]["gates"] for x in selected), "gate references unrelated case")
        require(gate["gate_id"] not in ("G2", "G3", "G5") or bool(selected), "gate lacks original observation")
    assumptions = q["residual_assumptions"]
    require(bool(assumptions) and len(assumptions) == len(set(assumptions)), "missing residual assumptions")
    pins = _TRUSTED_ADMISSION.get()
    require(type(pins) is frozenset and c["record_digest"] in pins,
            "no independently reviewed admission context installed", "BLOCKED_PLATFORM_PREREQUISITE")
    # The trusted context seals the independent semantic review, including raw
    # trace interpretation, original authorization and guarantee coverage. No
    # submitted status, callback or file digest can install this trust root.
    return value
