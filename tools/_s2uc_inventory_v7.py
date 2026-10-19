"""Fixed starter + bound-test closure. No project imports or source execution."""
from __future__ import annotations

import ast
import hashlib
import platform
import sys
from importlib import metadata
from pathlib import Path

from tools import _s2uc_dependencies as discovery
from tools._s2uc_resource_contract_v7 import _need, _same_typed

ROOT = Path(__file__).resolve().parents[1]
TESTS = (
    "tests/test_s2ub_candidate_confirmation.py",
    "tests/test_s2uc_neutral_connection.py",
    "tests/test_s2uc_materialization_connection.py",
    "tests/test_s2uc_resource_contract_v7.py",
    "tests/test_s2uc_prestart_v7.py",
    "tests/test_s2uc_publication_v7.py",
)
ENTRIES = ("tools/s2uc_run_bound_once.py",) + TESTS
VERSION = "s2uc.dependency-inventory.v7"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_file(root, name):
    """Exact spelling, no links, junctions, traversal, ADS or drive-relative paths."""
    _need(type(name) is str and bool(name) and "\\" not in name and ":" not in name,
          "V7_PATH_INVALID")
    parts = name.split("/")
    _need(all(part not in ("", ".", "..") for part in parts), "V7_PATH_INVALID")
    root = Path(root)
    _need(root.is_dir() and not root.is_symlink() and not root.is_junction(), "V7_ROOT_INVALID")
    path = root
    for part in parts:
        _need(part in {p.name for p in path.iterdir()}, "V7_FILE_MISSING_OR_NONCANONICAL")
        path = path / part
        _need(not path.is_symlink() and not path.is_junction(), "V7_FILE_ALIAS")
    _need(path.is_file() and path.resolve().is_relative_to(root.resolve()), "V7_PATH_INVALID")
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    _need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
          (after.st_dev, after.st_ino, len(data), after.st_mtime_ns), "V7_FILE_CHANGED")
    return {"path": name, "bytes": len(data), "sha256": sha(data)}, data, (after.st_dev, after.st_ino)


def runtime_identity(external):
    """Hash installed distribution files, not merely a declared version/RECORD.

    External bytes are explicitly outside C. This is an installation identity,
    not a RAM bound or an assertion that the entire host environment is sealed.
    """
    executable = Path(sys.executable).resolve()
    interpreter = {"path": executable.as_posix(), "sha256": sha(executable.read_bytes()),
                   "version": sys.version, "implementation": sys.implementation.name,
                   "cache_tag": sys.implementation.cache_tag, "platform": platform.platform()}
    distributions = []
    for module in sorted({r["module"] for r in external if r["kind"] == "third-party"}):
        dist = metadata.distribution(module)
        _need(bool(dist.files), "V7_EXTERNAL_FILES_MISSING")
        digest = hashlib.sha256()
        count = total = 0
        # Bytecode caches are generated at import time, not stable install evidence.
        for item in sorted(dist.files, key=str):
            if str(item).endswith(".pyc"):
                continue
            path = Path(dist.locate_file(item))
            _need(path.is_file(), "V7_EXTERNAL_FILES_MISSING")
            data = path.read_bytes()
            digest.update((str(item) + "\0" + str(len(data)) + "\0" + sha(data) + "\n").encode())
            count += 1
            total += len(data)
        distributions.append({"module": module, "distribution": dist.metadata["Name"],
                              "version": dist.version, "location": str(dist.locate_file("")),
                              "files": count, "installed_bytes": total, "files_sha256": digest.hexdigest()})
    return {"interpreter": interpreter, "modules": external, "distributions": distributions,
            "scope": "external installation identity; outside project C; process memory unmeasured"}


def _resolved_imports(root, rows):
    """Reject vanished project modules; discovery must not silently omit them.

    A from-import can name a declared symbol, a submodule or a registered lazy
    export. Namespace packages have no undeclared attributes to fall back to.
    """
    local = {"tools", "tests", "mcm_field_organism"}
    def source(module):
        base = root.joinpath(*module.split("."))
        return base.with_suffix(".py") if base.with_suffix(".py").is_file() else base / "__init__.py"
    def exists(module):
        return source(module).is_file() or root.joinpath(*module.split(".")).is_dir()
    symbols = {}
    def declared(module):
        if module not in symbols:
            names = set()
            path = source(module)
            if path.is_file():
                for node in ast.walk(ast.parse(path.read_bytes())):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        names.add(node.name)
                    elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                        names.add(node.id)
                    elif isinstance(node, ast.alias):
                        names.add(node.asname or node.name.split(".")[0])
            symbols[module] = names
        return symbols[module]
    lazy = {}
    for node in ast.parse((root / "mcm_field_organism/root_lazy_exports.py").read_bytes()).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ROOT_LAZY_EXPORTS" for t in node.targets):
            lazy = ast.literal_eval(node.value.args[0])
    for row in rows:
        package = row["path"].split("/")[:-1]
        tree = ast.parse((root / row["path"]).read_bytes())
        dynamic = {"__import__", "import_module", "_import_module"}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in {"importlib", "builtins"}:
                dynamic.update(a.asname or a.name for a in node.names if a.name in dynamic)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in local:
                        _need(exists(alias.name), "V7_PROJECT_IMPORT_MISSING")
            elif isinstance(node, ast.ImportFrom):
                base = ".".join(package[:len(package) - node.level + 1]) if node.level else ""
                module = ".".join(p for p in (base, node.module) if p)
                if module.split(".")[0] not in local:
                    continue
                _need(exists(module), "V7_PROJECT_IMPORT_MISSING")
                for alias in node.names:
                    if alias.name == "*":
                        if module == "mcm_field_organism":
                            _need(all(exists("mcm_field_organism." + v[0]) for v in lazy.values()),
                                  "V7_PROJECT_IMPORT_MISSING")
                        continue  # discovery expands the registered lazy exports.
                    if module == "mcm_field_organism" and alias.name in lazy:
                        _need(exists("mcm_field_organism." + lazy[alias.name][0]), "V7_PROJECT_IMPORT_MISSING")
                    else:
                        _need(exists(module + "." + alias.name) or alias.name in declared(module),
                              "V7_PROJECT_IMPORT_MISSING")
            elif isinstance(node, ast.Call):
                function = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
                if function in dynamic and node.args and isinstance(node.args[0], ast.Constant):
                    module = node.args[0].value
                    if isinstance(module, str) and module.split(".")[0] in local:
                        _need(exists(module), "V7_PROJECT_IMPORT_MISSING")


def current(project_root=ROOT):
    """The root is injectable for isolated tests only; the starter always uses ROOT."""
    return _collect(project_root, ENTRIES, VERSION)


def _collect(project_root, entries, version):
    root = Path(project_root)
    files = {}
    external = {}
    identities = {}
    for name in ("tests/__init__.py", "mcm_field_organism/__init__.py"):
        read_file(root, name)
    for entry in entries:
        read_file(root, entry)
        scan = discovery._scan(root, entry)
        for row in scan["files"]:
            actual, _, identity = read_file(root, row["path"])
            _need(_same_typed(actual, row), "V7_FILE_CHANGED")
            _need(identity not in identities or identities[identity] == row["path"], "V7_FILE_ALIAS")
            identities[identity] = row["path"]
            files[row["path"]] = {**actual, "category": "code"}
        for row in scan["external"]:
            external[row["module"]] = row
    rows = [files[name] for name in sorted(files)]
    _resolved_imports(root, rows)
    return {"version": version, "entries": list(entries), "files": rows,
            "code_bytes": sum(row["bytes"] for row in rows),
            "external": runtime_identity([external[name] for name in sorted(external)])}
