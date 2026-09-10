"""Bounded ZIP/DEFLATE evidence envelope; standard library, no project imports."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

VERSION = "s2oc.evidence-zip.v3"
MAX_FILES = 160
MAX_INDEX = 65536
MAX_MEMBER = 4194304
MAX_EXPANDED = 16777216
UNPACK_MEMORY_LIMIT = 10485760
CLASSES = ("states", "inputs", "steps", "scans", "nj", "formations", "generations",
           "metadata", "sources", "verification", "qualification", "report")


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


def segments(raw, name):
    """Split only existing JSON byte ranges; never reserialize evidence values."""
    if PurePosixPath(name).name not in ("record.json", "session.json"):
        return [(0,len(raw),category(name))]
    require(raw.isascii(), "CANONICAL_JSON_REQUIRED")
    text = raw.decode("ascii"); decoder = json.JSONDecoder()
    def walk(start, path, default="metadata"):
        value, end = decoder.raw_decode(text,start)
        if len(path)==3 and path[:2] in (("execution","states"),("execution","inputs"),("execution","scans")):
            return [(start,end,path[1])],end
        if len(path)==3 and path[:2]==("execution","source_receipts"):
            return [(start,end,"nj" if value["nj"] is not None else "metadata")],end
        if len(path)==2 and path[0]=="failed_prefix_steps":
            return [(start,end,"steps")],end
        if len(path)==4 and path[:2]==("execution","rows") and path[3] in ("formation","generations"):
            kind="metadata" if value is None else "formations" if path[3]=="formation" else "generations"
            return [(start,end,kind)],end
        row = len(path)==3 and path[:2]==("execution","rows")
        if row: default="steps"
        descend = not path or path==("execution",) or path in (("execution","states"),("execution","inputs"),
            ("execution","scans"),("execution","rows"),("execution","source_receipts"),("failed_prefix_steps",)) or row
        if not descend or not isinstance(value,(dict,list)):
            return [(start,end,default)],end
        spans=[]; cursor=start+1; previous=start
        keys=list(value) if isinstance(value,dict) else range(len(value))
        for key in keys:
            if cursor>start+1: cursor+=1
            if isinstance(value,dict):
                _,cursor=decoder.raw_decode(text,cursor); cursor+=1
            prefix_kind="metadata" if row and key in ("formation","generations") else default
            spans.append((previous,cursor,prefix_kind))
            nested,cursor=walk(cursor,path+(key,),default)
            spans.extend(nested); previous=cursor
        spans.append((previous,end,default))
        return spans,end
    spans,end=walk(0,())
    require(end==len(raw), "CANONICAL_JSON_REQUIRED")
    return [(a,z,k) for a,z,k in spans if z>a]


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
            groups={}; ranges=[]
            for a,e,k in segments(raw,name):
                buf=groups.setdefault(k,bytearray()); offset=len(buf)
                buf.extend(raw[a:e]); ranges.append([k,offset,e-a])
            ids={}
            for k,buf in groups.items():
                sha=hashlib.sha256(buf).hexdigest(); key=(k,sha)
                if key not in known:
                    n=len(objects); known[key]=n
                    require(n<MAX_FILES,"OBJECT_LIMIT")
                    entry=f"c/{n:04d}"
                    info=zipfile.ZipInfo(entry,(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
                    z.writestr(info,buf,compresslevel=9)
                    objects.append([entry,k,len(buf),sha])
                else:
                    n=known[key]; require(objects[n][2]==len(buf),"CONTENT_CONFLICT")
                ids[k]=n
            files.append([name,kind,len(raw),hashlib.sha256(raw).hexdigest(),[[ids[k],o,n] for k,o,n in ranges]])
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
        names, used = set(),set()
        for row in files:
            require(type(row) is list and len(row)==5,"FILE_BINDING_INVALID")
            name,kind,size,sha,parts=row
            require(safe_name(name) and name not in names and category(name)==kind and type(size) is int
                and 0<=size<=MAX_MEMBER and type(parts) is list,"FILE_BINDING_INVALID")
            names.add(name)
            for part in parts:
                require(type(part) is list and len(part)==3 and all(type(n) is int for n in part),"PART_INVALID")
                n,o,count=part
                require(0<=n<len(objects) and o>=0 and count>=0 and o+count<=objects[n][2],"PART_INVALID")
                used.add(n)
        require(used==set(range(len(objects))),"UNREFERENCED_CONTENT")
        require({i.filename for i in infos} == {"index.json"}|{o[0] for o in objects}, "ZIP_MEMBERS_INVALID")
        stored = dict.fromkeys(CLASSES, 0); expanded = dict.fromkeys(CLASSES, 0)
        unique_expanded = maximum = 0
        for n, obj in enumerate(objects):
            require(type(obj) is list and len(obj) == 4, "OBJECT_INVALID")
            entry, kind, size, sha = obj
            require(entry == f"c/{n:04d}" and kind in CLASSES and type(size) is int and 0 <= size <= MAX_MEMBER, "OBJECT_INVALID")
            info = z.getinfo(entry)
            require(info.file_size == size and info.compress_type == zipfile.ZIP_DEFLATED and not info.extra and not info.comment, "ZIP_FORM_INVALID")
            unique_expanded += size; maximum = max(maximum, size)
            require(unique_expanded <= MAX_EXPANDED, "EXPANDED_LIMIT")
            stored[kind] += info.compress_size+76+2*len(entry.encode("utf-8"))
        work=0
        for name,kind,size,sha,parts in files:
            cache={}; data=None
            for n in sorted({p[0] for p in parts}):
                entry,k,length,h=objects[n]
                work+=length
                require(work<=MAX_EXPANDED,"UNPACK_WORK_LIMIT")
                with z.open(entry) as f:
                    data=f.read(length+1)
                    require(len(data)==length and f.read(1)==b"","SIZE_CHANGED")
                require(hashlib.sha256(data).hexdigest()==h,"HASH_CHANGED")
                cache[n]=data
            require(sum(map(len,cache.values()))<=MAX_MEMBER,"UNPACK_MEMORY_LIMIT")
            restored=bytearray()
            for n,o,count in parts:
                restored.extend(cache[n][o:o+count]); expanded[objects[n][1]]+=count
                require(len(restored)<=size,"SIZE_CHANGED")
            require(len(restored)==size and hashlib.sha256(restored).hexdigest()==sha,"RESTORATION_CHANGED")
            if originals is not None:
                original=Path(originals)/name
                require(original.resolve().is_relative_to(Path(originals).resolve()),"PATH_INVALID")
                with original.open("rb") as f:
                    for offset in range(0,size,65536):
                        require(f.read(min(65536,size-offset))==restored[offset:offset+65536],"RESTORATION_CHANGED")
                    require(f.read(1)==b"","RESTORATION_CHANGED")
            require(sum(expanded.values())<=MAX_EXPANDED,"EXPANDED_LIMIT")
            del cache,restored,data
        stored["metadata"] += ii.compress_size+76+2*len(ii.filename)+22
        require(sum(stored.values()) == path.stat().st_size, "ZIP_OVERHEAD_UNACCOUNTED")
    with path.open("rb") as f:
        package_digest = hashlib.file_digest(f, "sha256").hexdigest()
    return dict(version=VERSION, sha256=package_digest, files=len(files),
        objects=len(objects), stored=stored, stored_total=sum(stored.values()), expanded=expanded,
        expanded_total=sum(expanded.values()), unique_expanded=unique_expanded, maximum_member=maximum,
        decompressed_bytes=work,
        index_expanded=ii.file_size, unpack_memory_limit=UNPACK_MEMORY_LIMIT, restored_exactly=True)


def verify_package(path, originals=None):
    try:
        return _verify_package(path, originals)
    except PackageError:
        raise
    except (zipfile.BadZipFile, KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PackageError("PACKAGE_INVALID") from exc
