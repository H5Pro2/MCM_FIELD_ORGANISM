"""Lossless shared JSON evidence. Intern only bytes actually supplied by each arm."""
import hashlib
import json
import os
from pathlib import Path

from tools import _memory_checkpoint as c
from tools import _media_restart_work as w
from tools import _media_restart_reservations as reservations
from tools import _media_restart_serialization as serialization
from tools import _media_publication_plan as publication
from tools import _media_checkpoint_budget_profile as profiles

VERSION = "media.restart-evidence.v5-publication-plan"
FAILURE_BYTES = 4096
FAILURE_RESERVE = 2 * FAILURE_BYTES
LIMITS = dict(total=4194304, metadata=131072, sources=327680,
              shared=393216, verification=262144)
require = w.require


def canonical(value):
    return serialization.canonical(value)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Store:
    def __init__(self, root, external=(), *, future=(), publication_plan=None, budget_profile=None):
        self.profile = profiles.bind(budget_profile)
        self.root = Path(root).resolve()
        self.external = tuple(external)
        self.future = reservations.bind(future)
        self.context = dict(phase="ADMINISTRATION", event=None, completed=0)
        self.failure_path = None
        self.plan = None if publication_plan is None else publication.Plan.bind(publication_plan)
        if self.plan is not None:
            require(self.plan.profile_digest == (None if self.profile is None else profiles.digest()),
                    "MEDIA_PLAN_PROFILE_BINDING")
        self._plan_seen = {}
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root/"objects").mkdir(exist_ok=True)

    @property
    def limits(self):
        return dict(LIMITS) if self.profile is None else self.profile.limits

    def publish_profile(self):
        require(self.profile is not None, "MEDIA_BUDGET_PROFILE_REQUIRED")
        self._write(self.root/"budget-profile.json", canonical(profiles.payload()), "metadata")

    def verify_budget_profile(self):
        if self.profile is None:
            return
        path = self.root/"budget-profile.json"
        require(path.is_file(), "MEDIA_BUDGET_PROFILE_MISSING")
        raw = serialization.read_bounded(path, 61440)
        require(raw == canonical(profiles.payload()) and sha(raw) == profiles.digest(),
                "MEDIA_BUDGET_PROFILE_CHANGED")

    def ledger(self, extra=()):
        rows = []
        seen = set()
        for path in sorted(self.root.rglob("*")):
            if not path.is_file():
                continue
            size = path.stat().st_size
            role = "metadata"
            if path.parent.name == "objects":
                value = json.loads(serialization.read_bounded(path))
                role = value["class"]
            elif path.suffix == ".py":
                role = "sources"
            rows.append(dict(path=path.relative_to(self.root).as_posix(), bytes=size, category=role))
            seen.add(path.resolve())
        for ref in self.external:
            path = Path(ref["path"]).resolve()
            require(path not in seen, "MEDIA_DUPLICATE_EXTERNAL")
            seen.add(path)
            require(path.stat().st_size == ref["bytes"], "MEDIA_EXTERNAL_CHANGED")
            digest, size = hashlib.sha256(), 0
            with path.open("rb") as stream:
                while chunk := stream.read(65536):
                    size += len(chunk)
                    require(size <= ref["bytes"], "MEDIA_EXTERNAL_CHANGED")
                    digest.update(chunk)
            require(size == ref["bytes"] and digest.hexdigest() == ref["sha256"], "MEDIA_EXTERNAL_CHANGED")
            rows.append(dict(path=str(path), bytes=size, category=ref["category"]))
        rows.extend(extra)
        totals = {k: sum(x["bytes"] for x in rows if x["category"] == k)
                  for k in ("metadata", "sources", "verification", "native", "field", "nj", "formations", "generations")}
        totals["shared"] = sum(totals[k] for k in ("sources", "nj", "formations", "generations"))
        totals["total"] = sum(x["bytes"] for x in rows)
        result = dict(files=rows, totals=totals, limits=self.limits,
                    violations=[k for k, cap in self.limits.items() if totals[k] > cap])
        if self.profile is not None:
            result["budget_profile_digest"] = profiles.digest()
        return result

    def budget(self, extra=(), *, emergency=False):
        return reservations.assess(self.ledger(extra), self.future,
                                   0 if emergency else FAILURE_RESERVE)

    def preflight(self):
        require(self.plan is not None, "PUBLICATION_PLAN_REQUIRED")
        return self.plan.preflight(self.ledger(), self.future, self.future, FAILURE_BYTES)

    def _offer(self, role, path, category, size):
        if self.plan is None:
            return
        slot = self.plan.offer(role, category, size)
        seen = self._plan_seen.setdefault(slot[0], set())
        key = (role, str(path))
        require(key in seen or len(seen) < slot[2], "PUBLICATION_POSITION_COUNT")
        seen.add(key)

    def _write(self, path, raw, category, *, emergency=False, role=None):
        require(path.resolve().is_relative_to(self.root) and not path.exists(), "MEDIA_PUBLICATION_CONFLICT")
        if self.profile is not None and not emergency:
            profiles.check_item(category, len(raw))
        if not emergency:
            self._offer(role or path.resolve().relative_to(self.root).as_posix(), path, category, len(raw))
        pending = path.with_name(path.name+".pending")
        rows = [dict(path=p.resolve().relative_to(self.root).as_posix(), bytes=len(raw), category=category)
                for p in (pending, path)]
        current = self.ledger()
        reserve = 0 if emergency else FAILURE_RESERVE
        before = self.budget(emergency=emergency)
        alternatives = publication.transaction(current, rows, self.future, self.future,
                                                0 if emergency else FAILURE_BYTES)
        proposed = alternatives["success"]
        blocking = ([key for key in alternatives["violations"] if key in self.limits]
                    if emergency else alternatives["violations"])
        require(not blocking, "MEDIA_STORE_BUDGET", dict(
            version=VERSION, primary_code="MEDIA_STORE_BUDGET", **self.context,
            evidence_class=category, current=current["totals"],
            requested_bytes=len(raw), publication_copies=2, requested_growth=2*len(raw),
            reserved_failure_bytes=reserve, prospective=proposed["charged"],
            future_before=before["future"], future_after=proposed["future"],
            reserved_administrative_closure_bytes=proposed["future_bytes"],
            limits=self.limits, violations=alternatives["violations"],
            publication_role=role, path=path.relative_to(self.root).as_posix(),
            failure_peaks=[{k: x["charged"][k] for k in {"metadata", "total", category}}
                           for x in alternatives["failure"]]))
        with pending.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(pending, path)
        pending.unlink()

    def intern(self, value, category, role=None):
        raw = self.encode({"class": category, "value": value}, category)
        # Digest equality alone is insufficient: compare available canonical contents.
        digest = sha(raw)
        path = self.root/"objects"/(digest+".json")
        self._offer(role, path, category, len(raw))
        if path.exists():
            require(serialization.read_bounded(path) == raw, "MEDIA_OBJECT_CONFLICT")
        else:
            self._write(path, raw, category, role=role)
        return {"$media_object": digest, "class": category, "bytes": len(raw)}

    def pack(self, value, prefix=""):
        def visit(node, key=None, trail=""):
            role = prefix+"#"+trail
            if isinstance(node, dict):
                if key in ("manifest", "binding", "runtime_config", "initial"):
                    return self.intern(node, "metadata", role)
                if key == "states":
                    return self.intern({k: self.intern(v, "native", role+"/"+k) for k, v in node.items()}, "metadata", role)
                if key == "field" and "layer" in node:
                    return self.intern(node, "field", role)
                if "verification_digest" in node:
                    return self.intern(node, "verification", role)
                if key in ("formation", "generations") and node:
                    return self.intern(node, "formations" if key == "formation" else "generations", role)
                if key == "nj" and node:
                    return self.intern(node, "nj", role)
                result = {k: visit(v, k, trail+"/"+k) for k, v in node.items()}
                return self.intern(result, "metadata", role) if key in ("core", "prefix") else result
            if isinstance(node, (list, tuple)):
                if key == "source_receipts":
                    return self.intern([self.intern(v, "nj", role+"/"+str(i)) for i, v in enumerate(node)], "metadata", role)
                if key in ("inputs", "scans"):
                    return self.intern([self.intern(v, "native", role+"/"+str(i)) for i, v in enumerate(node)], "metadata", role)
                if key == "rows":
                    return self.intern([self.intern(visit(row, trail=trail+"/"+str(i)), "native", role+"/"+str(i)) for i, row in enumerate(node)], "metadata", role)
                if key == "selections":
                    return self.intern([self.intern(v, "metadata", role+"/"+str(i)) for i, v in enumerate(node)], "metadata", role)
                return [visit(v, trail=trail+"/"+str(i)) for i, v in enumerate(node)]
            return node
        return visit(value)

    def resolve(self, value):
        meter = serialization.Meter()
        def visit(node, depth=0, active=frozenset()):
            require(depth <= 64, "MEDIA_REFERENCE_DEPTH")
            if isinstance(node, dict):
                if "$media_object" in node:
                    require(set(node) == {"$media_object", "class", "bytes"}, "MEDIA_REFERENCE_FORM")
                    h = node["$media_object"]
                    require(type(h) is str and len(h) == 64 and all(x in "0123456789abcdef" for x in h)
                            and h not in active, "MEDIA_REFERENCE_CYCLE_OR_PATH")
                    path = self.root/"objects"/(h+".json")
                    require(path.is_file(), "MEDIA_REFERENCE_MISSING")
                    raw = serialization.read_bounded(path)
                    require(len(raw) == node["bytes"] and sha(raw) == h, "MEDIA_REFERENCE_DIGEST")
                    item = json.loads(raw)
                    require(set(item) == {"class", "value"} and item["class"] == node["class"]
                            and canonical(item) == raw, "MEDIA_REFERENCE_CLASS")
                    return visit(item["value"], depth+1, active | {h})
                meter.container(len(node))
                result = {}
                for k, v in node.items():
                    meter.atom(k)
                    meter.charge(1)
                    result[k] = visit(v, depth+1, active)
                return result
            if isinstance(node, list):
                meter.container(len(node))
                return [visit(v, depth+1, active) for v in node]
            meter.atom(node)
            return node
        result = visit(value)
        require(len(canonical(result)) <= 4194304, "MEDIA_RESOLVED_SIZE")
        return result

    def read(self, path):
        path = Path(path).resolve()
        require(path.is_relative_to(self.root), "MEDIA_READ_PATH")
        value = json.loads(serialization.read_bounded(path))
        if self.profile is not None:
            self.verify_budget_profile()
            require(type(value) is dict and set(value) == {"budget_profile_digest", "value"}
                and value["budget_profile_digest"] == profiles.digest(), "MEDIA_RECORD_PROFILE_BINDING")
            value = value["value"]
        return self.resolve(value)

    def encode(self, value, category, limit=serialization.MAX_BYTES):
        try:
            return serialization.canonical(value, limit)
        except w.RestartError as exc:
            if exc.code == "MEDIA_SERIALIZATION_LIMIT":
                details = dict(exc.details or {}, primary_code=exc.code, **self.context,
                               evidence_class=category, current=self.ledger()["totals"])
                raise w.RestartError(exc.code, details) from exc
            raise

    def publish(self, path, value):
        self.verify_budget_profile()
        original = self.encode(value, "expanded_record")
        path = Path(path)
        packed = self.pack(value, path.resolve().relative_to(self.root).as_posix())
        require(canonical(self.resolve(packed)) == original, "MEDIA_PACK_ROUNDTRIP")
        if self.profile is not None:
            packed = dict(budget_profile_digest=profiles.digest(), value=packed)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._write(path, self.encode(packed, "metadata"), "metadata")

    def failure(self, path, value):
        # Use the reserved path directly: no interning, recursive ledger, or retry.
        if self.failure_path is not None:
            require(Path(path) == self.failure_path, "MEDIA_SECOND_FAILURE_PUBLICATION")
            return
        if self.profile is not None:
            self.verify_budget_profile()
            value = dict(budget_profile_digest=profiles.digest(), value=value)
        raw = self.encode(value, "metadata", FAILURE_BYTES)
        require(len(raw) <= FAILURE_BYTES, "MEDIA_FAILURE_FORM_SIZE",
                dict(actual=len(raw), limit=FAILURE_BYTES))
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._write(path, raw, "metadata", emergency=True)
        self.failure_path = path
