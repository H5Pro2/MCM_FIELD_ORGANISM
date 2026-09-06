"""Authorized one-shot S2-NF source preseal, followed by one read-only check."""

import json

from tools import _s2nf_private_source_binding as b
from tools import _s2nf_private_preseal_verification as verification

RUN_ID = "s2nf-source-preseal-20260906-01"


def main():
    out = b.preseal_once(RUN_ID, b.ROOT / "reports/s2nf")
    if (out / "failure.json").exists():
        print((out / "failure.json").read_text(encoding="ascii"))
        return 1
    result = verification.verify_once(out)
    print(json.dumps({k: result[k] for k in ("run_id", "status")}))
    return 0 if result["status"] == "S2NF_PRESEAL_BINDINGS_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
