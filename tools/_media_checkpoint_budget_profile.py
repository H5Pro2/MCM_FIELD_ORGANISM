"""One explicit checkpoint evidence profile; historical defaults stay elsewhere."""
from dataclasses import dataclass
import hashlib
import json

VERSION = "media.checkpoint-evidence-budget.v1"
PROFILE = "CHECKPOINT_COMPARISON_24M_V1"
LIMITS = (("total", 25165824), ("metadata", 3145728), ("sources", 524288),
          ("shared", 786432), ("verification", 262144))
# Historical two-copy publication ceilings, independent of aggregate expansion.
ITEM_LIMITS = dict(metadata=61440, native=2093056, field=2093056, sources=163840,
                   verification=131072, nj=196608, formations=196608, generations=196608)


class BudgetProfileError(ValueError):
    def __init__(self, code, details=None):
        self.code, self.details = code, details
        super().__init__(code)


def require(ok, code, details=None):
    if not ok:
        raise BudgetProfileError(code, details)


def payload():
    return dict(version=VERSION, profile=PROFILE, limits=dict(LIMITS))


def digest():
    raw = json.dumps(payload(), sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Profile:
    profile: str = PROFILE

    def __post_init__(self):
        require(self.profile == PROFILE, "MEDIA_BUDGET_PROFILE_INVALID")

    @property
    def limits(self):
        return dict(LIMITS)


def bind(value):
    if value is None:
        return None
    require(type(value) is dict and value == payload() and type(value["limits"]) is dict
            and all(type(v) is int for v in value["limits"].values()), "MEDIA_BUDGET_PROFILE_INVALID")
    return Profile()


def check_item(category, amount):
    require(category in ITEM_LIMITS and type(amount) is int and 0 <= amount <= ITEM_LIMITS[category],
            "MEDIA_HISTORICAL_ITEM_LIMIT", dict(category=category, bytes=amount, limit=ITEM_LIMITS.get(category)))


def check_ledger(ledger):
    if "budget_profile_digest" in ledger:
        require(ledger["budget_profile_digest"] == digest() and ledger["limits"] == dict(LIMITS),
                "MEDIA_BUDGET_LEDGER_BINDING")
