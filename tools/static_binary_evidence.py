"""Fail-closed static PE and CPython table evidence collector.

This module is intentionally a raw-byte parser. It must not load, import, or
link any target binary. Execution is separately gated by the research process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NoReturn


SCHEMA_CONTROL = "mcm-g1-static-binary-control-v1"
SCHEMA_EXPORT = "mcm-g1-pe-export-evidence-v1"
SCHEMA_TABLE = "mcm-g1-cpython-table-evidence-v1"
SCHEMA_REPORT = "mcm-g1-static-binary-report-v1"
SCHEMA_ERROR = "mcm-g1-static-binary-errors-v1"
MACHINE_AMD64 = 0x8664
PE32_PLUS_MAGIC = 0x20B
IMAGE_DIRECTORY_ENTRY_EXPORT = 0
IMAGE_DIRECTORY_ENTRY_BASERELOC = 5
IMAGE_REL_BASED_DIR64 = 10
MAX_ASCII = 1024
MAX_TABLE_ENTRIES = 4096
PE_PAGE_SIZE = 0x1000
PE_IMAGE_BASE_ALIGNMENT = 0x10000
PE_MIN_FILE_ALIGNMENT = 0x200
PE_MAX_FILE_ALIGNMENT = 0x10000


class EvidenceError(Exception):
    def __init__(
        self,
        code: str,
        detail: str,
        *,
        path: str | None = None,
        offset: int | None = None,
        rva: int | None = None,
        structure: str | None = None,
    ) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.path = path
        self.offset = offset
        self.rva = rva
        self.structure = structure

    def record(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "detail": self.detail,
            "offset": self.offset,
            "path": self.path,
            "rva": self.rva,
            "structure": self.structure,
        }


@dataclass(frozen=True)
class Binding:
    path: str
    role: str
    size: int
    sha256: str


@dataclass
class ErrorContext:
    started_utc: str
    expected_control: Binding | None = None
    control_binding: Binding | None = None
    tool_binding: Binding | None = None
    contract_binding: Binding | None = None
    input_bindings: list[Binding] | None = None

    def __post_init__(self) -> None:
        if self.input_bindings is None:
            self.input_bindings = []


@dataclass(frozen=True)
class Section:
    name: str
    virtual_address: int
    virtual_size: int
    raw_offset: int
    raw_size: int


@dataclass(frozen=True)
class Directory:
    rva: int
    size: int


@dataclass(frozen=True)
class Export:
    name: str
    ordinal: int
    function_rva: int
    forwarded: bool


@dataclass(frozen=True)
class Relocation:
    kind: int
    entry_file_offset: int
    block_page_rva: int
    target_rva: int


def _fail(code: str, detail: str, **location: Any) -> NoReturn:
    raise EvidenceError(code, detail, **location)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _canonical(path: Path) -> str:
    return path.resolve(strict=True).as_posix()


def _binding(path: Path, role: str) -> Binding:
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        _fail("INPUT_BINDING_MISMATCH", "input is not a regular file", path=str(path))
    stat = resolved.stat()
    return Binding(_canonical(resolved), role, stat.st_size, _sha256(resolved))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("INPUT_BINDING_MISMATCH", f"invalid JSON input: {exc}", path=str(path))
    if not isinstance(value, dict):
        _fail("INPUT_BINDING_MISMATCH", "JSON root must be an object", path=str(path))
    return value


def _parse_binding(value: Any, label: str) -> Binding:
    if not isinstance(value, dict):
        _fail("INPUT_BINDING_MISMATCH", f"{label} must be an object")
    path = value.get("path")
    role = value.get("role")
    size = value.get("size")
    sha256 = value.get("sha256")
    if not isinstance(path, str) or not path:
        _fail("INPUT_BINDING_MISMATCH", f"{label}.path must be a nonempty string")
    if not isinstance(role, str) or not role:
        _fail("INPUT_BINDING_MISMATCH", f"{label}.role must be a nonempty string")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        _fail("INPUT_BINDING_MISMATCH", f"{label}.size must be a nonnegative integer")
    if not isinstance(sha256, str) or len(sha256) != 64:
        _fail("INPUT_BINDING_MISMATCH", f"{label}.sha256 must contain 64 hex characters")
    try:
        int(sha256, 16)
    except ValueError:
        _fail("INPUT_BINDING_MISMATCH", f"{label}.sha256 is not hexadecimal")
    return Binding(path, role, size, sha256.upper())


def _verify_binding(expected: Binding) -> tuple[Path, Binding]:
    path = Path(expected.path)
    try:
        actual = _binding(path, expected.role)
    except (OSError, RuntimeError) as exc:
        _fail("INPUT_BINDING_MISMATCH", f"cannot bind input: {exc}", path=expected.path)
    if actual.path != Path(expected.path).resolve(strict=True).as_posix():
        _fail("INPUT_BINDING_MISMATCH", "canonical path mismatch", path=expected.path)
    if actual.size != expected.size or actual.sha256 != expected.sha256:
        _fail(
            "INPUT_BINDING_MISMATCH",
            f"expected {expected.size}/{expected.sha256}, got {actual.size}/{actual.sha256}",
            path=expected.path,
        )
    return path.resolve(strict=True), actual


class PEImage:
    def __init__(self, path: Path, data: bytes) -> None:
        self.path = path.resolve(strict=True).as_posix()
        self.data = data
        self.sections: list[Section] = []
        self.directories: list[Directory] = []
        self.image_base = 0
        self.size_of_image = 0
        self.size_of_headers = 0
        self._relocations: dict[int, Relocation] | None = None
        self._exports: list[Export] | None = None
        self._parse_headers()

    @classmethod
    def read(cls, path: Path) -> PEImage:
        try:
            return cls(path, path.read_bytes())
        except EvidenceError:
            raise
        except OSError as exc:
            _fail("INPUT_BINDING_MISMATCH", f"cannot read PE input: {exc}", path=str(path))

    def _bounds(self, offset: int, size: int, structure: str) -> None:
        if offset < 0 or size < 0 or offset > len(self.data) or size > len(self.data) - offset:
            _fail(
                "INTEGER_OR_FILE_BOUNDS",
                f"range {offset}+{size} exceeds {len(self.data)} bytes",
                path=self.path,
                offset=offset,
                structure=structure,
            )

    def _unpack(self, fmt: str, offset: int, structure: str) -> tuple[Any, ...]:
        size = struct.calcsize(fmt)
        self._bounds(offset, size, structure)
        try:
            return struct.unpack_from(fmt, self.data, offset)
        except struct.error as exc:
            _fail("TRUNCATED_STRUCTURE", str(exc), path=self.path, offset=offset, structure=structure)

    def _u16(self, offset: int, structure: str) -> int:
        return int(self._unpack("<H", offset, structure)[0])

    def _u32(self, offset: int, structure: str) -> int:
        return int(self._unpack("<I", offset, structure)[0])

    def _u64(self, offset: int, structure: str) -> int:
        return int(self._unpack("<Q", offset, structure)[0])

    def _i32(self, offset: int, structure: str) -> int:
        return int(self._unpack("<i", offset, structure)[0])

    def _parse_headers(self) -> None:
        if len(self.data) < 64 or self.data[:2] != b"MZ":
            _fail("UNSUPPORTED_PE_FORMAT", "missing DOS MZ header", path=self.path)
        pe_offset = self._u32(0x3C, "DOS.e_lfanew")
        self._bounds(pe_offset, 24, "PE headers")
        if self.data[pe_offset : pe_offset + 4] != b"PE\0\0":
            _fail("UNSUPPORTED_PE_FORMAT", "missing PE signature", path=self.path, offset=pe_offset)
        coff = pe_offset + 4
        machine, section_count, _, _, _, optional_size, _ = self._unpack(
            "<HHIIIHH", coff, "COFF header"
        )
        if machine != MACHINE_AMD64:
            _fail("UNSUPPORTED_PE_FORMAT", f"machine is 0x{machine:04X}", path=self.path)
        if section_count < 1 or section_count > 96:
            _fail("UNSUPPORTED_PE_FORMAT", f"invalid section count {section_count}", path=self.path)
        optional = coff + 20
        self._bounds(optional, optional_size, "optional header")
        if optional_size < 112 or self._u16(optional, "optional magic") != PE32_PLUS_MAGIC:
            _fail("UNSUPPORTED_PE_FORMAT", "expected PE32+ optional header", path=self.path)
        self.image_base = self._u64(optional + 24, "ImageBase")
        section_alignment = self._u32(optional + 32, "SectionAlignment")
        file_alignment = self._u32(optional + 36, "FileAlignment")
        self.size_of_image = self._u32(optional + 56, "SizeOfImage")
        self.size_of_headers = self._u32(optional + 60, "SizeOfHeaders")
        directory_count = self._u32(optional + 108, "NumberOfRvaAndSizes")
        if not self.image_base or not section_alignment or not file_alignment or not self.size_of_image:
            _fail("UNSUPPORTED_PE_FORMAT", "zero PE base, alignment, or image size", path=self.path)
        if (
            self.image_base % PE_IMAGE_BASE_ALIGNMENT
            or section_alignment & (section_alignment - 1)
            or file_alignment & (file_alignment - 1)
            or not PE_MIN_FILE_ALIGNMENT <= file_alignment <= PE_MAX_FILE_ALIGNMENT
            or section_alignment < file_alignment
            or (section_alignment < PE_PAGE_SIZE and file_alignment != section_alignment)
            or self.size_of_headers % file_alignment
            or self.size_of_image % section_alignment
        ):
            _fail("UNSUPPORTED_PE_FORMAT", "invalid PE alignment invariants", path=self.path)
        available_directories = max(0, (optional_size - 112) // 8)
        if directory_count > available_directories:
            _fail("TRUNCATED_STRUCTURE", "data directories exceed optional header", path=self.path)
        for index in range(directory_count):
            rva, size = self._unpack("<II", optional + 112 + index * 8, "data directory")
            self.directories.append(Directory(int(rva), int(size)))
        section_offset = optional + optional_size
        self._bounds(section_offset, section_count * 40, "section table")
        section_table_end = section_offset + section_count * 40
        if (
            self.size_of_headers < section_table_end
            or self.size_of_headers > len(self.data)
            or self.size_of_headers > self.size_of_image
        ):
            _fail(
                "UNSUPPORTED_PE_FORMAT",
                "SizeOfHeaders does not contain the PE and section headers",
                path=self.path,
            )
        for index in range(section_count):
            offset = section_offset + index * 40
            raw_name = self.data[offset : offset + 8].split(b"\0", 1)[0]
            try:
                name = raw_name.decode("ascii")
            except UnicodeDecodeError:
                _fail("UNSUPPORTED_PE_FORMAT", "non-ASCII section name", path=self.path, offset=offset)
            virtual_size, virtual_address, raw_size, raw_offset = self._unpack(
                "<IIII", offset + 8, "section header"
            )
            if raw_size:
                self._bounds(int(raw_offset), int(raw_size), f"section {name}")
                if int(raw_offset) < self.size_of_headers or int(raw_offset) % file_alignment:
                    _fail(
                        "UNSUPPORTED_PE_FORMAT",
                        f"section {name} raw data overlaps headers",
                        path=self.path,
                        offset=int(raw_offset),
                    )
            mapped_size = max(int(virtual_size), int(raw_size))
            if (
                int(virtual_address) < self.size_of_headers
                or int(virtual_address) % section_alignment
                or mapped_size > self.size_of_image - int(virtual_address)
            ):
                _fail(
                    "UNSUPPORTED_PE_FORMAT",
                    f"section {name} lies outside SizeOfImage or overlaps header RVAs",
                    path=self.path,
                    rva=int(virtual_address),
                )
            self.sections.append(
                Section(name, int(virtual_address), int(virtual_size), int(raw_offset), int(raw_size))
            )
        self._validate_sections()

    def _validate_sections(self) -> None:
        raw_ranges: list[tuple[int, int, str]] = []
        virtual_ranges: list[tuple[int, int, str]] = []
        for section in self.sections:
            if section.raw_size:
                raw_ranges.append((section.raw_offset, section.raw_offset + section.raw_size, section.name))
            span = max(section.virtual_size, section.raw_size)
            if span:
                virtual_ranges.append(
                    (section.virtual_address, section.virtual_address + span, section.name)
                )
        for ranges, label in ((raw_ranges, "raw"), (virtual_ranges, "virtual")):
            ranges.sort()
            for previous, current in zip(ranges, ranges[1:]):
                if current[0] < previous[1]:
                    _fail(
                        "AMBIGUOUS_RVA_MAPPING",
                        f"overlapping {label} sections {previous[2]} and {current[2]}",
                        path=self.path,
                    )

    def directory(self, index: int) -> Directory:
        if index >= len(self.directories):
            return Directory(0, 0)
        return self.directories[index]

    def rva_to_offset(self, rva: int, size: int, structure: str) -> int:
        if rva < self.size_of_headers:
            if size > self.size_of_headers - rva:
                _fail(
                    "AMBIGUOUS_RVA_MAPPING",
                    "header RVA range crosses SizeOfHeaders",
                    path=self.path,
                    rva=rva,
                    structure=structure,
                )
            self._bounds(rva, size, structure)
            return rva
        matches: list[int] = []
        for section in self.sections:
            delta = rva - section.virtual_address
            if delta < 0 or delta > section.raw_size:
                continue
            if size <= section.raw_size - delta:
                matches.append(section.raw_offset + delta)
        if len(matches) != 1:
            _fail(
                "AMBIGUOUS_RVA_MAPPING",
                f"RVA 0x{rva:X} maps to {len(matches)} raw ranges",
                path=self.path,
                rva=rva,
                structure=structure,
            )
        self._bounds(matches[0], size, structure)
        return matches[0]

    def ascii_at_rva(self, rva: int, structure: str) -> str:
        offset = self.rva_to_offset(rva, 1, structure)
        section_end = len(self.data)
        for section in self.sections:
            if section.raw_offset <= offset < section.raw_offset + section.raw_size:
                section_end = section.raw_offset + section.raw_size
                break
        limit = min(section_end, offset + MAX_ASCII + 1)
        terminator = self.data.find(b"\0", offset, limit)
        if terminator < 0 or terminator == offset:
            _fail(
                "INVALID_ASCII_NAME",
                "missing, empty, or overlong null-terminated name",
                path=self.path,
                offset=offset,
                rva=rva,
                structure=structure,
            )
        try:
            return self.data[offset:terminator].decode("ascii")
        except UnicodeDecodeError:
            _fail("INVALID_ASCII_NAME", "name is not ASCII", path=self.path, offset=offset)

    def exports(self) -> list[Export]:
        if self._exports is not None:
            return self._exports
        directory = self.directory(IMAGE_DIRECTORY_ENTRY_EXPORT)
        if not directory.rva or directory.size < 40:
            _fail("MISSING_EXPORT_DIRECTORY", "missing export directory", path=self.path)
        offset = self.rva_to_offset(directory.rva, 40, "IMAGE_EXPORT_DIRECTORY")
        values = self._unpack("<IIHHIIIIIII", offset, "IMAGE_EXPORT_DIRECTORY")
        base = int(values[5])
        function_count = int(values[6])
        name_count = int(values[7])
        functions_rva = int(values[8])
        names_rva = int(values[9])
        ordinals_rva = int(values[10])
        if function_count > 1_000_000 or name_count > function_count:
            _fail("INVALID_EXPORT_TABLE", "invalid export counts", path=self.path)
        functions_offset = self.rva_to_offset(functions_rva, function_count * 4, "export functions")
        names_offset = self.rva_to_offset(names_rva, name_count * 4, "export names")
        ordinals_offset = self.rva_to_offset(ordinals_rva, name_count * 2, "export ordinals")
        exports: list[Export] = []
        for index in range(name_count):
            name_rva = self._u32(names_offset + index * 4, "export name RVA")
            ordinal_index = self._u16(ordinals_offset + index * 2, "export ordinal index")
            if ordinal_index >= function_count:
                _fail("INVALID_EXPORT_TABLE", "ordinal index exceeds function table", path=self.path)
            function_rva = self._u32(functions_offset + ordinal_index * 4, "export function RVA")
            name = self.ascii_at_rva(name_rva, "export name")
            forwarded = directory.rva <= function_rva < directory.rva + directory.size
            exports.append(Export(name, base + ordinal_index, function_rva, forwarded))
        if len({item.name for item in exports}) != len(exports):
            _fail("INVALID_EXPORT_TABLE", "duplicate named exports", path=self.path)
        self._exports = sorted(exports, key=lambda item: (item.name, item.ordinal))
        return self._exports

    def export(self, name: str) -> Export:
        matches = [item for item in self.exports() if item.name == name]
        if len(matches) != 1:
            _fail("MISSING_DATA_SYMBOL", f"expected exactly one export named {name}", path=self.path)
        if matches[0].forwarded:
            _fail("MISSING_DATA_SYMBOL", f"data symbol {name} is forwarded", path=self.path)
        return matches[0]

    def relocations(self) -> dict[int, Relocation]:
        if self._relocations is not None:
            return self._relocations
        directory = self.directory(IMAGE_DIRECTORY_ENTRY_BASERELOC)
        if not directory.rva or not directory.size:
            _fail("UNSUPPORTED_RELOCATION", "missing base relocation directory", path=self.path)
        start = self.rva_to_offset(directory.rva, directory.size, "base relocations")
        cursor = start
        end = start + directory.size
        result: dict[int, Relocation] = {}
        while cursor < end:
            if end - cursor < 8:
                _fail("TRUNCATED_STRUCTURE", "truncated relocation block", path=self.path, offset=cursor)
            page_rva, block_size = self._unpack("<II", cursor, "relocation block")
            page_rva = int(page_rva)
            block_size = int(block_size)
            if block_size < 8 or block_size % 2 or block_size > end - cursor:
                _fail("UNSUPPORTED_RELOCATION", "invalid relocation block size", path=self.path)
            for item_offset in range(cursor + 8, cursor + block_size, 2):
                item = self._u16(item_offset, "relocation entry")
                kind = item >> 12
                target_rva = page_rva + (item & 0xFFF)
                if kind == 0:
                    continue
                if target_rva in result:
                    _fail("UNSUPPORTED_RELOCATION", "duplicate relocation target", path=self.path)
                result[target_rva] = Relocation(kind, item_offset, page_rva, target_rva)
            cursor += block_size
        self._relocations = result
        return result

    def data_pointer(self, symbol: str, *, allow_null: bool = False) -> tuple[int, int, int]:
        export = self.export(symbol)
        slot_rva = export.function_rva
        slot_offset = self.rva_to_offset(slot_rva, 8, f"{symbol} pointer slot")
        preferred_va = self._u64(slot_offset, f"{symbol} pointer value")
        if preferred_va == 0 and allow_null:
            return slot_rva, 0, 0
        relocation = self.relocations().get(slot_rva)
        if relocation is None or relocation.kind != IMAGE_REL_BASED_DIR64:
            _fail(
                "UNSUPPORTED_RELOCATION",
                f"{symbol} pointer slot lacks DIR64 relocation",
                path=self.path,
                rva=slot_rva,
            )
        if preferred_va == 0:
            _fail("UNRESOLVED_DATA_POINTER", f"{symbol} pointer is null", path=self.path)
        if preferred_va < self.image_base:
            _fail("UNRESOLVED_DATA_POINTER", f"{symbol} pointer is below ImageBase", path=self.path)
        target_rva = preferred_va - self.image_base
        if target_rva >= self.size_of_image:
            _fail("UNRESOLVED_DATA_POINTER", f"{symbol} pointer is outside image", path=self.path)
        self.rva_to_offset(target_rva, 1, f"{symbol} pointer target")
        return slot_rva, preferred_va, target_rva

    def pointer_to_rva(self, value: int, structure: str) -> int:
        if value < self.image_base:
            _fail("UNRESOLVED_DATA_POINTER", "pointer below ImageBase", path=self.path, structure=structure)
        rva = value - self.image_base
        if rva >= self.size_of_image:
            _fail("UNRESOLVED_DATA_POINTER", "pointer outside image", path=self.path, structure=structure)
        self.rva_to_offset(rva, 1, structure)
        return rva

    def relocated_pointer_at(
        self,
        field_rva: int,
        structure: str,
    ) -> tuple[int, int, dict[str, int]]:
        relocation = self.relocations().get(field_rva)
        if relocation is None or relocation.kind != IMAGE_REL_BASED_DIR64:
            _fail(
                "UNSUPPORTED_RELOCATION",
                "pointer field lacks DIR64 relocation",
                path=self.path,
                rva=field_rva,
                structure=structure,
            )
        offset = self.rva_to_offset(field_rva, 8, structure)
        value = self._u64(offset, structure)
        if value == 0:
            return 0, 0, asdict(relocation)
        return value, self.pointer_to_rva(value, structure), asdict(relocation)


def _platform() -> dict[str, str]:
    return {
        "architecture": "AMD64",
        "implementation": "CPython",
        "os": "Windows",
        "version": "3.14.4",
    }


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _evidence_locator(image: PEImage, rva: int, size: int) -> dict[str, int]:
    return {"file_offset": image.rva_to_offset(rva, size, "evidence locator"), "rva": rva}


def _collect_exports(path: Path, binding: Binding) -> dict[str, Any]:
    image = PEImage.read(path)
    export_directory = image.directory(IMAGE_DIRECTORY_ENTRY_EXPORT)
    export_directory_offset = image.rva_to_offset(
        export_directory.rva,
        export_directory.size,
        "export directory binding",
    )
    exports = image.exports()
    init_exports = [item for item in exports if item.name.startswith("PyInit_") and len(item.name) > 7]
    invalid_init = [item for item in init_exports if item.forwarded]
    if invalid_init:
        _fail("FORWARDED_INIT_EXPORT", "forwarded PyInit export", path=image.path)
    if len(init_exports) != 1:
        _fail(
            "INIT_EXPORT_CARDINALITY",
            f"expected one PyInit export, found {len(init_exports)}",
            path=image.path,
        )
    return {
        "binding": asdict(binding),
        "export_directory": {
            "file_offset": export_directory_offset,
            "rva": export_directory.rva,
            "size": export_directory.size,
        },
        "exports": [asdict(item) for item in exports],
        "init_candidates": [asdict(item) for item in init_exports],
        "machine": "AMD64",
    }


def _read_inittab(image: PEImage, symbol: str) -> dict[str, Any]:
    slot_rva, preferred_va, table_rva = image.data_pointer(symbol)
    slot_relocation = asdict(image.relocations()[slot_rva])
    entries: list[dict[str, Any]] = []
    for index in range(MAX_TABLE_ENTRIES):
        entry_rva = table_rva + index * 16
        offset = image.rva_to_offset(entry_rva, 16, f"{symbol}[{index}]")
        name_pointer = image._u64(offset, f"{symbol}[{index}].name")
        init_pointer = image._u64(offset + 8, f"{symbol}[{index}].initfunc")
        if name_pointer == 0 and init_pointer == 0:
            return {
                "entries": entries,
                "entry_size": 16,
                "preferred_pointer_va": preferred_va,
                "export_rva": slot_rva,
                "slot_rva": slot_rva,
                "slot_relocation": slot_relocation,
                "symbol": symbol,
                "table_rva": table_rva,
                "terminated": True,
            }
        if not name_pointer or not init_pointer:
            _fail("UNTERMINATED_TABLE", "partial inittab terminator", path=image.path, rva=entry_rva)
        _, name_rva, name_relocation = image.relocated_pointer_at(
            entry_rva, f"{symbol}[{index}].name"
        )
        _, init_rva, init_relocation = image.relocated_pointer_at(
            entry_rva + 8, f"{symbol}[{index}].initfunc"
        )
        entries.append(
            {
                "evidence_locator": _evidence_locator(image, entry_rva, 16),
                "index": index,
                "init_rva": init_rva,
                "init_relocation": init_relocation,
                "kind": "builtin",
                "name": image.ascii_at_rva(name_rva, f"{symbol}[{index}].name"),
                "name_relocation": name_relocation,
            }
        )
    _fail("UNTERMINATED_TABLE", f"{symbol} exceeds entry limit", path=image.path)


def _read_frozen(
    image: PEImage,
    symbol: str,
    table_kind: str,
    *,
    allow_null_pointer: bool = False,
) -> dict[str, Any]:
    slot_rva, preferred_va, table_rva = image.data_pointer(symbol, allow_null=allow_null_pointer)
    slot_relocation = (
        asdict(image.relocations()[slot_rva]) if slot_rva in image.relocations() else None
    )
    entries: list[dict[str, Any]] = []
    if table_rva == 0:
        return {
            "entries": entries,
            "entry_size": 24,
            "preferred_pointer_va": 0,
            "export_rva": slot_rva,
            "slot_rva": slot_rva,
            "slot_relocation": slot_relocation,
            "symbol": symbol,
            "table_kind": table_kind,
            "table_rva": 0,
            "terminated": True,
        }
    for index in range(MAX_TABLE_ENTRIES):
        entry_rva = table_rva + index * 24
        offset = image.rva_to_offset(entry_rva, 24, f"{symbol}[{index}]")
        name_pointer, code_pointer, size, is_package = image._unpack(
            "<QQii", offset, f"{symbol}[{index}]"
        )
        name_pointer = int(name_pointer)
        code_pointer = int(code_pointer)
        size = int(size)
        is_package = int(is_package)
        if name_pointer == 0 and code_pointer == 0 and size == 0 and is_package == 0:
            return {
                "entries": entries,
                "entry_size": 24,
                "preferred_pointer_va": preferred_va,
                "export_rva": slot_rva,
                "slot_rva": slot_rva,
                "slot_relocation": slot_relocation,
                "symbol": symbol,
                "table_kind": table_kind,
                "table_rva": table_rva,
                "terminated": True,
            }
        if not name_pointer or not code_pointer or size <= 0:
            _fail("UNTERMINATED_TABLE", "invalid frozen entry", path=image.path, rva=entry_rva)
        if is_package not in (0, 1):
            _fail("INVALID_PACKAGE_FLAG", f"package flag is {is_package}", path=image.path, rva=entry_rva)
        _, name_rva, name_relocation = image.relocated_pointer_at(
            entry_rva, f"{symbol}[{index}].name"
        )
        _, code_rva, code_relocation = image.relocated_pointer_at(
            entry_rva + 8, f"{symbol}[{index}].code"
        )
        image.rva_to_offset(code_rva, size, f"{symbol}[{index}].code bytes")
        entries.append(
            {
                "code_rva": code_rva,
                "code_relocation": code_relocation,
                "code_size": size,
                "evidence_locator": _evidence_locator(image, entry_rva, 24),
                "index": index,
                "is_package": bool(is_package),
                "kind": "frozen",
                "name": image.ascii_at_rva(name_rva, f"{symbol}[{index}].name"),
                "name_relocation": name_relocation,
                "table_kind": table_kind,
            }
        )
    _fail("UNTERMINATED_TABLE", f"{symbol} exceeds entry limit", path=image.path)


def _read_aliases(image: PEImage, symbol: str) -> dict[str, Any]:
    slot_rva, preferred_va, table_rva = image.data_pointer(symbol)
    slot_relocation = asdict(image.relocations()[slot_rva])
    entries: list[dict[str, Any]] = []
    for index in range(MAX_TABLE_ENTRIES):
        entry_rva = table_rva + index * 16
        offset = image.rva_to_offset(entry_rva, 16, f"{symbol}[{index}]")
        name_pointer = image._u64(offset, f"{symbol}[{index}].name")
        original_pointer = image._u64(offset + 8, f"{symbol}[{index}].original")
        if name_pointer == 0 and original_pointer == 0:
            aliases = {entry["name"]: entry["original"] for entry in entries}
            for start in aliases:
                seen: set[str] = set()
                current = start
                while current in aliases:
                    if current in seen:
                        _fail("ALIAS_CONFLICT_OR_CYCLE", f"alias cycle at {current}", path=image.path)
                    seen.add(current)
                    current = aliases[current]
            return {
                "entries": entries,
                "entry_size": 16,
                "preferred_pointer_va": preferred_va,
                "export_rva": slot_rva,
                "slot_rva": slot_rva,
                "slot_relocation": slot_relocation,
                "symbol": symbol,
                "table_rva": table_rva,
                "terminated": True,
            }
        if not name_pointer or not original_pointer:
            _fail("UNTERMINATED_TABLE", "partial alias terminator", path=image.path, rva=entry_rva)
        _, name_rva, name_relocation = image.relocated_pointer_at(
            entry_rva, f"{symbol}[{index}].name"
        )
        _, original_rva, original_relocation = image.relocated_pointer_at(
            entry_rva + 8, f"{symbol}[{index}].original"
        )
        entries.append(
            {
                "evidence_locator": _evidence_locator(image, entry_rva, 16),
                "index": index,
                "name": image.ascii_at_rva(name_rva, f"{symbol}[{index}].name"),
                "name_relocation": name_relocation,
                "original": image.ascii_at_rva(original_rva, f"{symbol}[{index}].original"),
                "original_relocation": original_relocation,
            }
        )
    _fail("UNTERMINATED_TABLE", f"{symbol} exceeds entry limit", path=image.path)


def _collect_tables(path: Path, binding: Binding) -> dict[str, Any]:
    image = PEImage.read(path)
    tables = [
        _read_inittab(image, "PyImport_Inittab"),
        _read_frozen(image, "_PyImport_FrozenBootstrap", "bootstrap"),
        _read_frozen(image, "_PyImport_FrozenStdlib", "stdlib"),
        _read_frozen(image, "_PyImport_FrozenTest", "test"),
        _read_aliases(image, "_PyImport_FrozenAliases"),
    ]
    override = _read_frozen(
        image,
        "PyImport_FrozenModules",
        "override",
        allow_null_pointer=True,
    )
    builtin_names = [entry["name"] for entry in tables[0]["entries"]]
    frozen_names = [
        entry["name"]
        for table in [*tables[1:4], override]
        for entry in table["entries"]
    ]
    if len(set(builtin_names)) != len(builtin_names):
        _fail("DUPLICATE_OR_CONFLICTING_ENTRY", "duplicate builtin names", path=image.path)
    if len(set(frozen_names)) != len(frozen_names):
        _fail("DUPLICATE_OR_CONFLICTING_ENTRY", "duplicate frozen names", path=image.path)
    known_frozen = set(frozen_names)
    alias_entries = tables[4]["entries"]
    alias_names = [entry["name"] for entry in alias_entries]
    if len(set(alias_names)) != len(alias_names):
        _fail("DUPLICATE_OR_CONFLICTING_ENTRY", "duplicate alias names", path=image.path)
    for entry in alias_entries:
        if entry["original"] not in known_frozen:
            _fail(
                "ALIAS_CONFLICT_OR_CYCLE",
                f"alias target is not a bound frozen name: {entry['original']}",
                path=image.path,
            )
        if entry["name"] in known_frozen:
            _fail(
                "ALIAS_CONFLICT_OR_CYCLE",
                f"alias conflicts with frozen entry: {entry['name']}",
                path=image.path,
            )
    return {"binding": asdict(binding), "override": override, "tables": tables}


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_outputs(output_dir: Path, documents: dict[str, dict[str, Any]]) -> None:
    if output_dir.exists():
        if not output_dir.is_dir() or any(output_dir.iterdir()):
            _fail("OUTPUT_ALREADY_EXISTS", "output directory is not empty", path=str(output_dir))
    parent = output_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    staging = parent / f".{output_dir.name}.static-binary-evidence.tmp"
    if staging.exists():
        _fail("OUTPUT_ALREADY_EXISTS", "staging directory already exists", path=str(staging))
    staging.mkdir(exist_ok=False)
    try:
        for name in sorted(documents):
            target = staging / name
            with target.open("xb") as handle:
                handle.write(_canonical_json(documents[name]))
                handle.flush()
                os.fsync(handle.fileno())
        if output_dir.exists():
            output_dir.rmdir()
        staging.replace(output_dir)
    except Exception:
        if staging.exists():
            for child in staging.iterdir():
                child.unlink(missing_ok=True)
            staging.rmdir()
        raise


def _load_control(path: Path) -> tuple[Binding, Binding, list[Binding]]:
    document = _read_json(path)
    if document.get("schema") != SCHEMA_CONTROL:
        _fail("INPUT_BINDING_MISMATCH", "unexpected control schema", path=str(path))
    tool = _parse_binding(document.get("tool_binding"), "tool_binding")
    contract = _parse_binding(document.get("contract_binding"), "contract_binding")
    raw_inputs = document.get("input_bindings")
    if not isinstance(raw_inputs, list) or not raw_inputs:
        _fail("INPUT_BINDING_MISMATCH", "input_bindings must be a nonempty array", path=str(path))
    inputs = [_parse_binding(item, f"input_bindings[{index}]") for index, item in enumerate(raw_inputs)]
    if len({item.path.casefold() for item in inputs}) != len(inputs):
        _fail("INPUT_BINDING_MISMATCH", "duplicate or case-colliding input paths", path=str(path))
    return tool, contract, inputs


def collect(
    control_path: Path,
    output_dir: Path,
    expected_control: Binding,
    error_context: ErrorContext,
) -> None:
    started = error_context.started_utc
    control_path_verified, control_binding = _verify_binding(expected_control)
    error_context.control_binding = control_binding
    if control_path_verified != control_path.resolve(strict=True):
        _fail(
            "INPUT_BINDING_MISMATCH",
            "independent control binding does not identify --control",
            path=str(control_path),
        )
    tool_expected, contract_expected, expected_inputs = _load_control(control_path)
    tool_path, tool_binding = _verify_binding(tool_expected)
    error_context.tool_binding = tool_binding
    _, contract_binding = _verify_binding(contract_expected)
    error_context.contract_binding = contract_binding
    if tool_path != Path(__file__).resolve(strict=True):
        _fail("INPUT_BINDING_MISMATCH", "tool_binding does not identify this file", path=str(tool_path))
    verified: list[tuple[Path, Binding]] = []
    for item in expected_inputs:
        verified_item = _verify_binding(item)
        verified.append(verified_item)
        error_context.input_bindings.append(verified_item[1])
    python_items = [(path, binding) for path, binding in verified if binding.role == "cpython-binary"]
    pyd_items = [(path, binding) for path, binding in verified if binding.role == "native-candidate"]
    other_roles = sorted({binding.role for _, binding in verified} - {"cpython-binary", "native-candidate"})
    if len(python_items) != 1 or len(pyd_items) != 53 or other_roles:
        _fail(
            "INPUT_BINDING_MISMATCH",
            f"expected one cpython-binary and 53 native-candidate inputs; other roles={other_roles}",
        )
    export_results = [
        _collect_exports(path, binding)
        for path, binding in sorted(pyd_items, key=lambda item: item[1].path.casefold())
    ]
    table_result = _collect_tables(*python_items[0])
    finished = _iso_now()
    common = {
        "complete": True,
        "contract_binding": asdict(contract_binding),
        "control_binding": asdict(control_binding),
        "errors": [],
        "finished_utc": finished,
        "input_bindings": [asdict(binding) for _, binding in sorted(verified, key=lambda x: x[1].path.casefold())],
        "platform": _platform(),
        "started_utc": started,
        "stops": [],
        "tool_binding": asdict(tool_binding),
    }
    export_document = {**common, "schema": SCHEMA_EXPORT, "files": export_results}
    table_document = {**common, "schema": SCHEMA_TABLE, **table_result}
    report_document = {
        **common,
        "schema": SCHEMA_REPORT,
        "counts": {
            "builtin_entries": len(table_result["tables"][0]["entries"]),
            "frozen_entries": sum(len(item["entries"]) for item in table_result["tables"][1:4]),
            "frozen_override_entries": len(table_result["override"]["entries"]),
            "frozen_alias_entries": len(table_result["tables"][4]["entries"]),
            "native_candidates": len(export_results),
            "native_init_exports": sum(len(item["init_candidates"]) for item in export_results),
        },
        "manifest_generated": False,
        "resolver_run": False,
    }
    _write_outputs(
        output_dir,
        {
            "cpython_table_evidence.json": table_document,
            "pe_export_evidence.json": export_document,
            "static_binary_evaluation_report.json": report_document,
        },
    )


def _write_error_only(
    output_dir: Path,
    error: EvidenceError,
    *,
    context: ErrorContext,
) -> None:
    document = {
        "complete": False,
        "contract_binding": asdict(context.contract_binding) if context.contract_binding else None,
        "control_binding_expected": asdict(context.expected_control) if context.expected_control else None,
        "control_binding_verified": asdict(context.control_binding) if context.control_binding else None,
        "errors": [error.record()],
        "finished_utc": _iso_now(),
        "input_bindings": [asdict(binding) for binding in context.input_bindings or []],
        "platform": _platform(),
        "schema": SCHEMA_ERROR,
        "started_utc": context.started_utc,
        "stops": [error.code],
        "tool_binding": asdict(context.tool_binding) if context.tool_binding else None,
    }
    _write_outputs(output_dir, {"static_binary_evaluation_errors.json": document})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", required=True, type=Path)
    parser.add_argument("--control-size", required=True, type=int)
    parser.add_argument("--control-sha256", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    started = _iso_now()
    error_context = ErrorContext(started_utc=started)
    try:
        expected_control = _parse_binding(
            {
                "path": str(args.control),
                "role": "control",
                "size": args.control_size,
                "sha256": args.control_sha256,
            },
            "independent_control_binding",
        )
        error_context.expected_control = expected_control
    except EvidenceError as exc:
        try:
            _write_error_only(args.output_dir, exc, context=error_context)
        except (EvidenceError, OSError):
            pass
        print(f"{exc.code}: {exc.detail}", file=sys.stderr)
        return 2
    try:
        collect(args.control, args.output_dir, expected_control, error_context)
    except EvidenceError as exc:
        try:
            _write_error_only(args.output_dir, exc, context=error_context)
        except (EvidenceError, OSError):
            pass
        print(f"{exc.code}: {exc.detail}", file=sys.stderr)
        return 2
    except Exception as exc:
        error = EvidenceError("INTERNAL_INVARIANT_FAILURE", f"{type(exc).__name__}: {exc}")
        try:
            _write_error_only(args.output_dir, error, context=error_context)
        except (EvidenceError, OSError):
            pass
        print(f"{error.code}: {error.detail}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
