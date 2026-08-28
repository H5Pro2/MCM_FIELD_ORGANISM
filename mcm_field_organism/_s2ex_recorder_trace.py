"""Private bounded E0-E8 recorder and read-only trace acceptance."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import PureWindowsPath
from threading import RLock

from ._s2er_publication_records import PublicationError, digest, encoded, loads, raw_digest, require
from ._s2ex_recorder_binding import (
    ATTEMPT, CASES, EU_DIGEST, NATIVE_RENAME_LAYOUT, PHASES, b64, clone, local_id, record, unb64,
)


PATH_APIS = ("CreateFileW", "GetFileAttributesW", "GetDriveTypeW")
API_OUTPUTS = {
    "CreateFileW": ("opened_handle",), "CloseHandle": (), "FlushFileBuffers": (),
    "WriteFile": ("lpNumberOfBytesWritten",), "ReadFile": ("lpBuffer", "lpNumberOfBytesRead"),
    "SetFilePointerEx": ("lpNewFilePointer",), "GetFileSizeEx": ("lpFileSize",),
    "GetFileInformationByHandleEx": ("lpFileInformation",),
    "GetFileInformationByHandle": ("lpFileInformation",), "SetFileInformationByHandle": (),
    "GetFinalPathNameByHandleW": ("lpszFilePath",), "GetFileAttributesW": (), "GetDriveTypeW": (),
    "GetVolumeInformationByHandleW": ("lpVolumeNameBuffer", "lpVolumeSerialNumber",
                                     "lpMaximumComponentLength", "lpFileSystemFlags", "lpFileSystemNameBuffer"),
}
CHECKS = ("sources-unchanged", "case-postconditions", "helper.before-rename", "helper.after-rename",
          "helper.sentinel-ready", "helper.foreign-open", "expected-parent-mismatch")


def typed(parameter, value, encoding=None):
    if encoding is None:
        encoding = "NULL" if value is None else "BOOLEAN" if type(value) is bool else "INTEGER"
    if encoding in ("BYTES_BASE64", "UTF16LE_BASE64"):
        value = b64(value if type(value) is bytes else value.encode("utf-16-le"))
    return {"parameter": parameter, "encoding": encoding, "value": value}


def validate_entry(entry, eu):
    require(set(entry) == set(eu["data_forms"]["TraceEntry"]), "entry fields differ")
    require(entry["schema_version"] == "s2eu.trace-entry.v1", "entry schema differs")
    require(type(entry["sequence"]) is int and entry["sequence"] > 0 and
            entry["phase"] in ("SETUP", *PHASES, "CLEANUP", "TERMINAL") and
            entry["event"] in ("PHASE_BEGIN", "PHASE_END", "CALL_BEGIN", "CALL_RETURN", "CHECK", "INJECTION", "TERMINAL") and
            entry["origin"] in ("CHECK", "NATIVE", "INJECTED"), "invalid trace event")
    for key in ("native_error", "injected_error", "raw_return"):
        value = entry[key]
        require(value is None or type(value) is int and (key == "raw_return" or value >= 0), "invalid native scalar")
    for key in ("call_id", "handle_id", "related_call_id"):
        if entry[key] is not None:
            local_id(entry[key])
    for key in ("arguments", "outputs"):
        require(type(entry[key]) is list, "typed slot list required")
        for slot in entry[key]:
            require(type(slot) is dict and set(slot) == {"parameter", "encoding", "value"} and
                    type(slot["parameter"]) is str and bool(slot["parameter"]), "typed slot fields")
            encoding, value = slot["encoding"], slot["value"]
            if encoding in ("BYTES_BASE64", "UTF16LE_BASE64"):
                raw = unb64(value)
                if encoding == "UTF16LE_BASE64":
                    raw.decode("utf-16-le")
            elif encoding == "LOGICAL_HANDLE":
                local_id(value)
            else:
                require(encoding == "INTEGER" and type(value) is int or encoding == "BOOLEAN" and type(value) is bool or
                        encoding == "NULL" and value is None, "invalid typed slot value")
    if entry["event"] in ("CALL_BEGIN", "CALL_RETURN", "INJECTION"):
        require(entry["call_id"] is not None and entry["operation"] in eu["recorder"]["api_parameters"] and
                entry["origin"] in ("NATIVE", "INJECTED") and type(entry["path_role"]) is str,
                "unbound call event")
        if entry["event"] == "CALL_BEGIN":
            require([v["parameter"] for v in entry["arguments"]] == eu["recorder"]["api_parameters"][entry["operation"]],
                    "API parameter slots differ")
        if entry["origin"] == "NATIVE":
            require(entry["injected_error"] is None, "native call contains injected error")
        else:
            require(entry["native_error"] is None, "proxy contains native failure")
    else:
        require(entry["origin"] == "CHECK" and entry["operation"] is None, "check/native event confusion")
    event = entry["event"]
    nulls = {"call_id", "operation", "handle_id", "path_role", "raw_return", "native_error",
             "injected_error", "check_id", "check_result", "subject_status", "related_call_id"}
    if event in ("CALL_BEGIN", "CALL_RETURN", "INJECTION"):
        nulls -= {"call_id", "operation", "handle_id", "path_role", "related_call_id"}
        if event == "CALL_RETURN":
            nulls -= {"raw_return", "native_error", "injected_error"}
            require(type(entry["raw_return"]) is int and entry["arguments"] == [], "return payload differs")
            require(tuple(v["parameter"] for v in entry["outputs"]) == API_OUTPUTS[entry["operation"]],
                    "API output slots differ")
        elif event == "CALL_BEGIN":
            require(entry["outputs"] == [], "begin contains output")
        else:
            require(entry["origin"] == "INJECTED", "native injection event")
    else:
        require(entry["arguments"] == [] and entry["outputs"] == [], "check has API slots")
        if event == "PHASE_END":
            nulls -= {"check_id", "check_result"}
            require(entry["check_id"] == "phase-complete" and type(entry["check_result"]) is bool,
                    "phase check differs")
        elif event == "CHECK":
            nulls -= {"check_id", "check_result"}
            require(entry["check_id"] in CHECKS and type(entry["check_result"]) is bool, "unknown check")
        elif event == "TERMINAL":
            nulls.remove("subject_status")
            require(entry["phase"] == "TERMINAL" and
                    entry["subject_status"] in eu["type_rules"]["enums"]["SubjectStatus"], "terminal differs")
    require(all(entry[key] is None for key in nulls), "nonapplicable event fields are not null")


class Trace:
    def __init__(self, binding, case_id, sink):
        eu, _, profile, run, source, _, actors, _ = binding.values()
        require(case_id in CASES and callable(sink), "case and sink required")
        self.binding, self.case_id, self.sink = binding, case_id, sink
        self.actors = actors
        self.spec = eu["cases"][CASES.index(case_id)]
        self.lock = RLock()
        self.phase = "SETUP"
        self.states = dict.fromkeys(PHASES, "NOT_REACHED")
        self.entries = []
        self.raw_parts = []
        self.byte_count = self.call_count = 0
        self.closed = self.broken = False
        self.header = record("s2eu.trace.v1", attempt_id=ATTEMPT, case_id=case_id,
                             profile_digest=profile["record_digest"], run_binding_digest=run["record_digest"],
                             source_manifest_digest=source["record_digest"], expected_contract_digest=EU_DIGEST)
        self.last_digest = self.header["record_digest"]
        self._write(self.header)

    def _write(self, value):
        raw = encoded(value) + b"\n"
        require(not self.broken and self.byte_count + len(raw) <= self.binding.limits.trace_bytes,
                "trace bound exceeded", "RECORDING_INCOMPLETE")
        try:
            self.sink(raw)
        except BaseException:
            self.broken = True
            raise
        self.byte_count += len(raw)
        self.raw_parts.append(raw)

    def emit(self, event, actor="worker", **fields):
        with self.lock:
            require(not self.closed and not self.broken, "trace terminal", "RECORDING_INCOMPLETE")
            require(actor in self.actors, "unbound actor")
            value = dict(schema_version="s2eu.trace-entry.v1", case_id=self.case_id,
                         sequence=len(self.entries) + 1, phase=self.phase, event=event,
                         call_id=None, operation=None, origin="CHECK", handle_id=None,
                         path_role=None, arguments=[], outputs=[], raw_return=None,
                         native_error=None, injected_error=None, check_id=None,
                         check_result=None, subject_status=None, previous_record_digest=self.last_digest,
                         actor_id=self.actors[actor], related_call_id=None)
            require(set(fields) <= set(value) - {"schema_version", "case_id", "sequence", "previous_record_digest"},
                    "unknown trace field")
            value.update(fields)
            value["record_digest"] = digest(value)
            self._write(value)
            self.entries.append(clone(value))
            self.last_digest = value["record_digest"]
            return value

    def call_id(self):
        with self.lock:
            require(self.call_count < self.binding.limits.calls, "call ceiling exceeded", "RECORDING_INCOMPLETE")
            self.call_count += 1
            return f"{ATTEMPT}.{self.case_id}.call.{self.call_count}"

    def check(self, name, ok, actor="worker", *, raise_failure=True):
        require(type(ok) is bool, "exact check boolean required")
        self.emit("CHECK", actor, check_id=name, check_result=ok)
        if raise_failure:
            require(ok, name)

    @contextmanager
    def at_phase(self, phase):
        require(phase in PHASES and self.states[phase] == "NOT_REACHED", "phase reused")
        if self.case_id != "p13":
            require(all(self.states[p] == "CONFIRMED" for p in PHASES[:PHASES.index(phase)]),
                    "phase predecessor missing")
        else:
            require(phase == "E8", "p13 is read-only E8")
        self.phase = phase
        self.states[phase] = "ENTERED"
        self.emit("PHASE_BEGIN")
        try:
            yield
        except BaseException:
            self.states[phase] = "FAILED"
            if not self.broken:
                self.emit("PHASE_END", check_id="phase-complete", check_result=False)
            raise
        else:
            self.states[phase] = "CONFIRMED"
            self.emit("PHASE_END", check_id="phase-complete", check_result=True)

    def finish(self, status):
        require(not self.closed, "trace already finished")
        self.phase = "TERMINAL"
        self.emit("TERMINAL", subject_status=status)
        observation = inspect_entries(self.header, self.entries, self.states, self.spec, self.actors, status, self.binding)
        footer = record("s2eu.trace-footer.v1", case_id=self.case_id, entry_count=len(self.entries),
                        last_entry_digest=self.last_digest, phase_states=dict(self.states), subject_status=status,
                        expected_outcome_matched=observation["matched"],
                        first_failed_native_call=observation["first_native"],
                        first_injected_failure=observation["first_injected"], cleanup_failures=observation["cleanup"])
        self._write(footer)
        self.closed = True
        return b"".join(self.raw_parts)


def _slot_values(slots, limit):
    values = []
    for slot in slots:
        kind, value = slot["encoding"], slot["value"]
        if kind in ("BYTES_BASE64", "UTF16LE_BASE64"):
            value = unb64(value)
            require(len(value) <= limit, "trace buffer ceiling", "RECORDING_INCOMPLETE")
            if kind == "UTF16LE_BASE64":
                value = value.decode("utf-16-le")
        values.append(value)
    return values


def _call_pairs(entries, binding):
    """Decode original pairs only; never call a fixture or a native backend."""
    eu, _, _, _, _, _, _, _ = binding.values()
    pending, result, applied = {}, [], {}
    seen = set()
    for entry in entries:
        event, key = entry["event"], entry["call_id"]
        if event == "CALL_BEGIN":
            require(key not in seen and len(seen) < binding.limits.calls, "call identity/limit differs")
            require(key == f"{ATTEMPT}.{entry.get('case_id') or 'control'}.call.{len(seen) + 1}",
                    "call sequence identity differs")
            seen.add(key)
            pending[key] = entry
        elif event == "INJECTION":
            require(key in pending and key not in applied, "duplicate or unpaired injection")
            begin = pending[key]
            require(all(entry[k] == begin[k] for k in
                        ("operation", "actor_id", "phase", "origin", "handle_id", "path_role",
                         "related_call_id", "arguments")), "injection source differs")
            applied[key] = entry
        elif event == "CALL_RETURN":
            require(key in pending, "return without source")
            begin = pending.pop(key)
            require(all(entry[k] == begin[k] for k in
                        ("operation", "actor_id", "phase", "origin", "handle_id", "path_role", "related_call_id")),
                    "return source differs")
            name = begin["operation"]
            require(name in API_OUTPUTS and [s["parameter"] for s in begin["arguments"]] ==
                    eu["recorder"]["api_parameters"][name] and
                    tuple(s["parameter"] for s in entry["outputs"]) == API_OUTPUTS[name], "API slots differ")
            a = _slot_values(begin["arguments"], binding.limits.buffer_bytes)
            o = _slot_values(entry["outputs"], binding.limits.buffer_bytes)
            require(begin["arguments"][0]["encoding"] ==
                    ("UTF16LE_BASE64" if name in PATH_APIS else "LOGICAL_HANDLE"), "path/handle encoding differs")
            require(begin["handle_id"] is None if name in PATH_APIS else a[0] == begin["handle_id"],
                    "path/handle identity differs")
            for slot in [*begin["arguments"][1:], *entry["outputs"]]:
                require(slot["encoding"] not in ("UTF16LE_BASE64", "BOOLEAN"), "unexpected native slot encoding")
                require(slot["encoding"] != "LOGICAL_HANDLE" or
                        name == "CreateFileW" and slot["parameter"] == "opened_handle", "unexpected logical handle slot")
            if begin["origin"] == "NATIVE":
                raw = entry["raw_return"]
                success = (raw not in (0, -1, 0xffffffff, 0xffffffffffffffff) if name == "CreateFileW" else
                           raw != 0xffffffff if name == "GetFileAttributesW" else
                           True if name == "GetDriveTypeW" else raw != 0)
                require((entry["native_error"] is None) == success and entry["injected_error"] is None,
                        "native error provenance differs")
                if name == "CreateFileW":
                    require((o[0] is not None) == success and entry["outputs"][0]["encoding"] ==
                            ("LOGICAL_HANDLE" if success else "NULL"), "opened handle differs")
            result.append({"begin": begin, "end": entry, "a": a, "o": o})
    require(not pending, "incomplete native pair", "RECORDING_INCOMPLETE")
    result.sort(key=lambda c: c["begin"]["sequence"])
    by_id = {c["begin"]["call_id"]: c for c in result}
    active = {}
    for e in entries:
        if e["event"] == "CALL_BEGIN":
            actor = e["actor_id"]
            stack = active.setdefault(actor, [])
            require((not stack and e["related_call_id"] is None) or
                    (len(stack) == 1 and e["related_call_id"] == stack[-1]), "unbound nested native call")
            stack.append(e["call_id"])
        elif e["event"] == "CALL_RETURN":
            stack = active.get(e["actor_id"], [])
            require(stack and stack.pop() == e["call_id"], "native return nesting differs")
    for c in result:
        b, r = c["begin"], c["end"]
        parent = b["related_call_id"]
        if parent is not None:
            require(parent in by_id, "forwarded parent missing")
            p = by_id[parent]
            require(p["begin"]["origin"] == "INJECTED" and b["origin"] == "NATIVE" and
                    p["begin"]["sequence"] < b["sequence"] < r["sequence"] < p["end"]["sequence"] and
                    all(b[k] == p["begin"][k] for k in ("operation", "actor_id", "phase", "path_role", "handle_id")),
                    "forwarded pair differs")
        if b["origin"] != "INJECTED":
            continue
        require(parent is None and b.get("case_id") in ("p07", "p08", "p09", "p10", "p11", "p12"),
                "unbound injected call")
        spec = eu["cases"][CASES.index(b["case_id"])]
        require(b["operation"] == spec["trigger"]["operation"] and b["phase"] == spec["terminal_phase"] and
                b["path_role"] == spec["trigger"]["role"], "injection trigger differs")
        children = [v for v in result if v["begin"]["related_call_id"] == b["call_id"]]
        require(len(children) == (0 if b["operation"] == "FlushFileBuffers" else 1), "forward count differs")
        if b["operation"] == "CloseHandle":
            child = children[0]
            require(child["a"] == c["a"] and r["raw_return"] == 0 and not c["o"], "close proxy differs")
            actual = child["end"]["native_error"] is None
            require((b["call_id"] in applied) == actual and r["injected_error"] == (5 if actual else None),
                    "native close failure mislabeled as injection")
        elif b["operation"] == "WriteFile":
            child = children[0]
            require(type(c["a"][2]) is int and c["a"][2] > 1 and
                    child["a"] == [c["a"][0], c["a"][1][:-1], c["a"][2] - 1, c["a"][3], c["a"][4]] and
                    c["o"] == child["o"] and r["raw_return"] == child["end"]["raw_return"] and
                    r["injected_error"] == child["end"]["native_error"], "short-write child differs")
            require(b["call_id"] in applied, "short-write injection event missing")
        else:
            require(r["raw_return"] == 0 and r["injected_error"] == 5 and b["call_id"] in applied,
                    "flush injection differs")
        if b["call_id"] in applied:
            e = applied[b["call_id"]]
            require(b["sequence"] < e["sequence"] < r["sequence"] and
                    (not children or children[0]["end"]["sequence"] < e["sequence"]) and
                    e["outputs"] == [typed("intended_request_bytes", c["a"][2] if b["operation"] == "WriteFile" else None),
                                      typed("actual_proxy_return", r["raw_return"]),
                                      typed("actual_proxy_error", r["injected_error"]), *r["outputs"]],
                    "applied injection payload/order differs")
    return result


class _Evidence:
    """Read-only native transcript decoder and finite file-evidence ledger."""

    def __init__(self, calls, binding, case):
        self.calls, self.binding, self.case = calls, binding, case
        self.eu, _, self.profile, self.run, self.source, self.refs, self.actors, self.paths = binding.values()
        self.rename_layout = loads(NATIVE_RENAME_LAYOUT)
        self.handles, self.reads, self.absent, self.inspections = {}, [], [], []
        self.creates, self.writes, self.flushes, self.renames, self.closes = [], [], [], [], []
        self.native = [c for c in calls if c["begin"]["origin"] == "NATIVE"]
        self.serials, self.raw_handles = {}, {}
        for actor in self.actors.values():
            self._actor([c for c in self.native if c["begin"]["actor_id"] == actor], actor)
        require(all(h["closed"] for h in self.handles.values()), "native handle not closed")
        for c in calls:
            if c["begin"]["origin"] == "INJECTED":
                b = c["begin"]
                require(b["actor_id"] == self.actors["worker"] and b["handle_id"] in self.handles,
                        "proxy owner differs")
                h = self.handles[b["handle_id"]]
                closes = [v for v in self.closes if v["begin"]["handle_id"] == h["id"]]
                require(h["writable"] and h["open"] < b["sequence"] < closes[0]["end"]["sequence"],
                        "proxy refers to non-live writer")

    def _ok(self, c):
        require(c["end"]["native_error"] is None, "required native operation failed")

    def _pair(self, seq, i, name, handle):
        require(i < len(seq), "required native operation missing")
        c = seq[i]
        require(c["begin"]["operation"] == name and c["begin"]["handle_id"] == handle["id"] and
                c["a"][0] == handle["id"] and c["begin"]["path_role"] == handle["row"].role and
                not handle["closed"], "native handle/operation differs")
        self._ok(c)
        return c

    def _inspect(self, seq, i, h):
        start = i
        c = self._pair(seq, i, "GetFileInformationByHandle", h)
        require(c["a"][1] == bytes(52) and len(c["o"][0]) == 52, "file information shape differs")
        raw = c["o"][0]
        attrs, links = int.from_bytes(raw[:4], "little"), int.from_bytes(raw[40:44], "little")
        require(not attrs & 0x400 and bool(attrs & 0x10) == h["directory"] and
                (h["directory"] or links == 1), "file type/reparse/link differs")
        c = self._pair(seq, i + 1, "GetFileInformationByHandleEx", h)
        require(c["a"][1:] == [18, bytes(24), 24] and len(c["o"][0]) == 24, "file identity shape differs")
        identity = {"volume": {"filesystem": "NTFS", "serial_hex": f"{int.from_bytes(c['o'][0][:8], 'little'):016x}"},
                    "file_id_hex": c["o"][0][8:].hex()}
        c = self._pair(seq, i + 2, "GetVolumeInformationByHandleW", h)
        require(c["a"][1:] == [None, 0, None, None, None, bytes(522), 261] and
                c["o"][:4] == [None] * 4 and len(c["o"][4]) == 522 and
                c["o"][4].decode("utf-16-le").split("\0", 1)[0] == "NTFS", "filesystem evidence differs")
        c = self._pair(seq, i + 3, "GetFinalPathNameByHandleW", h)
        require(c["a"][1:] == [bytes(65536), 32768, 0] and len(c["o"][0]) == 65536, "native name shape differs")
        name = c["o"][0].decode("utf-16-le").split("\0", 1)[0]
        require(0 < c["end"]["raw_return"] < 32768 and
                len(name.encode("utf-16-le")) // 2 == c["end"]["raw_return"], "truncated native name")
        if name.startswith("\\\\?\\") and len(name) > 6 and name[5:7] == ":\\":
            name = name[4:]
        require(name == h["row"].path, "native name does not identify bound path")
        i += 4
        if h["directory"]:
            c = self._pair(seq, i, "GetFileInformationByHandleEx", h)
            require(c["a"][1:] == [23, bytes(4), 4] and c["o"] == [bytes(4)], "directory case evidence differs")
            i += 1
        require(all(c["begin"]["phase"] == seq[start]["begin"]["phase"] for c in seq[start:i]),
                "inspection crosses phase")
        require(h["identity"] in (None, identity), "native identity changed")
        h["identity"] = identity
        self.inspections.append((h["id"], seq[start]["begin"]["sequence"], seq[i - 1]["end"]["sequence"]))
        return i

    def _read(self, seq, i, h):
        start = i
        direct_source = h["row"].role.startswith("source.")
        cold_record = self.case == "p13" and h["actor"] == self.actors["worker"] and h["row"].role != "final"
        if not direct_source and not cold_record:
            self._guard(seq, i, h["row"], h["actor"])
        c = self._pair(seq, i, "GetFileSizeEx", h)
        size = c["o"][0]
        require(c["a"][1] == 0 and type(size) is int and 0 <= size <= self.binding.limits.stream_bytes,
                "unbounded read size")
        c = self._pair(seq, i + 1, "SetFilePointerEx", h)
        require(c["a"][1:] == [0, None, 0] and c["o"] == [None], "read position differs")
        i += 2
        parts = []
        for offset in range(0, size, 1048576):
            count = min(1048576, size - offset)
            c = self._pair(seq, i, "ReadFile", h)
            require(c["a"][1:] == [bytes(count), count, 0, None] and type(c["o"][1]) is int and
                    c["o"][1] == count and type(c["o"][0]) is bytes and len(c["o"][0]) == count,
                    "partial or displaced read")
            parts.append(c["o"][0])
            i += 1
        c = self._pair(seq, i, "GetFileSizeEx", h)
        require(c["a"][1] == size and c["o"] == [size], "post-read size differs")
        i = self._inspect(seq, i + 1, h)
        require(all(c["begin"]["phase"] == seq[start]["begin"]["phase"] for c in seq[start:i]),
                "read crosses phase")
        self.reads.append({"handle": h["id"], "actor": h["actor"], "row": h["row"], "identity": clone(h["identity"]),
                           "phase": seq[start]["begin"]["phase"], "start": seq[start]["begin"]["sequence"],
                           "end": seq[i - 1]["end"]["sequence"], "raw": b"".join(parts)})
        h["read_started"] = True
        return i

    def _guard(self, seq, i, row, actor):
        parents = [h for h in self.handles.values() if h["actor"] == actor and h["directory"] and not h["closed"]]
        require(any(h["row"].path == str(PureWindowsPath(row.path).parent) for h in parents), "unretained parent")
        # Every guard uses the complete, immediately preceding retained-parent inspection sequence.
        end = seq[i]["begin"]["sequence"]
        for h in reversed(parents):
            matches = [(s, e) for key, s, e in self.inspections if key == h["id"] and e < end]
            require(bool(matches), "parent inspection missing")
            s, e = matches[-1]
            between = [c for c in seq[:i] if e < c["begin"]["sequence"] < end]
            require(not between, "parent guard is not adjacent")
            end = s

    def _actor(self, seq, actor):
        i = 0
        while i < len(seq):
            c = seq[i]
            b, r, a, o = c["begin"], c["end"], c["a"], c["o"]
            name = b["operation"]
            if name in PATH_APIS:
                row = self.paths.resolve(a[0])
                alias = self.case == "p06" and actor == self.actors["helper"] and name == "CreateFileW" and row.role == "case_reservation"
                require(b["path_role"] == ("foreign_write_handle" if alias else row.role), "path role differs")
                if not row.role.startswith(("source.", "directory.")) and self.case is not None:
                    require(row.case_id == ("p01" if self.case == "p13" else self.case) and
                            not row.role.startswith("recorder.") and row.role != "trace", "cross-case native access")
                if name == "GetDriveTypeW":
                    require(row.role.startswith("directory.") and str(PureWindowsPath(row.path).anchor) == row.path and
                            r["raw_return"] == 3, "drive evidence differs")
                elif name == "GetFileAttributesW":
                    self._guard(seq, i, row, actor)
                    require(r["raw_return"] == 0xffffffff and r["native_error"] == 2, "absence evidence differs")
                    self.absent.append((actor, row.path, b["phase"], b["sequence"]))
                else:
                    directory = row.role.startswith("directory.")
                    create = a[4] == 1
                    rename = row.path in self.paths.edges and create
                    require(a[3] is None and a[6] is None, "security/template differs")
                    if alias:
                        require(a[1:] == [0x40000000, 7, None, 3, 0x00200000, None] and
                                r["native_error"] == 32, "foreign-open countercase differs")
                        i += 1
                        continue
                    require(a[1] == (0x80000000 | (0x40000000 if create else 0) | (0x10000 if rename else 0)) and
                            a[2] == (1 if create or row.role.startswith("source.") else 3 if directory else 7) and a[4] in (1, 3) and
                            a[5] == (0x00200000 | (0x02000000 if directory else 0) | (0x80000000 if create else 0)),
                            "open flags differ")
                    if create:
                        require(not directory and not row.role.startswith("source."), "read-only path creation")
                        self._guard(seq, i, row, actor)
                        self.creates.append(c)
                    elif row.role.startswith("source."):
                        self._guard(seq, i, row, actor)
                    if r["native_error"] is not None:
                        require(create and self.case in ("p03", "p04") and r["native_error"] == 80,
                                "unexpected open failure")
                        i += 1
                        continue
                    key = o[0]
                    serial = self.serials.get(actor, 0) + 1
                    actor_role = next(k for k, v in self.actors.items() if v == actor)
                    require(key == f"{self.case or 'control'}.{actor_role}.handle.{serial}" and key not in self.handles,
                            "logical handle generation differs")
                    self.serials[actor] = serial
                    raw_key = (actor, r["raw_return"])
                    require(raw_key not in self.raw_handles or self.handles[self.raw_handles[raw_key]]["closed"],
                            "live native handle reused")
                    self.raw_handles[raw_key] = key
                    h = {"id": key, "actor": actor, "row": row, "initial_row": row, "directory": directory,
                         "writable": create, "rename": rename, "renamed": False, "closed": False,
                         "identity": None, "open": b["sequence"], "read_started": False}
                    self.handles[key] = h
                    i = self._inspect(seq, i + 1, h)
                    if create:
                        parents = [p for p in self.handles.values() if p["actor"] == actor and p["directory"] and
                                   p["row"].path == str(PureWindowsPath(row.path).parent)]
                        require(len(parents) == 1 and parents[0]["identity"]["volume"] == h["identity"]["volume"],
                                "created volume differs")
                    continue
                i += 1
                continue
            key = b["handle_id"]
            require(key in self.handles, "handle has no successful creation")
            h = self.handles[key]
            require(h["actor"] == actor and not h["closed"] and h["row"].role == b["path_role"],
                    "handle ownership/lifetime differs")
            if name == "GetFileInformationByHandle":
                i = self._inspect(seq, i, h)
                continue
            if name == "GetFileSizeEx":
                i = self._read(seq, i, h)
                continue
            if name == "CloseHandle":
                require(len(a) == 1, "close arguments differ")
                h["closed"] = True
                self.closes.append(c)
            elif name == "WriteFile":
                self._ok(c)
                require(h["writable"] and not h["read_started"] and not h["renamed"] and
                        type(a[1]) is bytes and type(a[2]) is int and 0 < a[2] <= 1048576 and
                        len(a[1]) == a[2] and a[3:] == [0, None] and o == [a[2]], "write extent/ownership differs")
                self.writes.append(c)
            elif name == "FlushFileBuffers":
                self._ok(c)
                require(h["writable"], "flush of unowned file")
                self.flushes.append(c)
            elif name == "SetFileInformationByHandle":
                require(h["writable"] and h["rename"] and not h["renamed"] and
                        type(a[1]) is int and a[1] == self.rename_layout["information_class"] and
                        type(a[2]) is bytes and type(a[3]) is int and 0 < a[3] <= 0xffffffff and len(a[2]) == a[3],
                        "rename shape/permission differs")
                raw = a[2]
                target = self.paths.edges[h["row"].path]
                name = target.encode("utf-16-le")
                length_field, name_field = self.rename_layout["fields"][3:]
                require("\0" not in target and 0 < len(name) <= 0xffffffff and len(name) % 2 == 0 and
                        a[3] == name_field["offset"] + len(name), "rename name extent differs")
                expected = (bytes(length_field["offset"]) +
                            len(name).to_bytes(length_field["bytes"], self.rename_layout["byte_order"]) + name)
                require(raw == expected, "rename bytes differ from bound native layout and edge")
                require(i >= 4 and seq[i - 4]["begin"]["operation"] == "GetFileInformationByHandle" and
                        seq[i - 4]["begin"]["handle_id"] == key, "rename identity barrier missing")
                self._guard(seq, i - 4, h["row"], actor)
                self.renames.append(c)
                h["renamed"] = True
                if r["native_error"] is None:
                    h["row"] = self.paths.resolve(target)
                else:
                    require(self.case == "p05", "unexpected rename failure")
            else:
                require(False, "standalone or undeclared native operation")
            i += 1

    def _proof(self, actor, path, phase, raw, after=0, before=None, identity=None):
        matches = [v for v in self.reads if v["actor"] == actor and v["row"].path == path and v["phase"] == phase and
                   v["start"] > after and (before is None or v["end"] < before) and v["raw"] == raw and
                   (identity is None or v["identity"] == identity)]
        require(bool(matches), "full byte/identity read evidence missing")
        return matches[0]

    def _sources(self, actor, phase):
        for ref in self.refs:
            require(any(v["actor"] == actor and v["phase"] == phase and v["row"].path == ref["path"] and
                        len(v["raw"]) == ref["byte_count"] and raw_digest(v["raw"]) == ref["raw_sha256"]
                        for v in self.reads), "original source read evidence missing")

    def _parents(self, actor, stop_at=None):
        parents = list(self.profile["parent_directories"].items())
        if stop_at is not None:
            parents = parents[:next(i for i, (role, _) in enumerate(parents) if role == stop_at) + 1]
        drives = [c for c in self.native if c["begin"]["actor_id"] == actor and c["begin"]["operation"] == "GetDriveTypeW"]
        require([c["a"][0] for c in drives] == [PureWindowsPath(parent["path"]).anchor for _, parent in parents],
                "parent drive-check sequence differs")
        phase = "SETUP" if self.case is None else "E8" if self.case == "p13" else "E0"
        require(all(c["begin"]["phase"] == phase for c in drives), "parent initialization phase differs")
        for _, parent in parents:
            require(any(h["actor"] == actor and h["directory"] and h["row"].path == parent["path"] and
                        h["identity"] == parent["identity"] for h in self.handles.values()), "parent source identity differs")

    def _fixture_bytes(self, case, identity):
        payload = ("S2EU PLATFORM FIXTURE " + case + "\n").encode("ascii")
        values, prior = {}, []
        for role in ("case_reservation", "target_reservation", "evidence", "sealed", "marker"):
            result = role in ("sealed", "marker")
            value = record("s2eu.fixture-record.v1", attempt_id=ATTEMPT, case_id=case, role=role,
                           profile_digest=self.profile["record_digest"], run_binding_digest=self.run["record_digest"],
                           prior_record_digests=list(prior), payload_byte_count=len(payload) if result else None,
                           payload_raw_sha256=raw_digest(payload) if result else None,
                           result_identity=identity if role == "marker" else None)
            values[role] = encoded(value)
            prior.append(value["record_digest"])
        return payload, values

    def accept_case(self, entries, states):
        worker, helper = self.actors["worker"], self.actors["helper"]
        self._parents(helper)
        if self.case != "p02":
            self._parents(worker)
        else:
            self._parents(worker, "output")
        cleanup_phase = "E8" if self.case in ("p01", "p12", "p13") else "CLEANUP"
        phase_intervals = {}
        for e in entries:
            if e["event"] == "PHASE_BEGIN":
                require(e["actor_id"] == worker, "phase actor differs")
                phase_intervals[e["phase"]] = [e["sequence"], None]
            elif e["event"] == "PHASE_END":
                require(e["actor_id"] == worker, "phase actor differs")
                phase_intervals[e["phase"]][1] = e["sequence"]
        checks = {"sources-unchanged": (helper, cleanup_phase), "case-postconditions": (helper, cleanup_phase)}
        if self.case == "p01":
            checks.update({"helper.before-rename": (helper, "E4"), "helper.after-rename": (helper, "E6")})
        if self.case == "p02":
            checks["expected-parent-mismatch"] = (worker, "E0")
        if self.case in ("p03", "p04", "p05"):
            checks["helper.sentinel-ready"] = (helper, "SETUP")
        seen_checks = set()
        for e in entries:
            if e["event"] == "CHECK":
                require(e["check_id"] in checks and e["check_id"] not in seen_checks and e["check_result"] is True and
                        (e["actor_id"], e["phase"]) == checks[e["check_id"]], "check site differs")
                seen_checks.add(e["check_id"])
            if e["event"] in ("CALL_BEGIN", "CALL_RETURN", "INJECTION") and e["phase"] in PHASES:
                begin, end = phase_intervals[e["phase"]]
                # E4's last absence/helper observation occurs after its explicit end marker.
                boundary = phase_intervals.get("E5", [end, None])[0] if e["phase"] == "E4" else end
                require(begin < e["sequence"] < boundary, "operation outside recorded phase")
                if e["phase"] == "E4" and e["sequence"] > end:
                    require(e["operation"] in ("GetFileInformationByHandle", "GetFileInformationByHandleEx",
                            "GetVolumeInformationByHandleW", "GetFinalPathNameByHandleW", "GetFileAttributesW"),
                            "E4 completion precedes its file obligation")
        require(seen_checks == set(checks), "mandatory check annotation missing")
        for actor in (worker, helper):
            handles = sorted((h for h in self.handles.values() if h["actor"] == actor), key=lambda h: h["open"], reverse=True)
            closes = sorted((c for c in self.closes if c["begin"]["actor_id"] == actor), key=lambda c: c["begin"]["sequence"])
            require([c["begin"]["handle_id"] for c in closes] == [h["id"] for h in handles] and
                    all(c["begin"]["phase"] == cleanup_phase for c in closes), "case close order/phase differs")
        worker_closes = [c["end"]["sequence"] for c in self.closes if c["begin"]["actor_id"] == worker]
        helper_closes = [c["begin"]["sequence"] for c in self.closes if c["begin"]["actor_id"] == helper]
        require(worker_closes and helper_closes and max(worker_closes) < min(helper_closes), "case owner close order differs")
        self._sources(helper, cleanup_phase)
        target_case = "p01" if self.case == "p13" else self.case
        path = lambda role: self.paths.get(target_case, role).path
        staging = [h for h in self.handles.values() if h["actor"] == worker and
                   h["initial_row"].path == path("final" if self.case == "p13" else "staging")]
        identity = staging[0]["identity"] if staging else None
        payload, records = self._fixture_bytes(target_case, identity)
        if self.case == "p13":
            require(not self.creates and not self.writes and not self.flushes and not self.renames,
                    "cold read mutates files")
            self._proof(worker, path("final"), "E8", payload, identity=identity)
            for role, raw in records.items():
                self._proof(worker, path(role), "E8", raw)
            return
        if states["E0"] == "CONFIRMED":
            self._sources(worker, "E0")
            for role in (*records, "staging", "final"):
                require(any(a == worker and p == path(role) and phase == "E0" for a, p, phase, _ in self.absent),
                        "E0 absence evidence missing")
        actions = [c for c in self.calls if c["begin"]["related_call_id"] is None and
                   (c["begin"]["operation"] in ("WriteFile", "FlushFileBuffers", "SetFileInformationByHandle") or
                    c["begin"]["operation"] == "CreateFileW" and c["a"][1] & 0x40000000)]
        expected = []
        def cycle(actor, phase, role, raw):
            expected.extend((actor, phase, role, op, raw if op == "WriteFile" else None) for op in
                            ("CreateFileW", "WriteFile", "FlushFileBuffers"))
        sentinel_role = {"p03": "case_reservation", "p04": "target_reservation", "p05": "final"}.get(self.case)
        sentinel = ("S2EU OCCUPIED " + self.case + "\n").encode("ascii")
        for phase, role in (("E1", "case_reservation"), ("E2", "target_reservation"), ("E3", "evidence"),
                            ("E4", "staging"), ("E4", "sealed"), ("E5", "staging"), ("E6", "final"), ("E7", "marker")):
            if sentinel_role is not None and ((phase == "E1" and self.case == "p03") or
                                             (phase == "E2" and self.case == "p04") or
                                             (phase == "E5" and self.case == "p05")):
                cycle(helper, "SETUP", sentinel_role, sentinel)
            if states[phase] == "NOT_REACHED":
                break
            if phase == "E5":
                expected.append((worker, phase, role, "SetFileInformationByHandle", None))
            elif phase == "E6":
                expected.append((worker, phase, role, "FlushFileBuffers", None))
            else:
                cycle(worker, phase, role, payload if role == "staging" else records[role])
            if self.case == "p06" and phase == "E1":
                expected.append((helper, phase, "foreign_write_handle", "CreateFileW", None))
        require(len(actions) <= len(expected), "extra mutation operation")
        for c, (actor, phase, role, operation, raw) in zip(actions, expected):
            b = c["begin"]
            require((b["actor_id"], b["phase"], b["path_role"], b["operation"]) == (actor, phase, role, operation),
                    "mutation order/role differs")
            if raw is not None:
                require(c["a"][1] == raw and c["a"][2:] == [len(raw), 0, None], "fixture original bytes differ")
        if self.case == "p02":
            require(not actions and any(c["begin"]["actor_id"] == worker and
                    c["begin"]["operation"] == "GetFileInformationByHandleEx" for c in self.native),
                    "parent mismatch lacks native evidence")
            parent = self.profile["parent_directories"]["output"]
            require(any(h["actor"] == worker and h["row"].path == parent["path"] and
                        h["identity"] == parent["identity"] for h in self.handles.values()),
                    "p02 original output identity missing")
        else:
            require(bool(actions), "phase markers have no native evidence")
            last = actions[-1]
            if self.case not in ("p01", "p12"):
                require(last["begin"]["phase"] == self.eu["cases"][CASES.index(self.case)]["terminal_phase"] and
                        (last["end"]["native_error"] is not None or last["begin"]["origin"] == "INJECTED"),
                        "mutation prefix does not stop at registered fault")
            else:
                require(len(actions) == len(expected), "complete mutation sequence missing")
        for index, c in enumerate(actions):
            b, r = c["begin"], c["end"]
            if b["operation"] == "FlushFileBuffers" and b["origin"] == "NATIVE" and r["native_error"] is None:
                role = b["path_role"]
                raw = sentinel if b["actor_id"] == helper else payload if role in ("staging", "final") else records[role]
                bound = actions[index + 1]["begin"]["sequence"] if index + 1 < len(actions) else None
                self._proof(b["actor_id"], path(role), b["phase"], raw, r["sequence"], bound)
        if sentinel_role:
            self._proof(helper, path(sentinel_role), "CLEANUP", sentinel)
            sentinel_create = next(c for c in actions if c["begin"]["actor_id"] == helper and c["begin"]["operation"] == "CreateFileW")
            predecessor = {"p03": "E0", "p04": "E1", "p05": "E4"}[self.case]
            require(sentinel_create["begin"]["sequence"] > phase_intervals[predecessor][1], "sentinel precedes prerequisite phase")
            if self.case == "p05":
                require(any(a == worker and p == path("final") and phase == "E4" and
                            phase_intervals["E4"][1] < s < sentinel_create["begin"]["sequence"]
                            for a, p, phase, s in self.absent), "p05 sentinel precedes last absence")
        if self.case in ("p05", "p09"):
            self._proof(helper, path("staging" if self.case == "p05" else "final"), "CLEANUP", payload, identity=identity)
        if self.case == "p11":
            marker = next(h for h in self.handles.values() if h["actor"] == worker and h["initial_row"].path == path("marker"))
            self._proof(helper, path("marker"), "CLEANUP", records["marker"], identity=marker["identity"])
        if self.case == "p09":
            require(any(a == helper and p == path("marker") and phase == "CLEANUP" for a, p, phase, _ in self.absent),
                    "p09 marker absence missing")
        if states["E6"] == "CONFIRMED":
            rename = self.renames[0]
            require(any(h["actor"] == worker and not h["writable"] and h["initial_row"].path == path("final") and
                        h["identity"] == identity and h["open"] > rename["end"]["sequence"] for h in self.handles.values()),
                    "final-name independent identity missing")
        if self.case in ("p01", "p12"):
            for role, raw in records.items():
                self._proof(worker, path(role), "E8", raw)
        if self.case == "p01":
            rename = self.renames[0]
            require(any(a == helper and p == path("final") and s < rename["begin"]["sequence"]
                        for a, p, _, s in self.absent), "independent pre-rename absence missing")
            self._proof(helper, path("final"), "E6", payload, rename["end"]["sequence"], identity=identity)
        if states["E4"] == "CONFIRMED":
            rename = self.renames[0]
            require(any(a == worker and p == path("final") and phase == "E4" and s < rename["begin"]["sequence"]
                        for a, p, phase, s in self.absent), "last final absence missing")

    def accept_control(self):
        actor = self.actors["supervisor"]
        require(all(c["begin"]["actor_id"] == actor and c["begin"]["phase"] == "SETUP" and
                    c["begin"]["origin"] == "NATIVE" for c in self.calls), "control actor/origin differs")
        require(all(c["end"]["native_error"] is None or c["begin"]["operation"] == "GetFileAttributesW" and
                    c["end"]["native_error"] == 2 for c in self.calls), "control native failure is terminal")
        for c in self.calls:
            if c["begin"]["operation"] in PATH_APIS:
                row = self.paths.resolve(c["a"][0])
                require(row.case_id is None or row.role.startswith("recorder.") or row.role == "trace" or
                        c["begin"]["operation"] == "GetFileAttributesW", "control accessed subject file")
        self._parents(actor)
        self._sources(actor, "SETUP")
        created = {c["o"][0]: c for c in self.creates}
        expected = {(None, "platform_reservation"), (None, "recorder.transcript.spool"),
                    (None, "recording_marker"), (None, "recorder.transcript.stage"),
                    (None, "recorder.report.stage"), (None, "recorder.manifest.stage")}
        expected.update((case, role) for case in CASES for role in ("recorder.trace.spool", "recorder.trace.stage"))
        require({(self.handles[key]["initial_row"].case_id, self.handles[key]["initial_row"].role)
                 for key in created} == expected and len(created) == len(expected), "control creation closure differs")
        file_bytes, refs = {}, {}
        for key, create in created.items():
            h = self.handles[key]
            writes = sorted((c for c in self.writes if c["begin"]["handle_id"] == key),
                            key=lambda c: c["begin"]["sequence"])
            flushes = sorted((c for c in self.flushes if c["begin"]["handle_id"] == key),
                             key=lambda c: c["begin"]["sequence"])
            renames = [c for c in self.renames if c["begin"]["handle_id"] == key]
            raw = b"".join(c["a"][1] for c in writes)
            require(bool(raw) and len(raw) <= self.binding.limits.stream_bytes and
                    len(flushes) == (2 if h["rename"] else 1) and len(renames) == int(h["rename"]),
                    "control write/flush/rename lifecycle differs")
            require(create["end"]["sequence"] < writes[0]["begin"]["sequence"] and
                    writes[-1]["end"]["sequence"] < flushes[0]["begin"]["sequence"], "control write order differs")
            self._proof(actor, h["initial_row"].path, "SETUP", raw, flushes[0]["end"]["sequence"],
                        renames[0]["begin"]["sequence"] if renames else None, h["identity"])
            if renames:
                require(renames[0]["end"]["sequence"] < flushes[1]["begin"]["sequence"], "post-rename flush order differs")
                self._proof(actor, h["row"].path, "SETUP", raw, flushes[1]["end"]["sequence"], identity=h["identity"])
                require(any(v["actor"] == actor and v["initial_row"].path == h["row"].path and
                            not v["writable"] and v["identity"] == h["identity"] and
                            v["open"] > flushes[1]["end"]["sequence"] for v in self.handles.values()),
                        "independent final-name open missing")
            file_bytes[(h["row"].case_id, h["row"].role)] = raw
            refs[(h["row"].case_id, h["row"].role)] = {"path": h["row"].path, "byte_count": len(raw), "raw_sha256": raw_digest(raw)}
        reservation = loads(file_bytes[(None, "platform_reservation")])
        require(reservation.get("explicit_authorization") in self.refs and reservation.get("preregistration_review") in self.refs,
                "control authorization reference differs")
        require(reservation == record("s2eu.attempt-reservation.v1", attempt_id=ATTEMPT,
                profile_digest=self.profile["record_digest"], run_binding_digest=self.run["record_digest"],
                source_manifest_digest=self.source["record_digest"], explicit_authorization=reservation["explicit_authorization"],
                preregistration_review=reservation["preregistration_review"], status="RESERVED"), "reservation bytes differ")
        observations, trace_refs = [], []
        for case in CASES:
            raw = file_bytes[(case, "trace")]
            require(raw == file_bytes[(case, "recorder.trace.spool")], "published trace differs from original spool")
            observation = validate_trace(raw, self.binding)
            require(observation["matched"], "control contains unmatched case")
            trace_refs.append(refs[(case, "trace")])
            observations.append({"case_id": case, "raw_trace": refs[(case, "trace")], "status": "OBSERVED_COMPLETE",
                                 "first_native_failure": observation["native_failure"]})
        transcript = file_bytes[(None, "transcript")]
        require(transcript == file_bytes[(None, "recorder.transcript.spool")] and transcript.endswith(b"\n"),
                "transcript differs from original spool")
        frames = [loads(line) for line in transcript.splitlines()]
        require(b"".join(encoded(v) + b"\n" for v in frames) == transcript, "noncanonical original stream")
        stdout = []
        for i, frame in enumerate(frames, 1):
            require(set(frame) == {"sequence", "channel", "bytes_base64"} and type(frame["sequence"]) is int and
                    frame["sequence"] == i and frame["channel"] in ("stdout", "stderr"), "stream frame differs")
            raw = unb64(frame["bytes_base64"])
            require(0 < len(raw) <= 65536, "stream chunk bound differs")
            if frame["channel"] == "stdout":
                stdout.append(raw)
        require(b"".join(stdout) == b"".join(file_bytes[(case, "trace")] for case in CASES),
                "trace records differ from original stdout")
        report = record("s2eq.platform-report.v1", platform_profile_digest=self.profile["record_digest"],
                        isolated_authorization=reservation["explicit_authorization"], isolated_attempt_id=ATTEMPT,
                        publisher_sources=self.profile["publisher_sources"], recorder_sources=self.profile["recorder_sources"],
                        platform_context=self.profile["platform_context"], parent_directories=self.profile["parent_directories"],
                        process_exit_code=0, recording_status="COMPLETE", original_transcript=refs[(None, "transcript")], cases=observations)
        require(file_bytes[(None, "report")] == encoded(report), "report source closure differs")
        manifest = record("s2eu.recording-manifest.v1", attempt_id=ATTEMPT,
                          profile_digest=self.profile["record_digest"], run_binding_digest=self.run["record_digest"],
                          platform_report=refs[(None, "report")], worker_transcript=refs[(None, "transcript")],
                          case_traces=trace_refs, worker_exit_code=0, recording_status="COMPLETE")
        require(file_bytes[(None, "recording_manifest")] == encoded(manifest), "manifest closure differs")
        marker = record("s2eu.recording-marker.v1", attempt_id=ATTEMPT,
                        manifest_raw_sha256=raw_digest(encoded(manifest)), manifest_record_digest=manifest["record_digest"],
                        profile_digest=self.profile["record_digest"], run_binding_digest=self.run["record_digest"])
        require(file_bytes[(None, "recording_marker")] == encoded(marker), "recording marker differs")
        publication_order = [(case, "recorder.trace.stage") for case in CASES] + [
            (None, "recorder.transcript.stage"), (None, "recorder.report.stage"),
            (None, "recorder.manifest.stage"), (None, "recording_marker")]
        ordered = sorted(created, key=lambda k: created[k]["begin"]["sequence"])
        require(self.handles[ordered[0]]["initial_row"].role == "platform_reservation" and
                [(self.handles[k]["initial_row"].case_id, self.handles[k]["initial_row"].role)
                 for k in ordered if self.handles[k]["initial_row"].role not in
                 ("platform_reservation", "recorder.trace.spool", "recorder.transcript.spool")] == publication_order,
                "control publication order differs")
        reservation_start = created[ordered[0]]["begin"]["sequence"]
        for row in self.paths.by_path.values():
            if not row.role.startswith(("source.", "directory.")):
                require(any(a == actor and p == row.path and s < reservation_start for a, p, _, s in self.absent),
                        "control initial absence closure missing")
        published_keys = [k for k in ordered if (self.handles[k]["initial_row"].case_id,
                          self.handles[k]["initial_row"].role) in publication_order]
        for index, key in enumerate(published_keys[:-1]):
            h = self.handles[key]
            flush = next(c for c in self.flushes if c["begin"]["handle_id"] == key and c["begin"]["path_role"] == h["row"].role)
            self._proof(actor, h["row"].path, "SETUP", file_bytes[(h["row"].case_id, h["row"].role)],
                        flush["end"]["sequence"], created[published_keys[index + 1]]["begin"]["sequence"], h["identity"])
        reservation_flush = next(c for c in self.flushes if c["begin"]["path_role"] == "platform_reservation")
        self._proof(actor, self.paths.get(None, "platform_reservation").path, "SETUP",
                    file_bytes[(None, "platform_reservation")], reservation_flush["end"]["sequence"],
                    created[ordered[1]]["begin"]["sequence"])
        first_publication = min(created[k]["begin"]["sequence"] for k in ordered if self.handles[k]["rename"])
        for key in ordered:
            h = self.handles[key]
            if h["initial_row"].role.endswith(".spool"):
                require(any(c["begin"]["handle_id"] == key and c["end"]["sequence"] < first_publication
                            for c in self.closes), "publication precedes spool freeze/close")
        marker_flush = next(c for c in self.flushes if c["begin"]["path_role"] == "recording_marker")
        for key in ordered:
            h = self.handles[key]
            if h["rename"]:
                self._proof(actor, h["row"].path, "SETUP", file_bytes[(h["row"].case_id, h["row"].role)],
                            marker_flush["end"]["sequence"], identity=h["identity"])
        for ref in self.refs:
            reads = [v for v in self.reads if v["row"].path == ref["path"] and len(v["raw"]) == ref["byte_count"] and
                     raw_digest(v["raw"]) == ref["raw_sha256"]]
            require(any(v["end"] < created[ordered[0]]["begin"]["sequence"] for v in reads) and
                    any(v["start"] > marker_flush["end"]["sequence"] for v in reads), "control source barriers missing")


def validate_control(raw, binding):
    require(type(raw) is bytes and raw.endswith(b"\n") and len(raw) <= binding.limits.trace_bytes,
            "control trace incomplete", "RECORDING_INCOMPLETE")
    eu, _, profile, run, source, _, actors, _ = binding.values()
    values = [loads(line) for line in raw.splitlines()]
    require(values and b"".join(encoded(v) + b"\n" for v in values) == raw, "noncanonical control trace")
    last, projected = source["record_digest"], []
    fields = {"CONTROL_HEADER": {"profile_digest", "run_binding_digest"},
              "CALL_BEGIN": {"call_id", "operation", "handle_id", "path_role", "origin", "related_call_id", "arguments"},
              "CALL_RETURN": {"call_id", "operation", "handle_id", "path_role", "origin", "related_call_id",
                              "outputs", "raw_return", "native_error"}}
    for i, value in enumerate(values, 1):
        require(set(value) == {"schema_version", "attempt_id", "sequence", "phase", "event", "actor_id",
                               "previous_record_digest", "fields", "record_digest"} and
                value["schema_version"] == "s2ex.control-entry.v1" and value["attempt_id"] == ATTEMPT and
                type(value["sequence"]) is int and value["sequence"] == i and value["phase"] == "SETUP" and
                value["actor_id"] == actors["supervisor"] and value["previous_record_digest"] == last and
                value["record_digest"] == digest({k: v for k, v in value.items() if k != "record_digest"}),
                "control identity/schema/chain differs")
        event, payload = value["event"], value["fields"]
        require(event in fields and type(payload) is dict and set(payload) == fields[event] and
                (event == "CONTROL_HEADER") == (i == 1), "control event fields differ")
        if i == 1:
            require(payload == {"profile_digest": profile["record_digest"], "run_binding_digest": run["record_digest"]},
                    "control header source differs")
        else:
            require(payload["origin"] == "NATIVE" and payload["related_call_id"] is None, "control injection prohibited")
            # Internal view only: no synthetic trace bytes or subject evidence are emitted.
            entry = dict(schema_version="s2eu.trace-entry.v1", case_id=None, sequence=i, phase="SETUP", event=event,
                         call_id=None, operation=None, origin="NATIVE", handle_id=None, path_role=None,
                         arguments=[], outputs=[], raw_return=None, native_error=None, injected_error=None,
                         check_id=None, check_result=None, subject_status=None, previous_record_digest=last,
                         actor_id=actors["supervisor"], related_call_id=None, record_digest=value["record_digest"])
            entry.update(payload)
            validate_entry(entry, eu)
            projected.append(entry)
        last = value["record_digest"]
    _Evidence(_call_pairs(projected, binding), binding, None).accept_control()


def inspect_entries(header, entries, states, spec, actors, status, binding):
    pending, returns, native_order, checks = {}, [], {}, {}
    seen_calls = set()
    derived_states = dict.fromkeys(PHASES, "NOT_REACHED")
    terminal = []
    last = header["record_digest"]
    eu = binding.values()[0]
    for index, entry in enumerate(entries, 1):
        validate_entry(entry, eu)
        require(entry["sequence"] == index and entry["case_id"] == header["case_id"] and
                entry["previous_record_digest"] == last and entry["record_digest"] == digest(
                    {k: v for k, v in entry.items() if k != "record_digest"}), "trace chain differs")
        require(entry["actor_id"] in actors.values(), "unknown trace actor")
        last = entry["record_digest"]
        event, call = entry["event"], entry["call_id"]
        if event == "PHASE_BEGIN":
            phase = entry["phase"]
            require(phase in PHASES and derived_states[phase] == "NOT_REACHED", "phase begin differs")
            if spec["case_id"] != "p13":
                require(all(derived_states[p] == "CONFIRMED" for p in PHASES[:PHASES.index(phase)]),
                        "phase ordering differs")
            else:
                require(phase == "E8", "p13 phase differs")
            derived_states[phase] = "ENTERED"
        elif event == "PHASE_END":
            phase = entry["phase"]
            require(phase in PHASES and derived_states[phase] == "ENTERED" and
                    type(entry["check_result"]) is bool, "phase end differs")
            derived_states[phase] = "CONFIRMED" if entry["check_result"] else "FAILED"
        elif event == "TERMINAL":
            terminal.append(entry)
        if event == "CALL_BEGIN":
            require(call is not None and call not in seen_calls, "duplicate call begin")
            seen_calls.add(call)
            related = entry["related_call_id"]
            if related is not None:
                require(related in pending and pending[related]["origin"] == "INJECTED" and
                        entry["origin"] == "NATIVE" and pending[related]["operation"] == entry["operation"],
                        "forwarded call is not bound to its live proxy")
            pending[call] = entry
            if entry["origin"] == "NATIVE":
                native_order[call] = len(native_order) + 1
        elif event == "CALL_RETURN":
            require(call in pending, "return without begin")
            begin = pending.pop(call)
            for key in ("operation", "origin", "handle_id", "path_role", "actor_id", "related_call_id", "phase"):
                require(entry[key] == begin[key], "call pair differs")
            returns.append(entry)
        elif event == "CHECK":
            require(type(entry["check_result"]) is bool and entry["check_id"], "invalid check")
            checks.setdefault(entry["check_id"], []).append(entry["check_result"])
        elif event == "INJECTION":
            require(call in pending and pending[call]["origin"] == "INJECTED" and entry["origin"] == "INJECTED" and
                    bool(entry["outputs"]), "injection lacks original/proxy binding")
    require(not pending, "dangling native call", "RECORDING_INCOMPLETE")
    require(states == derived_states and len(terminal) == 1 and terminal[0] == entries[-1] and
            terminal[0]["subject_status"] == status, "derived phase/terminal state differs")
    native_failures = [r for r in returns if r["origin"] == "NATIVE" and r["native_error"] is not None]
    injected = [r for r in returns if r["origin"] == "INJECTED" and
                (r["injected_error"] is not None or r["operation"] == "WriteFile")]
    cleanup = [r["call_id"] for r in returns if r["operation"] == "CloseHandle" and
               (r["native_error"] is not None or r["injected_error"] is not None)]
    trigger = spec["trigger"]
    matches = [r for r in returns if r["phase"] == spec["terminal_phase"] and
               r["operation"] == trigger["operation"] and r["path_role"] == trigger["role"] and
               r["actor_id"] == actors["helper" if spec["case_id"] == "p06" else "worker"] and
               r["origin"] == ("INJECTED" if spec["evidence_kind"] == "INJECTED" else "NATIVE") and
               (r["injected_error"] if r["origin"] == "INJECTED" else r["native_error"]) == trigger["error_code"]]
    if spec["case_id"] == "p05":
        matches = [r for r in returns if r["operation"] == "SetFileInformationByHandle" and
                   r["path_role"] == "staging" and r["phase"] == "E5" and
                   r["actor_id"] == actors["worker"] and r["native_error"] not in (None, 0)]
    if spec["case_id"] in ("p07", "p10"):
        by_id = {e["call_id"]: e for e in entries if e["event"] == "CALL_BEGIN"}
        def short_write(r):
            requested = next(v["value"] for v in by_id[r["call_id"]]["arguments"] if v["parameter"] == "nNumberOfBytesToWrite")
            transferred = next(v["value"] for v in r["outputs"] if v["parameter"] == "lpNumberOfBytesWritten")
            forwarded = [v for v in returns if v["related_call_id"] == r["call_id"] and v["origin"] == "NATIVE"]
            return (type(requested) is int and requested > 1 and type(transferred) is int and transferred == requested - 1
                    and r["raw_return"] != 0 and len(forwarded) == 1 and forwarded[0]["native_error"] is None)
        matches = [r for r in matches if short_write(r)]
    unexpected_native = [r for r in native_failures if r not in matches and not
                         (r["operation"] == "GetFileAttributesW" and r["native_error"] == 2)]
    expected = status == spec["expected_subject_status"] and not unexpected_native
    expected = expected and checks.get("sources-unchanged") == [True] and checks.get("case-postconditions") == [True]
    if spec["case_id"] == "p01":
        expected = expected and all(v == "CONFIRMED" for v in states.values()) and not cleanup and not injected
        expected = expected and checks.get("helper.before-rename") == [True] and checks.get("helper.after-rename") == [True]
    elif spec["case_id"] == "p02":
        expected = expected and states["E0"] == "FAILED" and checks.get("expected-parent-mismatch") == [True] and not cleanup
    elif spec["case_id"] == "p13":
        expected = expected and states["E8"] == "CONFIRMED" and all(states[p] == "NOT_REACHED" for p in PHASES[:-1]) and not cleanup
    else:
        expected = expected and len(matches) == 1 and states[spec["terminal_phase"]] == "FAILED"
        expected = expected and (not cleanup or spec["case_id"] == "p12" and cleanup == [matches[0]["call_id"]])
        if spec["evidence_kind"] == "INJECTED":
            expected = expected and len(injected) == 1
    calls = _call_pairs(entries, binding)
    if expected:
        evidence = _Evidence(calls, binding, spec["case_id"])
        evidence.accept_case(entries, states)
    first = min(native_failures, key=lambda r: native_order[r["call_id"]]) if native_failures else None
    return {"matched": bool(expected), "first_native": first["call_id"] if first else None,
            "first_injected": injected[0]["call_id"] if injected else None, "cleanup": cleanup,
            "native_failure": None if first is None else {"case_id": header["case_id"],
            "call_ordinal": native_order[first["call_id"]], "operation": first["operation"], "native_error": first["native_error"]}}


def validate_trace(raw, binding):
    require(type(raw) is bytes and raw.endswith(b"\n") and len(raw) <= binding.limits.trace_bytes,
            "incomplete or oversized trace", "RECORDING_INCOMPLETE")
    values = [loads(line) for line in raw.splitlines()]
    require(len(values) >= 2 and b"".join(encoded(v) + b"\n" for v in values) == raw, "noncanonical trace")
    eu, _, profile, run, source, _, actors, _ = binding.values()
    header, footer = values[0], values[-1]
    require(header["case_id"] in CASES, "unknown case")
    expected_header = record("s2eu.trace.v1", attempt_id=ATTEMPT, case_id=header["case_id"],
                             profile_digest=profile["record_digest"], run_binding_digest=run["record_digest"],
                             source_manifest_digest=source["record_digest"], expected_contract_digest=EU_DIGEST)
    require(header == expected_header, "trace source binding differs")
    for value, kind in [(footer, "TraceFooter"), *[(e, "TraceEntry") for e in values[1:-1]]]:
        require(set(value) == set(eu["data_forms"][kind]), "trace fields differ")
        if kind == "TraceEntry":
            validate_entry(value, eu)
    require(set(footer["phase_states"]) == set(PHASES), "phase state keys differ")
    observation = inspect_entries(header, values[1:-1], footer["phase_states"],
                                  eu["cases"][CASES.index(header["case_id"] )], actors, footer["subject_status"], binding)
    expected_footer = record("s2eu.trace-footer.v1", case_id=header["case_id"], entry_count=len(values) - 2,
                             last_entry_digest=values[-2]["record_digest"], phase_states=footer["phase_states"],
                             subject_status=footer["subject_status"], expected_outcome_matched=observation["matched"],
                             first_failed_native_call=observation["first_native"],
                             first_injected_failure=observation["first_injected"], cleanup_failures=observation["cleanup"])
    require(footer == expected_footer, "trace footer differs")
    return observation
