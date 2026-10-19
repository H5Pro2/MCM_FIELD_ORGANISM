"""Finite administrative publication plans; no media or state processing."""
from dataclasses import dataclass, replace
from fnmatch import fnmatchcase

from tools import _media_restart_reservations as r
from tools import _media_checkpoint_budget_profile as profiles

VERSION = "media.publication-plan.v1"
CATEGORIES = ("metadata", "sources", "verification", "native", "field", "nj", "formations", "generations")


class PlanError(ValueError):
    def __init__(self, code, details=None):
        self.code, self.details = code, details
        super().__init__(code)


def need(ok, code, details=None):
    if not ok:
        raise PlanError(code, details)


def extend(ledger, rows):
    result = dict(ledger, files=[*ledger["files"], *rows], totals=dict(ledger["totals"]))
    for row in rows:
        need(row["category"] in CATEGORIES and type(row["bytes"]) is int and row["bytes"] >= 0,
             "PUBLICATION_ROW_INVALID")
        category, size = row["category"], row["bytes"]
        result["totals"][category] = result["totals"].get(category, 0)+size
        result["totals"]["total"] += size
        if category in ("sources", "nj", "formations", "generations"):
            result["totals"]["shared"] += size
    return result


def transaction(ledger, rows, success_groups, failure_groups, failure_bytes):
    """Same arithmetic for a projected and a measured publication.

    Keep the existing protected reserve in success. Failure can happen before,
    during, or after linking; already written prefix/candidate bytes stay.
    Error copies replace their reserve, never add a second reserve to them.
    """
    profiles.check_ledger(ledger)
    need(type(failure_bytes) is int and failure_bytes >= 0, "PUBLICATION_FAILURE_RESERVE")
    success = r.assess(extend(ledger, rows), success_groups, 2*failure_bytes)
    errors = []
    for cut in range(len(rows)+1):
        error = [dict(path="__primary_failure__"+str(i), category="metadata", bytes=failure_bytes)
                 for i in range(2)]
        errors.append(r.assess(extend(ledger, [*rows[:cut], *error]), failure_groups, 0))
    return dict(success=success, failure=errors,
        violations=sorted(set(success["violations"]).union(*(set(x["violations"]) for x in errors))))


def full_layout(profile_digest=None, segmented=False):
    """Required publications of the fixed reference/suspend19/restore20 path."""
    layout = {} if profile_digest is None else {"budget-profile.json": ("metadata", 1)}
    layout["run.claim"] = ("metadata", 1)
    for stage, count in (("reference", 20), ("suspend19", 19), ("restore20", 20)):
        for suffix in (".stdout", ".stderr"):
            layout[stage+suffix] = ("metadata", 1)
        save = stage == "suspend19"
        root = stage+("/checkpoint.json" if save else "/record.json")
        core = root+("#/prefix" if save else "#/core")
        layout[stage+".claim"] = ("metadata", 1)
        if stage == "restore20":
            layout["suspend19/checkpoint.json.consumed"] = ("metadata", 1)
        if save:
            layout[root+"#/manifest"] = ("metadata", 1)
            layout[root+"#/field"] = ("field", 1)
        for name in ("runtime_config", "binding", "initial"):
            layout[core+"/"+name] = ("metadata", 1)
        for name, category, n in (("inputs", "native", count), ("source_receipts", "nj", count),
                                  ("rows", "native", count), ("states", "native", count+1)):
            if name == "rows":
                for sub in ("formation", "generations"):
                    layout[core+"/rows/*/"+sub] = ("formations" if sub == "formation" else "generations", count)
            layout[core+"/"+name+"/*"] = (category, n)
            layout[core+"/"+name] = ("metadata", 1)
        layout[core+"/scans"] = ("metadata", 1)
        layout[core] = ("metadata", 1)
        layout[root+"#/selections/*"] = ("metadata", count)
        layout[root+"#/selections"] = ("metadata", 1)
        if not save:
            layout[root+"#/field"] = ("field", 1)
        for path in (root, stage+"/player-close.json", stage+"-process.json"):
            layout[path] = ("metadata", 1)
    layout["restore20-verification.claim"] = ("metadata", 1)
    if segmented:
        layout["restore20/replay-*.json"] = ("metadata", 20)
    layout["restore20-verification.json#"] = ("verification", 1)
    for name in ("restore20-verification.json", "evaluation.json", "result.json", "REPORT.md", "balance.json"):
        layout[name] = ("metadata", 1)
    return layout


def evaluation_layout():
    layout = {"budget-profile.json": ("metadata", 1), "run.claim": ("metadata", 1)}
    for n in range(20):
        layout["evaluation.json#/rows/"+str(n)] = ("native", 1)
    layout["evaluation.json#/rows"] = ("metadata", 1)
    for name in ("evaluation.json", "origin.json", "result.json", "REPORT.md", "balance.json"):
        layout[name] = ("metadata", 1)
    return layout


@dataclass(frozen=True)
class Plan:
    positions: tuple
    scope: str
    profile_digest: str | None = None

    @classmethod
    def bind(cls, value):
        need(type(value) is dict and value.get("version") == VERSION, "PUBLICATION_PLAN_REQUIRED")
        need(value.get("scope") in ("FULL_RESTART", "FULL_REPLAY_RESTART", "POSTCHECKPOINT_EVALUATION_V1", "NEUTRAL_ADMIN"), "PUBLICATION_PLAN_SCOPE")
        profile_digest = value.get("budget_profile_digest")
        need(profile_digest is None or profile_digest == profiles.digest(), "PUBLICATION_PROFILE_INVALID")
        entries = value.get("positions")
        need(type(entries) is list and 0 < len(entries) <= 128, "PUBLICATION_PLAN_FORM")
        result = []
        for item in entries:
            need(type(item) is dict and set(item) == {"id", "category", "count", "lower", "upper"},
                 "PUBLICATION_POSITION_INVALID")
            key, category, count, lower, upper = (item[k] for k in ("id", "category", "count", "lower", "upper"))
            need(type(key) is str and 0 < len(key) <= 180 and ".." not in key and category in CATEGORIES
                and type(count) is int and 1 <= count <= 64 and type(lower) is int and lower >= 0
                and (upper is None or type(upper) is int and lower <= upper <= 4194304),
                "PUBLICATION_POSITION_INVALID")
            need(key not in [x[0] for x in result], "PUBLICATION_POSITION_DUPLICATE")
            result.append((key, category, count, lower, upper))
        if value["scope"] in ("FULL_RESTART", "FULL_REPLAY_RESTART"):
            layout = full_layout(profile_digest, value["scope"] == "FULL_REPLAY_RESTART")
            need({x[0]: (x[1], x[2]) for x in result} == layout, "PUBLICATION_POSITION_MISSING")
            need([x[0] for x in result] == list(layout), "PUBLICATION_ORDER_INVALID")
        if value["scope"] == "POSTCHECKPOINT_EVALUATION_V1":
            need({x[0]: (x[1], x[2]) for x in result} == evaluation_layout(), "PUBLICATION_POSITION_MISSING")
            need([x[0] for x in result] == list(evaluation_layout()), "PUBLICATION_ORDER_INVALID")
        return cls(tuple(result), value["scope"], profile_digest)

    def offer(self, role, category, size):
        hits = [x for x in self.positions if fnmatchcase(role, x[0]) and category == x[1]]
        # Wildcards may only stand for one path segment, not descendant roles.
        hits = [x for x in hits if x[0].count("/") == role.count("/")]
        need(len(hits) == 1, "PUBLICATION_POSITION_MISSING", dict(role=role, category=category))
        slot = hits[0]
        need(slot[4] is not None and slot[3] <= size <= slot[4], "PUBLICATION_POSITION_SIZE",
             dict(role=role, bytes=size, lower=slot[3], upper=slot[4]))
        return slot

    def preflight(self, ledger, success_groups, failure_groups, failure_bytes):
        need(ledger.get("budget_profile_digest") == self.profile_digest, "PUBLICATION_LEDGER_PROFILE")
        if self.profile_digest is not None:
            return self._profile_preflight(ledger, success_groups, failure_groups, failure_bytes)
        outcomes = []
        for upper in (False, True):
            current = ledger
            for role, category, count, low, high in self.positions:
                if upper and high is None:
                    need(False, "PUBLICATION_PLAN_UNBOUNDED", dict(role=role, phase="PREFLIGHT", completed=0))
                size = high if upper else low
                if self.profile_digest is not None:
                    profiles.check_item(category, size)
                for ordinal in range(count):
                    path = role if count == 1 else role.replace("*", str(ordinal))
                    final = dict(path=path, category=category, bytes=size)
                    temporary = dict(final, path=path+".pending")
                    decision = transaction(current, [temporary, final], success_groups, failure_groups, failure_bytes)
                    need(not decision["violations"], "PUBLICATION_PREFLIGHT_BUDGET",
                         dict(role=role, bound="upper" if upper else "lower", phase="PREFLIGHT", completed=0,
                              decision=decision))
                    current = extend(current, [final])
                    outcomes.append(dict(role=role, ordinal=ordinal, bound="upper" if upper else "lower",
                                         decision=decision))
            if upper and self.scope == "FULL_RESTART":
                # Publication order within repeated rows may vary. Bound every
                # temporary against all final upper sizes, without assuming dedup.
                # Keep unspent group space, but never count spent space twice.
                held_success = tuple(replace(g, closed_by="__unreleased__") for g in success_groups)
                held_failure = tuple(replace(g, closed_by="__unreleased__") for g in failure_groups)
                for role, category, _, _, size in self.positions:
                    temporary = dict(path=role+".pending-envelope", category=category, bytes=size)
                    decision = transaction(current, [temporary], held_success, held_failure, failure_bytes)
                    need(not decision["violations"], "PUBLICATION_PREFLIGHT_BUDGET",
                         dict(role=role, bound="all-final-upper-plus-temporary", phase="PREFLIGHT", completed=0,
                              decision=decision))
                    outcomes.append(dict(role=role, bound="all-final-upper-plus-temporary", decision=decision))
        return outcomes

    def _profile_preflight(self, ledger, success_groups, failure_groups, failure_bytes):
        """All final bounds plus each temporary; joint group caps count once.

        Held groups cover every allocation among their members. Final members
        are not also inserted as independent full-cap files. Actual writes still
        consume a group only through their real final path in reservations.assess.
        """
        profiles.check_ledger(ledger)
        need(success_groups == failure_groups, "PUBLICATION_GROUP_ALTERNATIVES_UNBOUND")
        groups = {g.name: g for g in (*success_groups, *failure_groups)}
        member_caps = {path: g.limit for g in groups.values() for path in g.paths}
        finals, temporary = [], []
        for role, category, count, _, high in self.positions:
            need(high is not None, "PUBLICATION_PLAN_UNBOUNDED", dict(role=role, phase="PREFLIGHT", completed=0))
            profiles.check_item(category, high)
            if role in member_caps:
                need(category == "metadata" and count == 1 and high <= member_caps[role], "PUBLICATION_GROUP_BINDING")
            else:
                finals.extend(dict(path=role.replace("*", str(i)), category=category, bytes=high) for i in range(count))
            temporary.append(dict(path=role+".pending-envelope", category=category, bytes=high))
        current = extend(ledger, finals)
        held_success = tuple(replace(g, closed_by="__unreleased__") for g in success_groups)
        held_failure = tuple(replace(g, closed_by="__unreleased__") for g in failure_groups)
        outcomes = []
        for item in temporary:
            decision = transaction(current, [item], held_success, held_failure, failure_bytes)
            need(not decision["violations"], "PUBLICATION_PREFLIGHT_BUDGET",
                 dict(role=item["path"], bound="joint-upper-plus-temporary", phase="PREFLIGHT", completed=0, decision=decision))
            outcomes.append(dict(role=item["path"], bound="joint-upper-plus-temporary", decision=decision))
        return outcomes
