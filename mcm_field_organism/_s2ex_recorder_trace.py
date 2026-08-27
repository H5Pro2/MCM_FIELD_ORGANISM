"""Private bounded E0-E8 recorder and read-only trace acceptance."""

from __future__ import annotations

from contextlib import contextmanager
from threading import RLock

from ._s2er_publication_records import PublicationError, digest, encoded, loads, require
from ._s2ex_recorder_binding import ATTEMPT, CASES, EU_DIGEST, PHASES, b64, clone, local_id, record, unb64


def typed(parameter, value, encoding=None):
    if encoding is None:
        encoding = "NULL" if value is None else "BOOLEAN" if type(value) is bool else "INTEGER"
    if encoding in ("BYTES_BASE64", "UTF16LE_BASE64"):
        value = b64(value if type(value) is bytes else value.encode("utf-16-le"))
    return {"parameter": parameter, "encoding": encoding, "value": value}


def validate_entry(entry, eu):
    require(set(entry) == set(eu["data_forms"]["TraceEntry"]), "entry fields differ")
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
        observation = inspect_entries(self.header, self.entries, self.states, self.spec, self.actors, status)
        footer = record("s2eu.trace-footer.v1", case_id=self.case_id, entry_count=len(self.entries),
                        last_entry_digest=self.last_digest, phase_states=dict(self.states), subject_status=status,
                        expected_outcome_matched=observation["matched"],
                        first_failed_native_call=observation["first_native"],
                        first_injected_failure=observation["first_injected"], cleanup_failures=observation["cleanup"])
        self._write(footer)
        self.closed = True
        return b"".join(self.raw_parts)


def inspect_entries(header, entries, states, spec, actors, status):
    pending, returns, native_order, checks = {}, [], {}, {}
    seen_calls = set()
    derived_states = dict.fromkeys(PHASES, "NOT_REACHED")
    terminal = []
    last = header["record_digest"]
    for index, entry in enumerate(entries, 1):
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
                                  eu["cases"][CASES.index(header["case_id"] )], actors, footer["subject_status"])
    expected_footer = record("s2eu.trace-footer.v1", case_id=header["case_id"], entry_count=len(values) - 2,
                             last_entry_digest=values[-2]["record_digest"], phase_states=footer["phase_states"],
                             subject_status=footer["subject_status"], expected_outcome_matched=observation["matched"],
                             first_failed_native_call=observation["first_native"],
                             first_injected_failure=observation["first_injected"], cleanup_failures=observation["cleanup"])
    require(footer == expected_footer, "trace footer differs")
    return observation
