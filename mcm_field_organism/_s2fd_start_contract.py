"""Private S2-FD start values and static budget derivation; no file I/O.

An internally consistent package is not an execution authorization. Native
admission remains an independent prerequisite owned by the calling reviewer.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import json
from pathlib import PureWindowsPath
import re


ATTEMPT = "s2em.002"
CONTRACT_DIGEST = "26a40bfcf3cf04b996e2203abbefd1244290d59121dfe8e0dc1780330e881df8"
METADATA_DIGEST = "b13e2a3a851f47ae0a2c65e1e03cb8aaccfac8e236ed242cef108b2c50d1af03"
METADATA_SHA256 = "afc36f8b5c847443af71f924d9e92ec6af0fa627c4aba8cac55acc1664dfb590"
LAYOUT_DIGEST = "17bbc27e533ea858780c061ef8fcb1a25f933e14fb2886ab73bbde383cf926a4"
REPOSITORY = r"C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace"
PARENTS = {
    "repository": REPOSITORY, "git_common": REPOSITORY + r"\.git",
    "ledger": REPOSITORY + r"\.git\mcm-execution-ledger",
    "output": REPOSITORY + r"\reports",
}
INFRASTRUCTURE = (
    "mcm_field_organism/_s2fd_start_contract.py",
    "mcm_field_organism/_s2fd_start_owner.py",
    "mcm_field_organism/_s2fd_completion_observer.py",
    "tools/run_s2fd_isolated_platform_once.py",
)
PARENT_ROLES = {"starter": "completion_observer", "supervisor": "starter", "worker": "supervisor"}
ENVELOPES = (
    "eu_raw", "ew_raw", "profile_raw", "run_raw", "source_raw",
    "read_references_raw", "actors_raw", "native_layout_raw",
    "authorization_raw", "preregistration_raw", "budget_inputs_raw",
)
LIMITS = ("calls", "trace_bytes", "buffer_bytes", "stream_bytes")
STATUSES = (
    "BLOCKED_PREREQUISITE", "ALREADY_CONSUMED", "BINDING_REJECTED",
    "ABORTED_INCOMPLETE", "COMPLETION_UNCONFIRMED", "ISOLATED_RECORDING_COMPLETE",
)
FORMS = {
    "metadata-admission": "metadata_file metadata_record_digest layout_contract_file layout_digest intended_runtime_digest encoder_sources parent_establishment_file parent_set_digest documentation_basis_file reviewer_identity decision",
    "budget-certificate": "implementation_sources recorder_read_refs runtime_read_refs path_inventory_digest derivation_rows size_dependency_order logical_calls_by_domain native_calls_by_domain bytes_by_domain peak_live_bytes_upper process_bounds limits admissible_host_envelope",
    "budget-row": "source_path source_sha256 qualified_symbol loop_or_branch domain input_bounds iteration_bound primitive_cost derived_upper assumptions",
    "start-package": "attempt_id source_commit infrastructure_sources recorder_binding_digest envelope_files runtime_identity_digest metadata_admission budget_certificate parent_set_digest owner_path_roles actor_roles process_contract",
    "start-admission": "attempt_id start_package_digest count reviewer_identity explicit_execution_authorization",
    "dispatch": "attempt_id start_package_digest start_admission_digest owner_role state",
    "dispatch-seal": "attempt_id start_package_digest dispatch_record_digest state",
    "observed-completion": "attempt_id start_package_digest dispatch_seal_digest process_observations worker_exit_code supervisor_exit_code starter_exit_code live_completion manifest_file marker_file control_file control_close_observed status failure_detail",
    "process-contract": "role interpreter_file argv cwd environment_allowlist import_source_refs inherited_channel_roles parent_role maximum_instances startup_deadline_ms completion_deadline_ms shutdown_deadline_ms maximum_ipc_bytes maximum_ipc_frames process_identity_rule",
    "process-observation": "role package_digest parent_role owned_handle_generation creation_identity exit_code pipe_eof_confirmed close_status",
}


class StartError(ValueError):
    def __init__(self, status, detail):
        super().__init__(detail)
        self.status = status


def require(condition, detail, status="BINDING_REJECTED"):
    if not condition:
        raise StartError(status, detail)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def _invalid_number(value):
    raise StartError("BINDING_REJECTED", "non-integer or nonfinite number: " + value)


def loads(raw):
    require(type(raw) is bytes, "immutable original bytes required")
    try:
        return json.loads(raw, object_pairs_hook=_pairs, parse_float=_invalid_number,
                          parse_constant=_invalid_number)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise StartError("BINDING_REJECTED", "invalid JSON") from error


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, separators=(",", ":")).encode("ascii")


def sha(raw):
    require(type(raw) is bytes, "hash requires bytes")
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(encoded(value))


def fields(value, names):
    require(type(value) is dict and set(value) == set(names), "closed fields differ")
    return value


def positive(value):
    require(type(value) is int and value > 0, "positive exact integer required")
    return value


def hash_text(value):
    require(type(value) is str and re.fullmatch("[0-9a-f]{64}", value) is not None, "invalid SHA256")
    return value


def text(value):
    require(type(value) is str and bool(value) and "\x00" not in value, "nonempty text required")
    return value


def canonical_path(value):
    text(value)
    path = PureWindowsPath(value)
    require(re.fullmatch(r"[A-Z]:\\.*", value) is not None and str(path) == value,
            "canonical absolute DOS path required")
    require("/" not in value and ":" not in value[2:], "path alias")
    for part in path.parts[1:]:
        require(part not in (".", "..") and not part.endswith((".", " ")) and
                not any(ord(c) < 32 or c in '<>"|?*' for c in part), "ambiguous path")
        require(not re.fullmatch(r"CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9]", part.split(".")[0].upper()),
                "reserved path component")
    return value


def file_ref(value):
    fields(value, ("path", "byte_count", "raw_sha256"))
    canonical_path(value["path"])
    positive(value["byte_count"])
    hash_text(value["raw_sha256"])
    return value


def refs(values):
    require(type(values) is list and bool(values), "nonempty source references required")
    for value in values:
        file_ref(value)
    require(len({v["path"].casefold() for v in values}) == len(values), "duplicate source path")
    return values


def record(kind, **values):
    value = {"schema_version": "s2fd." + kind + ".v1", **values}
    value["record_digest"] = digest(value)
    return checked(kind, value)


def checked(kind, value):
    require(kind in FORMS, "unknown private record")
    fields(value, ("schema_version", *FORMS[kind].split(), "record_digest"))
    require(value["schema_version"] == "s2fd." + kind + ".v1", "schema differs")
    require(hash_text(value["record_digest"]) == digest({k: v for k, v in value.items()
                                                      if k != "record_digest"}), "record digest differs")
    if "attempt_id" in value:
        require(value["attempt_id"] == ATTEMPT, "attempt differs")
    if kind == "observed-completion":
        require(value["status"] in STATUSES and type(value["control_close_observed"]) is bool,
                "completion status/type differs")
        if value["status"] == "ISOLATED_RECORDING_COMPLETE":
            require(value["failure_detail"] is None and all(value[k] is not None for k in
                    FORMS[kind].split() if k != "failure_detail"), "missing success evidence")
            require(value["control_close_observed"] is True, "control close unconfirmed")
        else:
            text(value["failure_detail"])
            require(all(k in value["failure_detail"] for k in FORMS[kind].split()
                        if value[k] is None), "missing evidence must be named in failure_detail")
    return value


def original(ref, originals):
    file_ref(ref)
    require(ref["path"] in originals, "missing original: " + ref["path"], "BLOCKED_PREREQUISITE")
    raw = originals[ref["path"]]
    require(type(raw) is bytes and len(raw) == ref["byte_count"] and sha(raw) == ref["raw_sha256"],
            "original byte binding differs: " + ref["path"])
    return raw


def owner_roles():
    return [
        {"role": "launch.dispatch", "path": PARENTS["ledger"] + r"\s2fd.s2em.002.dispatch.json",
         "owner": "completion_observer"},
        {"role": "launch.dispatch.seal", "path": PARENTS["ledger"] + r"\s2fd.s2em.002.dispatch.seal.json",
         "owner": "completion_observer"},
    ]


def _source_sites(raw):
    """Source locations, never an import or evaluation of the frozen module."""
    tree = ast.parse(raw)
    sites = {}

    def visit(node, scope):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            scope = (*scope, node.name)
        if isinstance(node, (ast.Call, ast.For, ast.While, ast.comprehension)):
            key = ".".join(scope) or "<module>"
            location = node.target if isinstance(node, ast.comprehension) else node
            label = f"{key}:{location.lineno}:{location.col_offset}:{type(node).__name__}"
            sites[label] = key
        for child in ast.iter_child_nodes(node):
            visit(child, scope)

    visit(tree, ())
    return sites


def _bound_expression(expression, variables):
    """Small nonnegative integer algebra, not eval or project execution."""
    tree = ast.parse(text(expression), mode="eval")

    def calculate(node):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value >= 0:
            return node.value
        if isinstance(node, ast.Name):
            require(node.id in variables, "unbound budget variable")
            value = variables[node.id]
            require(type(value) is int and value >= 0, "invalid budget input")
            return value
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mult, ast.FloorDiv)):
            left, right = calculate(node.left), calculate(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Mult):
                return left * right
            require(right > 0, "zero budget divisor")
            return left // right
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "q":
            require(len(node.args) == 1 and not node.keywords, "invalid chunk expression")
            return (calculate(node.args[0]) + 1048575) // 1048576
        raise StartError("BINDING_REJECTED", "unsupported budget expression")

    return calculate(tree.body)


def derive_budget_certificate(frozen_sources, local_read_refs, schema_bounds, process_plan):
    """Recompute reviewed, source-located bounds; unknown coverage is fatal.

    The static reviewer supplies loop/branch and schema proofs. This function
    checks their exact source sites and integer derivation, not their truth by
    running a fixture. Admission must independently accept these assumptions.
    """
    fields(schema_bounds, ("implementation_sources", "runtime_read_refs", "path_inventory_digest",
                          "derivation_rows", "size_dependency_order", "sizing", "host_envelope"))
    implementations = refs(schema_bounds["implementation_sources"])
    refs(local_read_refs)
    refs(schema_bounds["runtime_read_refs"])
    site_sets = {r["path"]: _source_sites(original(r, frozen_sources)) for r in implementations
                 if r["path"].endswith(".py")}
    source_hashes = {r["path"]: r["raw_sha256"] for r in implementations}
    require(type(frozen_sources) is dict and all(type(v) is bytes for v in frozen_sources.values()),
            "frozen source bytes required")
    covered = {p: set() for p in site_sets}
    rows, totals = [], {}
    require(type(schema_bounds["derivation_rows"]) is list and schema_bounds["derivation_rows"],
            "missing source-derived costs", "BLOCKED_PREREQUISITE")
    for item in schema_bounds["derivation_rows"]:
        row = checked("budget-row", item)
        path, symbol = row["source_path"], row["qualified_symbol"]
        require(path in source_hashes and row["source_sha256"] == source_hashes[path], "budget source differs")
        require(path in site_sets and row["loop_or_branch"] in site_sets[path] and
                site_sets[path][row["loop_or_branch"]] == symbol, "budget source site differs")
        require(type(row["input_bounds"]) is dict and type(row["assumptions"]) is list and
                bool(row["assumptions"]) and all(type(s) is str and s for s in row["assumptions"]),
                "explicit static proof assumptions required")
        for key, value in row["input_bounds"].items():
            text(key)
            require(type(value) is int and value >= 0, "non-integer budget input")
        iterations = positive(row["iteration_bound"])
        upper = iterations * _bound_expression(row["primitive_cost"], row["input_bounds"])
        require(type(row["derived_upper"]) is int and row["derived_upper"] == upper,
                "derived cost differs")
        domain = text(row["domain"])
        require(domain.split(":", 1)[0] in ("native", "logical", "bytes", "validation", "memory"),
                "unknown cost unit")
        key = (row["loop_or_branch"], domain)
        require(key not in covered[path], "duplicate cost row")
        covered[path].add(key)
        totals[domain] = totals.get(domain, 0) + upper
        rows.append(row)
    for path, sites in site_sets.items():
        require({key[0] for key in covered[path]} == set(sites), "incomplete static source coverage: " + path)
    order = schema_bounds["size_dependency_order"]
    require(order == ["sources", "fixtures", "case_traces", "worker_raw", "transcript",
                      "supervisor_control", "control_spool"], "cyclic or reordered sizing")
    sizing = fields(schema_bounds["sizing"], ("nodes", "buffer_upper", "peak_live_bytes_upper"))
    require(type(sizing["nodes"]) is list and len(sizing["nodes"]) == len(order), "size DAG differs")
    extents = {"source_bytes": sum(r["byte_count"] for r in local_read_refs), "fixture_bytes": 528}
    byte_values = {}
    for name, item in zip(order, sizing["nodes"]):
        fields(item, ("name", "expression", "upper"))
        require(item["name"] == name and name not in extents, "size node differs")
        value = _bound_expression(item["expression"], extents)
        require(positive(item["upper"]) == value, "size upper differs")
        extents[name] = byte_values[name] = value
    require(byte_values["sources"] >= extents["source_bytes"] and byte_values["fixtures"] >= 528,
            "source/fixture byte undercount")
    require(byte_values["worker_raw"] >= byte_values["case_traces"] and
            byte_values["transcript"] >= byte_values["worker_raw"], "capture byte undercount")
    # Even one-byte pipe fragments each carry an envelope. The reviewed formula
    # must account for framing; a raw-byte-only transcript bound is invalid.
    require(byte_values["transcript"] >= 4 * byte_values["worker_raw"], "missing base64/framing cost")
    native = {k.split(":", 1)[1]: v for k, v in totals.items() if k.startswith("native:")}
    logical = {k.split(":", 1)[1]: v for k, v in totals.items() if k.startswith("logical:")}
    domains = [f"p{i:02d}" for i in range(1, 14)] + ["control", "control_spool", "starter", "observer"]
    require(set(native) == set(domains) and set(logical) == set(domains), "missing call domains")
    require(all(logical[k] >= native[k] > 0 for k in domains), "logical/native cost mismatch")
    require(any(k.startswith("validation:") for k in totals) and any(k.startswith("memory:") for k in totals),
            "validation and memory work must be counted")
    peak = positive(sizing["peak_live_bytes_upper"])
    require(peak >= max(byte_values.values()) and peak >= sum(v for k, v in totals.items()
                                                             if k.startswith("memory:")), "peak memory undercount")
    limits = {"calls": max(logical.values()), "trace_bytes": max(byte_values["case_traces"],
              byte_values["supervisor_control"]), "buffer_bytes": positive(sizing["buffer_upper"]),
              "stream_bytes": max(byte_values["worker_raw"], byte_values["transcript"], byte_values["control_spool"])}
    host = fields(schema_bounds["host_envelope"], (*LIMITS, "peak_live_bytes_upper", "validation_work"))
    for key in LIMITS:
        require(limits[key] <= positive(host[key]), "host resource ceiling exceeded", "BLOCKED_PREREQUISITE")
    require(peak <= positive(host["peak_live_bytes_upper"]) and
            sum(v for k, v in totals.items() if k.startswith("validation:")) <= positive(host["validation_work"]),
            "host work/memory ceiling exceeded", "BLOCKED_PREREQUISITE")
    return record("budget-certificate", implementation_sources=implementations,
                  recorder_read_refs=local_read_refs, runtime_read_refs=schema_bounds["runtime_read_refs"],
                  path_inventory_digest=hash_text(schema_bounds["path_inventory_digest"]), derivation_rows=rows,
                  size_dependency_order=order, logical_calls_by_domain=logical, native_calls_by_domain=native,
                  bytes_by_domain={**byte_values, **totals}, peak_live_bytes_upper=peak,
                  process_bounds=process_plan, limits=limits, admissible_host_envelope=host)


@dataclass(frozen=True, slots=True)
class ValidatedPackage:
    raw: bytes
    originals: tuple[tuple[str, bytes], ...]

    def value(self):
        return loads(self.raw)

    @property
    def identity(self):
        return self.value()["record_digest"]

    def binding(self):
        from ._s2ex_recorder_binding import Limits, RecorderBinding
        value, originals = self.value(), dict(self.originals)
        envelopes = value["envelope_files"]
        return RecorderBinding(**{k: original(envelopes[k], originals) for k in ENVELOPES[:8]},
                               limits=Limits(**value["budget_certificate"]["limits"]))


def _process_contracts(values, originals, infrastructure):
    require(type(values) is list and [v.get("role") for v in values] == list(PARENT_ROLES), "process roles differ")
    for value in values:
        checked("process-contract", value)
        role = value["role"]
        require(value["parent_role"] == PARENT_ROLES[role] and type(value["maximum_instances"]) is int and
                value["maximum_instances"] == 1, "process ownership/count differs")
        original(value["interpreter_file"], originals)
        require(value["cwd"] == REPOSITORY, "child cwd differs")
        argv = value["argv"]
        require(argv == [value["interpreter_file"]["path"], "-I", "-B", "-S",
                         str(PureWindowsPath(REPOSITORY) / INFRASTRUCTURE[3]), role], "exact child argv required")
        env = value["environment_allowlist"]
        require(type(env) is dict and bool(env) and all(type(k) is str and type(v) is str and
                "\x00" not in k + v and "=" not in k for k, v in env.items()), "invalid environment")
        require(not any(k.upper().startswith(("PYTHON", "MCM", "S2")) for k in env), "environment activation forbidden")
        require(all(k == k.upper() for k in env), "canonical uppercase Windows environment required")
        for key in ("startup_deadline_ms", "completion_deadline_ms", "shutdown_deadline_ms",
                    "maximum_ipc_bytes", "maximum_ipc_frames"):
            positive(value[key])
        require(all(value[k] < 0xFFFFFFFF for k in ("startup_deadline_ms", "completion_deadline_ms", "shutdown_deadline_ms")),
                "deadline exceeds finite native DWORD range")
        require(value["inherited_channel_roles"] == ["parent.control.in", "parent.control.out", "parent.error"],
                "channel roles differ")
        text(value["process_identity_rule"])
        imported = refs(value["import_source_refs"])
        require(all(r in imported for r in infrastructure), "incomplete bootstrap source closure")
        for ref in imported:
            original(ref, originals)


def validate_start_package(package_raw, referenced_raw_files):
    """Pure admission validation; does not inspect a filesystem or native state."""
    package = checked("start-package", loads(package_raw))
    require(encoded(package) == package_raw, "noncanonical start package")
    require(type(referenced_raw_files) is dict and all(type(k) is str and type(v) is bytes
            for k, v in referenced_raw_files.items()), "original byte map required")
    originals = dict(referenced_raw_files)
    require(re.fullmatch("[0-9a-f]{40}", text(package["source_commit"])) is not None, "invalid source commit")
    infrastructure = refs(package["infrastructure_sources"])
    require([r["path"] for r in infrastructure] == [str(PureWindowsPath(REPOSITORY) / p) for p in INFRASTRUCTURE],
            "exact four infrastructure sources required")
    for ref in infrastructure:
        original(ref, originals)
    require(package["owner_path_roles"] == owner_roles(), "external ledger roles differ")
    envelope_refs = fields(package["envelope_files"], ENVELOPES)
    for ref in envelope_refs.values():
        original(ref, originals)
    budget = checked("budget-certificate", package["budget_certificate"])
    limits = fields(budget["limits"], LIMITS)
    for value in limits.values():
        positive(value)
    validated = ValidatedPackage(package_raw, tuple(sorted(originals.items())))
    binding = validated.binding()
    eu, ew, profile, run, source, local_refs, actors, inventory = binding.values()
    require(binding.identity() == hash_text(package["recorder_binding_digest"]), "recorder identity differs")
    require(package["runtime_identity_digest"] == digest(source["runtime_identity"]), "runtime identity differs")
    require(package["actor_roles"] == actors, "inner actors differ")
    require({k: v["path"] for k, v in profile["parent_directories"].items()} == PARENTS, "parent roles differ")
    require(package["parent_set_digest"] == digest(profile["parent_directories"]), "parent digest differs")
    require(len(inventory.edges) == 28 and len(run["payload_bytes"]) == 24, "fixed inventory differs")
    require(sum(p["byte_count"] for p in run["payload_bytes"]) == 528, "fixture byte count differs")
    for ref in refs(local_refs):
        require(any(PureWindowsPath(ref["path"]).is_relative_to(PureWindowsPath(PARENTS[k]))
                    for k in ("repository", "git_common")), "external runtime in recorder reads")
        original(ref, originals)
    require(not any(r["path"] in {p["path"] for p in owner_roles()} for r in local_refs), "owner role leaked")
    for key, schema in (("authorization_raw", "s2fd.inner-authorization.v1"),
                        ("preregistration_raw", "s2fd.inner-review.v1")):
        ref = envelope_refs[key]
        require(ref in local_refs, "inner authorization/review missing from read closure")
        value = loads(original(ref, originals))
        fields(value, ("schema_version", "attempt_id", "profile_digest", "run_binding_digest",
                       "source_manifest_digest", "count", "record_digest"))
        expected = {"schema_version": schema, "attempt_id": ATTEMPT, "profile_digest": profile["record_digest"],
                    "run_binding_digest": run["record_digest"], "source_manifest_digest": source["record_digest"], "count": 1}
        require(type(value["count"]) is int and value == {**expected, "record_digest": digest(expected)},
                "inner admission binding differs")
    admission = checked("metadata-admission", package["metadata_admission"])
    require(admission["decision"] == "ADMITTED", "metadata not admitted", "BLOCKED_PREREQUISITE")
    text(admission["reviewer_identity"])
    metadata = original(admission["metadata_file"], originals)
    require(len(metadata) == 38524 and sha(metadata) == METADATA_SHA256 and
            admission["metadata_record_digest"] == METADATA_DIGEST, "historical metadata differs")
    require(admission["layout_digest"] == LAYOUT_DIGEST and
            admission["intended_runtime_digest"] == package["runtime_identity_digest"] and
            admission["parent_set_digest"] == package["parent_set_digest"], "metadata admission relations differ")
    for key in ("layout_contract_file", "parent_establishment_file", "documentation_basis_file"):
        original(admission[key], originals)
    require(admission["parent_establishment_file"] == run["parent_establishment_evidence"] and
            admission["documentation_basis_file"] == run["documentation_basis"], "parent/durability source differs")
    origin = loads(original(envelope_refs["native_layout_raw"], originals))
    require(admission["encoder_sources"] == origin["encoder_sources"], "encoder provenance differs")
    _process_contracts(package["process_contract"], originals, infrastructure)
    schema_bounds = loads(original(envelope_refs["budget_inputs_raw"], originals))
    require(envelope_refs["budget_inputs_raw"] not in local_refs, "budget input cycle")
    derived = derive_budget_certificate(originals, local_refs, schema_bounds, package["process_contract"])
    require(derived == budget, "budget certificate not derived from frozen sources")
    require(budget["path_inventory_digest"] == digest(run["path_inventory"]), "budget inventory differs")
    require(all(r in budget["implementation_sources"] for r in infrastructure), "budget omitted infrastructure")
    for ref in budget["runtime_read_refs"]:
        original(ref, originals)
    contract_path = str(PureWindowsPath(REPOSITORY) / "docs/S2FD_STATISCHER_STARTINFRASTRUKTUR_VERTRAG_V1.json")
    require(contract_path in originals, "static contract source missing", "BLOCKED_PREREQUISITE")
    contract = loads(originals[contract_path])
    require(contract["artifact_digest"] == CONTRACT_DIGEST == digest({k: v for k, v in contract.items()
                                                                      if k != "artifact_digest"}), "S2-FD contract drift")
    historical_refs = []
    for source_ref in contract["source_evidence"]:
        ref = {"path": str(PureWindowsPath(REPOSITORY) / source_ref["path"]),
               "byte_count": source_ref["byte_count"], "raw_sha256": source_ref["raw_sha256"]}
        original(ref, originals)
        historical_refs.append(ref)
        if ref["path"].endswith(".py"):
            require(ref in budget["implementation_sources"], "budget omitted bound recorder source")
    require(admission["layout_contract_file"] in historical_refs, "unbound layout contract")
    require(admission["metadata_file"]["path"] == str(PureWindowsPath(REPOSITORY) / contract["metadata_binding"]["file_ref"]["path"]),
            "metadata path provenance differs")
    required_paths = {contract_path, *(r["path"] for r in historical_refs), *(r["path"] for r in local_refs)}

    def collect(value):
        if type(value) is dict:
            if set(value) == {"path", "byte_count", "raw_sha256"}:
                original(value, originals)
                required_paths.add(value["path"])
            else:
                for item in value.values():
                    collect(item)
        elif type(value) is list:
            for item in value:
                collect(item)

    collect(package)
    require(set(originals) == required_paths, "extra or missing raw source in start closure")
    require(all(PureWindowsPath(p).is_relative_to(PureWindowsPath(REPOSITORY)) or
                p in {r["path"] for r in budget["runtime_read_refs"]} for p in originals),
            "unbound external original")
    require(all(p["interpreter_file"] in budget["runtime_read_refs"] for p in package["process_contract"]),
            "interpreter absent from runtime budget")
    require(all(p["maximum_ipc_bytes"] >= budget["bytes_by_domain"]["worker_raw"]
                for p in package["process_contract"] if p["role"] == "worker"), "worker output IPC bound too small")
    return validated


def validate_admission(package, raw):
    value = checked("start-admission", loads(raw))
    require(value["start_package_digest"] == package.identity and type(value["count"]) is int and value["count"] == 1,
            "outer admission package/count differs")
    text(value["reviewer_identity"])
    authorization = file_ref(value["explicit_execution_authorization"])
    require(authorization in package.value()["budget_certificate"]["recorder_read_refs"],
            "execution authorization is not the bound inner authorization")
    require(authorization == package.value()["envelope_files"]["authorization_raw"], "authorization source differs")
    original(authorization, dict(package.originals))
    return value
