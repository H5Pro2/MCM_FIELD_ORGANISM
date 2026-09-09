"""One NW preseal, then one independent read-only metadata verification."""
import json
from tools import _s2nw_private_source_binding as b
from tools import _s2nw_private_preseal_verification as v


def main():
    out = b.preseal_once(b.RUN_ID)
    if (out/"failure.json").exists():
        print((out/"failure.json").read_text(encoding="ascii"))
        return 1
    result = v.verify_once(out)
    print(json.dumps(result))
    return 0 if result["status"] == "S2NW_PRESEAL_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
