"""One NH preseal followed by one independent, read-only binding check."""

import json
from tools import _s2nh_private_source_binding as b
from tools import _s2nh_private_preseal_verification as v


def main():
    out=b.preseal_once()
    if (out/"failure.json").exists():
        print((out/"failure.json").read_text(encoding="ascii"))
        return 1
    result=v.verify_once(out)
    print(json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="S2NH_PRESEAL_BINDINGS_VERIFIED" else 1


if __name__=="__main__":
    raise SystemExit(main())
