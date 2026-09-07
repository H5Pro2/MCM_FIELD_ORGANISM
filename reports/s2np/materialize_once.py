"""Authorized NP materialization plus one independent read-only check, no retry."""

import json

from tools import _s2np_private_source_binding as b
from tools import _s2np_private_receptor_materialization as m
from tools import _s2np_private_materialization_verification as v


def main():
    out, result = m.run_once()
    try:
        verification = v.verify_once(out)
    except Exception as exc:
        verification = dict(run_id=m.RUN_ID, status="NOT_EVALUABLE", phase="READ_ONLY_VERIFICATION",
            verification_calls=1, error_class=type(exc).__name__,
            code=str(exc)[:256] if isinstance(exc, ValueError) else "VERIFICATION_EXECUTION_ERROR")
        b.publish(out / "verification-failure.json", verification)
    print(json.dumps(dict(run_id=m.RUN_ID, status=result["status"], counts=result["counts"],
        failure=result["failure"], record_digest=result["record_digest"], verification=verification)))
    return 0 if result["status"] == "RECEPTOR_NJ_MATERIALIZATION_COMPLETE" and verification["status"] == "S2NP_MATERIALIZATION_VALID" else 1


if __name__ == "__main__":
    raise SystemExit(main())
