"""Private synchronous file-handle backend. Construction is explicit, never at import."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import os
from pathlib import PureWindowsPath

from ._s2er_publication_records import PublicationError, canonical_path, require


@dataclass(slots=True)
class _Handle:
    value: int | None
    path: str
    directory: bool
    writable: bool
    rename_allowed: bool
    identity: dict | None = None
    write_attempted: bool = False
    rename_attempted: bool = False


class WindowsFiles:
    """Owns handles until close_all; never creates directories or volume handles."""

    def __init__(self):
        require(os.name == "nt", "Windows backend required", "BLOCKED_PLATFORM_PREREQUISITE")
        self.handles: list[_Handle] = []
        self.parents: dict[str, _Handle] = {}
        self.source_roots: tuple[PureWindowsPath, ...] = ()
        self.failed = False
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        h, d, p = wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID
        signatures = {
            "CreateFileW": ((wintypes.LPCWSTR, d, d, p, d, d, h), h),
            "CloseHandle": ((h,), wintypes.BOOL),
            "FlushFileBuffers": ((h,), wintypes.BOOL),
            "WriteFile": ((h, p, d, ctypes.POINTER(d), p), wintypes.BOOL),
            "ReadFile": ((h, p, d, ctypes.POINTER(d), p), wintypes.BOOL),
            "SetFilePointerEx": ((h, ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong), d), wintypes.BOOL),
            "GetFileSizeEx": ((h, ctypes.POINTER(ctypes.c_longlong)), wintypes.BOOL),
            "GetFileInformationByHandleEx": ((h, ctypes.c_int, p, d), wintypes.BOOL),
            "GetFileInformationByHandle": ((h, p), wintypes.BOOL),
            "SetFileInformationByHandle": ((h, ctypes.c_int, p, d), wintypes.BOOL),
            "GetFinalPathNameByHandleW": ((h, wintypes.LPWSTR, d, d), d),
            "GetFileAttributesW": ((wintypes.LPCWSTR,), d),
            "GetDriveTypeW": ((wintypes.LPCWSTR,), wintypes.UINT),
            "GetVolumeInformationByHandleW": ((h, wintypes.LPWSTR, d, ctypes.POINTER(d),
                                               ctypes.POINTER(d), ctypes.POINTER(d), wintypes.LPWSTR, d), wintypes.BOOL),
        }
        for name, (args, result) in signatures.items():
            function = getattr(self.kernel, name)
            function.argtypes, function.restype = args, result

    def _ok(self, result, operation):
        if not result:
            error = ctypes.get_last_error()
            self.failed = True
            raise PublicationError("NATIVE_PUBLICATION_ERROR", operation, native_error=error)
        return result

    def _active(self):
        require(not self.failed, "backend is terminal", "PUBLICATION_TERMINAL")

    def _open(self, path, *, directory=False, create=False, rename=False, verification=False):
        self._active()
        canonical_path(path)
        access = 0x80000000 | (0x40000000 if create else 0) | (0x10000 if rename else 0)
        # Read verification must share the retained writer's access; owned
        # writers themselves share only reads, never foreign writes/deletes.
        sharing = 1 if create else (3 if directory else (7 if verification else 1))
        flags = 0x00200000 | (0x02000000 if directory else 0) | (0x80000000 if create else 0)
        handle = self.kernel.CreateFileW(path, access, sharing, None, 1 if create else 3, flags, None)
        if handle == ctypes.c_void_p(-1).value:
            error = ctypes.get_last_error()
            self.failed = True
            raise PublicationError("NATIVE_PUBLICATION_ERROR", "CreateFileW", native_error=error)
        owned = _Handle(handle, path, directory, create, rename)
        self.handles.append(owned)
        owned.identity = self.inspect(owned)
        return owned

    def inspect(self, handle: _Handle) -> dict:
        require(handle.value is not None, "closed handle")

        class FileIdInfo(ctypes.Structure):
            _fields_ = [("serial", ctypes.c_ulonglong), ("identifier", ctypes.c_ubyte * 16)]

        class ByHandleInfo(ctypes.Structure):
            _fields_ = [("attributes", wintypes.DWORD), ("creation", wintypes.FILETIME),
                        ("access", wintypes.FILETIME), ("write", wintypes.FILETIME),
                        ("serial", wintypes.DWORD), ("size_high", wintypes.DWORD),
                        ("size_low", wintypes.DWORD), ("links", wintypes.DWORD),
                        ("index_high", wintypes.DWORD), ("index_low", wintypes.DWORD)]

        info, identifier = ByHandleInfo(), FileIdInfo()
        self._ok(self.kernel.GetFileInformationByHandle(handle.value, ctypes.byref(info)), "GetFileInformationByHandle")
        require(not info.attributes & 0x400 and bool(info.attributes & 0x10) == handle.directory,
                "reparse or unexpected file type")
        require(handle.directory or info.links == 1, "unexpected hardlink")
        self._ok(self.kernel.GetFileInformationByHandleEx(handle.value, 18, ctypes.byref(identifier),
                                                       ctypes.sizeof(identifier)), "FileIdInfo")
        filesystem = ctypes.create_unicode_buffer(261)
        self._ok(self.kernel.GetVolumeInformationByHandleW(handle.value, None, 0, None, None, None,
                                                          filesystem, len(filesystem)), "GetVolumeInformationByHandleW")
        require(filesystem.value == "NTFS", "NTFS required", "BLOCKED_PLATFORM_PREREQUISITE")
        name = ctypes.create_unicode_buffer(32768)
        count = self.kernel.GetFinalPathNameByHandleW(handle.value, name, len(name), 0)
        self._ok(count, "GetFinalPathNameByHandleW")
        require(count < len(name), "truncated native path")
        native = name.value
        if native.startswith("\\\\?\\") and len(native) > 6 and native[5:7] == ":\\":
            native = native[4:]
        require(native == handle.path, "native path alias or changed name")
        if handle.directory:
            case_flags = wintypes.DWORD()
            self._ok(self.kernel.GetFileInformationByHandleEx(handle.value, 23, ctypes.byref(case_flags),
                                                           ctypes.sizeof(case_flags)), "FileCaseSensitiveInfo")
            require(case_flags.value == 0, "case-sensitive namespace is not admitted")
        return {"volume": {"filesystem": "NTFS", "serial_hex": f"{identifier.serial:016x}"},
                "file_id_hex": bytes(identifier.identifier).hex()}

    def pin_parents(self, parent_set: dict) -> None:
        self._active()
        self.source_roots = tuple(PureWindowsPath(parent_set[role]["path"])
                                  for role in ("repository", "git_common"))
        for parent in parent_set.values():
            path = PureWindowsPath(canonical_path(parent["path"]))
            require(self.kernel.GetDriveTypeW(path.anchor) == 3, "local fixed drive required")
            for ancestor in (*reversed(path.parents), path):
                name = str(ancestor)
                if name not in self.parents:
                    self.parents[name] = self._open(name, directory=True)
            require(self.parents[str(path)].identity == parent["identity"], "parent native identity differs",
                    "BLOCKED_PLATFORM_PREREQUISITE")
        self.verify_parents()

    def verify_parents(self):
        self._active()
        for handle in self.parents.values():
            require(self.inspect(handle) == handle.identity, "parent identity changed")

    def _pin_file_parent(self, path):
        require(str(PureWindowsPath(path).parent) in self.parents, "unbound parent directory")
        self.verify_parents()

    def require_absent(self, path):
        self._active()
        canonical_path(path)
        self._pin_file_parent(path)
        attributes = self.kernel.GetFileAttributesW(path)
        if attributes == 0xFFFFFFFF:
            error = ctypes.get_last_error()
            if error == 2:
                return
            self.failed = True
            raise PublicationError("NATIVE_PUBLICATION_ERROR", "GetFileAttributesW", native_error=error)
        raise PublicationError("PUBLICATION_ALREADY_CONSUMED", "destination already exists")

    def read_source(self, path: str, expected_size: int | None = None) -> tuple[_Handle, bytes]:
        self._active()
        parent = PureWindowsPath(path).parent
        # Sources may be nested under the pinned repository; every ancestor is
        # retained before opening, so source parent replacements cannot race us.
        require(any(parent.is_relative_to(p) for p in self.source_roots), "source outside pinned domain")
        for ancestor in (*reversed(parent.parents), parent):
            name = str(ancestor)
            if name not in self.parents:
                self.parents[name] = self._open(name, directory=True)
        self._pin_file_parent(path)
        handle = self._open(path)
        return handle, self.read(handle, expected_size)

    def create(self, path: str, *, rename=False) -> _Handle:
        self._active()
        self._pin_file_parent(path)
        handle = self._open(path, create=True, rename=rename)
        parent = self.parents[str(PureWindowsPath(path).parent)]
        require(handle.identity["volume"] == parent.identity["volume"], "created file changed volume")
        return handle

    def write_complete(self, handle: _Handle, raw: bytes) -> None:
        self._active()
        require(type(raw) is bytes and bool(raw) and handle.writable and not handle.write_attempted,
                "write requires fresh owned file and immutable bytes")
        requests = tuple(raw[start:start + 1048576] for start in range(0, len(raw), 1048576))
        handle.write_attempted = True
        for request in requests:
            transferred = wintypes.DWORD()
            buffer = ctypes.create_string_buffer(request)
            self._ok(self.kernel.WriteFile(handle.value, buffer, len(request), ctypes.byref(transferred), None), "WriteFile")
            if transferred.value != len(request):
                self.failed = True
                raise PublicationError("SHORT_WRITE", "short write is terminal")

    def flush(self, handle: _Handle) -> None:
        self._active()
        require(handle.writable and handle.value is not None, "owned writable file required")
        self._ok(self.kernel.FlushFileBuffers(handle.value), "FlushFileBuffers")

    def read(self, handle: _Handle, expected_size: int | None = None) -> bytes:
        size = ctypes.c_longlong()
        self._ok(self.kernel.GetFileSizeEx(handle.value, ctypes.byref(size)), "GetFileSizeEx")
        require(size.value >= 0 and (expected_size is None or expected_size == size.value), "file length differs")
        length = size.value
        self._ok(self.kernel.SetFilePointerEx(handle.value, 0, None, 0), "SetFilePointerEx")
        parts = []
        for start in range(0, length, 1048576):
            count = min(1048576, length - start)
            buffer, transferred = ctypes.create_string_buffer(count), wintypes.DWORD()
            self._ok(self.kernel.ReadFile(handle.value, buffer, count, ctypes.byref(transferred), None), "ReadFile")
            require(transferred.value == count, "short read")
            parts.append(buffer.raw)
        self._ok(self.kernel.GetFileSizeEx(handle.value, ctypes.byref(size)), "GetFileSizeEx")
        require(size.value == length and self.inspect(handle) == handle.identity, "file changed during read")
        return b"".join(parts)

    def verify(self, handle: _Handle, expected: bytes):
        self.verify_parents()
        require(self.read(handle, len(expected)) == expected, "full file content differs")

    def rename_no_replace(self, handle: _Handle, final: str) -> None:
        self._active()
        self._pin_file_parent(final)
        require(handle.rename_allowed and not handle.rename_attempted and handle.writable,
                "one retained staging rename required")
        require(PureWindowsPath(final).parent == PureWindowsPath(handle.path).parent, "rename parent differs")
        require(self.inspect(handle) == handle.identity, "staging identity changed")

        class RenameInfo(ctypes.Structure):
            _fields_ = [("replace", ctypes.c_ubyte), ("root", wintypes.HANDLE),
                        ("name_length", wintypes.DWORD), ("name", wintypes.WCHAR * 1)]

        name = final.encode("utf-16-le")
        buffer = ctypes.create_string_buffer(max(ctypes.sizeof(RenameInfo), RenameInfo.name.offset + len(name)))
        info = ctypes.cast(buffer, ctypes.POINTER(RenameInfo)).contents
        info.replace, info.root, info.name_length = 0, None, len(name)
        ctypes.memmove(ctypes.addressof(buffer) + RenameInfo.name.offset, name, len(name))
        handle.rename_attempted = True
        self._ok(self.kernel.SetFileInformationByHandle(handle.value, 3, buffer,
                                                       RenameInfo.name.offset + len(name)), "FileRenameInfo")
        handle.path = final

    def verify_final_name(self, handle: _Handle):
        reader = self._open(handle.path, verification=True)
        require(reader.identity == handle.identity, "final name identifies another file")

    def close_all(self, *, suppress=False):
        errors = []
        for handle in reversed(self.handles):
            if handle.value is not None:
                value, handle.value = handle.value, None
                if not self.kernel.CloseHandle(value):
                    error = ctypes.get_last_error()
                    errors.append(error)
        if errors:
            self.failed = True
            if not suppress:
                raise PublicationError("NATIVE_PUBLICATION_ERROR", "CloseHandle", native_error=errors[0])
        return tuple(errors)
