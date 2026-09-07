"""One authorized source preseal, then one independent read-only verification."""

import json

from tools import _s2np_private_source_binding as b
from tools import _s2np_private_preseal_verification as v

RUN_ID = "s2np-source-preseal-20260907-01"


def main():
    out = b.preseal_once(RUN_ID)
    if (out / "failure.json").exists():
        print((out / "failure.json").read_text(encoding="ascii"))
        return 1
    try:
        result = v.verify_once(out)
    except Exception as exc:
        result = dict(run_id=RUN_ID, status="NOT_EVALUABLE", phase="READ_ONLY_BINDING_VERIFICATION",
            verification_calls=1, error_class=type(exc).__name__,
            code=str(exc) if isinstance(exc, b.S2NPBindingError) else "VERIFICATION_EXECUTION_ERROR",
            payload_generation_calls=0, main_gate_after=False)
        b.publish(out / "verification-failure.json", result)
        print(json.dumps(result))
        return 1
    print(json.dumps({k: result[k] for k in ("run_id", "status", "source_count", "seal_digest", "verification_digest")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
