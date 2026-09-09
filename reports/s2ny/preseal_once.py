"""One authorized source preseal, then one read-only metadata verification."""
import json
from tools import _s2ny_private_source_binding as b
from tools import _s2ny_private_preseal_verification as v


def main():
    out = b.preseal_once(b.RUN_ID)
    if (out/"failure.json").exists():
        print((out/"failure.json").read_text(encoding="ascii"))
        return 1
    result = v.verify_once(out)
    print(json.dumps(result))
    return 0 if result["status"]=="S2NY_PRESEAL_VERIFIED" else 1


if __name__=="__main__":
    raise SystemExit(main())
