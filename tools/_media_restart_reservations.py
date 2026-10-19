"""Finite administrative future slots; physical files always remain in the ledger."""
from dataclasses import dataclass
from pathlib import PurePosixPath

from tools._media_restart_work import require

VERSION = "media.administrative-reservations.v3"


@dataclass(frozen=True)
class Group:
    name: str
    paths: tuple
    limit: int
    closed_by: str


def bind(values):
    result, names, paths = [], set(), set()
    for item in values:
        require(type(item) is dict and set(item) == {"name", "paths", "limit", "closed_by"},
                "MEDIA_RESERVATION_FORM")
        name, cap = item["name"], item["limit"]
        entries, marker = item["paths"], item["closed_by"]
        require(type(name) is str and 0 < len(name) <= 64 and name not in names,
                "MEDIA_RESERVATION_NAME")
        require(type(cap) is int and 0 < cap <= 131072, "MEDIA_RESERVATION_LIMIT")
        require(type(entries) in (tuple, list) and 0 < len(entries) <= 16,
                "MEDIA_RESERVATION_PATHS")
        for path in (*entries, marker):
            require(type(path) is str and 0 < len(path) <= 160 and "\\" not in path
                    and not PurePosixPath(path).is_absolute() and ".." not in PurePosixPath(path).parts
                    and PurePosixPath(path).as_posix() == path, "MEDIA_RESERVATION_PATH")
        require(len(set(entries)) == len(entries) and not (set(entries) & paths),
                "MEDIA_RESERVATION_OVERLAP")
        result.append(Group(name, tuple(entries), cap, marker))
        names.add(name)
        paths.update(entries)
    require(len(result) <= 8, "MEDIA_RESERVATION_COUNT")
    return tuple(result)


def assess(ledger, groups, failure_reserve):
    """Same assessment for current files, proposed publication, and closure.

    Only the final filename consumes a future slot. Its temporary publication
    copy remains additional physical occupancy. A declared terminal marker
    releases unused space; it does not remove any already written bytes.
    """
    files = {row["path"]: row for row in ledger["files"]}
    reservations, violations = [], []
    for group in groups:
        used = sum(files[path]["bytes"] for path in group.paths if path in files)
        closed = group.closed_by in files and files[group.closed_by]["bytes"] > 0
        remaining = 0 if closed else max(0, group.limit-used)
        reservations.append(dict(name=group.name, used=used, limit=group.limit,
                                 closed=closed, remaining=remaining))
        if used > group.limit:
            violations.append("reservation:"+group.name)
    future = sum(row["remaining"] for row in reservations)
    charged = dict(ledger["totals"])
    charged["metadata"] += future+failure_reserve
    charged["total"] += future+failure_reserve
    violations.extend(k for k, cap in ledger["limits"].items() if charged[k] > cap)
    return dict(occupied=ledger["totals"], future=reservations, future_bytes=future,
                primary_failure_reserve=failure_reserve, charged=charged,
                limits=ledger["limits"], violations=violations)
