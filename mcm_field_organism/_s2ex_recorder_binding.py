"""Private S2-EU/S2-EW value bindings; no file reads or native initialization."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PureWindowsPath
from types import MappingProxyType
import base64
import re

from ._s2er_publication_records import (
    BACKEND, EO_DIGEST, EQ_DIGEST, canonical_path, digest, encoded, loads, raw_digest, require,
)


EU_DIGEST = "2792f3b63d6021922cf2484b0084172904e1f81ac2cac23367a4d07a6b21a3e3"
EW_DIGEST = "92780addeb994b4bc5c4a5bd914fdc32441ff02e50257c9b0ef954ff1e01bf5c"
EZ_SHA256 = "666f3d6616fce5b1d1dfd445ee53099041892b33449ad700b5fa7a8aea6b4a17"
EZ_BYTES = 50408
ATTEMPT = "s2em.002"
CASES = tuple(f"p{i:02d}" for i in range(1, 14))
PHASES = tuple(f"E{i}" for i in range(9))


def record(schema: str, **fields) -> dict:
    value = {"schema_version": schema, **fields}
    return {**value, "record_digest": digest(value)}


def checked_record(value: dict, fields=None) -> dict:
    require(type(value) is dict, "record object required")
    if fields is not None:
        require(set(value) == set(fields), "record fields differ")
    require(value.get("record_digest") == digest({k: v for k, v in value.items()
                                                 if k != "record_digest"}), "record digest differs")
    return value


def clone(value):
    return loads(encoded(value))


def b64(raw: bytes) -> str:
    require(type(raw) is bytes, "immutable bytes required")
    return base64.b64encode(raw).decode("ascii")


def unb64(value: str) -> bytes:
    require(type(value) is str, "base64 text required")
    raw = base64.b64decode(value, validate=True)
    require(b64(raw) == value, "noncanonical base64")
    return raw


def utf16_key(value: str):
    raw = value.encode("utf-16-be")
    return tuple(int.from_bytes(raw[i:i + 2], "big") for i in range(0, len(raw), 2))


def local_id(value: str) -> str:
    require(type(value) is str and re.fullmatch(r"[a-z0-9][a-z0-9.-]*", value) is not None,
            "invalid local identity")
    return value


@dataclass(frozen=True, slots=True)
class Limits:
    """Literal ceilings must be independently pinned before any execution."""

    calls: int
    trace_bytes: int
    buffer_bytes: int
    stream_bytes: int

    def __post_init__(self):
        require(all(type(v) is int and v > 0 for v in
                    (self.calls, self.trace_bytes, self.buffer_bytes, self.stream_bytes)),
                "positive exact limits required")


@dataclass(frozen=True, slots=True)
class PathRole:
    case_id: str | None
    role: str
    path: str
    lifecycle: str


class PathInventory:
    def __init__(self, ew: dict, parents: dict, source_paths: tuple[str, ...], rows: list):
        require(set(parents) == {"repository", "git_common", "ledger", "output"},
                "exact four parent roles required")
        roots = {k: canonical_path(v["path"]) for k, v in parents.items()}
        generated = []
        for template in ew["role_templates"]:
            scope = template["case_scope"]
            cases = (None,) if scope == "NONE" else CASES[:12 if scope == "p01-p12" else 13]
            for case in cases:
                parent, name = template["path_template"].split("/", 1)
                name = name.replace("<case_id>", case or "")
                path = canonical_path(str(PureWindowsPath(roots[parent]) / name))
                generated.append(PathRole(case, template["role"], path, template["lifecycle"]))
        require(len(generated) == 133, "fixed path inventory differs")
        sources = sorted(set(canonical_path(p) for p in source_paths), key=utf16_key)
        directories = set()
        for path in [PureWindowsPath(p) for p in roots.values()] + [PureWindowsPath(p).parent for p in sources]:
            directories.update(str(p) for p in (path, *path.parents))
        for prefix, paths, lifecycle in (
            ("source", sources, "EXISTING_SOURCE"),
            ("directory", sorted(directories, key=utf16_key), "EXISTING_DIRECTORY"),
        ):
            generated.extend(PathRole(None, f"{prefix}.{i}", p, lifecycle) for i, p in enumerate(paths))
        generated.sort(key=lambda p: (p.case_id or "", utf16_key(p.role)))
        expected = [{"case_id": p.case_id, "role": p.role, "path": p.path} for p in generated]
        require(type(rows) is list and encoded(rows) == encoded(expected), "path closure differs")
        require(len({p.path for p in generated}) == len(generated), "path roles collide")
        require(len({p.path.casefold() for p in generated}) == len(generated), "case alias in inventory")
        self.by_path = MappingProxyType({p.path: p for p in generated})
        self.by_key = MappingProxyType({(p.case_id, p.role): p for p in generated})
        edges = {}
        for edge in ew["rename_edges"]:
            cases = (None,) if edge["case_scope"] == "NONE" else CASES[:12 if edge["case_scope"] == "p01-p12" else 13]
            for case in cases:
                source, target = self.get(case, edge["from"]), self.get(case, edge["to"])
                require(PureWindowsPath(source.path).parent == PureWindowsPath(target.path).parent,
                        "cross-parent rename")
                edges[source.path] = target.path
        self.edges = MappingProxyType(edges)

    def get(self, case: str | None, role: str) -> PathRole:
        require((case, role) in self.by_key, "unknown path role")
        return self.by_key[(case, role)]

    def resolve(self, path: str) -> PathRole:
        canonical_path(path)
        require(path in self.by_path, "unbound native path")
        return self.by_path[path]


@dataclass(frozen=True, slots=True)
class RecorderBinding:
    """Immutable envelopes, never trust an acceptance flag supplied by a worker."""

    eu_raw: bytes
    ew_raw: bytes
    profile_raw: bytes
    run_raw: bytes
    source_raw: bytes
    read_references_raw: bytes
    actors_raw: bytes
    limits: Limits

    def values(self):
        result = []
        for raw, expected in ((self.eu_raw, EU_DIGEST), (self.ew_raw, EW_DIGEST)):
            value = loads(raw)
            require(type(value) is dict, "contract object required")
            require(value.get("artifact_digest") == expected == digest({k: v for k, v in value.items()
                                                                        if k != "artifact_digest"}),
                    "recorder contract drift")
            result.append(value)
        eu, ew = result
        profile, run, source = (checked_record(loads(raw)) for raw in
                                (self.profile_raw, self.run_raw, self.source_raw))
        checked_record(run, ew["inheritance"]["run_binding"])
        checked_record(source, eu["data_forms"]["PlatformSourceManifest"])
        checked_record(profile, ("schema_version", "backend_contract_id", "s2eo_contract_digest", "s2eq_contract_digest",
                                 "isolation_contract", "recorder_format_contract", "publisher_sources", "recorder_sources",
                                 "platform_context", "parent_directories", "cases", "record_digest"))
        require(profile["schema_version"] == "s2eq.platform-profile.v1" and
                source["schema_version"] == "s2eu.source-manifest.v1", "envelope schema differs")
        require(profile["backend_contract_id"] == BACKEND and profile["s2eo_contract_digest"] == EO_DIGEST and
                profile["s2eq_contract_digest"] == EQ_DIGEST, "base publication contract differs")
        require(run["schema_version"] == "s2ew.run-binding.v1" and run["attempt_id"] == ATTEMPT,
                "run schema or attempt differs")
        require(run["profile_digest"] == profile["record_digest"] and
                run["source_manifest_digest"] == source["record_digest"], "source/profile binding differs")
        require(profile["publisher_sources"] == source["publisher_sources"] and
                profile["recorder_sources"] == source["recorder_sources"], "source closures differ")
        require(profile["platform_context"]["runtime_identity_digest"] == digest(source["runtime_identity"]),
                "runtime binding differs")
        require([c["case_id"] for c in profile["cases"]] == list(CASES), "case registry differs")
        ref = profile["isolation_contract"]
        require(ref["raw_sha256"] == raw_digest(self.ew_raw) and ref["byte_count"] == len(self.ew_raw),
                "S2-EW isolation reference differs")
        ref = profile["recorder_format_contract"]
        require(ref["raw_sha256"] == EZ_SHA256 and type(ref["byte_count"]) is int and
                ref["byte_count"] == EZ_BYTES, "S2-EZ recorder reference differs")
        for spec in profile["cases"]:
            ref = spec["expected_observation_contract"]
            require(ref["raw_sha256"] == raw_digest(self.eu_raw) and ref["byte_count"] == len(self.eu_raw),
                    "case expectation reference differs")
        refs, actors = loads(self.read_references_raw), loads(self.actors_raw)
        require(type(refs) is list and bool(refs), "independently reviewed read closure required")
        for ref in refs:
            require(set(ref) == {"path", "byte_count", "raw_sha256"}, "read reference fields")
            canonical_path(ref["path"])
            require(type(ref["byte_count"]) is int and ref["byte_count"] > 0 and
                    type(ref["raw_sha256"]) is str and re.fullmatch("[0-9a-f]{64}", ref["raw_sha256"]),
                    "invalid read reference")
        require(len({r["path"] for r in refs}) == len(refs), "duplicate read reference")
        by_path = {r["path"]: r for r in refs}
        repository = PureWindowsPath(profile["parent_directories"]["repository"]["path"])
        require(profile["recorder_format_contract"]["path"] == str(repository / "docs" /
                "S2EZ_STATISCHER_RECORDER_KORREKTURVERTRAG_V1.json"), "recorder contract path differs")
        for source_ref in profile["publisher_sources"] + profile["recorder_sources"]:
            require(set(source_ref) == {"repository_relative_path", "raw_sha256"}, "source reference fields")
            relative = source_ref["repository_relative_path"]
            require(type(relative) is str and "\\" not in relative and ":" not in relative and
                    all(p not in ("", ".", "..") for p in relative.split("/")), "invalid relative source")
            path = canonical_path(str(repository.joinpath(*relative.split("/"))))
            require(path in by_path and by_path[path]["raw_sha256"] == source_ref["raw_sha256"],
                    "source closure missing from read inventory")
        required_refs = [profile["isolation_contract"], profile["recorder_format_contract"],
                         run["parent_establishment_evidence"], run["documentation_basis"],
                         *[c["expected_observation_contract"] for c in profile["cases"]]]
        require(all(ref in refs for ref in required_refs), "required reference missing from read closure")
        require(type(actors) is dict and set(actors) == {"worker", "helper", "supervisor"}, "actor roles differ")
        require(len(set(local_id(v) for v in actors.values())) == 3, "actor identities collide")
        inventory = PathInventory(ew, profile["parent_directories"], tuple(r["path"] for r in refs), run["path_inventory"])
        expected_faults = []
        for case in eu["cases"]:
            trigger = case["trigger"]
            if trigger["operation"] != "NONE":
                expected_faults.append({"case_id": case["case_id"], "phase": case["terminal_phase"],
                                       "operation": trigger["operation"], "role": trigger["role"],
                                       "occurrence": trigger["occurrence"],
                                       "kind": "INJECTED" if case["evidence_kind"] == "INJECTED" else "NATIVE_EXPECTATION",
                                       "expected_error": trigger["error_code"]})
        require(encoded(run["fault_schedule"]) == encoded(expected_faults), "fault schedule differs")
        expected_payloads = []
        for case in CASES[:12]:
            for prefix in ("S2EU PLATFORM FIXTURE ", "S2EU OCCUPIED "):
                raw = (prefix + case + "\n").encode("ascii")
                expected_payloads.append({"case_id": case, "bytes_base64": b64(raw), "byte_count": len(raw),
                                          "raw_sha256": raw_digest(raw)})
        require(encoded(run["payload_bytes"]) == encoded(expected_payloads), "literal payload binding differs")
        return eu, ew, profile, run, source, refs, actors, inventory

    def identity(self) -> str:
        return digest({"envelopes": [raw_digest(r) for r in (self.eu_raw, self.ew_raw, self.profile_raw,
                       self.run_raw, self.source_raw, self.read_references_raw, self.actors_raw)],
                       "limits": {k: getattr(self.limits, k) for k in ("calls", "trace_bytes", "buffer_bytes", "stream_bytes")}})
