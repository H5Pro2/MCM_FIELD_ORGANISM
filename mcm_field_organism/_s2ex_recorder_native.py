"""Private per-instance native recording boundary. Execution remains locked."""

from __future__ import annotations

from dataclasses import dataclass
import ctypes

from ._s2er_publication_records import PublicationError, require
from ._s2er_windows_files import WindowsFiles
from ._s2ex_recorder_trace import typed


_PLATFORM_EXECUTION_RELEASED = False
_REVIEWED_BINDINGS = frozenset()


def require_execution(binding):
    require(_PLATFORM_EXECUTION_RELEASED is True and binding.identity() in _REVIEWED_BINDINGS,
            "separate execution authorization and independent source admission required",
            "BLOCKED_PLATFORM_PREREQUISITE")


@dataclass(slots=True)
class NativeHandle:
    logical_id: str
    row: object
    writable: bool
    rename_allowed: bool
    closed: bool = False


def number(value):
    return int(value.value if hasattr(value, "value") else value or 0)


class NativeRecorder:
    def __init__(self, kernel, binding, trace, actor):
        require_execution(binding)
        eu, _, _, _, _, _, _, inventory = binding.values()
        self.raw, self.binding, self.trace, self.actor = kernel, binding, trace, actor
        self.inventory, self.parameters = inventory, eu["recorder"]["api_parameters"]
        self.handles, self.occurrences = {}, {}
        self.created, self.rename_attempts = set(), set()
        self.handle_serial = 0
        self.injection_used = False
        self.failed_close_ids = []

    def __getattr__(self, name):
        require(name in self.parameters, "undeclared native API")
        return lambda *args: self.invoke(name, args)

    def _bytes(self, pointer, size):
        require(type(size) is int and 0 <= size <= self.binding.limits.buffer_bytes,
                "native buffer exceeds pinned ceiling", "RECORDING_INCOMPLETE")
        return ctypes.string_at(pointer, size) if pointer and size else b""

    def _scalar(self, pointer, wide=False):
        if not pointer:
            return None
        return ctypes.cast(pointer, ctypes.POINTER(ctypes.c_longlong if wide else ctypes.c_uint32))[0]

    def _handle(self, value):
        value = number(value)
        require(value in self.handles and not self.handles[value].closed, "unbound or closed native handle")
        return self.handles[value]

    def _row(self, operation, args):
        if operation in ("CreateFileW", "GetFileAttributesW", "GetDriveTypeW"):
            return self.inventory.resolve(args[0]), None
        handle = self._handle(args[0])
        return handle.row, handle

    def _authorize(self, operation, args, row, handle):
        case, phase = self.trace.case_id, self.trace.phase
        role = row.role
        if self.actor == "supervisor":
            require(row.case_id is None or role.startswith("recorder.") or role == "trace" or
                    operation == "GetFileAttributesW", "supervisor subject access")
        elif not role.startswith(("source.", "directory.")):
            require(row.case_id == case or case == "p13" and row.case_id == "p01", "foreign case path")
            require(not role.startswith("recorder.") and role != "trace", "subject recorder access")
        write = operation == "WriteFile" or operation == "CreateFileW" and bool(number(args[1]) & 0x40000000)
        if write or operation in ("FlushFileBuffers", "SetFileInformationByHandle"):
            require(not role.startswith(("source.", "directory.")) and case != "p13", "read-only path operation")
            if self.actor == "helper":
                allowed = {"p03": "case_reservation", "p04": "target_reservation", "p05": "final", "p06": "case_reservation"}
                require(role == allowed.get(case), "unbound helper write")
                require(case != "p06" or operation == "CreateFileW", "p06 only attempts foreign open")
            elif self.actor == "worker":
                phase_roles = {"E1": {"case_reservation"}, "E2": {"target_reservation"},
                               "E3": {"evidence"}, "E4": {"staging", "sealed"},
                               "E5": {"staging"}, "E6": {"final"}, "E7": {"marker"}}
                require(role in phase_roles.get(phase, set()), "write outside bound phase")
        if operation == "CreateFileW":
            require(args[3] is None and args[6] is None, "unbound security/template handle")
            access, sharing, disposition, flags = (number(args[i]) for i in (1, 2, 4, 5))
            require(disposition in (1, 3), "only CREATE_NEW or OPEN_EXISTING")
            if disposition == 1:
                require(row.path not in self.created, "creation retry")
                require(not role.startswith(("directory.", "source.")), "cannot create read-only path")
                require(access & 0xC0000000 == 0xC0000000 and sharing == 1 and flags & 0x80000000,
                        "owned file flags differ")
                require(row.lifecycle not in ("RECORDING_FINAL", "SUBJECT_FINAL") or
                        self.actor == "helper" and case == "p05", "direct final creation")
                self.created.add(row.path)
            elif access & (0x40000000 | 0x10000):
                require(self.actor == "helper" and case == "p06" and role == "case_reservation" and
                        access == 0x40000000 and sharing == 7, "foreign write access not admitted")
        if operation == "WriteFile":
            require(handle.writable, "unowned writer")
            require(row.lifecycle not in ("RECORDING_FINAL", "SUBJECT_FINAL") or
                    self.actor == "helper" and case == "p05", "cannot rewrite final output")
        if operation == "FlushFileBuffers":
            require(handle.writable, "unowned flush")
        if operation == "SetFileInformationByHandle":
            require(handle.rename_allowed and number(args[1]) == 3 and handle.logical_id not in self.rename_attempts,
                    "rename permission or retry")
            self.rename_attempts.add(handle.logical_id)

    def _arguments(self, name, args, handle):
        require(len(args) == len(self.parameters[name]), "native signature arity differs")
        result = []
        for index, (parameter, value) in enumerate(zip(self.parameters[name], args)):
            if index == 0 and name in ("CreateFileW", "GetFileAttributesW", "GetDriveTypeW"):
                item = typed(parameter, value, "UTF16LE_BASE64")
            elif index == 0:
                item = typed(parameter, handle.logical_id, "LOGICAL_HANDLE")
            elif name in ("ReadFile", "WriteFile") and index == 1:
                item = typed(parameter, self._bytes(value, number(args[2])), "BYTES_BASE64")
            elif name in ("ReadFile", "WriteFile") and index == 3:
                item = typed(parameter, self._scalar(value))
            elif name in ("GetFileInformationByHandleEx", "SetFileInformationByHandle") and index == 2:
                item = typed(parameter, self._bytes(value, number(args[3])), "BYTES_BASE64")
            elif name == "GetFileInformationByHandle" and index == 1:
                item = typed(parameter, self._bytes(value, 52), "BYTES_BASE64")
            elif name == "GetFinalPathNameByHandleW" and index == 1:
                item = typed(parameter, self._bytes(value, number(args[2]) * 2), "BYTES_BASE64")
            elif name == "GetVolumeInformationByHandleW" and index in (1, 6):
                item = typed(parameter, None) if not value else typed(parameter, self._bytes(value, number(args[index + 1]) * 2), "BYTES_BASE64")
            elif name == "GetVolumeInformationByHandleW" and index in (3, 4, 5):
                item = typed(parameter, self._scalar(value))
            elif name == "GetFileSizeEx" and index == 1 or name == "SetFilePointerEx" and index == 2:
                item = typed(parameter, self._scalar(value, wide=True))
            elif value is None:
                item = typed(parameter, None)
            else:
                require(type(value) is int or hasattr(value, "value"), "unserialized native pointer")
                item = typed(parameter, number(value))
            result.append(item)
        return result

    def _outputs(self, name, args, success, created):
        slots = {"WriteFile": (3,), "ReadFile": (1, 3), "GetFileSizeEx": (1,), "SetFilePointerEx": (2,),
                 "GetFileInformationByHandle": (1,), "GetFileInformationByHandleEx": (2,),
                 "GetFinalPathNameByHandleW": (1,), "GetVolumeInformationByHandleW": (1, 3, 4, 5, 6)}
        if name == "CreateFileW":
            return [typed("opened_handle", created.logical_id if created else None,
                          "LOGICAL_HANDLE" if created else "NULL")]
        if name in ("GetDriveTypeW", "GetFileAttributesW"):
            return []
        handle = self.handles.get(number(args[0]))
        values = self._arguments(name, args, handle)
        return [values[i] for i in slots.get(name, ())]

    def _rename_target(self, args):
        class RenameInfo(ctypes.Structure):
            _fields_ = [("replace", ctypes.c_ubyte), ("root", ctypes.c_void_p),
                        ("length", ctypes.c_uint32), ("name", ctypes.c_wchar * 1)]
        size = number(args[3])
        require(size >= RenameInfo.name.offset, "short rename buffer")
        info = ctypes.cast(args[2], ctypes.POINTER(RenameInfo)).contents
        require(info.replace == 0 and not info.root and info.length % 2 == 0 and
                size == RenameInfo.name.offset + info.length, "unbound rename buffer")
        raw = self._bytes(args[2], size)
        return raw[RenameInfo.name.offset:].decode("utf-16-le")

    def invoke(self, name, args, *, related=None, forwarded=False):
        row, handle = self._row(name, args)
        role = "foreign_write_handle" if self.actor == "helper" and self.trace.case_id == "p06" and name == "CreateFileW" and row.role == "case_reservation" else row.role
        if not forwarded:
            self._authorize(name, args, row, handle)
        key = (self.trace.phase, name, role)
        if not forwarded:
            self.occurrences[key] = self.occurrences.get(key, 0) + 1
        spec = getattr(self.trace, "spec", None)
        trigger = spec["trigger"] if spec else None
        inject = (not forwarded and self.actor == "worker" and spec is not None and
                  spec["evidence_kind"] == "INJECTED" and self.trace.phase == spec["terminal_phase"] and
                  name == trigger["operation"] and role == trigger["role"] and
                  self.occurrences[key] == trigger["occurrence"])
        call = self.trace.call_id()
        arguments = self._arguments(name, args, handle)
        common = dict(call_id=call, operation=name, handle_id=handle.logical_id if handle else None,
                      path_role=role, origin="INJECTED" if inject else "NATIVE", related_call_id=related)
        self.trace.emit("CALL_BEGIN", self.actor, arguments=arguments, **common)
        target = self._rename_target(args) if name == "SetFileInformationByHandle" else None
        if target is not None:
            require(self.inventory.edges.get(row.path) == target, "rename destination differs")
        if inject:
            require(not self.injection_used, "injection reused")
            self.injection_used = True
            if name == "WriteFile":
                request = number(args[2])
                require(request > 1, "short-write fixture too small")
                changed = list(args)
                changed[2] = request - 1
                result = self.invoke(name, tuple(changed), related=call, forwarded=True)
                error = ctypes.get_last_error() if not result else None
            elif name == "CloseHandle":
                result = self.invoke(name, args, related=call, forwarded=True)
                if not result:
                    error = ctypes.get_last_error()
                    self.trace.emit("CALL_RETURN", self.actor, outputs=[], raw_return=0,
                                    injected_error=None, **common)
                    ctypes.set_last_error(error)
                    return result
                error = 5
                result = 0
            else:
                result, error = 0, 5
            outputs = self._outputs(name, args, bool(result), None)
            self.trace.emit("INJECTION", self.actor, arguments=arguments,
                            outputs=[typed("intended_request_bytes", number(args[2]) if name == "WriteFile" else None),
                                     typed("actual_proxy_return", number(result)),
                                     typed("actual_proxy_error", error), *outputs], **common)
            self.trace.emit("CALL_RETURN", self.actor, outputs=outputs, raw_return=number(result), injected_error=error, **common)
            if error is not None:
                ctypes.set_last_error(error)
            return result
        if name == "CloseHandle":
            # An attempted close cannot be retried even when recording fails.
            handle.closed = True
        result = getattr(self.raw, name)(*args)
        if name == "CreateFileW":
            success = result not in (None, ctypes.c_void_p(-1).value)
        elif name == "GetFileAttributesW":
            success = number(result) != 0xFFFFFFFF
        elif name == "GetDriveTypeW":
            success = True
        else:
            success = bool(result)
        error = ctypes.get_last_error() if not success else None
        created = None
        if name == "CreateFileW" and success:
            self.handle_serial += 1
            created = NativeHandle(f"{self.trace.case_id or 'control'}.{self.actor}.handle.{self.handle_serial}", row,
                                   bool(number(args[1]) & 0x40000000), bool(number(args[1]) & 0x10000))
            self.handles[number(result)] = created
        outputs = self._outputs(name, args, success, created)
        self.trace.emit("CALL_RETURN", self.actor, outputs=outputs, raw_return=number(result), native_error=error, **common)
        if name == "CloseHandle":
            if not success:
                self.failed_close_ids.append(handle.logical_id)
        if name == "SetFileInformationByHandle" and success:
            handle.row = self.inventory.resolve(target)
        if error is not None:
            ctypes.set_last_error(error)
        return result

    def close_unrecorded_on_abort(self):
        """Last-resort cleanup only; the recording remains irrecoverably incomplete."""
        failures = []
        for value, handle in self.handles.items():
            if not handle.closed:
                handle.closed = True
                result = self.raw.CloseHandle(value)
                error = ctypes.get_last_error() if not result else None
                if error is not None:
                    failures.append((handle.logical_id, error))
        return tuple(failures)


def open_recorded_backend(binding, trace, actor):
    require_execution(binding)
    binding.values()
    backend = WindowsFiles()
    backend.kernel = NativeRecorder(backend.kernel, binding, trace, actor)
    return backend
