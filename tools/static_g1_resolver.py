"""Static G1 Python/NumPy dependency resolver specified by research package 213N.

This tool parses source files as data. It never imports a target module. A resolver
run requires a separate release; this file only contains the implementation.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence


EdgeState = Literal["required", "excluded", "alternative", "unresolved"]
ResolutionKind = Literal[
    "python",
    "package",
    "builtin",
    "frozen",
    "native",
    "missing",
    "collision",
    "g2",
    "open",
]

ENTRY_RELATIVE_PATH = "mcm_field_organism/_runtime_fixation_single_use_path.py"
ROOT_MODULES = (
    "__future__",
    "dataclasses",
    "enum",
    "hashlib",
    "hmac",
    "json",
    "math",
    "numpy",
    "pathlib",
    "queue",
    "re",
    "time",
    "typing",
)
FIXED_CONSTANTS: dict[str, Any] = {
    "os.name": "nt",
    "sys.platform": "win32",
    "sys.byteorder": "little",
    "sys.version_info": (3, 14, 4),
    "sys.implementation.name": "cpython",
    "typing.TYPE_CHECKING": False,
    "TYPE_CHECKING": False,
    "__NUMPY_SETUP__": False,
}
G2_CALLS = {
    "os.add_dll_directory",
    "site.addsitedir",
    "sys.path.append",
    "sys.path.extend",
    "sys.path.insert",
}
RESOURCE_CALLS = {
    "open",
    "Path",
    "pathlib.Path",
    "importlib.resources.files",
    "importlib.resources.open_binary",
    "importlib.resources.open_text",
    "pkgutil.get_data",
}
DYNAMIC_IMPORT_CALLS = {"__import__", "importlib.import_module"}


@dataclass(frozen=True)
class FileBinding:
    path: str
    size: int
    sha256: str
    kind: str


@dataclass(frozen=True)
class ModuleResolution:
    name: str
    kind: ResolutionKind
    candidates: tuple[str, ...] = ()
    detail: str = ""


@dataclass(frozen=True)
class ImportEdge:
    source: str
    line: int
    column: int
    syntax: str
    requested: str
    state: EdgeState
    condition: str
    resolution_kind: ResolutionKind
    targets: tuple[str, ...]
    detail: str = ""


@dataclass(frozen=True)
class ResourceEdge:
    source: str
    line: int
    column: int
    api: str
    state: EdgeState
    expression: str
    resolved_path: str | None
    detail: str


@dataclass(frozen=True)
class ParentDirectory:
    path: str
    exists: bool
    is_symlink: bool
    resolved_path: str | None
    root: str


@dataclass
class ResolverResult:
    specification: str = "213N"
    platform: dict[str, Any] = field(default_factory=lambda: dict(FIXED_CONSTANTS))
    input_bindings: list[FileBinding] = field(default_factory=list)
    files: list[FileBinding] = field(default_factory=list)
    import_edges: list[ImportEdge] = field(default_factory=list)
    resource_edges: list[ResourceEdge] = field(default_factory=list)
    parents: list[ParentDirectory] = field(default_factory=list)
    g2_references: list[str] = field(default_factory=list)
    stops: list[str] = field(default_factory=list)
    counters: dict[str, int] = field(default_factory=dict)
    g1_passed: bool = False


@dataclass(frozen=True)
class ResolverConfig:
    workspace: Path
    python_root: Path
    venv_root: Path
    builtin_manifest: Path
    native_manifest: Path
    specification: Path
    output: Path | None

    @property
    def roots(self) -> tuple[Path, ...]:
        return (
            self.workspace.resolve(),
            self.python_root.resolve(),
            self.venv_root.resolve(),
        )

    @property
    def search_roots(self) -> tuple[Path, ...]:
        return (
            (self.venv_root / "Lib" / "site-packages").resolve(),
            (self.python_root / "Lib").resolve(),
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _binding(path: Path, kind: str) -> FileBinding:
    stat = path.stat()
    return FileBinding(
        path=path.resolve().as_posix(),
        size=stat.st_size,
        sha256=_sha256(path),
        kind=kind,
    )


def _load_manifest(path: Path, label: str) -> dict[str, dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{label} manifest must be a JSON object")
    modules = document.get("modules")
    if not isinstance(modules, dict):
        raise ValueError(f"{label} manifest must contain an object named modules")
    normalized: dict[str, dict[str, Any]] = {}
    for name, value in modules.items():
        if not isinstance(name, str) or not isinstance(value, dict):
            raise ValueError(f"invalid {label} manifest entry")
        normalized[name] = value
    return normalized


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted_name(node.value)
        if parent:
            return f"{parent}.{node.attr}"
    return None


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
                return None
            parts.append(value.value)
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _literal_string(node.left)
        right = _literal_string(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def _source_text(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return node.__class__.__name__


class ConditionEvaluator:
    def __init__(self, constants: dict[str, Any]) -> None:
        self.constants = constants

    def evaluate(self, node: ast.AST) -> bool | None:
        value = self._value(node)
        return value if isinstance(value, bool) else None

    def _value(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        name = _dotted_name(node)
        if name in self.constants:
            return self.constants[name]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            value = self._value(node.operand)
            return None if value is None else not bool(value)
        if isinstance(node, ast.BoolOp):
            values = [self._value(item) for item in node.values]
            if isinstance(node.op, ast.And):
                if any(value is False for value in values):
                    return False
                return True if all(value is True for value in values) else None
            if any(value is True for value in values):
                return True
            return False if all(value is False for value in values) else None
        if isinstance(node, ast.Compare):
            values = [self._value(node.left), *(self._value(item) for item in node.comparators)]
            if any(value is None for value in values):
                return None
            comparisons: list[bool] = []
            for left, op, right in zip(values, node.ops, values[1:]):
                if isinstance(op, ast.Eq):
                    comparisons.append(left == right)
                elif isinstance(op, ast.NotEq):
                    comparisons.append(left != right)
                elif isinstance(op, ast.In):
                    comparisons.append(left in right)
                elif isinstance(op, ast.NotIn):
                    comparisons.append(left not in right)
                elif isinstance(op, ast.Lt):
                    comparisons.append(left < right)
                elif isinstance(op, ast.LtE):
                    comparisons.append(left <= right)
                elif isinstance(op, ast.Gt):
                    comparisons.append(left > right)
                elif isinstance(op, ast.GtE):
                    comparisons.append(left >= right)
                else:
                    return None
            return all(comparisons)
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            values = [self._value(item) for item in node.elts]
            return None if any(value is None for value in values) else type(node.elts)(values)
        return None


class ModuleLocator:
    def __init__(
        self,
        config: ResolverConfig,
        builtin: dict[str, dict[str, Any]],
        native: dict[str, dict[str, Any]],
    ) -> None:
        self.config = config
        self.builtin = builtin
        self.native = native

    def resolve(self, name: str) -> ModuleResolution:
        if name in self.builtin:
            kind = self.builtin[name].get("kind")
            if kind not in {"builtin", "frozen"}:
                return ModuleResolution(name, "open", detail="invalid builtin kind")
            return ModuleResolution(name, kind)
        if name in self.native:
            entry = self.native[name]
            raw_path = entry.get("path")
            if not isinstance(raw_path, str):
                return ModuleResolution(name, "open", detail="native path missing")
            path = Path(raw_path).resolve()
            return ModuleResolution(name, "native", (path.as_posix(),))

        relative = Path(*name.split("."))
        candidates: list[tuple[ResolutionKind, Path]] = []
        search_roots = self.config.search_roots
        if name == "mcm_field_organism" or name.startswith("mcm_field_organism."):
            search_roots = (self.config.workspace.resolve(),)
        for root in search_roots:
            module = root / relative.with_suffix(".py")
            package = root / relative / "__init__.py"
            if module.is_file():
                candidates.append(("python", module.resolve()))
            if package.is_file():
                candidates.append(("package", package.resolve()))
        unique = {(kind, path.as_posix()) for kind, path in candidates}
        if not unique:
            return ModuleResolution(name, "missing")
        if len(unique) > 1:
            return ModuleResolution(
                name,
                "collision",
                tuple(sorted(path for _, path in unique)),
                "multiple search-root candidates",
            )
        kind, path = next(iter(unique))
        return ModuleResolution(name, kind, (path,))


def _package_name(module_name: str, source: Path) -> str:
    return module_name if source.name == "__init__.py" else module_name.rpartition(".")[0]


def _absolute_import(module_name: str, source: Path, level: int, target: str | None) -> str | None:
    if level == 0:
        return target
    package = _package_name(module_name, source)
    parts = package.split(".") if package else []
    remove = level - 1
    if remove > len(parts):
        return None
    base = parts[: len(parts) - remove]
    if target:
        base.extend(target.split("."))
    return ".".join(base) or None


class SourceScanner(ast.NodeVisitor):
    def __init__(
        self,
        source: Path,
        module_name: str,
        locator: ModuleLocator,
        result: ResolverResult,
    ) -> None:
        self.source = source
        self.module_name = module_name
        self.locator = locator
        self.result = result
        self.states: list[tuple[EdgeState, str]] = [("required", "entry")]

    @property
    def state(self) -> EdgeState:
        return self.states[-1][0]

    @property
    def condition(self) -> str:
        return self.states[-1][1]

    def _visit_block(self, nodes: Iterable[ast.stmt], state: EdgeState, condition: str) -> None:
        self.states.append((state, condition))
        for node in nodes:
            self.visit(node)
        self.states.pop()

    def _record_import(self, node: ast.AST, name: str, syntax: str) -> None:
        resolution = self.locator.resolve(name)
        state = self.state
        detail = resolution.detail
        if resolution.kind in {"missing", "collision", "open"} and state == "required":
            state = "unresolved"
            detail = detail or f"required module classified as {resolution.kind}"
        self.result.import_edges.append(
            ImportEdge(
                source=self.source.resolve().as_posix(),
                line=node.lineno,
                column=node.col_offset,
                syntax=syntax,
                requested=name,
                state=state,
                condition=self.condition,
                resolution_kind=resolution.kind,
                targets=resolution.candidates,
                detail=detail,
            )
        )

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._record_import(node, alias.name, "import")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        target = _absolute_import(self.module_name, self.source, node.level, node.module)
        if target is None:
            self.result.import_edges.append(
                ImportEdge(
                    self.source.resolve().as_posix(),
                    node.lineno,
                    node.col_offset,
                    "from",
                    node.module or "",
                    "unresolved",
                    self.condition,
                    "open",
                    (),
                    "relative import escaped or lacked package context",
                )
            )
            return
        self._record_import(node, target, "from-star" if any(a.name == "*" for a in node.names) else "from")
        if any(alias.name == "*" for alias in node.names):
            self._record_star_exports(node, target)
        else:
            for alias in node.names:
                child = f"{target}.{alias.name}"
                resolution = self.locator.resolve(child)
                if resolution.kind in {"python", "package", "native", "builtin", "frozen"}:
                    self._record_import(node, child, "from-child")

    def _record_star_exports(self, node: ast.ImportFrom, target: str) -> None:
        resolution = self.locator.resolve(target)
        if resolution.kind not in {"python", "package"} or len(resolution.candidates) != 1:
            self.result.stops.append(f"open star import at {self.source}:{node.lineno}")
            return
        path = Path(resolution.candidates[0])
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, UnicodeError, SyntaxError):
            self.result.stops.append(f"unreadable star target {path.as_posix()}")
            return
        values: list[str] | None = None
        for statement in tree.body:
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                value = statement.value
                if any(isinstance(item, ast.Name) and item.id == "__all__" for item in targets):
                    if isinstance(value, (ast.List, ast.Tuple)) and all(
                        isinstance(item, ast.Constant) and isinstance(item.value, str) for item in value.elts
                    ):
                        values = [item.value for item in value.elts]
                    else:
                        values = None
                        break
        if values is None:
            self.result.stops.append(f"nonliteral __all__ at {path.as_posix()}")
            return
        for exported in values:
            child = f"{target}.{exported}"
            resolution = self.locator.resolve(child)
            if resolution.kind in {"python", "package", "native", "builtin", "frozen"}:
                self._record_import(node, child, "star-child")

    def visit_If(self, node: ast.If) -> None:
        value = ConditionEvaluator(FIXED_CONSTANTS).evaluate(node.test)
        expression = _source_text(node.test)
        if value is True:
            self._visit_block(node.body, self.state, f"{self.condition} and ({expression})")
            self._visit_block(node.orelse, "excluded", f"not ({expression})")
        elif value is False:
            self._visit_block(node.body, "excluded", expression)
            self._visit_block(node.orelse, self.state, f"{self.condition} and not ({expression})")
        else:
            self._visit_block(node.body, "alternative", expression)
            self._visit_block(node.orelse, "alternative", f"not ({expression})")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        self._visit_block(node.body, "alternative", f"function call {node.name} not statically proven")

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)

    def visit_For(self, node: ast.For) -> None:
        self.visit(node.iter)
        self._visit_block(node.body, "alternative", "loop iteration count not statically proven")
        self._visit_block(node.orelse, "alternative", "loop completion path")

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.visit_For(node)

    def visit_While(self, node: ast.While) -> None:
        value = ConditionEvaluator(FIXED_CONSTANTS).evaluate(node.test)
        if value is False:
            self._visit_block(node.body, "excluded", _source_text(node.test))
        else:
            self._visit_block(node.body, "alternative", "while execution not statically bounded")
        self._visit_block(node.orelse, "alternative", "while completion path")

    def visit_Match(self, node: ast.Match) -> None:
        self.visit(node.subject)
        for case in node.cases:
            self._visit_block(case.body, "alternative", "match case not statically selected")

    def visit_Try(self, node: ast.Try) -> None:
        catches_import = any(
            handler.type is None
            or _dotted_name(handler.type) in {"ImportError", "ModuleNotFoundError", "Exception", "BaseException"}
            for handler in node.handlers
        )
        if catches_import:
            self._visit_block(node.body, "alternative", "try import may fail during module execution")
            for handler in node.handlers:
                self._visit_block(handler.body, "alternative", f"except {_source_text(handler.type) if handler.type else 'bare'}")
        else:
            self._visit_block(node.body, self.state, self.condition)
            for handler in node.handlers:
                self._visit_block(handler.body, self.state, self.condition)
        self._visit_block(node.orelse, self.state, self.condition)
        self._visit_block(node.finalbody, self.state, self.condition)

    def visit_TryStar(self, node: ast.TryStar) -> None:
        self.visit_Try(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = _dotted_name(node.func)
        if name in DYNAMIC_IMPORT_CALLS:
            literal = _literal_string(node.args[0]) if node.args else None
            if literal is None:
                self.result.stops.append(f"dynamic import at {self.source}:{node.lineno}")
            else:
                self._record_import(node, literal, "dynamic-literal")
        if name in G2_CALLS:
            reference = f"{self.source.resolve().as_posix()}:{node.lineno}:{name}"
            self.result.g2_references.append(reference)
        if name in RESOURCE_CALLS or (name and name.endswith((".read_text", ".read_bytes"))):
            argument = node.args[0] if node.args else None
            literal = _literal_string(argument) if argument is not None else None
            self.result.resource_edges.append(
                ResourceEdge(
                    source=self.source.resolve().as_posix(),
                    line=node.lineno,
                    column=node.col_offset,
                    api=name,
                    state=self.state if literal is not None else "unresolved",
                    expression=_source_text(argument) if argument is not None else "",
                    resolved_path=None,
                    detail="literal resource requires root-relative resolution" if literal is not None else "nonliteral resource",
                )
            )
        self.generic_visit(node)


class StaticG1Resolver:
    def __init__(self, config: ResolverConfig) -> None:
        self.config = config
        self.result = ResolverResult()
        self.builtin = _load_manifest(config.builtin_manifest, "builtin")
        self.native = _load_manifest(config.native_manifest, "native")
        self.locator = ModuleLocator(config, self.builtin, self.native)
        self.queue: list[tuple[str, Path]] = []
        self.seen: set[tuple[str, str]] = set()
        self.file_bindings: dict[str, FileBinding] = {}

    def run(self) -> ResolverResult:
        self._bind_inputs()
        entry = (self.config.workspace / ENTRY_RELATIVE_PATH).resolve()
        self._enqueue("mcm_field_organism._runtime_fixation_single_use_path", entry)
        for module in ROOT_MODULES:
            resolution = self.locator.resolve(module)
            self._accept_resolution(module, resolution, "root")

        while self.queue:
            self.queue.sort(key=lambda item: (item[0].casefold(), item[1].as_posix().casefold()))
            module_name, source = self.queue.pop(0)
            key = (module_name.casefold(), source.as_posix().casefold())
            if key in self.seen:
                continue
            self.seen.add(key)
            self._scan(module_name, source)

        self._collect_parents()
        self._finalize()
        return self.result

    def _bind_inputs(self) -> None:
        for path, kind in (
            (self.config.specification, "resolver-specification"),
            (self.config.builtin_manifest, "builtin-manifest"),
            (self.config.native_manifest, "native-manifest"),
            (self.config.venv_root / "pyvenv.cfg", "venv-config"),
        ):
            if not path.is_file():
                self.result.stops.append(f"missing resolver input {path.resolve().as_posix()}")
                continue
            self.result.input_bindings.append(_binding(path, kind))

    def _enqueue(self, module_name: str, path: Path) -> None:
        self.queue.append((module_name, path.resolve()))

    def _accept_resolution(self, name: str, resolution: ModuleResolution, context: str) -> None:
        if resolution.kind in {"python", "package"} and len(resolution.candidates) == 1:
            self._enqueue_parent_packages(name)
            self._enqueue(name, Path(resolution.candidates[0]))
        elif resolution.kind in {"missing", "collision", "open"}:
            self.result.stops.append(f"{context} {name}: {resolution.kind} {resolution.detail}".rstrip())
        elif resolution.kind == "native":
            path = Path(resolution.candidates[0])
            if not path.is_file():
                self.result.stops.append(f"missing native module {name}: {path.as_posix()}")
            else:
                binding = _binding(path, "native")
                expected = self.native.get(name, {})
                expected_size = expected.get("size")
                expected_hash = expected.get("sha256")
                if expected_size != binding.size or not isinstance(expected_hash, str) or expected_hash.lower() != binding.sha256:
                    self.result.stops.append(f"native binding mismatch {name}: {path.as_posix()}")
                self.file_bindings[path.resolve().as_posix()] = binding

    def _enqueue_parent_packages(self, name: str) -> None:
        parts = name.split(".")
        for index in range(1, len(parts)):
            parent = ".".join(parts[:index])
            resolution = self.locator.resolve(parent)
            if resolution.kind == "package" and len(resolution.candidates) == 1:
                self._enqueue(parent, Path(resolution.candidates[0]))

    def _scan(self, module_name: str, source: Path) -> None:
        if not source.is_file():
            self.result.stops.append(f"missing source {source.as_posix()}")
            return
        try:
            raw = source.read_bytes()
            text = raw.decode("utf-8")
            tree = ast.parse(text, filename=str(source), type_comments=True)
        except (OSError, UnicodeError, SyntaxError) as error:
            self.result.stops.append(f"unreadable source {source.as_posix()}: {error}")
            return
        kind = "package" if source.name == "__init__.py" else "python"
        self.file_bindings[source.resolve().as_posix()] = FileBinding(
            source.resolve().as_posix(), len(raw), hashlib.sha256(raw).hexdigest(), kind
        )
        edge_start = len(self.result.import_edges)
        SourceScanner(source, module_name, self.locator, self.result).visit(tree)
        for edge in self.result.import_edges[edge_start:]:
            if edge.state == "excluded":
                continue
            resolution = ModuleResolution(edge.requested, edge.resolution_kind, edge.targets, edge.detail)
            if edge.state == "required":
                self._accept_resolution(edge.requested, resolution, f"edge {edge.source}:{edge.line}")
            elif edge.state in {"alternative", "unresolved"}:
                self.result.stops.append(f"{edge.state} edge {edge.source}:{edge.line}:{edge.requested}")

    def _root_for(self, path: Path) -> Path | None:
        resolved = path.resolve()
        matches = [root for root in self.config.roots if resolved == root or root in resolved.parents]
        return max(matches, key=lambda item: len(item.parts)) if matches else None

    def _collect_parents(self) -> None:
        parents: dict[str, ParentDirectory] = {}
        for binding in self.file_bindings.values():
            current = Path(binding.path).parent
            root = self._root_for(current)
            if root is None:
                self.result.stops.append(f"file outside registered roots: {binding.path}")
                continue
            while True:
                key = current.as_posix().casefold()
                if key not in parents:
                    exists = current.is_dir()
                    parents[key] = ParentDirectory(
                        path=current.as_posix(),
                        exists=exists,
                        is_symlink=current.is_symlink(),
                        resolved_path=current.resolve().as_posix() if exists else None,
                        root=root.as_posix(),
                    )
                    if not exists:
                        self.result.stops.append(f"missing parent {current.as_posix()}")
                if current == root:
                    break
                current = current.parent
        self.result.parents = sorted(parents.values(), key=lambda item: item.path.casefold())

    def _finalize(self) -> None:
        self.result.files = sorted(self.file_bindings.values(), key=lambda item: item.path.casefold())
        self.result.import_edges.sort(key=lambda item: (item.source.casefold(), item.line, item.column, item.requested))
        self.result.resource_edges.sort(key=lambda item: (item.source.casefold(), item.line, item.column))
        self.result.g2_references = sorted(set(self.result.g2_references), key=str.casefold)
        self.result.stops = sorted(set(self.result.stops), key=str.casefold)
        states = {state: 0 for state in ("required", "excluded", "alternative", "unresolved")}
        for edge in self.result.import_edges:
            states[edge.state] += 1
        for edge in self.result.resource_edges:
            if edge.state in {"alternative", "unresolved"} or edge.resolved_path is None:
                self.result.stops.append(f"open resource {edge.source}:{edge.line}:{edge.api}")
        self.result.stops = sorted(set(self.result.stops), key=str.casefold)
        self.result.counters = {
            "input_bindings": len(self.result.input_bindings),
            "files": len(self.result.files),
            "file_bytes": sum(item.size for item in self.result.files),
            "parents": len(self.result.parents),
            "import_edges": len(self.result.import_edges),
            "resource_edges": len(self.result.resource_edges),
            "g2_references": len(self.result.g2_references),
            "stops": len(self.result.stops),
            **{f"edges_{key}": value for key, value in states.items()},
        }
        self.result.g1_passed = (
            not self.result.stops
            and states["alternative"] == 0
            and states["unresolved"] == 0
            and not self.result.g2_references
            and all(item.exists for item in self.result.parents)
        )


def _jsonable(result: ResolverResult) -> dict[str, Any]:
    return asdict(result)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve the preregistered G1 static dependency graph.")
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--python-root", required=True, type=Path)
    parser.add_argument("--venv-root", required=True, type=Path)
    parser.add_argument("--builtin-manifest", required=True, type=Path)
    parser.add_argument("--native-manifest", required=True, type=Path)
    parser.add_argument("--specification", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    config = ResolverConfig(
        workspace=args.workspace,
        python_root=args.python_root,
        venv_root=args.venv_root,
        builtin_manifest=args.builtin_manifest,
        native_manifest=args.native_manifest,
        specification=args.specification,
        output=args.output,
    )
    result = StaticG1Resolver(config).run()
    encoded = json.dumps(_jsonable(result), indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if config.output is None:
        print(encoded, end="")
    else:
        config.output.write_text(encoded, encoding="utf-8", newline="\n")
    return 0 if result.g1_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
