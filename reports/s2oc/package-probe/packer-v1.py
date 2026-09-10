"""Bounded ZIP/DEFLATE evidence envelope; standard library, no project imports."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

VERSION = "s2oc.evidence-zip.v1"
MAX_FILES = 160
MAX_INDEX = 65536
MAX_MEMBER = 4194304
MAX_EXPANDED = 16777216
UNPACK_MEMORY_LIMIT = 10485760
CLASSES = ("runtime", "metadata", "sources", "verification", "qualification", "report")


class PackageError(ValueError):
    pass


def require(ok, code):
    if not ok:
        raise PackageError(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def category(name):
    p = PurePosixPath(name)
    if p.name == "record.json": return "runtime"
    if p.name in ("verification.json", "session-verification.json", "verification.claim"): return "verification"
    if p.name in ("source-inventory.json", "session-sources.json"): return "sources"
    if p.name == "session.json": return "metadata"
    if name == "BEFUND.md": return "report"
    if name in ("preregistration.json", "stdout.txt", "stderr.txt", "metrics.json", "result.json", "final-balance.json"):
        return "qualification"
    raise PackageError("UNCLASSIFIED_FILE")


def safe_name(name):
    if type(name) is not str:
        return False
    p = PurePosixPath(name)
    return type(name) is str and bool(name) and not p.is_absolute() and ".." not in p.parts and "\\" not in name and ":" not in name


def create_package(root, destination, names):
    root, destination = Path(root), Path(destination)
    require(not destination.exists(), "PACKAGE_EXISTS")
    require(len(names) <= MAX_FILES and len(set(names)) == len(names), "FILE_COUNT_INVALID")
    objects, files, known = [], [], {}
    total = 0
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=False) as z:
        for name in sorted(names):
            require(safe_name(name), "PATH_INVALID")
            kind = category(name)
            path = root/name
            require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), "PATH_INVALID")
            require(path.stat().st_size <= MAX_MEMBER, "MEMBER_LIMIT")
            raw = path.read_bytes()
            total += len(raw)
            require(len(raw) <= MAX_MEMBER and total <= MAX_EXPANDED, "EXPANDED_LIMIT")
            sha = hashlib.sha256(raw).hexdigest()
            key = (kind, sha)
            if key not in known:
                n = len(objects); known[key] = n
                entry = f"c/{n:04d}"
                info = zipfile.ZipInfo(entry, (1980,1,1,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, raw, compresslevel=9)
                objects.append([entry, kind, len(raw), sha])
            else:
                n = known[key]
                require(objects[n][2] == len(raw), "CONTENT_CONFLICT")
            files.append([name, n])
            del raw
        index = dict(version=VERSION, files=files, objects=objects)
        encoded = canonical(index)
        require(len(encoded) <= MAX_INDEX, "INDEX_LIMIT")
        info = zipfile.ZipInfo("index.json", (1980,1,1,0,0,0)); info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, encoded, compresslevel=9)
    return index


def _verify_package(path, originals=None):
    """Independent ZIP reader: recheck mapping, every expanded byte and originals."""
    path = Path(path)
    require(path.stat().st_size <= MAX_EXPANDED, "PACKAGE_READ_LIMIT")
    with zipfile.ZipFile(path, "r") as z:
        infos = z.infolist()
        require(len(infos) <= MAX_FILES+1 and len({i.filename for i in infos}) == len(infos), "ZIP_MEMBERS_INVALID")
        ii = z.getinfo("index.json")
        require(ii.file_size <= MAX_INDEX, "INDEX_LIMIT")
        index = json.loads(z.read(ii))
        require(set(index) == {"version", "files", "objects"} and index["version"] == VERSION, "INDEX_INVALID")
        files, objects = index["files"], index["objects"]
        require(type(files) is list and type(objects) is list and len(files) <= MAX_FILES and len(objects) <= MAX_FILES, "INDEX_INVALID")
        require(all(type(o) is list and len(o) == 4 for o in objects), "OBJECT_INVALID")
        names, uses = set(), {n: [] for n in range(len(objects))}
        for pair in files:
            require(type(pair) is list and len(pair) == 2, "FILE_BINDING_INVALID")
            name, n = pair
            require(safe_name(name) and name not in names and type(n) is int and n in uses, "FILE_BINDING_INVALID")
            names.add(name); uses[n].append(name)
        require(all(uses.values()), "UNREFERENCED_CONTENT")
        require({i.filename for i in infos} == {"index.json"}|{o[0] for o in objects}, "ZIP_MEMBERS_INVALID")
        stored = dict.fromkeys(CLASSES, 0); expanded = dict.fromkeys(CLASSES, 0)
        unique_expanded = maximum = 0
        for n, obj in enumerate(objects):
            require(type(obj) is list and len(obj) == 4, "OBJECT_INVALID")
            entry, kind, size, sha = obj
            require(entry == f"c/{n:04d}" and kind in CLASSES and type(size) is int and 0 <= size <= MAX_MEMBER, "OBJECT_INVALID")
            require(all(category(name) == kind for name in uses[n]), "CLASS_CHANGED")
            info = z.getinfo(entry)
            require(info.file_size == size and info.compress_type == zipfile.ZIP_DEFLATED and not info.extra and not info.comment, "ZIP_FORM_INVALID")
            with z.open(info) as f:
                raw = f.read(size+1)
                require(len(raw) == size and f.read(1) == b"", "SIZE_CHANGED")
            require(hashlib.sha256(raw).hexdigest() == sha, "HASH_CHANGED")
            unique_expanded += size; maximum = max(maximum, size)
            expanded[kind] += size*len(uses[n])
            require(sum(expanded.values()) <= MAX_EXPANDED and unique_expanded <= MAX_EXPANDED, "EXPANDED_LIMIT")
            stored[kind] += info.compress_size+76+2*len(entry.encode("utf-8"))
            if originals is not None:
                for name in uses[n]:
                    original = Path(originals)/name
                    require(original.resolve().is_relative_to(Path(originals).resolve()), "PATH_INVALID")
                    require(original.read_bytes() == raw, "RESTORATION_CHANGED")
            del raw
        stored["metadata"] += ii.compress_size+76+2*len(ii.filename)+22
        require(sum(stored.values()) == path.stat().st_size, "ZIP_OVERHEAD_UNACCOUNTED")
    with path.open("rb") as f:
        package_digest = hashlib.file_digest(f, "sha256").hexdigest()
    return dict(version=VERSION, sha256=package_digest, files=len(files),
        objects=len(objects), stored=stored, stored_total=sum(stored.values()), expanded=expanded,
        expanded_total=sum(expanded.values()), unique_expanded=unique_expanded, maximum_member=maximum,
        index_expanded=ii.file_size, unpack_memory_limit=UNPACK_MEMORY_LIMIT, restored_exactly=True)


def verify_package(path, originals=None):
    try:
        return _verify_package(path, originals)
    except PackageError:
        raise
    except (zipfile.BadZipFile, KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PackageError("PACKAGE_INVALID") from exc
