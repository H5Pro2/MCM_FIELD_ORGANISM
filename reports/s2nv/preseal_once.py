"""One NV preseal and exactly one independent metadata-only verification."""
import json
from tools import _s2nv_private_source_binding as b
from tools import _s2nv_private_preseal_verification as v


def main():
    out = b.preseal_once(b.RUN_ID)
    if (out/"failure.json").exists():
        print((out/"failure.json").read_text(encoding="ascii"))
        return 1
    result = v.verify_once(out)
    print(json.dumps(result))
    return 0 if result["status"]=="S2NV_PRESEAL_VERIFIED" else 1


if __name__=="__main__":
    raise SystemExit(main())
