"""One NT preseal, then one independent metadata-only verification."""
import json
from tools import _s2nt_private_source_binding as b
from tools import _s2nt_private_preseal_verification as v


def main():
    out = b.preseal_once(b.RUN_ID)
    if (out/"failure.json").exists():
        print((out/"failure.json").read_text())
        return 1
    report = v.verify_once(out)
    print(json.dumps(report))
    return 0 if report["status"] == "S2NT_PRESEAL_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
