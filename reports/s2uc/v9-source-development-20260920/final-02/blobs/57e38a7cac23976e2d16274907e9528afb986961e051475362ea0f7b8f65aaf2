"""Read-only import closure for the fixed S2-UC starter; never imports suppliers."""
from __future__ import annotations

import ast
import hashlib
import sys
from importlib import metadata
from pathlib import Path


def _scan(root: Path, entry: str):
    pending = [entry]
    seen = set()
    edges = {}
    external = set()
    lazy_path = root / "mcm_field_organism/root_lazy_exports.py"
    lazy = {}
    if lazy_path.is_file():
        for node in ast.parse(lazy_path.read_text(encoding="utf-8-sig")).body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ROOT_LAZY_EXPORTS" for t in node.targets):
                value = node.value.args[0] if isinstance(node.value, ast.Call) else node.value
                lazy = ast.literal_eval(value)

    def resolve(module):
        parts = module.split(".")
        paths = set()
        for count in range(1, len(parts) + 1):
            initializer = Path(*parts[:count]) / "__init__.py"
            if (root / initializer).is_file():
                paths.add(initializer.as_posix())
        source = Path(*parts).with_suffix(".py")
        if (root / source).is_file():
            paths.add(source.as_posix())
        elif len(parts) == 2 and parts[0] == "mcm_field_organism" and parts[1] in lazy:
            paths.update(resolve("mcm_field_organism." + lazy[parts[1]][0]))
        if not paths and not (root / parts[0]).is_dir():
            external.add(parts[0])
        return paths

    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        edges[name] = set()
        package = name.split("/")[:-1]
        tree = ast.parse((root / name).read_text(encoding="utf-8-sig"))
        dynamic_names = {"__import__", "import_module", "_import_module"}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in {"importlib", "builtins"}:
                dynamic_names.update(alias.asname or alias.name for alias in node.names
                                     if alias.name in {"import_module", "__import__"})
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = ".".join(package[:len(package) - node.level + 1]) if node.level else ""
                module = ".".join(p for p in (base, node.module) if p)
                modules = [module] + [module + "." + alias.name for alias in node.names]
                if any(alias.name == "*" for alias in node.names) and module == "mcm_field_organism":
                    modules.extend("mcm_field_organism." + value[0] for value in lazy.values())
            elif isinstance(node, ast.Call):
                function = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
                if function in dynamic_names:
                    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        module = node.args[0].value
                        if module.startswith("."):
                            raise ValueError("FINAL_DEPENDENCY_DISCOVERY_UNRESOLVED")
                        modules = [module]
                    elif (name == "mcm_field_organism/__init__.py" and function == "_import_module"
                          and ast.unparse(node) == "_import_module(f'.{source_module}', __name__)"):
                        # This package dispatches statically requested exports through
                        # ROOT_LAZY_EXPORTS; resolve() includes those selected modules.
                        continue
                    else:
                        raise ValueError("FINAL_DEPENDENCY_DISCOVERY_UNRESOLVED")
            for module in modules:
                if module:
                    paths = resolve(module)
                    edges[name].update(paths)
                    pending.extend(paths - seen)

    files = []
    for name in sorted(seen):
        data = (root / name).read_bytes()
        files.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    runtimes = []
    for name in sorted(external):
        standard = name in sys.stdlib_module_names
        runtimes.append({"module": name, "kind": "stdlib" if standard else "third-party",
                         "version": sys.version.split()[0] if standard else metadata.version(name)})
    return {"files": files, "external": runtimes,
            "project_source_bytes": sum(item["bytes"] for item in files),
            "imports": {name: sorted(paths) for name, paths in sorted(edges.items())}}


def current():
    """Fixed project and entry: no binding-controlled roots or test switches."""
    return _scan(Path(__file__).resolve().parents[1], "tools/s2uc_run_bound_once.py")
